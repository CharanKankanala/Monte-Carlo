# Research Methodology

## Question

Can systematic, long-only multi-asset allocations improve out-of-sample risk-adjusted performance relative to simple S&P 500 and 60/40 benchmarks after plausible trading costs?

## Walk-forward protocol

At each 21-trading-day rebalance, the system uses only the preceding 504 observations. It estimates equal weight, long-only minimum variance, cross-sectional momentum tilt, and equal-risk-contribution allocations. The selected weights remain fixed for the following evaluation segment. The first return in that segment absorbs the rebalance cost, which is economically equivalent to charging the portfolio once when the trade occurs instead of spreading a single trade over unrelated days.

The base run charges 10 basis points per unit of turnover. A separate run adds 25 basis points to test whether the strategy ranking survives worse liquidity.

## Benchmarks

SPY is the passive equity benchmark. The 60/40 benchmark holds 60% SPY and 40% IEF. Both remain in every performance table and wealth chart; model complexity is not counted as a benefit unless it improves a stated decision metric.

## Distribution models

The empirical model resamples contiguous blocks of daily log returns. Blocking retains contemporaneous cross-asset dependence and short-run time structure that an independent bootstrap would destroy.

The parametric competitor fits per-asset GARCH(1,1) variance, a two-state Gaussian hidden Markov market regime, rank-transformed dependence, and Student-t copula innovations with six degrees of freedom. Six degrees of freedom provides meaningfully heavier tails than a Gaussian while retaining finite variance and avoiding an excessively unstable tail calibration for this sample size.

## Evaluation

The backtest reports CAGR, annualized volatility, Sharpe, Sortino, Calmar, maximum drawdown, daily VaR and expected shortfall. Benchmark comparison adds annualized excess return, tracking error, information ratio, and a mean-difference t-test. Distribution checks cover skew, excess kurtosis, normality, return autocorrelation, squared-return autocorrelation, and Kupiec unconditional VaR coverage.

## Method risk

The 504/21 schedule, constraints, t degrees of freedom, and cost levels are research judgments rather than universally optimal constants. A stronger follow-up would nest these choices inside a fully pre-registered sensitivity grid and reserve a final untouched evaluation period. That would separate robustness testing from the temptation to tune decisions after seeing the complete sample.
