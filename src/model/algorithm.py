import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from db_utils import DBC, open_connection, get_logit_inputs


def compute_term_trend(
    term_df: pd.DataFrame
) -> dict[str, float]:
    """Fits a logistic regression model & extracts - amongst other parameters (e.g. error) -
    the coefficient of the time covariate whose value (and polarity) is indicative of 'trend' 
    (if positive) or 'shrinkage' (if negative).

    Note: input `term_df` is specific to a given term (e.g. 'trump') and each record 
    represents the daily result of a series of 'trials' to appear ('success') or 
    not appear ('failure').

    :param term_df: A `pd.DataFrame` object with fields: 
                    * `successes`
                    * `failures`
                    * `cum_time_elapsed`
    :return: a dictionary of 
    """
    model = smf.glm(
        "successes + failures ~ cum_time_elapsed", 
        family=sm.families.Binomial(), 
        data=term_df
    ).fit()
    # NB: logit(p) = coef_intercept + coef_time * t (where 't' is 'cum_time_elapsed')
    return {
        "coef_intercept": float(model.params["Intercept"]),
        "coef_time": float(model.params["cum_time_elapsed"]),
        "rse_time": float(model.bse["cum_time_elapsed"] / abs(model.params["cum_time_elapsed"])),
        "p_value_time": float(model.pvalues["cum_time_elapsed"])
    }
    

def compute_batch_trend(
    logit_inputs: pd.DataFrame
) -> pd.DataFrame:
    """Runs the trend fitting exercise (via `compute_term_trend()`) across a series of terms.

    :param logit_inputs: A `pd.DataFrame` object with fields: 
                         * `headline_term`
                         * `successes`
                         * `failures`
                         * `cum_time_elapsed`
    :return: statistical fitting output associated with each `headline_term`
    """
    terms = list(logit_inputs["headline_term"].unique())
    trend_factors = {}
    for term in terms:
        term_df = logit_inputs[logit_inputs["headline_term"] == term]
        try:
            trend_factors[term] = compute_term_trend(term_df)
        except RuntimeWarning:
            print(f"Erroneous fitting detected for term '{term}'; negating output.")
            trend_factors[term] = None
    return pd.DataFrame.from_dict(trend_factors, orient="index")


if __name__ == '__main__':

    from datetime import date

    dbc = DBC(
        dbname='publications',
        user='postgres',
        password='XXX'
    )
    conn = open_connection(
        dbc
    )
    logit_inputs = get_logit_inputs(
        conn, 
        min_publication_date=date(2024, 6, 1),
        max_publication_date=date(2024, 12, 1)
    )
    trend_factors = compute_batch_trend(logit_inputs)
    print(trend_factors)
