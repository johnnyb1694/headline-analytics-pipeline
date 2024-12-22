{% macro aggregate_frequency(group_by_column) %}

select
    publication,
    {{ group_by_column }},
    sum(frequency) as total_frequency
from
    {{ ref('fct_daily_term_counts') }}
group by
    publication,
    {{ group_by_column }}

{% endmacro %}

