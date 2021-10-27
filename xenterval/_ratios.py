from __future__ import annotations
from fractions import Fraction
from typing import Iterator
from xenterval.typing import Rat, RatFloat

__all__ = ('convergents',)

def convergents(x: RatFloat) -> Iterator[Rat]:
    if isinstance(x, int | float):
        x = Fraction(x)

    m_prev, m, n_prev, n = 0, 1, 1, 0
    while True:
        a, frac = divmod(x, 1)
        m_prev, m = m, a * m + m_prev
        n_prev, n = n, a * n + n_prev
        yield Fraction(m, n)
        if not frac:
            break
        x = 1 / frac
