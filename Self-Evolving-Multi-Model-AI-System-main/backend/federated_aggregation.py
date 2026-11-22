"""Pure validation and equal-weight aggregation for demo model updates."""
from __future__ import annotations

import math
from numbers import Real
from typing import Sequence


def average_weight_updates(updates: Sequence[Sequence[Real]]) -> list[float]:
    """Average equally weighted client vectors after validating their shape/values.

    This is an equal-client average for the current demo; it is not sample-count
    weighted FedAvg and should not be described as such until client sample
    counts are supplied to the aggregation protocol.
    """
    if not updates:
        raise ValueError("At least one client update is required.")

    first = updates[0]
    if isinstance(first, (str, bytes)) or not isinstance(first, Sequence) or not first:
        raise ValueError("Client weight updates must be non-empty numeric vectors.")

    width = len(first)
    validated: list[list[float]] = []
    for index, vector in enumerate(updates):
        if isinstance(vector, (str, bytes)) or not isinstance(vector, Sequence):
            raise ValueError(f"Client update {index} must be a numeric vector.")
        if len(vector) != width:
            raise ValueError("All client updates must have the same vector length.")
        row: list[float] = []
        for value in vector:
            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError("Client weights must be finite real numbers.")
            number = float(value)
            if not math.isfinite(number):
                raise ValueError("Client weights must be finite real numbers.")
            row.append(number)
        validated.append(row)

    return [
        math.fsum(row[column] / len(validated) for row in validated)
        for column in range(width)
    ]
