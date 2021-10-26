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

__version__ = '0.1.2'


#TODO? <https://en.xen.wiki/w/SHEFKHED_interval_names>

#TODO? things about interval approximation?:
# <https://en.xen.wiki/w/Interval_calculator>
# <https://untwelve.org/interval_calc>
# convergents (and semi-convergents) to arbitrary intervals?
# edo-step (“)convergents(”)?

def _main():
    """Older tests and some other things, don’t run if you don’t know why."""

    # pylint: disable=redefined-outer-name
    from fractions import Fraction

    class WikiIntervalInfobox:  # NB there’s only short color name
        def __init__(self) -> None:
            self._fjs = FJS()

        def __call__(self, ratio: str | Fraction | int) -> str:
            ratio = Fraction(ratio)
            monzo = Monzo.from_ratio(ratio)
            cents = Interval(ratio=ratio).cents
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

    def xen_wiki_stuff():  # might be outdated now
        infobox = WikiIntervalInfobox()
        print(infobox('19/10'))
        #print(r := Monzo(2, -1, -1, 0, 0, 0, 1).ratio)
        #print(Interval.from_ratio(r).cents)

    xen_wiki_stuff()

if __name__ == '__main__':
    _main()
