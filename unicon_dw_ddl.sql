
CREATE SEQUENCE unicon_dw.task_dim_task_id_seq;

CREATE TABLE unicon_dw.task_dim (
                task_id INTEGER NOT NULL DEFAULT nextval('unicon_dw.task_dim_task_id_seq'),
                task_name VARCHAR NOT NULL,
                project_name VARCHAR NOT NULL,
                program_name VARCHAR NOT NULL,
                client_name VARCHAR NOT NULL,
                CONSTRAINT task_dim_pk PRIMARY KEY (task_id)
);


ALTER SEQUENCE unicon_dw.task_dim_task_id_seq OWNED BY unicon_dw.task_dim.task_id;

CREATE TABLE unicon_dw.time_dim (
                entry_date DATE NOT NULL,
                day_of_month INTEGER NOT NULL,
                month INTEGER NOT NULL,
                quarter INTEGER NOT NULL,
                year INTEGER NOT NULL,
                CONSTRAINT time_dim_pk PRIMARY KEY (entry_date)
);
COMMENT ON TABLE unicon_dw.time_dim IS 'time dimension, with "cube" values for day of month, month, quarter, year, etc';


CREATE SEQUENCE unicon_dw.person_dim_person_id_seq;

CREATE TABLE unicon_dw.person_dim (
                person_id INTEGER NOT NULL DEFAULT nextval('unicon_dw.person_dim_person_id_seq'),
                first_name VARCHAR NOT NULL,
                last_name VARCHAR NOT NULL,
                employee_type VARCHAR NOT NULL,
                position VARCHAR NOT NULL,
                CONSTRAINT pk_person_dim PRIMARY KEY (person_id)
);
COMMENT ON TABLE unicon_dw.person_dim IS 'table of persons, may be employee or contractor';
COMMENT ON COLUMN unicon_dw.person_dim.person_id IS 'identifier for person, also the primary key';


ALTER SEQUENCE unicon_dw.person_dim_person_id_seq OWNED BY unicon_dw.person_dim.person_id;

CREATE TABLE unicon_dw.timecard_entry_fact (
                person_id INTEGER NOT NULL,
                entry_date DATE NOT NULL,
                task_id INTEGER NOT NULL,
                hours REAL NOT NULL,
                billable BOOLEAN NOT NULL,
                comment_text VARCHAR NOT NULL,
                CONSTRAINT pk_timecard_entry_fact PRIMARY KEY (person_id, entry_date, task_id)
);
COMMENT ON TABLE unicon_dw.timecard_entry_fact IS 'fact table of timecard entries.';
COMMENT ON COLUMN unicon_dw.timecard_entry_fact.person_id IS 'identifier for person, also the primary key';
COMMENT ON COLUMN unicon_dw.timecard_entry_fact.hours IS 'The number of hours in the timecard entry, may be fractional.';
COMMENT ON COLUMN unicon_dw.timecard_entry_fact.billable IS 'true - hours were billable
false - hours were not billable';


ALTER TABLE unicon_dw.timecard_entry_fact ADD CONSTRAINT task_dim_timecard_entry_fact_fk
FOREIGN KEY (task_id)
REFERENCES unicon_dw.task_dim (task_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE unicon_dw.timecard_entry_fact ADD CONSTRAINT time_dim_timecard_entry_fact_fk
FOREIGN KEY (entry_date)
REFERENCES unicon_dw.time_dim (entry_date)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE unicon_dw.timecard_entry_fact ADD CONSTRAINT person_dim_timecard_entry_fact_fk
FOREIGN KEY (person_id)
REFERENCES unicon_dw.person_dim (person_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;
