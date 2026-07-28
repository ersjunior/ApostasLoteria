"""Reexporta estatísticas do core de domínio."""

from loterias_core.statistics import (
    chi_square_uniformity_test,
    empirical_probability,
    frequency,
    frequency_by_period,
)

__all__ = [
    "chi_square_uniformity_test",
    "empirical_probability",
    "frequency",
    "frequency_by_period",
]
