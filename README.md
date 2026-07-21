# Multi-Asset Fintech Risk Lab

An end-to-end quantitative research platform for testing portfolio allocations against transparent benchmarks. The project joins real multi-asset prices, walk-forward backtesting, implementation costs, conditional-volatility and regime models, heavy-tail simulation, statistical validation, and a responsive research dashboard.

![Multi-Asset Risk Lab dashboard](docs/dashboard-overview.png)

## What the project does

- Uses adjusted prices for nine liquid asset-class ETFs from 2014 onward
- Re-estimates four long-only allocation policies with past data only
- Compares every strategy with the S&P 500 and a 60/40 equity-Treasury portfolio
- Charges turnover-based trading costs and runs a higher-cost liquidity stress
- Compares a moving-block bootstrap with a GARCH-regime-t-copula simulator
- Reports CAGR, volatility, Sharpe, Sortino, Calmar, drawdown, VaR, CVaR, tracking error, and coverage tests
- Publishes the same production results through an interactive dashboard
- Validates Python and dashboard behavior on every push

## Current result

The committed run contains 3,154 aligned trading days from January 2014 through July 2026. The S&P 500 led raw CAGR, the 60/40 benchmark led realized Sharpe, and minimum variance had the shallowest drawdown. The heavy-tail model produced more conservative tail-loss estimates than the historical bootstrap. I kept these benchmark results visible because a useful research system should reveal when a simple portfolio remains competitive.

![Walk-forward wealth and risk controls](docs/dashboard-research.png)

## Quick start

`research_pipeline.py` is the single production entry point.

```bash
python -m pip install -e ".[test]"
python research_pipeline.py --refresh --paths 10000
python -m pytest -q
```

Omit `--refresh` to reproduce the study from the committed market-data cache.

Run the dashboard separately:

```bash
cd dashboard
pnpm install
pnpm dev
```

## Why I made these choices

I chose SPY, QQQ, IWM, EFA, IEF, TLT, GLD, VNQ, and DBC because they create a compact but interpretable cross-asset universe: several equity risk segments, two duration exposures, inflation-sensitive assets, and real estate. They are liquid enough for a portfolio project and have a common history long enough to cover multiple market regimes.

I use the moving-block bootstrap as the empirical baseline because it preserves observed cross-asset relationships and short bursts of serial dependence without forcing a parametric distribution. I compare it with a GARCH-regime-t-copula model because volatility clustering, latent market states, and joint tail dependence are precisely where the historical resample can be too passive. Disagreement between the models is treated as model-risk information, not averaged away.

The 504-day lookback gives each allocation roughly two trading years of evidence, while the 21-day holding period approximates monthly rebalancing and prevents daily parameter noise from becoming excessive turnover. With more time, I would replace the fixed universe and proportional-cost assumption with point-in-time constituents, bid-ask spreads, and volume-dependent market impact.

## Research artifacts

- [Research report](RESEARCH_REPORT.md) - current findings and interpretation
- [Methodology](RESEARCH_METHODOLOGY.md) - experiment and validation protocol
- [Dataset card](DATA_CARD.md) - market-data provenance and caveats
- [Dashboard guide](dashboard/README.md) - UI behavior and local commands

## Architecture

```text
portfolio_risk/
  core.py              bootstrap simulation, allocation, and risk metrics
  data.py              adjusted-price acquisition and cache
  advanced_models.py   GARCH, hidden regimes, and rank-copula simulation
  backtesting.py       walk-forward evaluation, benchmarks, and costs
  validation.py        statistical and VaR-coverage tests
research_pipeline.py   sole production research entry point
dashboard/             interactive research UI
tests/                 numerical, statistical, and integration tests
.github/workflows/     CI and weekly market-data refresh
```

## Appropriate use

This repository is a portfolio research system, not an execution service or recommendation engine. Its value is in the reproducible experiment, model comparison, and audit trail. Anyone adapting it for capital allocation should first replace the retail data source and simplified cost model with controls appropriate to their institution.

## License

MIT - see [LICENSE](LICENSE).
