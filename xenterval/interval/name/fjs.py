from __future__ import annotations
from typing import final, Final, Sequence, Iterator, Mapping
from dataclasses import dataclass
from fractions import Fraction
from math import log2, floor, sqrt
from xenterval.typing import Rat
from xenterval.interval import Interval
from xenterval.ji import Monzo
from xenterval._primes import KNOWN_PRIMES

__all__ = ('FJS', 'FJSName')


#TODO? Neutral FJS


_SQRT2: Final[float] = sqrt(2)


@final
class FJS:
    """Naming of intervals using FJS.
    
    See <https://misotanni.github.io/fjs/en/index.html>."""
    _radius_cents: Final[float]
    commas: Final[Sequence[Monzo[int]]]

    def _formal_comma(self, p: int) -> Monzo[int]:
        two: Final[Fraction] = Fraction(2)
        three: Final[Fraction] = Fraction(3)

        def reduced_balanced(r: Rat) -> Rat:
            octaves = floor(log2(r))
            r /= two ** octaves
            return r if r < _SQRT2 else r / 2

        def all_shifts() -> Iterator[int]:
            yield 0
            k = 0
            while True:
                k += 1
                yield k
                yield -k

        radius = self._radius_cents
        for k in all_shifts():
            comma = reduced_balanced(p * three ** -k)
            if abs(float(Interval(ratio=comma).cents)) < radius:
                return Monzo.from_ratio(comma)
        assert False, 'Unreachable'

    def __init__(self, tolerance_radius: float = 65 / 63) -> None:
        """Initialize an FJS namer.
        Set custom radius of tolerance only if you want to experiment."""

        assert tolerance_radius > 0
        self._radius_cents = float(Interval(ratio=tolerance_radius).cents)
        self.commas = tuple(self._formal_comma(p) for p in KNOWN_PRIMES[2:])

    def name(self, m: Monzo[int]) -> FJSName:
        """Name an interval using FJS notation."""

        commas_ks = ((c, -x) for c, x in zip(self.commas, m.entries[2:]))
        pythagorean = Monzo.lin_comb((m, 1), *commas_ks)

        otonal_commas = tuple(p for p, x in m.primes_exponents(2)
                                if x > 0 for _ in range(x))
        utonal_commas = tuple(p for p, x in m.primes_exponents(2)
                                if x < 0 for _ in range(-x))

        def var_deg_oct_sign(twos: int, fifths: int, sign: int) -> tuple[int, int, int, int]:
            fifths_d7, fifths_m7 = divmod(fifths, 7)
            octave_shift = (0, 0, 1, 1, 2, 2, 3)[fifths_m7] + 4 * fifths_d7
            octaves = twos + fifths + octave_shift

            fifths_sign = (1 if fifths >= 0 else -1)
            abs_fifths = abs(fifths)
            if abs_fifths <= 1:  # P
                variant = 0
            elif abs_fifths <= 5:  # m, M
                variant = 1
            else:  # d, A, dd, AA, ...
                variant = (abs_fifths + 8) // 7

            degree = (0, 4, 1, 5, 2, 6, 3)[fifths_m7]
            return variant * fifths_sign, degree, octaves, sign

        twos, threes = pythagorean.entry_at(0), pythagorean.entry_at(1)
        for candidate in ((twos, threes, 1), (-twos, -threes, -1)):
            variant, degree, octaves, sign = var_deg_oct_sign(*candidate)
            if octaves >= 0:  # avoid neg. octave shifts, use neg. degrees
                return FJSName(variant, (degree + octaves * 7) * sign,
                               otonal_commas, utonal_commas)
        assert False, 'Unreachable'

@final
@dataclass(frozen=True)
class FJSName:
    """A unified FJS name representation, allowing to generate different string representations (use `str` or `format`)."""

    variant: int  # P → 0, m → -1, M → +1, d → -2, A → +2, dd → -3, AA → +3…
    degree: int
    otonal_commas: tuple[int, ...]
    utonal_commas: tuple[int, ...]

    def __str__(self) -> str:
        return format(self, '')

    def __format__(self, spec: str) -> str:
        try:
            fo1, fo2, fu1, fu2, fc = _format_data[spec]
        except KeyError:
            raise ValueError('Spec should be one of "", "h", "t".') from None
        segments = []
        v = self.variant
        if -1 <= v <= 1:
            segments.append(('m', 'P', 'M')[v + 1])
        else:
            segments.append(('d' if v < 0 else 'A') * (abs(v) - 1))
        if self.degree < 0:
            segments.append('-')
        segments.append(str(abs(self.degree) + 1))
        if self.otonal_commas:
            segments.append(fo1)
            segments.append(fc.join(map(str, self.otonal_commas)))
            segments.append(fo2)
        if self.utonal_commas:
            segments.append(fu1)
            segments.append(fc.join(map(str, self.utonal_commas)))
            segments.append(fu2)
        return ''.join(segments)

_format_data: Final[Mapping[str, tuple[str, str, str, str, str]]] = {
    '': ('^', '', '_', '', ','),  # ASCII
    'h': ('<sup>', '</sup>', '<sub>', '</sub>', ','),  # HTML
    't': ('^{', '}{}', '_{', '}', '{,}'),  # TeX
}
