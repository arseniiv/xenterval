from __future__ import annotations
from typing import Sequence, final, Final, TypeVar, Generic, overload, Iterator
from itertools import islice
from functools import cached_property, lru_cache
from fractions import Fraction
from math import prod
from more_itertools import pairwise
from xenterval._common import Rat, RatFloat, KNOWN_PRIMES

__all__ = ('known_primes', 'Monzo', 'JISubgroup',)

#_TR = TypeVar('_TR', int, Rat)
#_TR = TypeVar('_TR', bound=Rat)
_TR = TypeVar('_TR', int, Fraction)

def known_primes() -> Sequence[int]:
    """All the primes this package may use."""

    return KNOWN_PRIMES

@final
class Monzo(Generic[_TR]):
    """A monzo."""

    def __init__(self, *entries: _TR) -> None:
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
        self._entries: Final[tuple[_TR, ...]] = entries

    @property
    def entries(self) -> tuple[_TR, ...]:
        return self._entries

    def entry_at(self, index: int) -> int | _TR:
        return self._entries[index] if index < len(self) else 0

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

    def _extended_entries(self, length: int) -> tuple[_TR, ...]:
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
    def lin_comb(*elems: tuple[Monzo[Fraction], Rat]) -> Monzo[Fraction]: ...
    @staticmethod
    #def lin_comb(*elems: tuple[Monzo[_TR], int | _TR]) -> Monzo[_TR]:
    def lin_comb(*elems):
        """A linear combination of several monzos."""

        length = max(len(m) for m, _ in elems)
        # pylint: disable=protected-access
        ext_elems = (m._extended_entries(length) for m, _ in elems)
        ks = tuple(k for _, k in elems)
        # entries = (sum(e * k for e, k in zip(single_entries, ks))
        #                      for single_entries in cast(
        #                          'Iterator[tuple[_TR, ...]]',
        #                          zip(*ext_elems)))
        entries = (sum(e * k for e, k in zip(single_entries, ks))
                             for single_entries in zip(*ext_elems))
        return Monzo(*entries)

    @property
    def limit(self) -> int:
        """Which smallest JI limit this monzo belongs to."""

        return KNOWN_PRIMES[len(self) - 1] if self else -1

    def primes_exponents(self, start: int = 0, stop: int | None = None) -> tuple[tuple[int, _TR], ...]:
        """Return a tuple of pairs (prime, exponent) for the number this monzo represents."""

        all_ = zip(KNOWN_PRIMES, self._entries)
        return tuple((p, x) for p, x in islice(all_, start, stop) if x != 0)

    @overload
    def ratio(self: Monzo[int]) -> Fraction: ...
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
        # hopefully rations wouldn’t get that complex;
        # use a simple factorization method

        def p_adic_val(n: int, p: int) -> tuple[int, int]:
            """Returns (d_p(n), n / p ** d_p(n))."""
            result = 0
            while True:
                quot, rem = divmod(n, p)
                if rem != 0:
                    break
                n = quot
                result += 1
            return result, n

        n, d = ratio.numerator, ratio.denominator
        if n == 1 == d:
            return Monzo()
        if n <= 0:
            raise ValueError('Ratio should be positive.')
        entries: list[int] = []
        for p in KNOWN_PRIMES:
            pos_exp, n = p_adic_val(n, p)
            neg_exp, d = p_adic_val(d, p)
            entries.append(pos_exp - neg_exp)
            if n == 1 == d:
                return Monzo(*entries)
        raise ValueError('This ratio contains large primes I don’t know.')


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
            # pylint: disable=undefined-variable #TODO? remove when possible
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
        for i, kp in enumerate(KNOWN_PRIMES):
            if p == kp:
                return JISubgroup(*KNOWN_PRIMES[:i + 1])
            if p < kp:
                raise ValueError(f'{p} is not a prime.')
        raise ValueError(f'{p} is too large and is not a prime I know about.')

    def __str__(self) -> str:
        return '.'.join(str(x) for x in self.generators)

    __repr__ = __str__ # I prefer readability of tuples etc.

    def __contains__(self, elem: Rat | Monzo[int]) -> bool:
        if isinstance(elem, int | Fraction):
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
            assert len(elem) < len(m) #TODO later delete this
        return not elem
