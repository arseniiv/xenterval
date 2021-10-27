from __future__ import annotations
from functools import lru_cache
from typing import Final, Mapping
from bisect import bisect_left
from types import MappingProxyType
from xenterval.typing import Rat

__all__ = ('KNOWN_PRIMES', 'prime_index', 'prime_faсtors')

# the first 100 prime numbers
KNOWN_PRIMES: Final[tuple[int, ...]] = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
    233, 239, 241, 251, 257, 263, 269, 271, 277, 281,
    283, 293, 307, 311, 313, 317, 331, 337, 347, 349,
    353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
    419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
    467, 479, 487, 491, 499, 503, 509, 521, 523, 541,
)

def prime_index(p: int) -> int:
    index = bisect_left(KNOWN_PRIMES, p)
    if index < len(KNOWN_PRIMES) and KNOWN_PRIMES[index] == p:
        return index
    raise ValueError('Either this is not a prime or it’s too large.')

@lru_cache
def prime_faсtors(ratio: Rat) -> Mapping[int, int]:
    """Factorize a positive number into prime powers.

    For example, as 81/1210 = 2⁻¹ ⋅ 3⁴ ⋅ 5⁻¹ ⋅ 11⁻², we have
    `prime_factors(Fraction(81, 1210)) == {2: -1, 3: 4, 5: -1, 11: -2}`.
    
    If there are primes too large, `ValueError` is raised."""
    # using a simple factorization method here

    def p_adic_val(n: int, p: int) -> tuple[int, int]:
        """For n > 0, returns (d_p(n), n / p ** d_p(n)).

        For d_p, see <https://en.wikipedia.org/wiki/P-adic_order>."""

        result = 0
        while True:
            quot, rem = divmod(n, p)
            if rem != 0:
                break
            n = quot
            result += 1
        return result, n

    n, d = ratio.numerator, ratio.denominator
    if n == 1 == d:
        return MappingProxyType({})
    if n <= 0:
        raise ValueError('Ratio should be positive.')

    entries: dict[int, int] = {}
    for p in KNOWN_PRIMES:
        pos_exp, n = p_adic_val(n, p)
        neg_exp, d = p_adic_val(d, p)
        exp = pos_exp - neg_exp
        if exp:
            entries[p] = exp
        if n == 1 == d:
            return MappingProxyType(entries)

    raise ValueError('This ratio contains large primes I don’t know.')
