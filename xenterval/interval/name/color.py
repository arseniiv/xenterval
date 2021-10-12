from __future__ import annotations
from typing import Final, Iterator, Mapping
from functools import lru_cache
from math import floor
from xenterval._common import KNOWN_PRIMES
from xenterval.interval import Interval
from xenterval.ji import Monzo

__all__ = ('color_name', 'color_val')

# pylint: disable=unsubscriptable-object

_SUP_TRANSLATION: Final[dict[int, int | None]] = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')

def color_name(m: Monzo[int]) -> str:
    def multiplied(s: str, n: int) -> str:
        n = abs(n)
        if n < 2:
            return s * n
        if n == 2:
            return s + s[-1]
        return s + str(n).translate(_SUP_TRANSLATION)

    def primary(p: int, x: int) -> str:
        mode = 0 if x > 0 else 1
        try:
            s = _data[p][mode]
        except KeyError:
            s = str(p) + ('o', 'u')[mode]
        return multiplied(s, x)

    stepspan = sum(e1 * e2 for e1, e2 in zip(m.entries, color_val()))
    negative = stepspan < 0
    stepspan = abs(stepspan)
    octaves, reduced_stepspan = divmod(stepspan, 7)
    if 7 <= stepspan <= 9 or stepspan == 15:
        octaves -= 1
        reduced_stepspan += 7
    degree = reduced_stepspan + 1
    magnitude = round(sum(m.entries[1:]) / 7)

    segments = []
    color_chunks = tuple((p, x) for p, x in reversed(m.primes_exponents(2)))

    segments.append(multiplied('L' if magnitude > 0 else 's', magnitude))
    segments.append(multiplied('c', octaves))
    if not color_chunks:
        segments.append('w')
    for p, x in color_chunks:
        segments.append(primary(p, x))
    if negative:
        segments.append('-')
    segments.append(str(degree))

    return ''.join(segments)

@lru_cache
def color_val() -> tuple[int, ...]:
    degrees_24edo = (0, 1, 1, 1, 1, 2, # 0 — 50 — 100 — 150 — 200 — 250 — 300
                     2, 2, 2, 3, 3, 3, # 300 — ... — 600
                     4, 4, 4, 5, 5, 5, # 600 — ... — 900
                     5, 6, 6, 6, 6, 7) # 900 — ... — 1200

    def gen() -> Iterator[int]:
        for p in KNOWN_PRIMES:
            cents = Interval.from_ratio(p).cents
            octaves, reduced_cents = divmod(cents, 1200)
            reduced_steps = degrees_24edo[floor(reduced_cents / 50)]
            yield reduced_steps + round(octaves) * 7

    return tuple(gen())

_data: Final[Mapping[int, tuple[str, str]]] = {
    5: ('y', 'g'),
    7: ('z', 'r'),
    11: ('1o', '1u'),
    13: ('3o', '3u'),
}
