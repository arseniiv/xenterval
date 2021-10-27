from __future__ import annotations
from functools import cached_property
from typing import Final, Iterator, final, Literal, overload
from fractions import Fraction
from math import isfinite, log, log2, floor, prod
from types import MappingProxyType
from more_itertools import all_equal
from xenterval.typing import Rat, RatFloat, Factors
from xenterval._primes import prime_faсtors
from xenterval._ratios import convergents

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


#TODO? Now refactor what `Monzo` class is for

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
    interval('6\\22') == Interval.from_edx_steps(6, 22, period=2)
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
                return Interval.from_edx_steps(steps, edo)
        except ValueError:
            pass
        raise ValueError('Unknown format.')

    if isinstance(x, int) and isinstance(y, int):
        return Interval(ratio=Fraction(x, y))

    raise TypeError('Wrong arguments, expected str or two ints.')


def _count_nones(*xs: object) -> int:
    return sum(1 if x is None else 0 for x in xs)


@final
class Interval:
    """A musical interval.

    To construct instances, use:
    * `Interval(cents=750)`
    * `Interval(ratio=Fraction(7, 5))`
    * `Interval(factorization={2: -4, 3: 1, 7: 1})`
    * static methods `zero()`, `from_edx_steps(m, n, p=2)`

    The corresponding accessors are `cents`, `ratio`, `edx_steps(n, p=2)`, `factorization`.
    Intervals support arithmetic and comparison.
    """

    def __init__(self, factorization: Factors | None = None,
                       *,
                       cents: RatFloat | None = None,
                       ratio: RatFloat | None = None) -> None:
        if _count_nones(factorization, cents, ratio) != 2:
            raise ValueError('Just a single one of factorization, cents and ratio should be defined.')

        MAGIC: Final = 3600  # well

        if factorization is not None:
            fact: Factors | float = factorization
        elif ratio is not None:
            if not isfinite(ratio) or ratio <= 0:
                raise ValueError('Ratio should be positive and finite.')
            if (ratio * MAGIC) % 1 == 0:
                ratio = Fraction(floor(ratio * MAGIC), MAGIC)
            if isinstance(ratio, int | Fraction):
                fact = prime_faсtors(ratio)
            else:
                cents = log2(ratio) * 1200
                if cents % 1 != 0:
                    fact = ratio
        elif cents is not None:
            if (cents * MAGIC) % 1 == 0:
                cents = Fraction(floor(cents * MAGIC), MAGIC)
            if isinstance(cents, float):
                fact = 2 ** (cents / 1200)
            elif cents:
                fact = {2: Fraction(cents, 1200)}
            else:
                fact = {}

        if not isinstance(fact, float):
            if 0 in fact.values():
                fact = {p: d for p, d in fact.items() if d != 0}
            if not isinstance(fact, MappingProxyType):
                fact = MappingProxyType(fact)
        self._fact: Final[Factors | float] = fact

    def _is_rational(self) -> Rat | None:
        """Returns `int` or `Fraction` representing this interval accurately, or `None` otherwise."""

        if isinstance(self._fact, float):
            return None

        m, n = 1, 1
        for p, d in self._fact.items():
            if not isinstance(d, int):
                return None
            if d > 0:
                m *= p ** d
            else:
                n *= p ** -d
        return Fraction(m, n) if n != 1 else m

    def _is_multiple_of(self, ratio: Rat | Factors) -> Rat | None:
        """If this interval is an `int` or `Fractional` power of a given ratio, returns the exponent, or `None` otherwise."""

        if isinstance(self._fact, float):
            return None

        if isinstance(ratio, int | Fraction):
            ratio_fact: Factors = prime_faсtors(ratio)
        else:
            ratio_fact = ratio

        exp_multipliers = [Fraction(self._fact.get(p, 0), d)
                           for p, d in ratio_fact.items()]
        if not all_equal(exp_multipliers):
            return None
        if not self._fact.keys() <= ratio_fact.keys():
            return None
        return exp_multipliers[0] if exp_multipliers else 0

    @property
    def factorization(self) -> Factors | None:
        """Factorization of this interval, if any.

        `interval('14/9').factorization == {2: 1, 3: -2, 7: 1}`
        `interval('400c').factorization == {2: Fraction(1, 3)}`"""
        if isinstance(self._fact, float):
            return None
        return self._fact

    @cached_property
    def ratio(self) -> RatFloat:
        """This interval as a ratio."""

        exact_ratio = self._is_rational()
        if exact_ratio is not None:
            return exact_ratio
        if isinstance(self._fact, float):
            return self._fact
        return prod(p ** d for p, d in self._fact.items())

    def edx_steps(self, divisions: RatFloat,
                  period: RatFloat = 2) -> RatFloat:
        """This interval measured in steps of a given edX where X is `period` and defaults to 2 (thus, an edo)."""

        if (isinstance(divisions, int | Fraction) and
            isinstance(period, int | Fraction)):
            exact_steps = self._is_multiple_of(period)
            if exact_steps is not None:
                return exact_steps * divisions
        return log(self.ratio, period) * divisions

    @cached_property
    def cents(self) -> RatFloat:
        """This interval measured in cents."""

        return self.edx_steps(1200, 2)

    @staticmethod
    def zero() -> Interval:
        """A zero interval (unison)."""

        return Interval({})

    @staticmethod
    def from_edx_steps(steps: RatFloat, divisions: RatFloat,
                       period: RatFloat = 2) -> Interval:
        """Construct an interval from an amount of edX steps where X, `period`, defaults to 2 (thus, an edo)."""

        if isinstance(steps, int):
            steps = Fraction(steps)
        return Interval(ratio=period) * (steps / divisions)

    def __repr__(self) -> str:
        if isinstance(self._fact, float):
            return f'Interval(ratio={self._fact})'
        return f'Interval({dict(self._fact)})'

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
                x = self.edx_steps(1)
                if isinstance(x, int | Fraction):
                    return f'{x.numerator}\\{x.denominator}'
                if isinstance(cents, int):
                    return f'{cents}¢'
            return f'{float(cents)}¢'
        raise ValueError(f'Unknown format spec: {spec}. Use "", "c", "r" or "p".')


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

        #TODO replace with match when mypy is ready!
        if isinstance(other, Interval):
            # pylint: disable=protected-access
            fact1, fact2 = self._fact, other._fact
            if (not isinstance(fact1, float) and
                not isinstance(fact2, float)):
                fact = {p: fact1.get(p, 0) + fact2.get(p, 0)
                        for p in fact1.keys() | fact2.keys()}
                return Interval(fact)
            return Interval(ratio=self.ratio * other.ratio)
        elif isinstance(other, int | float):
            return self.ratio * other


    def multiply(self, other: RatFloat) -> Interval:
        """Stack this interval on itself several times, or stretch it an amount.

        Also use: `*` `/`
        """

        fact = self._fact
        if not isinstance(fact, float) and not isinstance(other, float):
            return Interval({p: d * other for p, d in fact.items()})
        return Interval(ratio=self.ratio ** other)

    def stretch_factor(self, other: Interval) -> RatFloat:
        """How much should this interval stretch to become another.
        That is, `i1.multiply(i1.stretch_factor(i2)) == i2`.

        Also use: `/`
        """

        if not isinstance(self._fact, float):
            exact_stretch = other._is_multiple_of(self._fact)
            if exact_stretch is not None:
                return exact_stretch
        return log(other.ratio, self.ratio)

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

        if period.ratio == 1:
            raise ZeroDivisionError('Period should not be an unison.')

        upwards = True
        if period.ratio < 1:
            upwards = False
            self = self.inverse  # pylint: disable=self-cls-assignment
            period = period.inverse

        quot = floor(self.cents // period.cents)
        rem = self - period * quot

        # let’s protect ourselves from possible floating-point inaccuracies
        if rem.ratio < 1:
            rem += period
            quot += 1
        elif rem >= period:
            rem -= period
            quot -= 1

        assert rem.ratio >= 1 and rem < period
        return quot, (rem if upwards else rem.inverse)

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
        self / intv == intv.stretch_factor(self)
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

        return self if self.ratio > 1 else self.inverse

    def approximate_in_edx(self, divisions: RatFloat,
                           period: RatFloat = 2) -> tuple[int, Interval]:
        """Approximate this interval in a given edX, returning the closest number of steps and the error.

        X, `period`, defaults to 2 (thus, an edo)."""

        steps = round(self.edx_steps(divisions, period))
        approx = Interval.from_edx_steps(steps, divisions, period)
        return steps, approx - self

    def ratio_convergents(self) -> Iterator[tuple[Rat, Interval]]:
        """Give successive rational approximations (via convergents) of this interval, yielding pairs (ratio, error)."""

        for c in convergents(self.ratio):
            yield c, Interval(ratio=float(c)) - self

    def edx_convergents(self, period: RatFloat = 2) -> Iterator[tuple[Rat, Interval]]:
        """Give successive approximations (via convergents) of this interval in various edX with the given period, yielding pairs (steps/divisions, error)."""

        edx_steps = self.edx_steps(1, period)
        for c in convergents(edx_steps):
            yield c, Interval.from_edx_steps(c, 1, period) - self
