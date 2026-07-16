# Descriptive Statistics

## Measures of central tendency
- Mean: arithmetic average. Sensitive to outliers (one billionaire walks into a bar and the "average" patron is rich).
- Median: middle value when sorted. Robust to outliers; preferred for skewed data like income, home prices, deal sizes.
- Mode: most frequent value. Useful for categorical data.
- Rule of thumb: if mean >> median, the distribution is right-skewed (long tail of big values). Housing prices, CEO pay, startup returns.

## Measures of spread
- Range: max minus min. Crude, outlier-driven.
- Variance: average of squared deviations from the mean. Units are squared (dollars squared), so hard to interpret directly.
- Standard deviation (SD): square root of variance, back in original units. The workhorse measure of risk in finance.
- Coefficient of variation: SD divided by mean. Lets you compare volatility across things with different scales (a $10 stock vs a $1,000 stock).
- Interquartile range (IQR): 75th percentile minus 25th percentile. Robust to outliers; the "box" in a box plot.

## Shape
- Skewness: right/positive skew = long right tail (income). Left/negative skew = long left tail (exam scores when most do well).
- Kurtosis: fat tails vs thin tails. Fat tails = extreme events more common than a normal distribution predicts. Critical in risk management - the 2008 crisis was a fat-tail event.

## Business intuition anchors
- "Average customer" claims: always ask mean or median, and what the spread is.
- Two portfolios can have the same mean return with wildly different SDs - the SD is the risk.
- Percentiles beat averages for operations: "95th percentile delivery time" tells you what your unhappy customers experience.
