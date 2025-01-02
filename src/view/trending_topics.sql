WITH ranked_topics AS (

    SELECT 
        mo.headline_term,
        ROW_NUMBER() OVER (ORDER BY coef_time ASC) AS top_shrinking,
        ROW_NUMBER() OVER (ORDER BY coef_time DESC) AS top_growing
    FROM model.output mo
    JOIN model.run mr ON mo.model_run_id = mr.model_run_id
    WHERE max_publication_date = {as_at}
    -- Filter out models with relatively high volatility (standard error)
    AND mo.rse_time < 0.30
    -- Filter out 'months' (technical debt; should be eliminated earlier on)
    AND mo.headline_term NOT IN (
        'january', 
        'february', 
        'march', 
        'april', 
        'may', 
        'june', 
        'july', 
        'august', 
        'september', 
        'october', 
        'november', 
        'december'
    )

)

SELECT
    fct.headline_term,
    fct.publication_date,
    fct.p_estimate AS relative_frequency
FROM dwh.fct_logit_inputs fct
JOIN ranked_topics rt ON rt.headline_term = fct.headline_term
WHERE rt.top_growing <= {n_trending}
ORDER BY fct.headline_term, fct.publication_date