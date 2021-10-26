from __future__ import annotations
from typing import Any, Callable, Final, Iterable, Sequence, SupportsAbs, cast, final, Literal, overload
from dataclasses import dataclass
from fractions import Fraction
from math import isfinite, log2, floor
from xenterval._common import Rat, RatFloat

__all__ = ('interval', 'Interval',)


def _parse_ratfloat(s: str, prefer_fraction: bool = False) -> RatFloat | None:
    classes: tuple[type[int | float | Fraction], ...]
    if prefer_fraction:
        classes = (int, Fraction, float)
    else:
        classes = (int, float, Fraction)
    for cls in classes:
        try:
            return cls(s)
        except ValueError:
            pass
    return None


#TODO? Use prime factorization with rational exponents like <https://github.com/m-yac/microtonal-utils> does? Then refactor what `Monzo` class is for

@overload
def interval(s: str) -> Interval:
    ...
@overload
def interval(numerator: int, denominator: int) -> Interval:
    ...
def interval(x, y=None):
    """An interval constructor for lazy hands:

    ```
    interval(7, 5) == Interval.from_ratio(Fraction(7, 5))
    interval('7/5') == ^
    interval('3.1416') == Interval.from_ratio(3.1416)
    interval('700c') == Interval.from_cents(700)
    interval('6\\22') == Interval.from_edo_steps(6, 22)
    ```
    """

    if isinstance(x, str):
        ratio = _parse_ratfloat(x)
        if ratio is not None:
            return Interval(ratio=ratio)
        if x.endswith(('c', '¢')):
            cents = _parse_ratfloat(x[:-1])
            if cents is not None:
                return Interval(cents=cents)
        try:
            steps_s, edo_s = x.split('\\')
            parse = lambda s: _parse_ratfloat(s, prefer_fraction=True)
            steps, edo = parse(steps_s), parse(edo_s)
            if steps is not None and edo is not None:
                return Interval.from_edo_steps(steps, edo)
        except ValueError:
            pass
        raise ValueError('Unknown format.')

    if isinstance(x, int) and isinstance(y, int):
        return Interval(ratio=Fraction(x, y))

    raise TypeError('Wrong arguments, expected str or two ints.')


@final
@dataclass(eq=False, order=False, frozen=True, slots=True)
class Interval:
    """A musical interval.

    To construct instances, use:
    * `Interval(cents=cent_val)` or `Interval(ratio=ratio_val)`
    or, if you’re surely consistent, specify both.
    * static method `from_edo_steps`

    `cents`, `ratio` and `edo_steps(n)` are the corresponding
    numeric values. Intervals support arithmetic and comparison.
    """

    cents: RatFloat
    ratio: RatFloat

    def __init__(self, cents: RatFloat | None = None,
                       ratio: RatFloat | None = None) -> None:
        if ratio is None:
            r_octaves = None
            ratio_goodness: Literal[0, 1, 2] = 0
        elif isfinite(ratio) and ratio > 0:
            r_octaves = log2(ratio)
            if isinstance(r_octaves, float) and r_octaves % 1 == 0:
                r_octaves = floor(r_octaves)
            ratio_goodness = 1 if isinstance(ratio, float) else 2
        else:
            raise ValueError('Ratio should be positive and finite.')

        if cents is None:
            c_octaves = None
            cents_goodness: Literal[0, 1, 2] = 0
        else:
            cents = Fraction(cents) if isinstance(cents, int) else cents
            c_octaves = cents / 1200
            cents_goodness = 1 if isinstance(cents, float) else 2

        if cents is None is ratio:
            raise ValueError('At least one of cents or ratio should be present.')
        if (r_octaves is not None and
            c_octaves is not None and
            abs(r_octaves - c_octaves) > 1e-8):
            raise ValueError('Cents and ratio should represent the same interval with good precision.')

        if cents_goodness < ratio_goodness:
            cents = 1200 * cast(RatFloat, r_octaves)
        if ratio_goodness < cents_goodness:
            ratio = 2 ** cast(RatFloat, c_octaves)

        object.__setattr__(self, 'cents', cents)
        object.__setattr__(self, 'ratio', ratio)

    def __str__(self) -> str:
        cents, ratio = self.cents, self.ratio
        if isinstance(ratio, int | Fraction):
            return str(ratio)
        if isinstance(cents, int | Fraction):
            return f'{cents}¢'
        return f'({self:c} ~ {self:.5fr})'

    def __format__(self, spec: str) -> str:
        if spec == '': # default
            return self.__str__()
        if spec.endswith('c'): # cents
            prefix_spec = spec[:-1] or '.2f'
            return f'{float(self.cents):{prefix_spec}}¢'
        if spec.endswith('r'): # ratio
            prefix_spec = spec[:-1] or '.5f'
            return format(float(self.ratio), prefix_spec)
        if spec.endswith('p'): # parsable by `interval` and good-looking
            if prefix_spec := spec[:-1]:
                raise ValueError(f'Extraneous spec: {prefix_spec} when using "p".')
            if isinstance(self.ratio, int | Fraction):
                return str(self.ratio)
            cents = self.cents
            if isinstance(cents, int | Fraction):
                x = self.edo_steps(1)
                if isinstance(x, int | Fraction):
                    return f'{x.numerator}\\{x.denominator}'
                if isinstance(cents, int):
                    return f'{cents}¢'
            return f'{float(cents)}¢'
        raise ValueError(f'Unknown format spec: {spec}. Use "", "c", "r" or "p".')

    def edo_steps(self, edo: RatFloat) -> RatFloat:
        """This interval measured in steps of a given edo."""

        x = self.cents * edo
        if isinstance(x, int):
            return Fraction(x, 1200)
        return x / 1200

    @staticmethod
    def zero() -> Interval:
        """A zero interval (unison)."""

        return Interval(0, 1)

    @staticmethod
    def from_edo_steps(steps: RatFloat,
                       edo: RatFloat) -> Interval:
        """Construct an interval steps\\edo."""

        octaves: RatFloat
        # match steps, edo:
        #     case int(), int():
        #         octaves = Fraction(steps, edo)
        #     case _:
        #         octaves = steps / edo
        #TODO replace with match when mypy is ready!
        if isinstance(steps, int) and isinstance(edo, int):
            # if at least one is a `Fraction`, `/` is enough, but not here
            octaves = Fraction(steps, edo)
        else:
            octaves = steps / edo
        return Interval(octaves * 1200, None)

    @overload
    def stack(self, other: Interval) -> Interval:
        ...
    @overload
    def stack(self, other: float) -> float:
        ...
    def stack(self, other):
    #def stack(self, other: Interval | float) -> Interval | float:
        """Stack another interval on top of this, or go this interval from the specified frequency.

        Also use: binary `+` `-`
        """

        ratio, cents = self.ratio, self.cents
        # match other:
        #     case Interval(cents2, ratio2):
        #         return Interval(cents + cents2, ratio * ratio2)
        #     case float(freq):
        #         return freq * ratio
        #TODO replace with match when mypy is ready!
        if isinstance(other, Interval):
            return Interval(cents + other.cents, ratio * other.ratio)
        elif isinstance(other, int | float):
            return other * ratio


    def multiply(self, other: RatFloat) -> Interval:
        """Stack this interval on itself several times, or stretch it an amount.

        Also use: `*` `/`
        """
        return Interval(self.cents * other, self.ratio ** other)

    def stretch_factor(self, other: Interval) -> RatFloat:
        """How much should this interval stretch to become another.
        That is, `i1.multiply(i1.stretch_factor(i2)) == i2`.

        Also use: `/`
        """

        if isinstance(self.cents, int) and isinstance(other.cents, int):
            return Fraction(other.cents, self.cents)
        return other.cents / self.cents

    @property
    def inverse(self: Interval) -> Interval:
        """Invert the interval, making it go downwards if it went upwards and vice versa.

        Also use: unary or binary `-`
        """
        return self.multiply(-1)

    def modulo(self, period: Interval) -> Interval:
        """Take this interval modulo some period.
        Also known as a reduced period (say, octave-reduced etc.).

        Also use: `%`
        """
        return self.divmod(period)[1]

    def divmod(self, period: Interval) -> tuple[int, Interval]:
        """Take this interval modulo some period. Also return how many periods you need to stack upwards to get this interval back.

        Also use: `divmod` function
        """

        periods, reduced_cents = divmod(self.cents, period.cents)
        if (isinstance(self.ratio, int | Fraction) and
            isinstance(period.ratio, int | Fraction)):
            period_ratio = Fraction(period.ratio)
            periods, reduced_ratio = 0, self.ratio
            while reduced_ratio >= period_ratio:
                periods += 1
                reduced_ratio /= period_ratio
            while reduced_ratio < 1:
                periods -= 1
                reduced_ratio *= period_ratio
            return periods, Interval(reduced_cents, reduced_ratio)
        return floor(periods), Interval(reduced_cents, None)

    @property
    def _coarse_cents(self) -> float:
        """A rounded value of cents useful for comparison and hashing."""

        return round(float(self.cents), 10)

    def compare(self, other: Interval) -> Literal[-1, 0, 1]:
        """Compare intervals (algebraically).

        If the cents agree to first 10 fractional digits, they are deemed equal.

        Also use: `==` `!=` `<` `<=` `>` `>=`
        """

        # pylint: disable=protected-access
        diff = self._coarse_cents - other._coarse_cents
        return 0 if not diff else (-1 if diff < 0 else 1)

    def __hash__(self) -> int:
        # needs to be no finer than equality (see `compare`)
        return hash(self._coarse_cents)

    @overload
    def __add__(self, other: Interval) -> Interval:
        ...
    @overload
    def __add__(self, other: float) -> float:
        ...
    def __add__(self, other):
        """`self + other == self.stack(other)`"""

        if isinstance(other, Interval | int | float):
            return self.stack(other)
        return NotImplemented

    @overload
    def __radd__(self, other: Interval) -> Interval:
        ...
    @overload
    def __radd__(self, other: float) -> float:
        ...
    def __radd__(self, other):
        """`other + self == self.stack(other)`"""

        if isinstance(other, Interval | int | float):
            return self.stack(other)
        return NotImplemented

    def __sub__(self, other: Interval) -> Interval:
        """`self - other == self.stack(other.inverse)`"""

        if isinstance(other, Interval):
            return self.stack(other.inverse)
        return NotImplemented

    def __neg__(self) -> Interval:
        """`-self == self.inverse`"""

        return self.inverse

    def __mul__(self, other: RatFloat) -> Interval:
        """`self * other == self.multiply(other)`"""

        if isinstance(other, int | float | Fraction):
            return self.multiply(other)
        return NotImplemented

    def __rmul__(self, other: RatFloat) -> Interval:
        """`other * self == self.multiply(other)`"""

        if isinstance(other, int | float | Fraction):
            return self.multiply(other)
        return NotImplemented

    @overload
    def __truediv__(self, other: RatFloat) -> Interval:
        ...
    @overload
    def __truediv__(self, other: Interval) -> RatFloat:
        ...
    def __truediv__(self, other):
        """See `multiply` and `stretch_factor`

        ```
        self / num == self.multiply(1 / num)
        intv / self == intv.stretch_factor(self)
        ```
        """

        if isinstance(other, int | float | Fraction):
            return self.multiply(1 / other)
        elif isinstance(other, Interval):
            return other.stretch_factor(self)
        return NotImplemented

    def __mod__(self, other: Interval) -> Interval:
        """`self % other == self.modulo(other)`"""

        if isinstance(other, Interval):
            return self.modulo(other)
        return NotImplemented

    def __floordiv__(self, other: Interval) -> int:
        """`self // other == self.divmod(other)[0]`"""

        if isinstance(other, Interval):
            return self.divmod(other)[0]
        return NotImplemented

    def __divmod__(self, other: Interval) -> tuple[int, Interval]:
        """`divmod(self, other) == self.divmod(other)`"""

        if isinstance(other, Interval):
            return self.divmod(other)
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        """See `compare`."""

        if isinstance(other, Interval):
            return self.compare(other) == 0
        return False

    def __ne__(self, other: object) -> bool:
        """See `compare`."""

        if isinstance(other, Interval):
            return self.compare(other) != 0
        return True

    def __lt__(self, other: Interval) -> bool:
        """See `compare`."""

        if isinstance(other, Interval):
            return self.compare(other) < 0
        return NotImplemented

    def __le__(self, other: Interval) -> bool:
        """See `compare`."""

        if isinstance(other, Interval):
            return self.compare(other) <= 0
        return NotImplemented

    def __gt__(self, other: Interval) -> bool:
        """See `compare`."""

        if isinstance(other, Interval):
            return self.compare(other) > 0
        return NotImplemented

    def __ge__(self, other: Interval) -> bool:
        """See `compare`."""

        if isinstance(other, Interval):
            return self.compare(other) >= 0
        return NotImplemented

    def __abs__(self) -> Interval:
        """If this interval is downwards, invert it; otherwise return as it is. The result always goes upwards."""

        ratio = self.ratio
        if isinstance(ratio, int):
            ratio = Fraction(ratio)
        cents: SupportsAbs[RatFloat] = self.cents
        return Interval(abs(cents), 1 / ratio if ratio < 1 else ratio)

    def approximate_in_edo(self, edo: int) -> tuple[Interval, Interval]:
        """Approximate this interval in a given edo, returning the approximation and the error."""

        steps = self.edo_steps(edo)
        edo_approx = Interval.from_edo_steps(round(steps), edo)
        return edo_approx, edo_approx - self
