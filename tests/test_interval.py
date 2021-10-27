from fractions import Fraction
from math import nan, inf
from typing import Any
from itertools import islice
import pytest
from xenterval.typing import Factors
from xenterval.interval import interval as i, Interval


@pytest.mark.parametrize('ratio', [-3, 0, nan, inf, -inf])
def test_incorrect_init_ratio(ratio: float) -> None:
    with pytest.raises(ValueError, match='positive and finite'):
        Interval(ratio=ratio)

def test_incorrect_init() -> None:
    with pytest.raises(ValueError, match='a single one'):
        Interval()
    with pytest.raises(ValueError, match='a single one'):
        Interval(factorization={2: 8}, cents=50)
    with pytest.raises(ValueError, match='a single one'):
        Interval(factorization={2: 8}, cents=50, ratio=1.5)

@pytest.mark.parametrize(['text', 'data', 'two_way'], [
    ('1', Interval.zero(), True),
    ('0 c', Interval.zero(), False),
    ('0¢', Interval.zero(), False),
    ('0\\13', Interval.zero(), False),
    ('7\\12', Interval.from_edx_steps(7, 12), True),
    ('3.5\\6', Interval.from_edx_steps(7, 12), False),
    ('1\\2', Interval.from_edx_steps(6, 12), True),
    ('6\\12', Interval.from_edx_steps(1, 2), False),
    ('-4\\17', Interval.from_edx_steps(-4, 17), True),
    ('3/2', Interval(ratio=Fraction(3, 2)), True),
    ('33/22', Interval(ratio=Fraction(3, 2)), False),
    ('1.5', Interval(ratio=1.5), False),
    ('700c', Interval.from_edx_steps(7, 12), False),
    ('7\\12', Interval(cents=700.), True),
])
def test_parsing(text, data, two_way: bool) -> None:
    assert i(text) == data
    assert two_way is (format(data, 'p') == text)

@pytest.mark.parametrize(['intv_str', 'fact'], [
    ('4/1', {2: 2}),
    ('14/9', {2: 1, 3: -2, 7: 1}),
    ('400c', {2: Fraction(1, 3)}),
    ('0c', {}),
    ('3.1416', None),
    ('1.0', {}),
    ('1.2', {2: 1, 3: 1, 5: -1}),
])
def test_factorization(intv_str: str, fact: Factors | None) -> None:
    assert i(intv_str).factorization == fact

def assert_equal_precisely(i1: Interval, i2: Interval) -> None:
    __tracebackhide__ = True  # pylint: disable=unused-variable
    assert i1.cents == i2.cents
    assert i1.ratio == i2.ratio

@pytest.mark.parametrize(['i1', 'i2'], [
    (Interval(cents=0), Interval.zero()),
    (Interval(ratio=1), Interval.zero()),
    (Interval.from_edx_steps(0, 31), Interval.zero()),
    (Interval.from_edx_steps(17, 17), Interval(ratio=2)),
    (Interval(cents=1200), Interval(ratio=2)),
    (Interval(cents=750), Interval.from_edx_steps(15, 24)),
    (Interval({3: Fraction(5, 9)}), Interval.from_edx_steps(5, 9, 3)),
])
def test_consistency(i1: Interval, i2) -> None:
    assert_equal_precisely(i1, i2)

def test_consistency2() -> None:
    cents = Fraction(7503, 10)
    assert Interval(cents=cents).cents == cents
    ratio = 7.503
    assert Interval(ratio=ratio).ratio == ratio
    steps1, divs1 = 12.5, 7
    intv1 = Interval.from_edx_steps(steps1, divs1)
    assert intv1.edx_steps(divs1) == pytest.approx(steps1)
    steps2, divs2, period2 = 5.8, 6, 5
    intv2 = Interval.from_edx_steps(steps2, divs2, period2)
    assert intv2.edx_steps(divs2, period2) == pytest.approx(steps2)


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
    ((i('3.1416') * 3) / i('3.1416'), 3),
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

@pytest.mark.parametrize(['intv', 'edo', 'steps'], [
    (i('2'), 19, 19),
    (i('4/3'), 17, 7),
    (i('4/5'), 12, -4),
    (i('6.499999999\\19'), 19, 6),
    (i('6.500000001\\19'), 19, 7),
])
def test_approximate_in_edx(intv: Interval, edo: int, steps: int) -> None:
    true_steps, error = intv.approximate_in_edx(edo)
    assert true_steps == steps

    halfstep = Interval.from_edx_steps(Fraction(1, 2), edo)
    assert abs(error) <= halfstep

def test_ratio_convergents() -> None:
    expected = (1, Fraction(3, 2), Fraction(442, 295), Fraction(2213, 1477))
    actual = (c for c, _ in i('7\\12').ratio_convergents())
    assert expected == tuple(islice(actual, len(expected)))

def test_edx_convergents() -> None:
    expected = (0, 1, Fraction(1, 2), Fraction(3, 5), Fraction(7, 12))
    actual = (c for c, _ in i('3/2').edx_convergents())
    assert expected == tuple(islice(actual, len(expected)))
