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
