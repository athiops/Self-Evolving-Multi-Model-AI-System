import pytest

try:
    from federated_core import validate_update, weighted_fedavg
except ModuleNotFoundError:
    from backend.federated_core import validate_update, weighted_fedavg


def test_weighted_fedavg_uses_client_sample_counts():
    result = weighted_fedavg(
        [
            {"weights": [1, 3], "sample_count": 1},
            {"weights": [5, 7], "sample_count": 3},
        ],
        expected_dimension=2,
    )
    assert result == pytest.approx([4, 6])


@pytest.mark.parametrize(
    "weights,count",
    [
        ([], 1),
        ([1.0], 1),
        ([1.0, float("nan")], 1),
        ([1.0, float("inf")], 1),
        ([True, 2.0], 1),
        ([1.0, 2.0], 0),
        ([1.0, 2.0], True),
    ],
)
def test_invalid_update_is_rejected(weights, count):
    with pytest.raises(ValueError):
        validate_update(weights, count, expected_dimension=2)


def test_weighted_fedavg_rejects_empty_update_set():
    with pytest.raises(ValueError, match="at least one"):
        weighted_fedavg([], expected_dimension=2)


def test_weighted_fedavg_rejects_dimension_mismatch():
    with pytest.raises(ValueError, match="exactly"):
        weighted_fedavg(
            [{"weights": [1.0], "sample_count": 2}],
            expected_dimension=2,
        )


def test_valid_update_is_normalized_to_floats():
    assert validate_update([1, 2.5], 4, 2) == [1.0, 2.5]
