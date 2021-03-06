from __future__ import annotations
from typing import Sequence, TypeAlias, final, Final, TypeVar, Generic, overload, Iterator
from itertools import islice
from functools import cached_property, lru_cache
from fractions import Fraction
from math import prod
from more_itertools import pairwise
from xenterval.typing import Rat, RatFloat
from xenterval._primes import KNOWN_PRIMES, prime_index, prime_faсtors

__all__ = ('known_primes', 'known_prime_index', 'Monzo', 'JISubgroup',)

#_TR = TypeVar('_TR', int, Rat)
#_TR = TypeVar('_TR', bound=Rat)
_TR = TypeVar('_TR', int, Fraction)
MonzoRat: TypeAlias = 'Monzo[int] | Monzo[Fraction]'


def known_primes() -> Sequence[int]:
    """All the primes this package may use."""

    return KNOWN_PRIMES

def known_prime_index(p: int) -> int | None:
    """Get an index of a prime in `known_primes()`, or None."""

    try:
        return prime_index(p)
    except ValueError:
        return None


@final
class Monzo(Generic[_TR]):
    """A monzo."""

    __match_args__ = ('entries',)

    def __init__(self, *entries: int | _TR) -> None:
        """Make a monzo from its entries, which can be `int`s or `Fraction`s."""

        # strip unnecessary zeros
        for i, x in enumerate(reversed(entries)):
            if x != 0:
                entries = tuple(entries[:len(entries) - i])
                break
        else:
            entries = ()
        if len(entries) > len(KNOWN_PRIMES):
            raise ValueError('There are more entries than primes I know of.')
        self._entries: Final[tuple[int | _TR, ...]] = entries

    @property
    def entries(self) -> tuple[int | _TR, ...]:
        return self._entries

    def entry_at(self, index: int) -> int | _TR:
        if index < 0:
            raise ValueError('Index should be nonnegative.')
        return self._entries[index] if index < len(self) else 0

    def entry_at_prime(self, p: int) -> int | _TR:
        return self.entry_at(prime_index(p))

    def __len__(self) -> int:
        return len(self._entries)

    def __str__(self) -> str:
        return f'[{" ".join(str(x) for x in self._entries)}>'

    __repr__ = __str__ # I prefer readability of tuples etc.

    def __format__(self, spec: str) -> str:
        if spec == '': # ket
            return self.__str__()
        if spec == 's': # just space-delimited numbers
            return " ".join(str(x) for x in self._entries)
        if spec == 'd': # prime decomposition
            def gen() -> Iterator[str]:
                for p, x in self.primes_exponents():
                    if x == 1:
                        yield str(p)
                    elif x.denominator == 1:
                        yield f'{p}^{x}'
                    else:
                        yield f'{p}^({x})'
            return " * ".join(gen())
        raise ValueError(f'Unknown format spec: {spec}. Use "", "s" or "d".')

    def _extended_entries(self, length: int) -> tuple[int | _TR, ...]:
        entries = self._entries
        extra = length - len(entries)
        if extra > 0:
            return entries + (0,) * extra  # type: ignore
            #^ `int` has all we need from `Fraction` api, so no harm done
        return entries

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Monzo):
            return (self._extended_entries(len(other)) ==
                    other._extended_entries(len(self)))
        return False

    def __ne__(self, other: object) -> bool:
        if isinstance(other, Monzo):
            return (self._extended_entries(len(other)) !=
                    other._extended_entries(len(self)))
        return False

    def __hash__(self) -> int:
        return hash(self._entries)

    @overload
    @staticmethod
    def lin_comb(*elems: tuple[Monzo[int], int]) -> Monzo[int]: ...
    @overload
    @staticmethod
    def lin_comb(*elems: tuple[Monzo[int], Fraction]) -> Monzo[Fraction]: ...
    @overload
    @staticmethod
    def lin_comb(*elems: tuple[Monzo[int], int | Fraction]) -> MonzoRat: ...
    @overload
    @staticmethod
    def lin_comb(*elems: tuple[Monzo[Fraction], Rat]) -> Monzo[Fraction]: ...
    @overload
    @staticmethod
    def lin_comb(*elems: tuple[MonzoRat, Rat]) -> MonzoRat: ...
    @staticmethod
    #def lin_comb(*elems: tuple[Monzo[_TR], int | _TR]) -> Monzo[_TR]:
    def lin_comb(*elems):
        """A linear combination of several monzos."""

        length = max(len(m) for m, _ in elems)
        # pylint: disable=protected-access
        ext_elems = (m._extended_entries(length) for m, _ in elems)
        ks = tuple(k for _, k in elems)
        entries = (sum(e * k for e, k in zip(single_entries, ks))
                             for single_entries in zip(*ext_elems))
        return Monzo(*entries)

    @property
    def limit(self) -> int:
        """Which smallest JI limit this monzo belongs to."""

        return KNOWN_PRIMES[len(self) - 1] if self else -1

    def primes_exponents(self, start: int = 0, stop: int | None = None) -> tuple[tuple[int, int | _TR], ...]:
        """Return a tuple of pairs (prime, exponent) for the number this monzo represents, with only nonzero exponents."""

        all_ = zip(KNOWN_PRIMES, self._entries)
        return tuple((p, x) for p, x in islice(all_, start, stop) if x != 0)

    @overload
    def ratio(self: Monzo[int]) -> Rat: ...
    @overload
    #def ratio(self: Monzo[Rat]) -> float: ...
    #def ratio(self: Monzo[Rat]) -> RatFloat: ...
    def ratio(self: Monzo[Fraction]) -> RatFloat: ...
    @cached_property
    #def ratio(self: Monzo[int | Rat]) -> RatFloat:
    #def ratio(self) -> RatFloat:
    def ratio(self):
        """Value of this monzo as a ratio (or a float, if it has fractional entries)."""

        return prod(
            (Fraction(p) ** x for p, x in self.primes_exponents()),
            start=1
        )

    @staticmethod
    @lru_cache
    def from_ratio(ratio: Rat) -> Monzo[int]:
        """Get a ratio’s monzo."""

        factorization = dict(prime_faсtors(ratio))
        entries: list[int] = []
        for p in KNOWN_PRIMES:
            if not factorization:
                return Monzo(*entries)
            d = factorization.get(p)
            if d is not None:
                del factorization[p]
            entries.append(d or 0)

        assert not factorization
        return Monzo(*entries)


#TODO: Val, norms, multiplication?


@final
class JISubgroup:
    """A finitely-generated subgroup of JI."""

    generators: Final[tuple[Rat, ...]]
    gen_monzos: Final[tuple[Monzo[int], ...]]
    limit: Final[int]

    def __init__(self, *generators: Rat):
        """Make a JI subgroup from a normal list of its generators.

        Normalness and independence of generators are checked.
        """

        # check normality
        if any((bad_g := g) <= 1 for g in generators):
            # pylint: disable=undefined-variable
            raise ValueError(f'Should be a normal list but {bad_g} <= 1.')
        gen_monzos = tuple(Monzo.from_ratio(g) for g in generators)
        for  m1, m2 in pairwise(gen_monzos):
            if len(m1) >= len(m2):
                raise ValueError(f'Should be a normal list but {m1} before {m2}.')
        self.generators = tuple(generators)
        self.gen_monzos = gen_monzos
        self.limit = gen_monzos[-1].limit if gen_monzos else -1

    @staticmethod
    def p_limit(p: int) -> JISubgroup:
        """Produce a p-limit group."""

        for i, kp in enumerate(KNOWN_PRIMES):
            if p == kp:
                return JISubgroup(*KNOWN_PRIMES[:i + 1])
            if p < kp:
                raise ValueError(f'{p} is not a prime.')
        raise ValueError(f'{p} is too large and is not a prime I know about.')

    def __str__(self) -> str:
        return '.'.join(str(x) for x in self.generators)

    __repr__ = __str__  # I prefer readability of tuples etc.

    def contains(self, elem: Rat | MonzoRat) -> bool:
        """Determine if elem lies in this subgroup."""

        if isinstance(elem, Monzo):
            if any(e.denominator != 1 for e in elem.entries):
                raise ValueError('Fractional monzo is never in a JI subgroup.')
        else:
            elem = Monzo.from_ratio(elem)
        for m in reversed(self.gen_monzos):
            if not elem: # unison
                return True
            if len(elem) > len(m):
                return False
            if len(elem) < len(m):
                continue
            e_lead, m_lead = elem.entries[-1], m.entries[-1]
            quot, rem = divmod(e_lead, m_lead)
            if rem != 0:
                return False
            elem = Monzo.lin_comb((elem, 1), (m, -quot))
        return not elem

    def is_subgroup_of(self, other: JISubgroup) -> bool:
        """Whether this group is a subgroup of another."""

        return all(other.contains(m) for m in reversed(self.gen_monzos))

    def isomorphic(self, other: JISubgroup) -> bool:
        """Whether the two groups are subgroups of each other."""

        if self.limit != other.limit:
            return False
        return (self.is_subgroup_of(other) and
                other.is_subgroup_of(self))

    def __contains__(self, elem: Rat | MonzoRat) -> bool:
        """`elem in self == self.contains(elem)`"""

        return self.contains(elem)

    def __le__(self, other: JISubgroup) -> bool:
        """`self <= other == self.is_subgroup_of(other)`"""

        if isinstance(other, JISubgroup):
            return self.is_subgroup_of(other)
        return NotImplemented

    def __ge__(self, other: JISubgroup) -> bool:
        """`self >= other == other.is_subgroup_of(self)`"""

        if isinstance(other, JISubgroup):
            return other.is_subgroup_of(self)
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        """`(self == other) == self.isomorphic(other)`"""

        if isinstance(other, JISubgroup):
            return self.isomorphic(other)
        return False

    def __ne__(self, other: object) -> bool:
        """`(self != other) == self.isomorphic(other)`"""

        if isinstance(other, JISubgroup):
            return not self.isomorphic(other)
        return True
