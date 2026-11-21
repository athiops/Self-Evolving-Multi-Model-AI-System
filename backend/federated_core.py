"""Validated primitives for federated model-update aggregation.

These helpers intentionally do not claim that a submitted vector is a trained
model. The caller is responsible for producing updates from a compatible local
training process and for authenticating the submitting client.
"""
from __future__ import annotations

import math
from typing import Iterable, Mapping, Sequence


def _validate_dimension(expected_dimension: int) -> None:
    if (
        isinstance(expected_dimension, bool)
        or not isinstance(expected_dimension, int)
        or expected_dimension <= 0
    ):
        raise ValueError("expected_dimension must be a positive integer")


def validate_update(
    weights: Sequence[float],
    sample_count: int,
    expected_dimension: int,
) -> list[float]:
    """Return a normalized finite update vector or raise ValueError."""
    _validate_dimension(expected_dimension)
    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count <= 0:
        raise ValueError("sample_count must be a positive integer")
    if not isinstance(weights, (list, tuple)) or not weights:
        raise ValueError("weights must be a non-empty list or tuple")
    if len(weights) != expected_dimension:
        raise ValueError(
            f"weights must contain exactly {expected_dimension} values"
        )

    normalized: list[float] = []
    for index, value in enumerate(weights):
        if isinstance(value, bool):
            raise ValueError(f"weights[{index}] must be a finite number")
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"weights[{index}] must be a finite number") from exc
        if not math.isfinite(number):
            raise ValueError(f"weights[{index}] must be a finite number")
        normalized.append(number)
    return normalized


def weighted_fedavg(
    updates: Iterable[Mapping[str, object]],
    expected_dimension: int,
) -> list[float]:
    """Compute sample-count-weighted FedAvg after validating every update."""
    _validate_dimension(expected_dimension)
    validated: list[tuple[list[float], int]] = []
    for update in updates:
        if not isinstance(update, Mapping):
            raise ValueError("each update must be a mapping")
        weights = update.get("weights")
        sample_count = update.get("sample_count")
        validated.append(
            (
                validate_update(weights, sample_count, expected_dimension),  # type: ignore[arg-type]
                sample_count,  # type: ignore[arg-type]
            )
        )
    if not validated:
        raise ValueError("at least one client update is required")

    total_samples = sum(count for _, count in validated)
    return [
        sum(vector[index] * count for vector, count in validated) / total_samples
        for index in range(expected_dimension)
    ]
