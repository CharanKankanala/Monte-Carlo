from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass(frozen=True)
class SimulationConfig:
    paths: int = 10_000
    horizon: int = 252
    block_size: int = 5
    seed: int = 42
    initial_value: float = 100_000.0


def load_prices(path: str | Path) -> pd.DataFrame:
    prices = pd.read_csv(path, index_col=0, parse_dates=True)
    if prices.shape[0] < 60 or prices.shape[1] < 2:
        raise ValueError("Price data must contain at least 60 rows and two assets")
    if prices.isna().any().any() or not np.isfinite(prices.to_numpy()).all():
        raise ValueError("Price data contains missing or non-finite values")
    if (prices <= 0).any().any() or prices.index.has_duplicates:
        raise ValueError("Prices must be positive and dates unique")
    if not prices.index.is_monotonic_increasing:
        prices = prices.sort_index()
    return prices.astype(float)


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    returns = np.log(prices / prices.shift(1)).dropna()
    if not np.isfinite(returns.to_numpy()).all():
        raise ValueError("Calculated returns are not finite")
    return returns


def optimize_weights(returns: pd.DataFrame) -> dict[str, np.ndarray]:
    n = returns.shape[1]
    equal = np.full(n, 1.0 / n)
    cov = returns.cov().to_numpy() * 252
    result = minimize(lambda w: float(w @ cov @ w), equal, method="SLSQP",
                      bounds=[(0.0, 1.0)] * n,
                      constraints={"type": "eq", "fun": lambda w: w.sum() - 1.0},
                      options={"ftol": 1e-12, "maxiter": 2_000})
    if not result.success:
        raise RuntimeError(f"Minimum-variance optimization failed: {result.message}")
    momentum = returns.tail(min(126, len(returns))).mean().to_numpy()
    shifted = np.maximum(momentum - momentum.min(), 0) + 1e-9
    tilt = shifted / shifted.sum()
    return {"equal_weight": equal, "minimum_variance": result.x,
            "momentum_tilt": tilt}


def moving_block_sample(returns: np.ndarray, paths: int, horizon: int,
                        block_size: int, rng: np.random.Generator) -> np.ndarray:
    rows, assets = returns.shape
    if block_size < 1 or block_size > rows:
        raise ValueError("block_size must be between 1 and the return history length")
    blocks = int(np.ceil(horizon / block_size))
    starts = rng.integers(0, rows - block_size + 1, size=(paths, blocks))
    offsets = np.arange(block_size)
    sampled = returns[(starts[..., None] + offsets).reshape(paths, -1)]
    return sampled[:, :horizon, :].reshape(paths, horizon, assets)


def simulate_paths(returns: pd.DataFrame, weights: np.ndarray,
                   config: SimulationConfig, volatility_multiplier: float = 1.0,
                   seed_offset: int = 0) -> np.ndarray:
    centered = returns.to_numpy() - returns.to_numpy().mean(axis=0)
    adjusted = returns.to_numpy().mean(axis=0) + centered * volatility_multiplier
    rng = np.random.default_rng(config.seed + seed_offset)
    sampled = moving_block_sample(adjusted, config.paths, config.horizon,
                                  config.block_size, rng)
    portfolio_returns = sampled @ weights
    growth = np.exp(np.cumsum(portfolio_returns, axis=1))
    return np.column_stack([np.full(config.paths, config.initial_value),
                            config.initial_value * growth])


def maximum_drawdown(paths: np.ndarray) -> np.ndarray:
    peaks = np.maximum.accumulate(paths, axis=1)
    return ((paths - peaks) / peaks).min(axis=1)


def calculate_metrics(paths: np.ndarray, confidence: float = 0.95) -> dict[str, float]:
    terminal_returns = paths[:, -1] / paths[:, 0] - 1
    losses = -terminal_returns
    var = float(np.quantile(losses, confidence))
    tail = losses[losses >= var]
    drawdowns = maximum_drawdown(paths)
    se = terminal_returns.std(ddof=1) / np.sqrt(len(terminal_returns))
    mean = terminal_returns.mean()
    return {
        "expected_terminal_value": float(paths[:, -1].mean()),
        "expected_return": float(mean),
        "terminal_volatility": float(terminal_returns.std(ddof=1)),
        "var_95": var,
        "cvar_95": float(tail.mean()),
        "average_max_drawdown": float(drawdowns.mean()),
        "worst_max_drawdown": float(drawdowns.min()),
        "return_ci_95_low": float(mean - 1.96 * se),
        "return_ci_95_high": float(mean + 1.96 * se),
        "sharpe_equivalent": float(mean / terminal_returns.std(ddof=1)) if terminal_returns.std(ddof=1) else 0.0,
    }

