from __future__ import annotations
from typing import Final
from fractions import Fraction
from bisect import bisect_left

__all__ = ('Rat', 'RatFloat', 'KNOWN_PRIMES', 'prime_index',)

Rat = int | Fraction
RatFloat = float | Fraction

# the first 50 prime numbers
KNOWN_PRIMES: Final[tuple[int, ...]] = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211, 223, 227, 229,)

def prime_index(p: int) -> int:
    index = bisect_left(KNOWN_PRIMES, p)
    if KNOWN_PRIMES[index] == p:
        return index
    raise ValueError('Either this is not a prime or it’s too large.')
