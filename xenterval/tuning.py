from __future__ import annotations
from fractions import Fraction
from typing import Sequence
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from more_itertools import pairwise
from xenterval.interval import Interval

__all__ = ('IntervalTuning', 'GroupedTuning', 'regular_tuning', 'Tuning',)

class IntervalTuning(ABC):
    """A tuning without information about note frequencies."""

    @abstractmethod
    def __getitem__(self, index: int) -> Interval:
        """Get the specified step of the tuning."""
        raise NotImplementedError


@dataclass(frozen=True)
class GroupedTuning(IntervalTuning):
    """A tuning from the given intervals, repeating by stacking the last interval."""

    intervals: Sequence[Interval]

    def __post_init__(self) -> None:
        if not self.intervals:
            raise ValueError('Tuning should have at least one step.')
        if any(x > y for x, y in pairwise(self.intervals)):
            raise ValueError('Steps should be non-decreasing.')

    @lru_cache
    def __getitem__(self, index: int) -> Interval:
        intervals = self.intervals
        group_count, index = divmod(index - 1, len(intervals))
        return intervals[index] + intervals[-1] * group_count

    def __str__(self) -> str:
        return ('GroupedTuning:\n  ' +
                '\n  '.join(str(i) for i in self.intervals))

    @property
    def period(self) -> Interval:
        """The period of this tuning."""

        return self.intervals[-1]

#TODO? shift, stretch, mode (subset), detune(?), export; shift to make good approximations of specified intervals?..
#TODO: MOS tunings and maybe 2D and other temperaments


def regular_tuning(step_count: int, period: Interval) -> GroupedTuning:
    """An equal-division-of-period tuning."""

    if step_count <= 0:
        raise ValueError('Tuning should have at least one step.')

    intervals = (period * Fraction(index, step_count)
                 for index in range(1, step_count + 1))
    return GroupedTuning(tuple(intervals))


@dataclass
class Tuning:
    """A tuning with information about note frequencies."""

    base_freq: float
    int_tun: IntervalTuning

    def __getitem__(self, index: int) -> float:
        return self.int_tun[index] + self.base_freq
