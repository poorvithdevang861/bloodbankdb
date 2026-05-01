-- TRIGGER: Validate donor eligibility rules at DB level
CREATE OR REPLACE TRIGGER trg_validate_donor
BEFORE INSERT OR UPDATE ON donor
FOR EACH ROW
BEGIN
    IF :NEW.gender = 'M' THEN
        IF :NEW.age > 60 OR :NEW.age < 18 OR :NEW.weight_kg < 45 THEN
            RAISE_APPLICATION_ERROR(-20010, 'Donor must be age 18-60 and weight >= 45 kg');
        END IF;
    ELSIF :NEW.gender = 'F' THEN
        IF :NEW.age > 60 OR :NEW.age < 18 OR :NEW.weight_kg < 45 THEN
            RAISE_APPLICATION_ERROR(-20011, 'Donor must be age 18-60 and weight >= 45 kg');
        END IF;
    ELSIF :NEW.gender = 'O' THEN
        IF :NEW.age > 60 OR :NEW.age < 18 OR :NEW.weight_kg < 45 THEN
            RAISE_APPLICATION_ERROR(-20012, 'Donor must be age 18-60 and weight >= 45 kg');
        END IF;
    END IF;
END;
/

-- TRIGGER: Validate donation blood group + minimum gap
CREATE OR REPLACE TRIGGER trg_validate_donation
BEFORE INSERT ON donation
FOR EACH ROW
DECLARE
    v_donor_blood donor.blood_group%TYPE;
    v_last_donation DATE;
BEGIN
    SELECT blood_group INTO v_donor_blood
    FROM donor
    WHERE donor_id = :NEW.donor_id;

    IF v_donor_blood <> :NEW.blood_group THEN
        RAISE_APPLICATION_ERROR(-20002, 'Donation blood group must match donor blood group');
    END IF;

    SELECT MAX(donation_date)
    INTO v_last_donation
    FROM donation
    WHERE donor_id = :NEW.donor_id;

    IF v_last_donation IS NOT NULL AND :NEW.donation_date < v_last_donation + 90 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Minimum 90 days gap required between donations');
    END IF;
END;
/

-- TRIGGER: Update stock after donation
CREATE OR REPLACE TRIGGER trg_after_donation
AFTER INSERT ON donation
FOR EACH ROW
BEGIN
    MERGE INTO blood_bank bb
    USING (SELECT :NEW.blood_group AS blood_group FROM dual) src
    ON (bb.blood_group = src.blood_group)
    WHEN MATCHED THEN
        UPDATE SET units_available = bb.units_available + :NEW.units
    WHEN NOT MATCHED THEN
        INSERT (blood_group, units_available) VALUES (src.blood_group, :NEW.units);
END;
/

-- STORED PROCEDURE WITH CURSOR
CREATE OR REPLACE PROCEDURE process_request(
    p_request_id NUMBER
)
IS
    v_units_needed NUMBER;
    v_blood_group VARCHAR2(5);
    v_available NUMBER;
    v_status request.status%TYPE;

BEGIN
    -- Get request details and process only pending requests
    SELECT units, blood_group, status
    INTO v_units_needed, v_blood_group, v_status
    FROM request
    WHERE request_id = p_request_id;

    IF v_status <> 'Pending' THEN
        RETURN;
    END IF;

    SELECT units_available
    INTO v_available
    FROM blood_bank
    WHERE blood_group = v_blood_group;

    IF v_available >= v_units_needed THEN
        UPDATE blood_bank
        SET units_available = units_available - v_units_needed
        WHERE blood_group = v_blood_group
          AND units_available >= v_units_needed;

        IF SQL%ROWCOUNT = 1 THEN
            UPDATE request
            SET status = 'Approved'
            WHERE request_id = p_request_id;
        ELSE
            UPDATE request
            SET status = 'Pending'
            WHERE request_id = p_request_id;
        END IF;
    ELSE
        UPDATE request
        SET status = 'Pending'
        WHERE request_id = p_request_id;
    END IF;
END;
/