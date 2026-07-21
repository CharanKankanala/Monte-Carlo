# Multi-Asset Fintech Risk Lab — Research Report

## Executive summary

This study evaluates implementable portfolio policies using 3,154 aligned daily observations from January 2014 through July 2026. The universe spans US large-cap, technology and small-cap equities, developed international equity, intermediate and long Treasuries, gold, real estate, and broad commodities.

The walk-forward design uses only information available at each rebalance. After transaction costs, the 60/40 benchmark produced the strongest realized Sharpe ratio (0.93), while minimum variance had the shallowest maximum drawdown (-17.1%). The S&P 500 delivered the highest raw CAGR but also experienced the deepest drawdown. These are historical research results, not investment recommendations.

## Research design

- 504-day rolling estimation window and 21-trading-day rebalancing
- 10 bps proportional transaction costs and a separate 25 bps liquidity-stress increment
- Equal weight, long-only minimum variance, momentum tilt, and risk parity
- S&P 500 and 60/40 equity–Treasury benchmarks
- Moving-block bootstrap and GARCH(1,1)–regime–t-copula Monte Carlo models
- 10,000 one-year paths, 95% VaR/CVaR, pathwise drawdown, and confidence intervals
- Distribution diagnostics, Kupiec VaR coverage, and benchmark mean-difference tests

## Principal results

| Portfolio | CAGR | Annual volatility | Sharpe | Maximum drawdown |
|---|---:|---:|---:|---:|
| Equal weight | 10.25% | 11.36% | 0.92 | -22.36% |
| Minimum variance | 3.30% | 5.70% | 0.60 | -17.11% |
| Momentum tilt | 9.94% | 12.26% | 0.83 | -22.85% |
| Risk parity | 7.94% | 8.97% | 0.90 | -21.54% |
| S&P 500 | 15.08% | 17.81% | 0.88 | -33.72% |
| 60/40 | 9.78% | 10.67% | 0.93 | -21.02% |

The result is not that complexity automatically wins. The 60/40 portfolio remained difficult to beat on realized Sharpe, while minimum variance materially reduced drawdown at the cost of return. That tradeoff is more credible than selecting only a favorable metric.

## Advanced distribution model

Each asset receives a GARCH(1,1) conditional-variance model. Dependence is estimated with a rank copula and six-degree-of-freedom Student-t innovations. A two-state Gaussian hidden Markov model controls market drift and volatility. The fitted low- and high-volatility state annualized volatilities were approximately 7.0% and 18.6%.

For the minimum-variance portfolio, the advanced model estimated one-year 95% VaR near 6.1% and expected shortfall near 8.2%, both more severe than the moving-block bootstrap. This divergence is a direct model-risk finding: tail estimates depend materially on distribution assumptions.

## Interpretation and governance

Risk-adjusted performance is evaluated jointly with drawdown, turnover, tail loss, and benchmark-relative evidence. Statistical p-values quantify uncertainty and are not treated as proof of economic value.

Yahoo Finance adjusted ETF prices are convenient research inputs, not a licensed institutional feed. ETFs are asset-class proxies and the universe contains survivorship choices. The study excludes taxes and nonlinear market impact. GARCH, hidden-state, and copula specifications are approximations subject to model risk. Historical backtests can overfit and cannot establish future profitability.
