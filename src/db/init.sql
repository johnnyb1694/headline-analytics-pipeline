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

/*
---- SCHEMAS ----
*/

-- Container for all raw data that is 'staged' by the running process
CREATE SCHEMA raw;

-- Container for all metadata
CREATE SCHEMA meta;

/* 
---- RELATIONS ----
*/

-- Stores headlines in 'raw' staging format prior to transformation
CREATE TABLE raw.headline (
    publication VARCHAR(100) NOT NULL,
    headline TEXT NOT NULL,
    url VARCHAR(2083) NOT NULL -- NB: maximum URL length in most browsers
);

-- Logs ELT pipeline metadata 
CREATE TABLE meta.batch (
    id SERIAL PRIMARY KEY,
    created_by VARCHAR(50),
    created_at TIMESTAMP NOT NULL,
    status VARCHAR(20),
    runtime_seconds REAL NOT NULL, -- NB: 4-byte floating-point number
    valid BIT NOT NULL,
    narrative VARCHAR(255),
    CONSTRAINT uc_batch UNIQUE (created_at, status, valid)
);