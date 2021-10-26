from fractions import Fraction
from math import nan, inf
from typing import Any
import pytest
from xenterval.interval import interval as i, Interval


@pytest.mark.parametrize('ratio', [-3, 0, nan, inf, -inf])
def test_incorrect_init_ratio(ratio: float) -> None:
    with pytest.raises(ValueError, match='positive and finite'):
        Interval(ratio=ratio)

def test_incorrect_init() -> None:
    with pytest.raises(ValueError, match='should be present'):
        Interval(None, None)
    with pytest.raises(ValueError, match='should represent the same'):
        Interval(0, 1.5)

@pytest.mark.parametrize(['text', 'data', 'two_way'], [
    ('1', Interval.zero(), True),
    ('0 c', Interval.zero(), False),
    ('0¢', Interval.zero(), False),
    ('0\\13', Interval.zero(), False),
    ('7\\12', Interval.from_edo_steps(7, 12), True),
    ('3.5\\6', Interval.from_edo_steps(7, 12), False),
    ('1\\2', Interval.from_edo_steps(6, 12), True),
    ('6\\12', Interval.from_edo_steps(1, 2), False),
    ('-4\\17', Interval.from_edo_steps(-4, 17), True),
    ('3/2', Interval(ratio=Fraction(3, 2)), True),
    ('33/22', Interval(ratio=Fraction(3, 2)), False),
    ('1.5', Interval(ratio=1.5), False),
    ('700c', Interval.from_edo_steps(7, 12), False),
    ('700.0¢', Interval(cents=700.), True),
])
def test_parsing(text, data, two_way: bool) -> None:
    assert i(text) == data
    assert two_way is (format(data, 'p') == text)

def assert_equal_precisely(i1: Interval, i2: Interval) -> None:
    __tracebackhide__ = True  # pylint: disable=unused-variable
    assert i1.cents == i2.cents
    assert i1.ratio == i2.ratio

@pytest.mark.parametrize(['i1', 'i2'], [
    (Interval(cents=0), Interval.zero()),
    (Interval(ratio=1), Interval.zero()),
    (Interval.from_edo_steps(0, 31), Interval.zero()),
    (Interval.from_edo_steps(17, 17), Interval(ratio=2)),
    (Interval(cents=1200), Interval(ratio=2)),
    (Interval(cents=750), Interval.from_edo_steps(15, 24)),
])
def test_consistency(i1: Interval, i2) -> None:
    assert_equal_precisely(i1, i2)

def test_consistency2() -> None:
    cents = 750.3
    assert Interval(cents=cents).cents == cents
    ratio = 7.503
    assert Interval(ratio=ratio).ratio == ratio
    steps, edo = 12.5, 7
    intv = Interval.from_edo_steps(steps=steps, edo=edo)
    assert intv.edo_steps(edo) == pytest.approx(steps)

@pytest.mark.parametrize('spec', ['', 'c', '.8fc', 'r', '.8fr', 'p'])
def test_formats_work(spec: str) -> None:
    format(i('1.742'), spec)

# pylint: disable=invalid-unary-operand-type
@pytest.mark.parametrize(['i1', 'i2'], [
    (i('4/3') + i('3/2'), i('2')),
    (i('7\\15') + i('2'), i('22\\15')),
    (i('7\\15') + i('1200c'), i('22\\15')),
    (i('2\\5') + i('3\\8'), i('31\\40')),
    (i('50\\7') - i('4'), i('36\\7')),
    (-i('4/13'), i('13/4')),
    (i('8/7') * 2, i('64/49')),
    (i('-8\\7') * 3, i('-24\\7')),
    (i('5') % i('2'), i('5/4')),
    (i('49\\24') % i('10\\12'), i('9\\24')),
    (divmod(-i('4\\12'), i('7\\12')), (-1, i('3\\12'))),
    (divmod(-i('6/5'), i('3/2')), (-1, i('5/4'))),
    (i('1200c') / i('750c'), Fraction(1200, 750)),
    (i('1\\763') * (763 * 3), i('8')),
    (i('99\\34') * Fraction(34, 99), i('2')),
])
def test_exact_arithmetic(i1: Any, i2: Any) -> None:
    if isinstance(i1, Interval) and isinstance(i2, Interval):
        assert_equal_precisely(i1, i2)
    else:
        assert i1 == i2

@pytest.mark.parametrize(['i1', 'i2'], [
    (i('183.1c') + i('202.2c'), i('385.3c')),
    (i('2.5') + 440, 1100),
    (440 + i('2.5'), 1100),
    (i('2.5') - i('2'), i('1.25')),
    (-i('4/3'), i('3/4')),
    (i('100.c') * 3.5, i('350.c')),
    (3.5 * i('100.c'), i('350.c')),
    (i('350.c') / 3.5, i('100.c')),
    (i('350.c') / i('100.c'), 3.5),
    (i('350.c') // i('100.c'), 3),
    (i('350.c') % i('100.c'), i('50.c')),
    (i('4/3') == (i('5/4')), False),
    (i('4/3') != (i('5/4')), True),
    (i('4/3') <= (i('3/2')), True),
    (i('4/3') >= (i('3/2')), False),
    (i('4/3') < (i('3/2')), True),
    (i('4/3') > (i('3/2')), False),
    (abs(i('0.625')), i('1.6')),
    (abs(i('1.6')), i('1.6')),
])
def test_arithmetic(i1: Any, i2: Any) -> None:
    assert i1 == i2

@pytest.mark.parametrize(['intv', 'edo', 'approx'], [
    (i('2'), 19, i('19\\19')),
    (i('4/3'), 17, i('7\\17')),
    (i('4/5'), 12, i('-4\\12')),
    (i('6.499999999\\19'), 19, i('6\\19')),
    (i('6.500000001\\19'), 19, i('7\\19')),
])
def test_approximate_in_edo(intv: Interval, edo: int, approx: Interval) -> None:
    true_approx, error = intv.approximate_in_edo(edo)
    assert true_approx == approx

    halfstep = Interval.from_edo_steps(Fraction(1, 2), edo)
    assert abs(error) <= halfstep
