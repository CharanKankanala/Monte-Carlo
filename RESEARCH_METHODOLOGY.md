# Research Methodology

## Objective

Evaluate whether systematic multi-asset allocations improve implementable, out-of-sample risk-adjusted performance relative to transparent S&P 500 and 60/40 benchmarks.

## Data

The production dataset uses split- and distribution-adjusted daily prices for SPY, QQQ, IWM, EFA, IEF, TLT, GLD, VNQ, and DBC. The universe represents US large-cap, technology and small-cap equities; developed international equity; intermediate and long-duration US Treasuries; gold; real estate; and broad commodities. A cached copy makes every reported run reproducible.

## Walk-forward protocol

At each 21-trading-day rebalance, the system uses only the preceding 504 observations. It estimates equal-weight, long-only minimum-variance, momentum-tilt, and equal-risk-contribution allocations. The selected allocation is held over the next evaluation segment. Returns deduct proportional turnover costs of 10 basis points; a separate stress run adds 25 basis points.

## Benchmarks

SPY represents a passive US equity benchmark. The 60/40 benchmark holds 60% SPY and 40% IEF. Benchmarks remain visible in performance tables and charts so additional model complexity must earn its place.

## Distribution models

The historical model uses moving blocks of daily log returns, preserving contemporaneous cross-asset dependence and short-run serial structure. The advanced model combines per-asset GARCH(1,1) conditional variance, a two-state Gaussian hidden Markov regime process, rank-transformed dependence, and six-degree-of-freedom Student-t copula innovations.

## Evaluation and validation

The platform reports CAGR, annualized volatility, Sharpe, Sortino, Calmar, maximum drawdown, daily VaR and expected shortfall, tracking error, information ratio, and benchmark mean-difference tests. Distribution diagnostics include skewness, excess kurtosis, normality tests, return and squared-return autocorrelation. VaR exception frequency is evaluated with Kupiec unconditional coverage.

## Limitations

ETF data is a research proxy rather than a licensed institutional feed. Results are sensitive to universe selection, lookback, rebalance frequency, cost assumptions, and the chosen probability models. Taxes, capacity, nonlinear impact, and intraday liquidity are excluded. Statistical significance does not guarantee economic value, and historical performance cannot establish future profitability.
