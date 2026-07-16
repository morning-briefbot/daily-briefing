# Probability & Distributions

## Probability basics
- Probability ranges 0 to 1. Independent events: P(A and B) = P(A) x P(B). Mutually exclusive: P(A or B) = P(A) + P(B).
- Conditional probability P(A|B): probability of A given B happened. The heart of updating beliefs with data.
- Bayes' theorem in words: updated belief = prior belief adjusted by how well the evidence fits. Classic trap: a 99%-accurate test for a rare disease still gives mostly false positives, because the disease is rare. Base rates matter.
- Expected value: sum of (outcome x probability). The foundation of decision trees and any bet/investment analysis. A negative-EV decision can still be right if it caps catastrophic risk (that's why insurance exists).

## Key distributions
- Normal (bell curve): symmetric, defined fully by mean and SD. Empirical rule: ~68% of data within 1 SD, ~95% within 2 SD, ~99.7% within 3 SD.
- Standard normal / z-scores: z = (x - mean) / SD. "How many SDs from the mean is this?" A z of 2+ is notable; 3+ is rare.
- Binomial: count of successes in n independent yes/no trials (e.g., how many of 100 sales calls convert).
- Poisson: count of events per time period (customer arrivals per hour, defects per batch). Used in queueing and operations.
- Uniform: every outcome equally likely (rolling a die).

## Why the normal shows up everywhere
- Sums and averages of many small independent effects tend toward normal (preview of the Central Limit Theorem).
- But beware: financial returns, viral growth, and network effects are NOT normal - they have fat tails and skew. Using normal assumptions where they don't belong is how risk models blow up.

## Business intuition anchors
- Expected value thinking: a 20% chance of a $10M deal is "worth" $2M for pipeline planning - but you can't spend an expected value.
- z-scores standardize: comparing a salesperson 2 SDs above their region's mean vs one 0.5 SD above theirs beats comparing raw numbers.
