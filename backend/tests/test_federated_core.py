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


@pytest.mark.parametrize("dimension", [0, -1, True, 1.5, "2"])
def test_invalid_expected_dimension_is_rejected(dimension):
    with pytest.raises(ValueError, match="expected_dimension"):
        validate_update([1.0, 2.0], 1, dimension)


def test_weighted_fedavg_rejects_invalid_dimension_even_for_empty_input():
    with pytest.raises(ValueError, match="expected_dimension"):
        weighted_fedavg([], expected_dimension=0)


def test_weighted_fedavg_rejects_non_mapping_update():
    with pytest.raises(ValueError, match="each update must be a mapping"):
        weighted_fedavg([None], expected_dimension=2)


def test_weighted_fedavg_avoids_overflow_from_large_sample_counts():
    result = weighted_fedavg(
        [
            {"weights": [1e308], "sample_count": 10**300},
            {"weights": [1e308], "sample_count": 10**300},
        ],
        expected_dimension=1,
    )
    assert result == pytest.approx([1e308])


def test_weighted_fedavg_returns_finite_convex_average_for_opposite_extremes():
    result = weighted_fedavg(
        [
            {"weights": [1e308], "sample_count": 1},
            {"weights": [-1e308], "sample_count": 1},
        ],
        expected_dimension=1,
    )
    assert result == pytest.approx([0.0])
