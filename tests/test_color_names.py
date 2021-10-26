from fractions import Fraction
import pytest
from xenterval.ji import Monzo
from xenterval.interval.name.color import color_name

@pytest.mark.parametrize(['ratio_str', 'name'], [
    ('531441/524288', 'LLw-2'),
    ('27/14', 'r7'),
    ('31/16', '31o7'),
    ('49/25', 'zzgg9'),
    ('19/10', '19og8'),
    ('225/128', 'Lyy6'),
    ('19/11', '19o1u7'),
    ('38/23', '23u19o6'),
    ('128/81', 'sw6'),
    ('49/36', 'zz5'),
    ('4/3', 'w4'),
    ('77/60', '1ozg4'),
    ('76/61', '61u19o4'),
    ('71/57', '71o19u3'),
    ('625/512', 'Ly⁴2'),
    ('39/32', '3o3'),
    ('25/21', 'ryy2'),
    ('7/6', 'z3'),
    ('97/84', '97or2'),
    ('9/8', 'w2'),
    ('55/49', '1orry1'),
    ('243/224', 'Lr1'),
    ('648/625', 'g⁴2'),
    ('50/49', 'rryy-2'),
    ('3125/3072', 'Ly⁵-2'),
    ('100/99', '1uyy1'),
    ('13/2', 'cc3o6'),
    ('7/3', 'z10'),
    ('9/1', 'c³w2'),
])
def test_color_name(ratio_str: str, name: str) -> None:
    m = Monzo.from_ratio(Fraction(ratio_str))
    assert color_name(m) == name
