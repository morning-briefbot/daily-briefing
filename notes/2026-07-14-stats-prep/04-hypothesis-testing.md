# Hypothesis Testing

## The logic
- Null hypothesis (H0): the boring default - "no effect", "no difference", "the new ad performs the same as the old."
- Alternative (H1): what you suspect - "the new ad converts better."
- You assume H0 is true, then ask: how surprising is my data under that assumption? If very surprising, reject H0.
- The p-value is that surprise level: the probability of seeing data this extreme IF the null were true. p = 0.03 means "if nothing were going on, I'd see results like this only 3% of the time."
- Common threshold (alpha): 0.05. Below it, "statistically significant." The threshold is a convention, not physics.

## What a p-value is NOT
- NOT the probability the null is true.
- NOT the probability your result is a fluke.
- NOT a measure of how big or important the effect is. With a huge sample, a trivially tiny effect can be "significant." Always pair significance with EFFECT SIZE: "significant" 0.1% lift may not pay for the engineering time.

## Errors and power
- Type I error (false positive): rejecting a true null - shipping a change that does nothing. Probability = alpha.
- Type II error (false negative): missing a real effect. Probability = beta; Power = 1 - beta.
- Power grows with: bigger sample, bigger true effect, more lenient alpha. Underpowered tests mostly produce misses and flukes.
- Multiple testing trap: run 20 tests at alpha 0.05 and expect ~1 false positive by chance. Torture the data and it will confess. This is p-hacking.

## Common tests (know what they're for, not the formulas)
- t-test: compare means of two groups (A/B test conversion, treated vs control).
- Paired t-test: same subjects before/after.
- Chi-square: relationships between categorical variables (region vs churn yes/no).
- ANOVA: comparing means across 3+ groups.

## Business intuition anchors
- A/B testing IS hypothesis testing: control = null, variant = alternative.
- "Not significant" does not mean "no effect" - it often means "not enough data to tell."
- Ask three questions of any test result: How big is the effect? How precise is the estimate? Was this one test or the survivor of many?
