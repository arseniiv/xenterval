from fractions import Fraction
import pytest
from xenterval.ji import Monzo


def test_monzo_sanity() -> None:
    fr = Fraction('-3/2')
    m = Monzo(-2, -3, 0, 1, 0, fr, 1, 0, 0, 0)
    assert len(m.entries) == 7
    for index, entry in [(1, -3), (4, 0), (50, 0)]:
        assert m.entry_at(index) == entry
    assert m.entry_at_prime(7) == 1
    assert str(m) == '[-2 -3 0 1 0 -3/2 1>'
    assert m == m
    assert m.limit == 17
    assert m.primes_exponents(4) == ((13, fr), (17, 1))
    assert m.primes_exponents(1, 5) == ((3, -3), (7, 1))
    # pylint: disable=comparison-with-callable
    assert m.ratio == pytest.approx(2 ** (-2) * 3 ** (-3) * 7 * 13 ** fr * 17)

def test_formats() -> None:
    m = Monzo(1, 2, 1, 0, Fraction(1, 2), 0, 0, 0, -1)
    assert format(m, '') == '[1 2 1 0 1/2 0 0 0 -1>'
    assert format(m, 's') == '1 2 1 0 1/2 0 0 0 -1'
    assert format(m, 'd') == '2 * 3^2 * 5 * 11^(1/2) * 23^-1'

def test_lin_comb() -> None:
    ms = ((Monzo(1, 2, 3), 2),
          (Monzo(0, 4, 0, 2, 0, 0), Fraction('-1/2')),
          (Monzo(), 5),
          (Monzo(1, 0, 1, 0, -1, 0, 1, 0, 0), 1),
          (Monzo(0, 0, 0, 0, 0, 0, 3), Fraction('-1/3')))
    assert Monzo.lin_comb(*ms) == Monzo(3, 2, 7, -1, -1)

@pytest.mark.parametrize(['m', 'ratio'], [
    (Monzo(), 1),
    (Monzo(1, -2, 0, 2, -1, 0), Fraction(2 * 7 ** 2, 3 ** 2 * 11)),
    (Monzo(3, Fraction(1, 2), -1), 2 ** 3 * 3 ** 0.5 / 5),
])
def test_to_ratio(m: Monzo, ratio: int | Fraction | float) -> None:
    assert m.ratio == (pytest.approx(ratio) if isinstance(ratio, float) else ratio)

@pytest.mark.parametrize(['m', 'ratio'], [
    (Monzo(), 1),
    (Monzo(1, -2, 0, 2, -1, 0), Fraction(2 * 7 ** 2, 3 ** 2 * 11)),
    (Monzo(0, 0, 0, 1, 0, 0, 2, 0, 0, 3), 7 * 17 ** 2 * 29 ** 3),
])
def test_from_ratio(m: Monzo, ratio: int | Fraction) -> None:
    assert m == Monzo.from_ratio(ratio)
