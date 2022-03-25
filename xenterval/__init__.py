"""Xenharmonic and tuning-related utilities.

By arseniiv. Preferably use with Python 3.10.
License: https://opensource.org/licenses/MIT
"""

from __future__ import annotations
from xenterval.typing import *
from xenterval.interval import *
from xenterval.tuning import *
from xenterval.ji import *
from xenterval.interval.name.fjs import *
from xenterval.interval.name.color import *

__version__ = '0.2.1'


#TODO? <https://en.xen.wiki/w/SHEFKHED_interval_names>

#TODO? things about interval approximation?:
# <https://en.xen.wiki/w/Interval_calculator>
# <https://untwelve.org/interval_calc>
# <https://www.yacavone.net/xen-calc>
# NB semi-convergents?


if __name__ == '__main__':
    from xenterval._xenwiki import _main
    _main()
