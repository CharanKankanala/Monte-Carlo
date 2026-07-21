# Monte Carlo Portfolio Risk Framework

A reproducible Python framework for evaluating portfolio allocations with a moving-block bootstrap Monte Carlo simulation. It compares equal-weight, long-only minimum-variance, and momentum-tilted portfolios across five volatility regimes.

## Highlights

- 10,000 simulated paths and a 252-trading-day horizon by default
- Moving-block resampling preserves cross-asset dependence and short-run time dependence
- 95% VaR, 95% CVaR (expected shortfall), drawdown, volatility, confidence intervals, and terminal wealth
- 1K/5K/10K convergence analysis
- 5,000-portfolio efficient-frontier visualization and analytics dashboard
- Validated CSV ingestion, deterministic results, automated tests, and an executive narrative

## Run

```bash
python -m pip install -r requirements.txt
python monte_carlo_portfolio.py
python -m pytest -q
```

The first run generates a deterministic synthetic demonstration dataset at `data/demo_prices.csv`. Supply historical adjusted-close prices with `--prices your_file.csv`; the first column must contain dates and all remaining columns must contain positive asset prices.

Useful options:

```bash
python monte_carlo_portfolio.py --paths 10000 --horizon 252 --seed 42 --output outputs
```

## Outputs

`risk_metrics.csv`, `portfolio_weights.csv`, `convergence_analysis.csv`, `analytics_dashboard.png`, `efficient_frontier.png`, and `executive_risk_narrative.md` are written to the output directory.

## Model limitations

Simulation results are conditional scenario estimates—not forecasts, investment advice, or evidence of regulatory approval. Historical or synthetic samples may omit structural breaks. The model excludes transaction costs, taxes, liquidity constraints, and parameter uncertainty. Use an approved adjusted-close dataset before characterizing results as historical research.

## Architecture

- `portfolio_risk/core.py`: validation, allocation, bootstrap simulation, and risk metrics
- `portfolio_risk/reporting.py`: dashboard and efficient-frontier reporting
- `monte_carlo_portfolio.py`: CLI orchestration and executive narrative
- `tests/`: numerical, optimization, reproducibility, and dimensional checks
