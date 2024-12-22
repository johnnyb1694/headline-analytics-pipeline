{{ config(materialized='view') }}

with fct_daily_term_counts as (

    select * from {{ ref('fct_daily_term_counts') }}

),

fct_daily_counts as (

    select * from {{ ref('fct_daily_counts') }}

),

fct_term_counts as (

    select * from {{ ref('fct_term_counts') }}

),

fct_logit_inputs as (

    select
        fct_dtc.publication,
        fct_dtc.headline_term,
        fct_dtc.publication_date,
        fct_dtc.frequency as successes,
        (fct_dc.total_frequency - fct_dtc.frequency) as failures,
        fct_dc.total_frequency as trials,
        (fct_dtc.frequency / fct_dc.total_frequency) as p_estimate,
        fct_tc.total_frequency as headline_term_frequency
    from fct_daily_term_counts fct_dtc
    join fct_daily_counts fct_dc on fct_dc.publication = fct_dtc.publication
                                 and fct_dc.publication_date = fct_dtc.publication_date
    join fct_term_counts fct_tc on fct_tc.publication = fct_dtc.publication
                                and fct_tc.headline_term = fct_dtc.headline_term
    where fct_dtc.stop_word = 0

)

select * from fct_logit_inputs