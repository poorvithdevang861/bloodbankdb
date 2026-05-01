-- DROP TABLES (for re-run safety)
DROP TABLE request CASCADE CONSTRAINTS;
DROP TABLE donation CASCADE CONSTRAINTS;
DROP TABLE patient CASCADE CONSTRAINTS;
DROP TABLE donor CASCADE CONSTRAINTS;
DROP TABLE blood_bank CASCADE CONSTRAINTS;
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE request_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE donation_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE donor_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

-- DONOR TABLE
CREATE TABLE donor (
    donor_id NUMBER PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    age NUMBER NOT NULL,
    gender CHAR(1) NOT NULL,
    weight_kg NUMBER(5,2) NOT NULL,
    blood_group VARCHAR2(5) NOT NULL,
    phone VARCHAR2(15),
    CONSTRAINT chk_donor_age CHECK (age BETWEEN 18 AND 60),
    CONSTRAINT chk_donor_gender CHECK (gender IN ('M', 'F', 'O')),
    CONSTRAINT chk_donor_weight CHECK (weight_kg >= 45),
    CONSTRAINT chk_donor_blood CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-'))
);

-- PATIENT TABLE
CREATE TABLE patient (
    patient_id NUMBER PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    blood_group VARCHAR2(5) NOT NULL,
    phone VARCHAR2(15)
);

-- BLOOD BANK TABLE
CREATE TABLE blood_bank (
    blood_group VARCHAR2(5) PRIMARY KEY,
    units_available NUMBER DEFAULT 0 NOT NULL,
    CONSTRAINT chk_stock_units CHECK (units_available >= 0)
);

-- DONATION TABLE
CREATE TABLE donation (
    donation_id NUMBER PRIMARY KEY,
    donor_id NUMBER NOT NULL,
    blood_group VARCHAR2(5) NOT NULL,
    units NUMBER NOT NULL,
    donation_date DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT chk_donation_units CHECK (units > 0),
    CONSTRAINT chk_donation_blood CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    FOREIGN KEY (donor_id) REFERENCES donor(donor_id)
);

-- REQUEST TABLE
CREATE TABLE request (
    request_id NUMBER PRIMARY KEY,
    patient_id NUMBER NOT NULL,
    blood_group VARCHAR2(5) NOT NULL,
    units NUMBER NOT NULL,
    request_date DATE DEFAULT SYSDATE NOT NULL,
    status VARCHAR2(20) DEFAULT 'Pending' NOT NULL,
    CONSTRAINT chk_request_units CHECK (units > 0),
    CONSTRAINT chk_request_blood CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    CONSTRAINT chk_request_status CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- SEQUENCES FOR AUTO-ID GENERATION
CREATE SEQUENCE donor_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE donation_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE request_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;