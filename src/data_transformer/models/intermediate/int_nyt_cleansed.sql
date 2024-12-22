with int_nyt_unnested as (

    select * from {{ ref('int_nyt_unnested') }}
    
),

remove_missing_values as (

    select
        headline_id,
        headline_term
    from int_nyt_unnested
    where headline_term != ''
    or headline_term is not null

),

remove_numeric_values as (

    select
        headline_id,
        headline_term
    from remove_missing_values
    where headline_term !~ '[0-9]'

),

remove_possessives as (

    select
        headline_id,
        regexp_replace(headline_term, '’s', '', 'g') as headline_term
    from remove_numeric_values
    
),

remove_specials as (

    select
        headline_id,
        regexp_replace(headline_term, '[^A-Za-z0-9]', '', 'g') as headline_term
    from remove_possessives

),

convert_term_case_to_lower as (

    select
        headline_id,
        lower(headline_term) as headline_term
    from remove_specials

)

select * from convert_term_case_to_lower