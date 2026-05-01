# Blood Bank Management System

This project is a Flask + Oracle database web application for managing blood donors, blood requests, and stock.

## Quick Start (Easiest)

### 1) Clone and enter project

```bash
git clone https://github.com/poorvithdevang861/bloodbankdb.git
cd bloodbankdb
```

### 2) Create and activate virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install flask oracledb
```

### 4) Set Oracle DB and app environment variables

macOS/Linux:

```bash
export FLASK_SECRET_KEY='replace-with-a-random-secret'
export DB_USER='system'
export DB_PASSWORD='replace-with-your-db-password'
export DB_DSN='localhost:1521/FREEPDB1'
```

Windows (PowerShell):

```powershell
$env:FLASK_SECRET_KEY='replace-with-a-random-secret'
$env:DB_USER='system'
$env:DB_PASSWORD='replace-with-your-db-password'
$env:DB_DSN='localhost:1521/FREEPDB1'
```

### 5) Run the app

```bash
python app.py
```

Open `http://127.0.0.1:5000`

---

## ERD Diagram

![Blood Bank ERD](docs/erd-diagram.png)

---

It is designed so that:
- frontend forms collect user input,
- Flask routes validate and persist data,
- Oracle SQL/PLSQL enforces database rules and stock logic.

---

## 1) Project Architecture

### Frontend (HTML templates)

Templates in `templates/` render:
- Login screen
- Dashboard menu
- Add Donor form
- Add Request form
- View Donors table
- View Requests table
- View Stock table

Frontend responsibilities:
- collect input from staff/doctor users,
- show validation/operation messages (success/warning/error),
- provide route navigation.

### Backend (Flask app)

`app.py` handles:
- authentication by role (`staff`, `doctor`),
- form input validation (age, weight, blood group, units, etc.),
- SQL DML execution (insert/select/delete),
- calling stored procedure `process_request`,
- friendly error mapping for Oracle errors.

### Database (Oracle SQL + PL/SQL)

SQL files:
- `01_final_schema.sql`: tables, constraints, sequences
- `02_final_plsql.sql`: triggers + stored procedure
- `03_final_data_and_test.sql`: seed/test data

Database responsibilities:
- enforce schema constraints,
- enforce donor and donation business rules,
- apply stock updates and approval logic atomically.

---

## 2) Role-Based Workflow

### Staff

Can:
- add donors,
- view donors,
- view/process requests,
- view blood stock.

### Doctor

Can:
- create blood requests.

---

## 3) Backend <-> Database Interaction

## A) Add Donor flow

1. User submits `Add Donor` form.
2. Flask route `/add_donor` validates:
   - age range,
   - minimum weight,
   - valid gender,
   - valid blood group.
3. Flask inserts donor using `donor_seq.NEXTVAL`.
4. Flask updates stock row for that blood group (`MERGE`):
   - increments by `1`,
   - creates row if missing.
5. Commit transaction.

Result: donor added and stock updated immediately.

## B) Delete Donor flow

1. Staff clicks delete in donor table.
2. Flask removes dependent donation records for that donor.
3. Flask removes donor record.
4. Flask decrements corresponding blood stock by `1` (not below `0`).
5. Commit transaction.

## C) Add Request flow

1. Doctor submits request.
2. Flask validates blood group + units.
3. Flask inserts request using `request_seq.NEXTVAL` with status `Pending`.
4. UI redirects with success message.

Result: request created, waiting for staff processing.

## D) Process Request flow

1. Staff clicks `Process` in `View Requests`.
2. Flask calls Oracle procedure:
   - `cursor.callproc('process_request', [request_id])`
3. Procedure checks request status/stock:
   - if enough stock: deduct units + mark `Approved`,
   - else keep `Pending`.
4. Flask re-reads status and shows:
   - success message on approval,
   - warning message on insufficient stock.

Result: stock and request status stay consistent.

## E) View Stock flow

`/stock` route returns all 8 blood groups (`A+, A-, B+, B-, AB+, AB-, O+, O-`) via left join query and shows `0` where unavailable.

Result: complete stock table always visible.

---

## 4) Trigger and Procedure Usage

Defined in `02_final_plsql.sql`:

- `trg_validate_donor` (BEFORE INSERT/UPDATE on `donor`)
  - enforces age/weight eligibility.

- `trg_validate_donation` (BEFORE INSERT on `donation`)
  - checks blood group match and minimum donation gap.

- `trg_after_donation` (AFTER INSERT on `donation`)
  - updates stock after donation insert.

- `process_request(p_request_id)` procedure
  - central request-approval/stock-deduction logic.

Even when Flask validates first, DB rules remain the final safety layer.

---

## 5) Error Handling Strategy

Flask converts Oracle exceptions into user-friendly messages:
- duplicate key,
- missing FK record,
- rule-check failures,
- insufficient stock situations,
- schema/setup mismatch hints.

This prevents raw SQL errors from appearing directly in UI.

---

## 6) Database Setup Notes

### Apply DB scripts

Run in this order:
1. `01_final_schema.sql`
2. `02_final_plsql.sql`
3. `03_final_data_and_test.sql`

---

## 7) Summary

Frontend handles user interaction, Flask handles orchestration and validations, and Oracle enforces persistent business rules with SQL constraints, triggers, and procedures.

This layered design keeps behavior consistent, safe, and easier to demo.
