from fractions import Fraction
from math import pi
from xenterval._ratios import convergents

def test_convergents() -> None:
    pi_convergents = list(convergents(pi))
    assert pi_convergents[:3] == [3, Fraction(22, 7), Fraction(333, 106)]
    assert pi_convergents[-1] == pi
    assert list(convergents(0)) == [0]
