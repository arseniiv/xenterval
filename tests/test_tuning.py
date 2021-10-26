from fractions import Fraction
import pytest
from xenterval.interval import interval as i
from xenterval.tuning import GroupedTuning, regular_tuning, Tuning

def test_grouped_tuning() -> None:
    with pytest.raises(ValueError, match='at least one step'):
        GroupedTuning(())

    with pytest.raises(ValueError, match='non-decreasing'):
        GroupedTuning((i('3/2'), i('6/5'), i('2')))

    t = GroupedTuning((i('600c'), i('2/1')))
    assert t[0] == i('1')
    assert t[5] == i('3000c')
    assert t[-1] == i('-600c')

def test_regular_tuning() -> None:
    with pytest.raises(ValueError, match='at least one step'):
        regular_tuning(0, i('3/1'))

    t = regular_tuning(34, i('2'))
    assert t[0] == i('1')
    assert t[99] == i('99\\34')

def test_tuning() -> None:
    t = regular_tuning(1, i('2'))
    nt = Tuning(440, t)
    assert nt[3] == 440 * 2 ** 3
