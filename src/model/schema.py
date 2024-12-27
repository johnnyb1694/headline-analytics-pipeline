"""Contains the relevant schema definitions for performing data validation on modelling input.
"""
import pandera as pa

CHECK_NON_NEGATIVE = pa.Check.greater_than_or_equal_to(0)

# Model - Inputs

TERM_DF = pa.DataFrameSchema(
    {
        "successes": pa.Column(int, CHECK_NON_NEGATIVE),
        "failures": pa.Column(int, CHECK_NON_NEGATIVE),
        "cum_time_elapsed": pa.Column(int, CHECK_NON_NEGATIVE)
    }
)

LOGIT_INPUTS = pa.DataFrameSchema(
    {
        "headline_term": pa.Column(str),
        "successes": pa.Column(int, CHECK_NON_NEGATIVE),
        "failures": pa.Column(int, CHECK_NON_NEGATIVE),
        "cum_time_elapsed": pa.Column(int, CHECK_NON_NEGATIVE)
    }
)

# Model - Outputs

LOGIT_OUTPUTS = pa.DataFrameSchema(
    {   
        "headline_term": pa.Column(str, unique=True),
        "coef_intercept": pa.Column(float),
        "coef_time": pa.Column(float),
        "rse_time": pa.Column(float),
        "p_value_time": pa.Column(float)
    }
)