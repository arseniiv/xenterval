from __future__ import annotations
from typing import final, Literal, overload
from dataclasses import dataclass
from fractions import Fraction
from math import log2, floor
from xenterval._common import Rat, RatFloat

__all__ = ('Interval',)


@final
@dataclass(frozen=True)
class Interval:
    """A musical interval.

       Use static methods `from_cents`, `from_ratio` or `from_edo_steps`
       to construct instances, or be consistent in case of constructing
       by specifying both cents and ratio.

       `cents`, `ratio` and `edo_steps(n)` are the corresponding
       numeric values. Intervals support arithmetic and comparison.
    """
    cents: RatFloat
    ratio: RatFloat

    def __str__(self) -> str:
        return f'{self:c} ~ {self:.5fr}'

    __repr__ = __str__ # I prefer readability of tuples etc.

    def __format__(self, spec: str) -> str:
        if spec == '': # default
            return self.__str__()
        if spec.endswith('c'): # cents
            prefix_spec = spec[:-1] or '.2f'
            return f'{float(self.cents):{prefix_spec}}¢'
        if spec.endswith('r'): # ratio
            prefix_spec = spec[:-1]
            if prefix_spec:
                return format(float(self.ratio), prefix_spec)
            return str(self.ratio)
        raise ValueError(f'Unknown format spec: {spec}. Use "", "c" or "r".')

    def edo_steps(self, edo: RatFloat) -> RatFloat:
        """This interval measured in steps of a given edo."""
        return self.cents * edo / 1200

    @staticmethod
    def zero() -> Interval:
        """A zero interval (unison)."""
        return Interval(0, 1)

    @staticmethod
    def from_cents(cents: RatFloat) -> Interval:
        """Construct an interval of given cents value."""
        return Interval(cents, 2 ** (cents / 1200))

    @staticmethod
    def from_ratio(ratio: RatFloat) -> Interval:
        """Construct an interval with given ratio."""
        if ratio <= 0:
            raise ValueError('Ratio should be positive.')
        octaves = log2(ratio)
        if isinstance(octaves, float) and octaves % 1 == 0:
            octaves = floor(octaves)
        return Interval(octaves * 1200, ratio)

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
            octaves = Fraction(steps, edo)
        else:
            octaves = steps / edo
        return Interval(octaves * 1200, 2 ** octaves)

    @overload
    def stack(self, other: Interval) -> Interval:
        ...
    @overload
    def stack(self, other: float) -> float:
        ...
    def stack(self, other):
    #def stack(self, other: Interval | float) -> Interval | float:
        """Stack another interval on top of this, or go this interval from the specified frequency."""
        # match other:
        #     case Interval(cents, ratio):
        #         return Interval(self.cents + cents,
        #                         self.ratio * ratio)
        #     case float(freq):
        #         return freq * self.ratio
        #TODO replace with match when mypy is ready!
        if isinstance(other, Interval):
            return Interval(self.cents + other.cents,
                            self.ratio * other.ratio)
        elif isinstance(other, float):
            return other * self.ratio

    def multiply(self, other: RatFloat) -> Interval:
        """Stack this interval on itself several times."""
        return Interval(self.cents * other,
                        self.ratio ** other)

    @property
    def inverse(self: Interval) -> Interval:
        """Invert the interval."""
        return self.multiply(-1)

    def modulo(self, period: Interval) -> Interval:
        """Take this interval modulo some period."""
        return self.divmod(period)[1]

    def divmod(self, period: Interval) -> tuple[int, Interval]:
        """Take this interval modulo some period. Also return how many periods you need to stack to get this interval back."""
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
        return floor(periods), Interval.from_cents(reduced_cents)

    def compare(self, other: Interval) -> Literal[-1, 0, 1]:
        """Compare intervals (algebraically).

           If the cent difference is less than 1e-10, they are deemed equal.
        """
        diff = float(self.cents - other.cents)
        if abs(diff) < 1e-10:
            return 0
        return -1 if diff < 0 else 1

    @overload
    def __add__(self, other: Interval) -> Interval:
        ...
    @overload
    def __add__(self, other: float) -> float:
        ...
    def __add__(self, other):
        """`self + other = self.stack(other)`"""
        if isinstance(other, Interval | float):
            return self.stack(other)
        return NotImplemented

    @overload
    def __radd__(self, other: Interval) -> Interval:
        ...
    @overload
    def __radd__(self, other: float) -> float:
        ...
    def __radd__(self, other):
        """`other + self = self.stack(other)`"""
        if isinstance(other, Interval | float):
            return self.stack(other)
        return NotImplemented

    def __neg__(self) -> Interval:
        """`-self = self.inverse`"""
        return self.inverse

    def __mul__(self, other: RatFloat) -> Interval:
        """`self * other = self.multiply(other)`"""
        if isinstance(other, (float, Fraction)):
            return self.multiply(other)
        return NotImplemented

    def __rmul__(self, other: RatFloat) -> Interval:
        """`other * self = self.multiply(other)`"""
        if isinstance(other, (float, Fraction)):
            return self.multiply(other)
        return NotImplemented

    def __div__(self, other: RatFloat) -> Interval:
        """`self / other = self.multiply(1 / other)`"""
        if isinstance(other, (float, Fraction)):
            return self.multiply(1 / other)
        return NotImplemented

    def __mod__(self, other: Interval) -> Interval:
        """`self % other = self.modulo(other)`"""
        if isinstance(other, Interval):
            return self.modulo(other)
        return NotImplemented

    def __divmod__(self, other: Interval) -> tuple[int, Interval]:
        """`divmod(self, other) = self.divmod(other)`"""
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
        return False

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
