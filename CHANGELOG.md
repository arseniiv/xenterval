# Changelog

## 0.1.0

Initial release.

## 0.1.1

* Equality of intervals is now more correct (is an equivalence relation), and their hash is now no finer than the equality.
* Added `interval`, a simple way to make intervals from strings like `700c`, `7/5`, `1.618` or `12\19`. Also, `interval(7, 5) = interval('7/5')`.
* Infinite or NaN ratios are not allowed anymore, who’d thought that!
* You can now match just `Monzo(seq)` instead of `Monzo(entries=seq)`. Intervals don’t obtain that, as usually you’d want to extract either a ratio or a value in cents, and named arguments thus are the way to go.
* Now the more exact of `cents` or `ratio` is used in applying to a frequency, so you can have `interval('1\17') * 17 + 440 = 880` exactly.
* `Monzo.entry_at_prime(p)` is a comfortable way to get an entry instead of guessing prime indices.
* Minor tweaks and typo corrections.
* Still no proper unit tests.

## 0.1.2

* `Interval` initializer now allows specifying just one of `cents` or `ratio`, and when both are present, uses the more exact one (like `cents=700` or `ratio=Fraction(7, 5)` vs. floating-point values) to recalculate the other.
* Thus, a breaking change: `from_cents` and `from_ratio` are no more.
* A new formatting specificator for intervals: `p` for outputting strings parsable by `interval` and less noisy than the default str.
* Binary minus may be used now: `i1 - i2 = i1 + (-i2) = i1.stack(i2.inverse)`.
* `Interval.stretch_from` and `/` accompany `multiply` and `*` now. For completeness, there’s also `//` which uses the already existing `divmod`.
* Intervals also now support `abs`.
* A new shorthand `Interval.approximate_in_edo` to get an approximation and its error in a single line.
* Finally, unit tests. And what revelations have they brought!
* `JISubgroup` got more usable: now you can test for subgroup containment or isomorphism of two groups.
* Typos (and off-by-1 errors, ugh) as always.
