"""Contains the core logic required to fit a logistic growth model to the appropriate input data.
"""
from src.model.algorithm import compute_batch_trend
from src.model.db_utils import DBC, open_connection, get_logit_inputs, load_logit_outputs