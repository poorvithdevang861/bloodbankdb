-- INSERT BLOOD STOCK
INSERT INTO blood_bank VALUES ('A+', 10);
INSERT INTO blood_bank VALUES ('B+', 8);
INSERT INTO blood_bank VALUES ('O+', 15);

-- INSERT DONORS
INSERT INTO donor VALUES (1, 'Rahul', 25, 'M', 68, 'A+', '1111111111');
INSERT INTO donor VALUES (2, 'Amit', 30, 'M', 72, 'B+', '2222222222');

-- INSERT PATIENTS
INSERT INTO patient VALUES (1, 'Riya', 'A+', '9999999999');

-- TEST DONATION (TRIGGER TEST)
INSERT INTO donation VALUES (1, 1, 'A+', 5, SYSDATE);

-- CHECK STOCK AFTER TRIGGER
SELECT * FROM blood_bank;

-- INSERT REQUEST
INSERT INTO request VALUES (1, 1, 'A+', 3, SYSDATE, 'Pending');

-- CALL PROCEDURE
BEGIN
    process_request(1);
END;
/

-- CHECK REQUEST STATUS
SELECT * FROM request;

-- JOIN QUERY (FOR MARKS)
SELECT d.name, d.blood_group, dn.units
FROM donor d
JOIN donation dn ON d.donor_id = dn.donor_id;

-- GROUP BY QUERY (FOR MARKS)
SELECT blood_group, SUM(units) AS total_donated
FROM donation
GROUP BY blood_group;

-- UPDATE (CRUD)
UPDATE donor SET age = 26 WHERE donor_id = 1;

-- DELETE (CRUD)
DELETE FROM donor WHERE donor_id = 2;

-- KEEP SEQUENCES IN SYNC AFTER MANUAL SEED IDS
DECLARE
    v_target NUMBER;
    v_curr NUMBER;
BEGIN
    SELECT NVL(MAX(donor_id), 0) + 1 INTO v_target FROM donor;
    SELECT donor_seq.NEXTVAL INTO v_curr FROM dual;
    IF (v_target - v_curr) <> 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE donor_seq INCREMENT BY ' || (v_target - v_curr);
        SELECT donor_seq.NEXTVAL INTO v_curr FROM dual;
    END IF;
    EXECUTE IMMEDIATE 'ALTER SEQUENCE donor_seq INCREMENT BY 1';
END;
/

DECLARE
    v_target NUMBER;
    v_curr NUMBER;
BEGIN
    SELECT NVL(MAX(donation_id), 0) + 1 INTO v_target FROM donation;
    SELECT donation_seq.NEXTVAL INTO v_curr FROM dual;
    IF (v_target - v_curr) <> 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE donation_seq INCREMENT BY ' || (v_target - v_curr);
        SELECT donation_seq.NEXTVAL INTO v_curr FROM dual;
    END IF;
    EXECUTE IMMEDIATE 'ALTER SEQUENCE donation_seq INCREMENT BY 1';
END;
/

DECLARE
    v_target NUMBER;
    v_curr NUMBER;
BEGIN
    SELECT NVL(MAX(request_id), 0) + 1 INTO v_target FROM request;
    SELECT request_seq.NEXTVAL INTO v_curr FROM dual;
    IF (v_target - v_curr) <> 0 THEN
        EXECUTE IMMEDIATE 'ALTER SEQUENCE request_seq INCREMENT BY ' || (v_target - v_curr);
        SELECT request_seq.NEXTVAL INTO v_curr FROM dual;
    END IF;
    EXECUTE IMMEDIATE 'ALTER SEQUENCE request_seq INCREMENT BY 1';
END;
/