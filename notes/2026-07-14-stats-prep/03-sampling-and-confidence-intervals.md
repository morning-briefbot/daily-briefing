# Sampling & Confidence Intervals

## Sampling fundamentals
- Population vs sample: you almost never see the population; you infer it from a sample.
- Random sampling is the gold standard. Convenience samples (whoever answered the survey) bake in bias no math can fix.
- Selection bias examples: surveying current customers about churn (the churned ones aren't there to answer), WWII planes analyzed for bullet holes (survivorship bias - armor where the holes AREN'T).
- Sampling error is unavoidable noise; bias is a systematic tilt. More data shrinks error but does nothing for bias.

## Central Limit Theorem (CLT) - the big one
- Take many samples and compute each sample's mean: those means form a roughly normal distribution, EVEN IF the underlying data isn't normal, once samples are reasonably large (rule of thumb n >= 30).
- This is why we can build confidence intervals and run hypothesis tests on means of messy real-world data.
- Standard error (SE) = SD / sqrt(n). The spread of sample means. Key insight: to halve your uncertainty you need 4x the sample size (sqrt in the denominator).

## Confidence intervals (CI)
- A 95% CI for the mean: sample mean +/- roughly 2 standard errors.
- Correct interpretation: if we repeated this sampling process many times, ~95% of the intervals built this way would contain the true value. Loose everyday reading: "we're pretty sure the truth is in this range."
- Wide interval = little information. A "10% lift" with a CI of -5% to +25% is a shrug, not a win.
- Bigger n -> narrower CI. More variability in data -> wider CI.

## Business intuition anchors
- Polls say "+/- 3 points": that's a 95% CI from a ~1,000-person sample.
- NPS moved from 42 to 45 on 80 responses? The CI on each number is bigger than the move. Don't reorganize over noise.
- Sample size math is why A/B tests on small customer bases take weeks - and why you shouldn't peek early and declare victory.
