with versioned_nytas as (

    select
        row_number() over (partition by url order by publication_date desc) as headline_version,
        *
    from {{ source('src_nyt', 'nytas') }}

),

final as (

    select
        row_number() over (order by publication_date) as headline_id,
        headline,
        publication_date::DATE,
        coalesce(author, 'Unknown') as author,
        coalesce(news_desk, 'Unknown') as news_desk,
        url
    from versioned_nytas
    where headline_version = 1
    and headline is not null

)

select * from final
