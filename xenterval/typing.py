from __future__ import annotations
from fractions import Fraction
from typing import Mapping

__all__ = ('Rat', 'RatFloat', 'Factors',)

Rat = int | Fraction
RatFloat = int | float | Fraction
Factors = Mapping[int, Rat]
