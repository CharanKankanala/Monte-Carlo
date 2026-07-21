"""Walk-forward portfolio evaluation with implementation frictions."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from .core import optimize_weights
from .data import BENCHMARKS


def performance_metrics(returns: pd.Series, periods: int = 252) -> dict[str, float]:
    r = returns.dropna().astype(float)
    wealth = (1 + r).cumprod()
    years = len(r) / periods
    cagr = float(wealth.iloc[-1] ** (1 / years) - 1) if years > 0 else 0.0
    vol = float(r.std(ddof=1) * np.sqrt(periods))
    dd = wealth / wealth.cummax() - 1
    downside = r[r < 0].std(ddof=1) * np.sqrt(periods)
    return {"cagr": cagr, "annual_volatility": vol,
            "sharpe": float(r.mean() * periods / vol) if vol else 0.0,
            "sortino": float(r.mean() * periods / downside) if downside else 0.0,
            "max_drawdown": float(dd.min()), "calmar": float(cagr / abs(dd.min())) if dd.min() else 0.0,
            "var_95_daily": float(-r.quantile(.05)), "cvar_95_daily": float(-r[r <= r.quantile(.05)].mean())}


def _risk_parity(returns: pd.DataFrame) -> np.ndarray:
    cov = returns.cov().to_numpy() * 252; n = len(cov); start = np.full(n, 1 / n)
    def loss(w):
        sigma = np.sqrt(w @ cov @ w); marginal = cov @ w / sigma
        contribution = w * marginal
        return float(np.sum((contribution - contribution.mean()) ** 2))
    result = minimize(loss, start, method="SLSQP", bounds=[(0, .45)] * n,
                      constraints={"type": "eq", "fun": lambda w: w.sum() - 1})
    return result.x if result.success else start


def _weights(train: pd.DataFrame, strategy: str) -> np.ndarray:
    if strategy in ("equal_weight", "minimum_variance", "momentum_tilt"):
        return optimize_weights(train)[strategy]
    if strategy == "risk_parity": return _risk_parity(train)
    raise ValueError(f"Unknown strategy: {strategy}")


def walk_forward_backtest(prices: pd.DataFrame, lookback: int = 504,
                          rebalance_days: int = 21, transaction_cost_bps: float = 10,
                          liquidity_stress_bps: float = 0) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Re-estimate allocations on past-only data and trade monthly out of sample."""
    returns = prices.pct_change().dropna()
    strategies = ["equal_weight", "minimum_variance", "momentum_tilt", "risk_parity"]
    daily = pd.DataFrame(index=returns.index[lookback:], columns=strategies, dtype=float)
    weights_records, turnover_records = [], []
    for strategy in strategies:
        old = np.zeros(returns.shape[1])
        for start in range(lookback, len(returns), rebalance_days):
            stop = min(start + rebalance_days, len(returns))
            train = np.log1p(returns.iloc[start - lookback:start])
            w = _weights(train, strategy)
            turnover = float(np.abs(w - old).sum())
            cost = turnover * (transaction_cost_bps + liquidity_stress_bps) / 10_000
            segment = returns.iloc[start:stop].to_numpy() @ w
            if len(segment): segment[0] -= cost
            daily.loc[returns.index[start:stop], strategy] = segment
            weights_records.append({"date": returns.index[start], "strategy": strategy, **dict(zip(returns.columns, w))})
            turnover_records.append({"date": returns.index[start], "strategy": strategy, "turnover": turnover, "trading_cost": cost})
            old = w
    for name, allocation in BENCHMARKS.items():
        daily[name] = sum(returns.loc[daily.index, ticker] * weight for ticker, weight in allocation.items())
    return daily.dropna(), pd.DataFrame(weights_records), pd.DataFrame(turnover_records)

