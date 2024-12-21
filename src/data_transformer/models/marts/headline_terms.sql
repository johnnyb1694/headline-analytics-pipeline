with stg_nyt as (

    select * from {{ ref('stg_nyt') }}

),

int_nyt_cleansed as (

    select * from {{ ref('int_nyt_cleansed') }}

),

-- NB: this requires pre-seeding with `dbt seed`
stop_words as (

    select * from {{ ref('stop_words') }}

),

nyt_headline_terms_dated as (

    select
        'NYT' as publication,
        stg_nyt.publication_date,
        int_nytc.headline_term
    from stg_nyt 
    join int_nyt_cleansed int_nytc on int_nytc.headline_id = stg_nyt.headline_id
    
),

nyt_headline_terms_agg as (

    select
        publication,
        publication_date,
        headline_term,
        count(*) as frequency
    from nyt_headline_terms_dated
    group by 
        publication,
        publication_date,
        headline_term

),

final as (

    select
        publication,
        publication_date,
        headline_term,
        case
            when stop_words.stop_word is not null then 1
            else 0
        end as stop_word,
        frequency
    from nyt_headline_terms_agg nyt_agg
    left join stop_words on stop_words.stop_word = nyt_agg.headline_term

)

select * from final

