/*
This script is responsible for 'initialising' infrastructure inside the database layer when
the Postgres docker service is initialised.

In practice, this only involves:

(a) A schema & relation for storing 'metadata' *about* the pipeline itself (e.g. when was the last 
extraction performed)
(b) A schema & relation for storing 'raw' data extracted from a given publication (e.g. the NYT)

We do not need to 'initialise' other tables because `dbt` (the transformation layer) will do that
for us automatically.
*/

-----------------
---- SCHEMAS ----
-----------------

-- Container for all raw data that is 'staged' by the running process
CREATE SCHEMA raw;

-- Container for all metadata
CREATE SCHEMA meta;

-- Container for all model-related outputs and other relevant data
CREATE SCHEMA model;

-------------------
---- RELATIONS ----
-------------------

-- Stores NYT headlines in 'raw' staging format prior to transformation
CREATE TABLE raw.nytas (
    headline TEXT,
    publication_date TIMESTAMP,
    author VARCHAR(1000),
    news_desk VARCHAR(100),
    url VARCHAR(2083), -- NB: maximum URL length in most browsers
    _etl_loaded_at_date TIMESTAMP DEFAULT NOW()
);

-- Logs ELT pipeline metadata 
CREATE TABLE meta.batch (
    batch_id SERIAL PRIMARY KEY,
    created_by VARCHAR(50),
    created_at TIMESTAMP NOT NULL,
    status VARCHAR(20),
    runtime_seconds REAL NOT NULL, -- NB: 4-byte floating-point number
    valid BIT NOT NULL,
    narrative VARCHAR(255),
    CONSTRAINT uc_batch UNIQUE (created_at, status, valid)
);

-- Logs metadata on when the trending algorithm was run (and with which publication date params)
CREATE TABLE model.run (
    model_run_id SERIAL PRIMARY KEY,
    created_by VARCHAR(50) NOT NULL DEFAULT current_user,
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