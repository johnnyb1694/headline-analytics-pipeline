import pytest
from datetime import datetime
from src.data_loader.transform import nytas_transform_date, nytas_transform_author


def test_nytas_transform_date():
  
    # Test case 1: Valid date string
    raw_date = "2022-09-01T00:25:54+0000"
    expected_date = "2022-09-01T00:25:54+00:00"
    assert nytas_transform_date(raw_date) == expected_date

    # Test case 2: Invalid date string (should raise ValueError)
    with pytest.raises(ValueError):
        nytas_transform_date("invalid-date")


def test_nytas_transform_author():
  
    # Test case 1: Valid author string
    raw_author = "By Johnny Breen"
    expected_author = "Johnny Breen"
    assert nytas_transform_author(raw_author) == expected_author

    # Test case 2: Author string without 'By ' prefix
    raw_author = "Johnny Breen"
    expected_author = "Johnny Breen"
    assert nytas_transform_author(raw_author) == expected_author

    # Test case 3: Author string with additional 'By ' inside
    raw_author = "By Johnny By Breen"
    expected_author = "Johnny By Breen"
    assert nytas_transform_author(raw_author) == expected_author
