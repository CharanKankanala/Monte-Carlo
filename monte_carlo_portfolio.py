from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from portfolio_risk.core import (SimulationConfig, calculate_metrics, load_prices,
                                 log_returns, optimize_weights, simulate_paths)
from portfolio_risk.reporting import dashboard, efficient_frontier

REGIMES = {"low_volatility": .65, "baseline": 1.0, "high_volatility": 1.35,
           "stress": 1.75, "extreme_stress": 2.25}


def demo_prices(path: Path, seed: int = 7) -> None:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2019-01-02", periods=1_500)
    names = ["US_EQUITY", "INTL_EQUITY", "US_BONDS", "REAL_ESTATE", "COMMODITIES"]
    means = np.array([.00035, .00027, .00010, .00022, .00014])
    vols = np.array([.011, .012, .004, .010, .013])
    corr = np.full((5, 5), .18); np.fill_diagonal(corr, 1)
    corr[0, 1] = corr[1, 0] = .72; corr[0, 3] = corr[3, 0] = .55
    cov = corr * np.outer(vols, vols)
    rets = rng.multivariate_normal(means, cov, size=len(dates))
    prices = 100 * np.exp(np.cumsum(rets, axis=0))
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(prices, index=dates, columns=names).rename_axis("Date").to_csv(path)


def run(price_file: Path, output: Path, config: SimulationConfig) -> None:
    output.mkdir(parents=True, exist_ok=True)
    if not price_file.exists(): demo_prices(price_file)
    returns = log_returns(load_prices(price_file))
    weights = optimize_weights(returns)
    pd.DataFrame(weights, index=returns.columns).to_csv(output / "portfolio_weights.csv")
    results, rows = {}, []
    for s_idx, (strategy, w) in enumerate(weights.items()):
        for r_idx, (regime, multiplier) in enumerate(REGIMES.items()):
            paths = simulate_paths(returns, w, config, multiplier, s_idx * 100 + r_idx)
            metrics = calculate_metrics(paths)
            results[(strategy, regime)] = (paths, metrics)
            rows.append({"strategy": strategy, "regime": regime, **metrics})
    pd.DataFrame(rows).to_csv(output / "risk_metrics.csv", index=False)
    convergence = []
    for count in (1_000, 5_000, 10_000):
        cfg = SimulationConfig(min(count, config.paths), config.horizon, config.block_size,
                               config.seed, config.initial_value)
        for idx, (strategy, w) in enumerate(weights.items()):
            m = calculate_metrics(simulate_paths(returns, w, cfg, seed_offset=500 + idx))
            convergence.append({"paths": cfg.paths, "strategy": strategy,
                                "var_95": m["var_95"], "cvar_95": m["cvar_95"]})
    pd.DataFrame(convergence).drop_duplicates().to_csv(output / "convergence_analysis.csv", index=False)
    dashboard(results, output); efficient_frontier(returns, output, config.seed)
    baseline = pd.DataFrame(rows).query("regime == 'baseline'").sort_values("cvar_95")
    best = baseline.iloc[0]
    narrative = ("# Executive Risk Narrative\n\n"
        f"The analysis evaluated {config.paths:,} paths over {config.horizon} trading days across "
        f"three allocations and five volatility regimes. Under baseline conditions, **{best.strategy}** "
        f"had the lowest 95% expected shortfall ({best.cvar_95:.2%}) and a 95% VaR of {best.var_95:.2%}.\n\n"
        "Results are scenario estimates, not forecasts or regulatory approval. Replace the included "
        "synthetic demonstration series with an approved adjusted-close dataset before using the analysis "
        "as historical research. Transaction costs, taxes, liquidity, and parameter uncertainty are excluded.\n")
    (output / "executive_risk_narrative.md").write_text(narrative, encoding="utf-8")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Monte Carlo portfolio-risk analysis")
    p.add_argument("--prices", type=Path, default=Path("data/demo_prices.csv"))
    p.add_argument("--output", type=Path, default=Path("outputs"))
    p.add_argument("--paths", type=int, default=10_000)
    p.add_argument("--horizon", type=int, default=252)
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    run(a.prices, a.output, SimulationConfig(paths=a.paths, horizon=a.horizon, seed=a.seed))

