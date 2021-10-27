from fractions import Fraction
from math import isqrt
from itertools import pairwise
from typing import Mapping
import pytest
from xenterval._primes import KNOWN_PRIMES, prime_index, prime_faсtors


def is_positive_prime(x: int) -> bool:
    if x <= 1 or (x != 2 and x % 2 == 0):
        return False
    return all(x % divisor != 0 for divisor in range(3, isqrt(x), 2))

def assert_positive_prime(x: int) -> None:
    __tracebackhide__ = True  # pylint: disable=unused-variable
    if not is_positive_prime(x):
        pytest.fail(f'not a prime: {x}')

def test_all_primes() -> None:
    for p in KNOWN_PRIMES:
        assert_positive_prime(p)

def test_all_increasing() -> None:
    assert all(x < y for x, y in pairwise(KNOWN_PRIMES))

def test_prime_index() -> None:
    for x in range(-1, KNOWN_PRIMES[-1] + 2):
        if x in KNOWN_PRIMES:
            assert KNOWN_PRIMES[prime_index(x)] == x
        else:
            with pytest.raises(ValueError, match='not a prime'):
                prime_index(x)

@pytest.mark.parametrize(['ratio_str', 'factors'], [
    ('1', {}),
    ('81/1210', {2: -1, 3: 4, 5: -1, 11: -2}),
    ('104060401', {101: 4}),
    ('370069474229841/734815760', {541: 2, 149: 1, 53: 3, 3: 1, 19: 1,
                                   2: -4, 5: -1, 7: -3, 439: -1, 61: -1}),
])
def test_prime_factors(ratio_str: str, factors: Mapping[int, int]) -> None:
    actual_factors = prime_faсtors(Fraction(ratio_str))
    assert actual_factors == factors
