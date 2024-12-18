with stg_nyt as (

    select * from {{ ref('stg_nyt') }}
    
),

split_nyt_headlines as (

    select
        headline_id,
        string_to_array(headline, ' ') as headline_split
    from stg_nyt

),

unnested_nyt_headlines as (

    select 
        headline_id,
        unnest(headline_split) as headline_term
    from split_nyt_headlines

),

final as (

    select 
        headline_id,
        headline_term as headline_term
    from unnested_nyt_headlines

)

select * from final
