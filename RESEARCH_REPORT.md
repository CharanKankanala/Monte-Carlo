# Multi-Asset Fintech Risk Lab - Research Report

## Executive summary

The study evaluates implementable portfolio policies over 3,154 aligned daily observations from January 2014 through July 2026. The universe spans US large-cap, technology and small-cap equities, developed international equity, intermediate and long Treasuries, gold, real estate, and broad commodities.

With a past-only rolling design and transaction costs, the 60/40 benchmark produced the strongest realized Sharpe ratio (0.93), minimum variance had the shallowest maximum drawdown (-17.1%), and the S&P 500 delivered the highest raw CAGR with the deepest drawdown. The result is a trade-off map rather than a single winning portfolio.

## Research design

- 504-day estimation window and 21-trading-day rebalancing
- 10 bps proportional trading cost plus a 25 bps liquidity-stress increment
- Equal weight, minimum variance, momentum tilt, and risk parity
- S&P 500 and 60/40 equity-Treasury benchmarks
- Moving-block bootstrap and GARCH-regime-t-copula Monte Carlo models
- 10,000 one-year paths with VaR, CVaR, confidence intervals, and pathwise drawdown
- Distribution diagnostics, benchmark tests, and Kupiec VaR coverage

## Principal results

| Portfolio | CAGR | Annual volatility | Sharpe | Maximum drawdown |
|---|---:|---:|---:|---:|
| Equal weight | 10.25% | 11.36% | 0.92 | -22.36% |
| Minimum variance | 3.30% | 5.70% | 0.60 | -17.11% |
| Momentum tilt | 9.94% | 12.26% | 0.83 | -22.85% |
| Risk parity | 7.94% | 8.97% | 0.90 | -21.54% |
| S&P 500 | 15.08% | 17.81% | 0.88 | -33.72% |
| 60/40 | 9.78% | 10.67% | 0.93 | -21.02% |

The simple 60/40 portfolio remained hard to beat on realized Sharpe. Minimum variance reduced drawdown substantially but surrendered return. That contrast is the central practical finding: lower realized risk did not translate into the strongest overall efficiency once growth was considered.

## Tail-model comparison

The advanced simulator fits GARCH(1,1) conditional variance to each asset, estimates a two-state market regime, and joins standardized marginals with a heavy-tail rank copula. Its fitted low- and high-volatility state annualized volatilities were approximately 7.0% and 18.6%.

For the minimum-variance portfolio, the advanced model estimated one-year 95% VaR near 6.1% and expected shortfall near 8.2%, both more severe than the block-bootstrap estimates. The gap is itself useful: tail conclusions are sensitive to whether future shocks are constrained to historical blocks or allowed to combine dynamic volatility with new heavy-tail dependence draws.

## Reading the results responsibly

The tables describe this universe, period, and implementation rule. They do not establish that the same ranking will persist, and the p-values do not convert a backtest into a tradable edge. The best use of the report is to identify which assumptions drive a decision and then challenge those assumptions with new data, wider cost scenarios, and a genuinely untouched holdout period.
