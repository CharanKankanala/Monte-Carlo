"""End-to-end institutional-style fintech research pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from portfolio_risk.advanced_models import fit_garch11, fit_two_state_regime, simulate_garch_regime_copula
from portfolio_risk.backtesting import performance_metrics, walk_forward_backtest
from portfolio_risk.core import SimulationConfig, calculate_metrics, log_returns, optimize_weights, simulate_paths
from portfolio_risk.data import ASSETS, download_market_data
from portfolio_risk.validation import benchmark_tests, diagnostics, kupiec_test


def _records(frame: pd.DataFrame) -> list[dict]:
    return frame.replace([np.inf, -np.inf], np.nan).where(pd.notna(frame), None).to_dict(orient="records")


def research_report(output: Path, source: str, prices: pd.DataFrame,
                    performance: pd.DataFrame, advanced_metrics: dict, regime) -> None:
    leader = performance.sort_values("sharpe", ascending=False).iloc[0]
    safest = performance.sort_values("max_drawdown", ascending=False).iloc[0]
    report = f"""# Multi-Asset Fintech Risk Lab — Research Report

## Executive summary

This study evaluates implementable portfolio policies using **{len(prices):,} daily observations** from {prices.index.min():%Y-%m-%d} through {prices.index.max():%Y-%m-%d}. The run used `{source}` data spanning US large-cap, technology and small-cap equities, developed international equity, intermediate and long Treasuries, gold, real estate, and broad commodities.

The walk-forward design uses only information available at each rebalance. After transaction costs, **{leader['strategy']}** produced the strongest realized Sharpe ratio ({leader['sharpe']:.2f}); **{safest['strategy']}** had the shallowest maximum drawdown ({safest['max_drawdown']:.1%}). These are historical research results, not investment recommendations.

## Research design

- 504-day rolling estimation window and 21-trading-day rebalancing
- 10 bps proportional transaction costs and a separate 25 bps liquidity-stress increment
- Equal weight, long-only minimum variance, momentum tilt, and risk parity
- S&P 500 and 60/40 equity–Treasury benchmarks
- Moving-block bootstrap and GARCH(1,1)–regime–t-copula Monte Carlo models
- 10,000 one-year paths, 95% VaR/CVaR, pathwise drawdown, and confidence intervals
- Distribution diagnostics, Kupiec VaR coverage, and benchmark mean-difference tests

## Advanced distribution model

Each asset receives a GARCH(1,1) conditional-variance model. Dependence is estimated with a rank copula and six-degree-of-freedom heavy-tailed innovations. A two-state Gaussian hidden Markov model controls market drift and volatility. Fitted low- and high-volatility state annualized volatilities were {np.sqrt(regime.variances[0] * 252):.1%} and {np.sqrt(regime.variances[1] * 252):.1%}.

For the minimum-variance portfolio, the advanced model estimated one-year 95% VaR of {advanced_metrics['var_95']:.1%}, expected shortfall of {advanced_metrics['cvar_95']:.1%}, and worst simulated maximum drawdown of {advanced_metrics['worst_max_drawdown']:.1%}.

## Interpretation

Risk-adjusted performance is evaluated jointly with drawdown, turnover, tail loss, and benchmark-relative evidence. A strategy is not declared superior solely because it has the highest return. Statistical p-values quantify uncertainty and are not treated as proof of economic value.

## Governance and limitations

Yahoo Finance adjusted ETF prices are convenient research inputs, not a licensed institutional feed. ETFs are asset-class proxies and the universe contains survivorship choices. The study excludes taxes and nonlinear market impact. GARCH, hidden-state, and copula specifications are approximations subject to model risk. Historical backtests can overfit and cannot establish future profitability.
"""
    (output / "RESEARCH_REPORT.md").write_text(report, encoding="utf-8")


def run(output: Path, paths: int = 10_000, refresh: bool = False, seed: int = 42) -> None:
    output.mkdir(parents=True, exist_ok=True)
    prices, source = download_market_data(refresh=refresh)
    prices = prices.dropna(); prices.to_csv(output / "market_prices_used.csv")
    log_r = log_returns(prices)

    backtest, weight_history, turnover = walk_forward_backtest(prices)
    stressed, _, _ = walk_forward_backtest(prices, liquidity_stress_bps=25)
    backtest.to_csv(output / "walk_forward_returns.csv")
    wealth = (1 + backtest).cumprod(); wealth.to_csv(output / "walk_forward_wealth.csv")
    weight_history.to_csv(output / "allocation_history.csv", index=False)
    turnover.to_csv(output / "turnover_and_costs.csv", index=False)

    performance = pd.DataFrame([{"strategy": c, **performance_metrics(backtest[c])} for c in backtest])
    stressed_perf = pd.DataFrame([{"strategy": c, **performance_metrics(stressed[c])} for c in stressed])
    performance = performance.merge(stressed_perf[["strategy", "cagr", "sharpe"]], on="strategy", suffixes=("", "_liquidity_stress"))
    performance.to_csv(output / "backtest_performance.csv", index=False)
    diag = diagnostics(log_r); comparisons = benchmark_tests(backtest)
    diag.to_csv(output / "statistical_diagnostics.csv", index=False)
    comparisons.to_csv(output / "benchmark_tests.csv", index=False)

    weights = optimize_weights(log_r)["minimum_variance"]
    bootstrap = simulate_paths(log_r, weights, SimulationConfig(paths=paths, seed=seed))
    conditional_window = log_r.tail(1_500)
    advanced = simulate_garch_regime_copula(conditional_window, weights, paths=paths, seed=seed)
    model_metrics = pd.DataFrame([
        {"model": "moving_block_bootstrap", **calculate_metrics(bootstrap)},
        {"model": "garch_regime_t_copula", **calculate_metrics(advanced)},
    ])
    model_metrics.to_csv(output / "model_comparison.csv", index=False)
    advanced_metrics = calculate_metrics(advanced)

    regime = fit_two_state_regime(log_r.mean(axis=1).to_numpy())
    pd.DataFrame(regime.probabilities, index=log_r.index, columns=["low_volatility", "high_volatility"]).to_csv(output / "regime_probabilities.csv")
    garch_rows = []
    for col in log_r:
        fit = fit_garch11(conditional_window[col].to_numpy())
        garch_rows.append({"asset": col, "omega": fit.omega, "alpha": fit.alpha, "beta": fit.beta,
                           "persistence": fit.alpha + fit.beta, "latest_annualized_volatility": np.sqrt(fit.conditional_variance[-1] * 252)})
    garch = pd.DataFrame(garch_rows); garch.to_csv(output / "garch_parameters.csv", index=False)
    var95 = -backtest["minimum_variance"].quantile(.05)
    pd.DataFrame([kupiec_test(backtest["minimum_variance"], var95)]).to_csv(output / "var_backtest.csv", index=False)
    research_report(output, source, prices, performance, advanced_metrics, regime)

    payload = {
        "meta": {"source": source, "start": str(prices.index.min().date()), "end": str(prices.index.max().date()), "observations": len(prices), "paths": paths, "assets": ASSETS},
        "performance": _records(performance.round(6)), "models": _records(model_metrics.round(6)),
        "comparisons": _records(comparisons.round(6)), "garch": _records(garch.round(6)),
        "wealth": [{"date": str(i.date()), **{k: round(float(v), 6) for k, v in row.items()}} for i, row in wealth.iloc[::5].iterrows()],
        "regimes": [{"date": str(i.date()), "high_volatility": round(float(v), 6)} for i, v in pd.Series(regime.probabilities[:, 1], index=log_r.index).iloc[::5].items()],
    }
    target = Path("dashboard/public/results.json"); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the complete fintech research platform")
    parser.add_argument("--output", type=Path, default=Path("research_outputs"))
    parser.add_argument("--paths", type=int, default=10_000)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(); run(args.output, args.paths, args.refresh, args.seed)
