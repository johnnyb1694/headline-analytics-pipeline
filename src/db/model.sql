/*
This script is responsible for 'initialising' infrastructure inside the database layer concerning
the results of algorithmic 'trend' models which may have been applied to data residing in the
database.
*/

-----------------
---- SCHEMAS ----
-----------------

-- Container for all model-related outputs and other relevant data
CREATE SCHEMA model;

-------------------
---- RELATIONS ----
-------------------

-- Logs metadata on when the trending algorithm was run (and with which publication date params)
CREATE TABLE model.run (
    model_run_id SERIAL PRIMARY KEY,
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    publication VARCHAR(50) NOT NULL,
    min_publication_date DATE NOT NULL,
    max_publication_date DATE NOT NULL,
    CONSTRAINT uc_model UNIQUE (publication, min_publication_date, max_publication_date)
);

CREATE TABLE model.output (
    model_output_id SERIAL PRIMARY KEY,
    headline_term VARCHAR(50) NOT NULL,
    coef_intercept NUMERIC NOT NULL,
    coef_time NUMERIC NOT NULL,
    rse_time NUMERIC NOT NULL,
    p_value_time NUMERIC NOT NULL,
    model_run_id INT NOT NULL,
    FOREIGN KEY (model_run_id) REFERENCES model.run(model_run_id)
);