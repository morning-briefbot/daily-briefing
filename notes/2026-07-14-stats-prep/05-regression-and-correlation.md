# Correlation & Regression

## Correlation
- Correlation coefficient r: ranges -1 to +1. Sign = direction, magnitude = strength. |r| above ~0.7 is strong, below ~0.3 is weak (context-dependent).
- Correlation measures LINEAR relationships only. r near 0 can hide a strong U-shaped relationship.
- Correlation is not causation. Three explanations for any correlation: X causes Y, Y causes X, or lurking variable Z causes both (ice cream sales and drownings - both driven by summer).

## Simple linear regression
- Fits the line Y = a + bX minimizing squared errors.
- Slope b: expected change in Y per one-unit change in X. THE number to interpret: "each additional $1K of ad spend is associated with 12 more signups."
- Intercept a: value of Y when X = 0 (often not meaningful on its own).
- R-squared: share of variation in Y explained by the model, 0 to 1. R-squared of 0.6 = 60% of the variation explained; 40% is other stuff. Low R-squared with a significant slope is common and still useful.

## Multiple regression
- Y = a + b1X1 + b2X2 + ... Each coefficient is the effect of that variable HOLDING THE OTHERS CONSTANT - this is the superpower: isolating price effects from seasonality, store size, region.
- Omitted variable bias: leave out something that matters (and correlates with an included variable) and your coefficients lie to you. Classic: estimating the effect of education on income without controlling for family background.
- Dummy variables: 0/1 encodings let categories into the model (holiday week yes/no).
- Multicollinearity: when predictors move together (age and experience), individual coefficients get shaky even if the overall model predicts fine.

## Reading regression output (what to check, in order)
1. Sign and size of the coefficient you care about - is it economically meaningful?
2. Its p-value / confidence interval - is it distinguishable from zero?
3. R-squared - how much does the model explain overall?
4. Sanity: does the story survive adding obvious controls?

## Business intuition anchors
- Pricing, demand forecasting, marketing mix models, comp benchmarking - all regression under the hood.
- Extrapolation warning: a model fit on $10K-$50K ad budgets says nothing reliable about $500K.
- "Beta" in finance is literally a regression slope: stock returns regressed on market returns.
