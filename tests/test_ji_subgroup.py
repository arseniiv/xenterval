from fractions import Fraction
import pytest
from xenterval.ji import Monzo, JISubgroup


def test_ji_subgroup_sanity() -> None:
    F = Fraction
    m1 = Monzo(-1, 1, 0, 0)
    m2 = Monzo(-1, 0, F(1, 2))
    m3 = Monzo.from_ratio(F(81, 80))
    gr1 = JISubgroup(2, F(5, 3), F(7, 5), F(11, 3))
    assert str(gr1) == '2.5/3.7/5.11/3'
    assert gr1.limit == 11
    assert m1 not in gr1
    assert m3 not in gr1
    gr2 = JISubgroup(2, F(27, 25), F(7, 3))
    assert m1 not in gr2
    gr3 = JISubgroup.p_limit(5)
    assert gr3.limit == 5
    assert gr3.generators == (2, 3, 5)
    assert m1 in gr3
    assert Monzo(1, 1) in gr3
    assert Monzo(0, 2, -1) in gr3
    assert Monzo(-3) in gr3
    assert Monzo(0, -4, 0, 0, 1) not in gr3
    with pytest.raises(ValueError, match='never in a JI subgroup'):
        m2 in gr3
    assert m3 in gr3
    assert not gr1 <= gr3 and not gr3 >= gr2
    assert not gr1 <= gr2 and not gr1 >= gr2
    assert JISubgroup.p_limit(2) <= gr3
    assert JISubgroup.p_limit(7) >= gr2
    assert JISubgroup.p_limit(3) == JISubgroup(F(2), F(8, 3))
