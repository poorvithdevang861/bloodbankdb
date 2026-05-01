from flask import Flask, render_template, request, redirect, session
import oracledb
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")

DB_USER = os.getenv("DB_USER", "system")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DSN = os.getenv("DB_DSN", "localhost/XE")
VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
BLOOD_GROUP_OPTIONS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
VALID_GENDERS = {"M", "F", "O"}
DONOR_RULES = {
    "M": {"min_age": 18, "max_age": 60, "min_weight": 45},
    "F": {"min_age": 18, "max_age": 60, "min_weight": 45},
    "O": {"min_age": 18, "max_age": 60, "min_weight": 45},
}

connection = None


def get_connection():
    global connection
    if connection is None:
        connection = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        )
    return connection


def db_error_response(exc):
    return f"Database unavailable: {exc}. Check Oracle service and DSN ({DB_DSN}).", 503


def friendly_db_error(exc, fallback_message="Something went wrong while saving data."):
    if isinstance(exc, oracledb.DatabaseError) and exc.args:
        err = exc.args[0]
        code = getattr(err, "code", None)
        message = str(err)
        if code == 1:
            return "This ID already exists. Please use a different ID."
        if code == 2290:
            return "Input failed a database rule check. Please verify age, weight, blood group, or gender."
        if code == 2291:
            return "Referenced record does not exist (for example, patient ID)."
        if code == 2289:
            return "Database sequence is missing. Please rerun schema setup scripts."
        if code == 904:
            return "Database schema is outdated (missing/renamed column). Please rerun setup scripts."
        if code == 942:
            return "Required database table is missing. Please rerun setup scripts."
        if code == 1400:
            return "A required field is missing. Please fill all mandatory values."
        if code == 28000:
            return "Database account is locked. Ask admin to unlock the Oracle user."
        if code == 20001:
            return "Donation blocked: minimum 90 days gap between donations is required."
        if "ORA-20001" in message:
            return "Donation blocked: minimum 90 days gap between donations is required."
        if "ORA-20002" in message:
            return "Donation blood group must match the donor blood group."
        if "ORA-20010" in message:
            return "Donor eligibility failed (age 18-60 and minimum 45 kg required)."
        if "ORA-20011" in message:
            return "Donor eligibility failed (age 18-60 and minimum 45 kg required)."
        if "ORA-20012" in message:
            return "Donor eligibility failed (age 18-60 and minimum 45 kg required)."
        if "ORA-02289" in message:
            return "Database sequence is missing. Please rerun schema setup scripts."
        if "ORA-00904" in message:
            return "Database schema is outdated (missing/renamed column). Please rerun setup scripts."
        if "ORA-00942" in message:
            return "Required database table is missing. Please rerun setup scripts."
        if "ORA-28000" in message:
            return "Database account is locked. Ask admin to unlock the Oracle user."
    return fallback_message


def normalize_blood_group(value):
    if value is None:
        return ""
    return value.strip().upper()


def normalize_gender(value):
    if value is None:
        return ""
    return value.strip().upper()


def get_donor_options():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT donor_id, name, blood_group FROM donor ORDER BY donor_id")
    return cursor.fetchall()


def get_patient_options():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, name, blood_group FROM patient ORDER BY patient_id")
    return cursor.fetchall()

# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "staff" and password == "123":
            session['role'] = 'staff'
            return redirect('/')
        elif username == "doctor" and password == "123":
            session['role'] = 'doctor'
            return redirect('/')
        else:
            return "Invalid login"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ================= HOME =================

@app.route('/')
def index():
    if 'role' not in session:
        return redirect('/login')
    return render_template('index.html', role=session['role'])


# ================= DONOR =================

@app.route('/add_donor', methods=['GET', 'POST'])
def add_donor():
    if session.get('role') != 'staff':
        return "Access Denied"

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = normalize_gender(request.form['gender'])
        weight = request.form['weight']
        blood = normalize_blood_group(request.form['blood'])
        phone = request.form['phone']
        form_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "weight": weight,
            "blood": blood,
            "phone": phone
        }

        try:
            age_value = int(age)
        except (TypeError, ValueError):
            return render_template(
                'add_donor.html',
                error="Age must be a valid number.",
                form_data=form_data,
                blood_groups=BLOOD_GROUP_OPTIONS
            ), 400

        try:
            weight_value = float(weight)
        except (TypeError, ValueError):
            return render_template(
                'add_donor.html',
                error="Weight must be a valid number in kg.",
                form_data=form_data,
                blood_groups=BLOOD_GROUP_OPTIONS
            ), 400

        if gender not in VALID_GENDERS:
            return render_template(
                'add_donor.html',
                error="Gender must be M, F, or O.",
                form_data=form_data,
                blood_groups=BLOOD_GROUP_OPTIONS
            ), 400

        rules = DONOR_RULES[gender]
        if age_value < rules["min_age"] or age_value > rules["max_age"]:
            return render_template(
                'add_donor.html',
                error=f"Donor age for gender {gender} must be between {rules['min_age']} and {rules['max_age']}.",
                form_data=form_data,
                blood_groups=BLOOD_GROUP_OPTIONS
            ), 400

        if weight_value < rules["min_weight"]:
            return render_template(
                'add_donor.html',
                error=f"Minimum donor weight for gender {gender} is {rules['min_weight']} kg.",
                form_data=form_data,
                blood_groups=BLOOD_GROUP_OPTIONS
            ), 400

        if blood not in VALID_BLOOD_GROUPS:
            return render_template(
                'add_donor.html',
                error="Invalid blood group. Use one of: A+, A-, B+, B-, AB+, AB-, O+, O-.",
                form_data=form_data,
                blood_groups=BLOOD_GROUP_OPTIONS
            ), 400

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO donor (donor_id, name, age, gender, weight_kg, blood_group, phone)
                VALUES (donor_seq.NEXTVAL, :1, :2, :3, :4, :5, :6)
                """,
                (name, age_value, gender, weight_value, blood, phone)
            )
            cursor.execute(
                """
                MERGE INTO blood_bank bb
                USING (SELECT :1 AS blood_group FROM dual) src
                ON (bb.blood_group = src.blood_group)
                WHEN MATCHED THEN
                    UPDATE SET bb.units_available = bb.units_available + 1
                WHEN NOT MATCHED THEN
                    INSERT (blood_group, units_available) VALUES (src.blood_group, 1)
                """,
                (blood,)
            )
            conn.commit()
        except Exception as exc:
            message = friendly_db_error(
                exc,
                "Unable to add donor right now. Please verify values and try again."
            )
            return render_template('add_donor.html', error=message, form_data=form_data, blood_groups=BLOOD_GROUP_OPTIONS), 400

        return redirect('/view_donors')

    return render_template('add_donor.html', blood_groups=BLOOD_GROUP_OPTIONS)


@app.route('/view_donors')
def view_donors():
    if session.get('role') != 'staff':
        return "Access Denied"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM donor")
        donors = cursor.fetchall()
    except Exception as exc:
        return db_error_response(exc)
    return render_template('view_donors.html', donors=donors)


@app.route('/delete/<int:id>')
def delete_donor(id):
    if session.get('role') != 'staff':
        return "Access Denied"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT blood_group FROM donor WHERE donor_id = :1", (id,))
        row = cursor.fetchone()
        donor_blood = row[0] if row else None

        # delete child first
        cursor.execute("DELETE FROM donation WHERE donor_id = :1", (id,))

        # then delete donor
        cursor.execute("DELETE FROM donor WHERE donor_id = :1", (id,))
        if donor_blood:
            cursor.execute(
                """
                UPDATE blood_bank
                SET units_available = CASE
                    WHEN units_available > 0 THEN units_available - 1
                    ELSE 0
                END
                WHERE blood_group = :1
                """,
                (donor_blood,)
            )
        conn.commit()
    except Exception as exc:
        return db_error_response(exc)
    return redirect('/view_donors')


# ================= REQUEST =================

@app.route('/add_request', methods=['GET', 'POST'])
def add_request():
    if session.get('role') not in ['staff', 'doctor']:
        return "Access Denied"

    try:
        patient_options = get_patient_options()
    except Exception as exc:
        return db_error_response(exc)

    if request.method == 'POST':
        try:
            patient_id = request.form['patient_id']
            blood = normalize_blood_group(request.form['blood'])
            units = request.form['units']
            form_data = {
                "patient_id": patient_id,
                "blood": blood,
                "units": units
            }

            if blood not in VALID_BLOOD_GROUPS:
                return render_template(
                    'add_request.html',
                    error="Invalid blood group. Use one of: A+, A-, B+, B-, AB+, AB-, O+, O-.",
                    form_data=form_data,
                    patient_options=patient_options,
                    blood_groups=BLOOD_GROUP_OPTIONS
                ), 400

            try:
                units_value = int(units)
            except (TypeError, ValueError):
                return render_template(
                    'add_request.html',
                    error="Units must be a valid number.",
                    form_data=form_data,
                    patient_options=patient_options,
                    blood_groups=BLOOD_GROUP_OPTIONS
                ), 400

            if units_value <= 0:
                return render_template(
                    'add_request.html',
                    error="Units must be greater than zero.",
                    form_data=form_data,
                    patient_options=patient_options,
                    blood_groups=BLOOD_GROUP_OPTIONS
                ), 400

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO request (request_id, patient_id, blood_group, units, request_date, status)
                VALUES (request_seq.NEXTVAL, :1, :2, :3, SYSDATE, 'Pending')
                """,
                (patient_id, blood, units_value)
            )
            conn.commit()

            return redirect('/add_request?success=1')

        except Exception as exc:
            message = friendly_db_error(
                exc,
                "Unable to add request right now. Please verify values and try again."
            )
            return render_template(
                'add_request.html',
                error=message,
                form_data=form_data,
                patient_options=patient_options,
                blood_groups=BLOOD_GROUP_OPTIONS
            ), 400

    success = request.args.get('success') == '1'
    return render_template(
        'add_request.html',
        patient_options=patient_options,
        blood_groups=BLOOD_GROUP_OPTIONS,
        success=success
    )


@app.route('/view_requests')
def view_requests():
    if session.get('role') != 'staff':
        return "Access Denied"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.request_id, p.name, r.blood_group, r.units, r.request_date, r.status
            FROM request r
            JOIN patient p ON r.patient_id = p.patient_id
        """)
        data = cursor.fetchall()
    except Exception as exc:
        return db_error_response(exc)
    success = request.args.get('success') == '1'
    warning = request.args.get('warning') == '1'
    return render_template('view_requests.html', requests=data, success=success, warning=warning)


@app.route('/process/<int:id>')
def process(id):
    if session.get('role') != 'staff':
        return "Access Denied"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc('process_request', [id])
        cursor.execute("SELECT status FROM request WHERE request_id = :1", (id,))
        row = cursor.fetchone()
        conn.commit()
    except Exception as exc:
        return db_error_response(exc)
    if row and row[0] == 'Approved':
        return redirect('/view_requests?success=1')
    return redirect('/view_requests?warning=1')


# ================= STOCK =================

@app.route('/stock')
def stock():
    if session.get('role') != 'staff':
        return "Access Denied"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.blood_group, NVL(b.units_available, 0) AS units_available
            FROM (
                SELECT 'A+' AS blood_group FROM dual UNION ALL
                SELECT 'A-' FROM dual UNION ALL
                SELECT 'B+' FROM dual UNION ALL
                SELECT 'B-' FROM dual UNION ALL
                SELECT 'AB+' FROM dual UNION ALL
                SELECT 'AB-' FROM dual UNION ALL
                SELECT 'O+' FROM dual UNION ALL
                SELECT 'O-' FROM dual
            ) g
            LEFT JOIN blood_bank b ON b.blood_group = g.blood_group
            ORDER BY g.blood_group
        """)
        data = cursor.fetchall()
    except Exception as exc:
        return db_error_response(exc)
    return render_template('stock.html', stock=data)


# ================= RUN =================

if __name__ == '__main__':
    app.run(debug=True)