import math

import pytest

from federated_aggregation import average_weight_updates


def test_averages_equal_weight_client_vectors():
    assert average_weight_updates([[1, 3], [3, 5], [5, 7]]) == [3.0, 5.0]


def test_supports_single_client_update():
    assert average_weight_updates([[1, 2.5]]) == [1.0, 2.5]


@pytest.mark.parametrize("updates", [[], [[]], [[1, 2], [3]], [[1], [2, 3]]])
def test_rejects_empty_or_mismatched_vectors(updates):
    with pytest.raises(ValueError):
        average_weight_updates(updates)


@pytest.mark.parametrize("value", [True, "1", float("nan"), float("inf"), -float("inf")])
def test_rejects_non_numeric_or_non_finite_weights(value):
    with pytest.raises(ValueError):
        average_weight_updates([[value]])


def test_does_not_return_non_finite_average_from_large_inputs():
    # Finite inputs whose naive sum overflows are safely averaged via fsum.
    result = average_weight_updates([[1e308], [1e308]])
    assert math.isfinite(result[0])
    assert result[0] == 1e308
