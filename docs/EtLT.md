# EtLT - Infrastructure

## Scope

This document outlines the structure of the EtLT infrastructure, namely:

* `src/data_loader`: responsible for loading data into Postgres
* `src/data_transformer`: responsible for 'big T' transformations post upload via `dbt`
* `src/db`: responsible for initialising the database infrastructure (once at the start)

## `data_loader`

The `data_loader` container is simply responsible for:

1. `extract.py`: extracting data from a certain publication outlet (e.g. the New York Times)
2. `load.py`: flattening the resultant JSON into a CSV format and uploading to Postgres (via the `COPY` statement)

There _is_ a 'little t' transformation as well (cf. `transform.py`) which applies some very minor
transformations to the extracted publications archive (such as reformatting dates) but, the bulk
of the work executed by this application is the 'EL' part of 'EtLT'!

## TODO

Some items that may require attention at some point:

* Many functions in the `data_loader` module are prepended with `nytas` to indicate that the functionality relates to the 
publication API 'New York Times Archive Search'; however, perhaps a better method of organisation
would be to place all related functions inside a module or submodule and delegate the prefix to
Python (this is perhaps a better long term solution!)
* Investigate slicker options of deploying changes to Postgres (perhaps `liquibase` or o/w)

