from fractions import Fraction
from typing import Callable
import pytest
from xenterval.ji import Monzo
from xenterval.interval.name.fjs import FJS, FJSName

def test_fjs_commas() -> None:
    commas_str = (
        '80/81',
        '63/64',
        '33/32',
        '1053/1024',
        '4131/4096',
        '513/512',
        '736/729',
        '261/256',
        '248/243',
    )
    commas_expected = tuple(map(Fraction, commas_str))
    fjs = FJS()
    commas_actual = tuple(map(lambda m: m.ratio, fjs.commas[:len(commas_str)]))
    assert commas_actual == commas_expected

Namer = Callable[[Monzo], FJSName]

@pytest.fixture(scope='module')
def fjs_namer() -> Namer:
    return FJS().name

# pylint: disable=redefined-outer-name

@pytest.mark.parametrize(['ratio_str', 'name'], [
    ('66/65', 'P1^11_5,13'),
    ('99/98', 'm-2^11_7,7'),
    ('98/99', 'm2^7,7_11'),
    ('648/625', 'd2_5,5,5,5'),
    ('11/10', 'm2^11_5'),
    ('6272/5625', 'ddd4^7,7_5,5,5,5'),
    ('9/8', 'M2'),
    ('64/55', 'm3_5,11'),
    ('161/128', 'M3^7,23'),
    ('25/18', 'A4^5,5'),
    ('16384/10935', 'd6_5'),
    ('19/11', 'm7^19_11'),
    ('959/540', 'dd8^7,137_5'),
    ('19/10', 'd8^19_5'),
    ('49/25', 'd9^7,7_5,5'),
    ('16/5', 'm13_5'),
    ('4/1', 'P15'),
    ('5/1', 'M17^5'),
    ('6/1', 'P19'),
    ('7/1', 'm21^7'),
    ('182/9', 'd32^7,13'),
    ('1333341/34816', 'AAA36^31,59_17'),
    ('1/1', 'P1'),
    ('2048/2187', 'd1'),
    ('2187/2048', 'A1'),
    ('2/1', 'P8'),
    ('1/2', 'P-8'),
    ('4096/2187', 'd8'),
    ('2187/1024', 'A8'),
    ('1024/2187', 'A-8'),
    ('2187/4096', 'd-8'),
    ('4194304/4782969', 'dd1'),
    ('4782969/4194304', 'AA1'),
    ('1073741824/1162261467', 'dd2'),
    ('43046721/33554432', 'AA2'),
    ('1162261467/1073741824', 'dd-2'),
    ('33554432/43046721', 'AA-2'),
    ('128/2187', 'A-29'),
    ('2187/128', 'A29'),
    ('81/16', 'M17'),
    ('16/81', 'M-17'),
    ('243/32', 'M21'),
    ('32/243', 'M-21'),
    ('2/3', 'P-5'),
    ('128/27', 'm17'),
    ('27/128', 'm-17'),
    ('64/9', 'm21'),
    ('9/64', 'm-21'),
    ('531441/262144', 'A7'),
    ('531441/524288', 'd-2'),
])
def test_fjs_name(fjs_namer: Namer, ratio_str: str, name: str) -> None:
    m = Monzo.from_ratio(Fraction(ratio_str))
    assert str(fjs_namer(m)) == name
