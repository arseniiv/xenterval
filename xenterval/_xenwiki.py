from fractions import Fraction
from xenterval import Rat, Interval, Monzo, FJS, color_name

__all__ = ()


class WikiIntervalInfobox:  # NB there’s only short color name
    def __init__(self) -> None:
        self._fjs = FJS()

    def __call__(self, ratio: str | Rat) -> str:
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


def _main():  # might be outdated now
    infobox = WikiIntervalInfobox()
    print(infobox('19/10'))
    #print(r := Monzo(2, -1, -1, 0, 0, 0, 1).ratio)
    #print(Interval.from_ratio(r).cents)

if __name__ == '__main__':
    _main()
