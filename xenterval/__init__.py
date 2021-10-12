"""Xenharmonic and tuning-related utilities.

   By arseniiv. Preferably use with Python 3.10.
   License: https://opensource.org/licenses/MIT
"""

from __future__ import annotations
from xenterval.interval import *
from xenterval.tuning import *
from xenterval.ji import *
from xenterval.interval.name.fjs import *
from xenterval.interval.name.color import *

__version__ = '0.1.0'


#TODO? <https://en.xen.wiki/w/SHEFKHED_interval_names>

#TODO? things about interval approximation?:
# <https://en.xen.wiki/w/Interval_calculator>
# <https://untwelve.org/interval_calc>
# convergents (and semi-convergents) to arbitrary intervals?
# edo-step (“)convergents(”) (what are they?)?


def _main():
    """Tests and some other things, don’t run if you don’t know why."""

    # pylint: disable=redefined-outer-name  # TODO? what is with it today
    from typing import Union, Callable
    from fractions import Fraction
    from xenterval._common import KNOWN_PRIMES

    class WikiIntervalInfobox: # NB there’s only short color name
        def __init__(self) -> None:
            self._fjs = FJS()

        def __call__(self, ratio: Union[str, Fraction, int]) -> str:
            ratio = Fraction(ratio)
            monzo = Monzo.from_ratio(ratio)
            cents = Interval.from_ratio(ratio).cents
            return f"""{{{{Infobox Interval
| JI glyph = 
| Ratio = {ratio.numerator}/{ratio.denominator}
| Monzo = {monzo:s}
| Cents = {cents:.5f}
| Name = 
| Color name = {color_name(monzo)}
| FJS name = {self._fjs.name(monzo)}
| Sound = 
}}}}"""

    f_ = Fraction

    def assert_name_is(namer: Callable[[Monzo[int]], str],
                       ratio: str, res: str) -> None:
        m = Monzo.from_ratio(Fraction(ratio))
        actual = namer(m)
        assert actual == res, f'[{m:d}] Expected: {res}, actual: {actual}'

    def ex1(): # regular_tuning, Interval
        tuning_12edo = regular_tuning(12, Interval.from_ratio(f_(2, 1)))
        print(tuning_12edo)

    ex1()

    def ex2(): # Monzo, JISubgroup
        m1 = Monzo(-1, 1, 0, 0)
        print(m1, m1.ratio, m1.limit)
        m2 = Monzo(-1, 0, f_(1, 2))
        print(m2, m2.ratio, m2.limit)
        print(Monzo.lin_comb((m1, 1), (m2, -1)))
        m3 = Monzo.from_ratio(f_(81, 80))
        print(m3, m3.ratio, m3.limit)
        gr1 = JISubgroup(2, f_(5, 3), f_(7, 5), f_(11, 3))
        print(gr1, gr1.gen_monzos, gr1.limit)
        gr2 = JISubgroup(2, f_(27, 25), f_(7, 3))
        print(gr2, gr2.gen_monzos, gr2.limit)
        print(m1 in gr1, m1 in gr2, m3 in gr1)
        gr3 = JISubgroup.p_limit(5)
        print(m1 in gr3, m2 in gr3, m3 in gr3)

    ex2()

    def ex3(): # xen wiki stuff: infobox, interval cents (might be outdated now)
        infobox = WikiIntervalInfobox()
        print(infobox('19/10'))
        #print(r := Monzo(2, -1, -1, 0, 0, 0, 1).ratio)
        #print(Interval.from_ratio(r).cents)

    ex3()

    def ex4(): # monzo formatting
        m = Monzo(1, 2, 1, 0, f_(1, 2), 0, 0, 0, -1)
        print(f'{m}', f'{m:s}', f'{m:d}', sep='\n')
        print(color_val())

    ex4()

    def ex5(): # color names
        cases: tuple[tuple[str, str], ...] = (
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
        )
        for case in cases:
            assert_name_is(color_name, *case)

    ex5()

    def ex6(): # FJS commas and names
        fjs = FJS()

        commas: tuple[str, ...] = (
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
        for expected, actual, p in zip(commas, fjs.commas, KNOWN_PRIMES[2:]):
            if Fraction(expected) != actual:
                assert False, f'[{p}] Expected: {expected}, actual: {actual}'

        cases: tuple[tuple[str, str], ...] = (
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
        )
        def namer(m: Monzo) -> str:
            return str(fjs.name(m))
        for case in cases:
            assert_name_is(namer, *case)

    ex6()

if __name__ == '__main__':
    _main()
