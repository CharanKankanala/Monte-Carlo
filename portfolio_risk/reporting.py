from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def dashboard(results: dict[tuple[str, str], tuple[np.ndarray, dict]], output: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    base = {k: v for k, v in results.items() if k[1] == "baseline"}
    for (strategy, _), (paths, _) in base.items():
        terminal = paths[:, -1] / paths[:, 0] - 1
        axes[0, 0].hist(terminal, bins=50, alpha=.35, label=strategy)
        axes[0, 1].plot(np.median(paths, axis=0), label=strategy)
        dd = paths / np.maximum.accumulate(paths, axis=1) - 1
        axes[1, 0].plot(np.median(dd, axis=0), label=strategy)
    metrics = pd.DataFrame({k[0]: v[1] for k, v in base.items()}).T
    axes[1, 1].scatter(metrics.terminal_volatility, metrics.expected_return)
    for name, row in metrics.iterrows():
        axes[1, 1].annotate(name, (row.terminal_volatility, row.expected_return))
    axes[0, 0].set_title("Terminal Return Distributions")
    axes[0, 1].set_title("Median Portfolio Growth")
    axes[1, 0].set_title("Median Drawdown")
    axes[1, 1].set_title("Risk–Return Profile")
    for ax in axes.flat: ax.grid(alpha=.2)
    axes[0, 0].legend(); axes[0, 1].legend(); axes[1, 0].legend()
    fig.tight_layout(); fig.savefig(output / "analytics_dashboard.png", dpi=160); plt.close(fig)


def efficient_frontier(returns: pd.DataFrame, output: Path, seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    w = rng.dirichlet(np.ones(returns.shape[1]), size=5_000)
    mu = returns.mean().to_numpy() * 252
    cov = returns.cov().to_numpy() * 252
    ret = w @ mu
    vol = np.sqrt(np.einsum("ij,jk,ik->i", w, cov, w))
    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(vol, ret, c=np.divide(ret, vol, where=vol != 0), s=8, cmap="viridis")
    ax.set(xlabel="Annualized volatility", ylabel="Annualized expected return", title="5,000-Portfolio Efficient Frontier")
    ax.grid(alpha=.2); fig.colorbar(sc, label="Return / volatility")
    fig.tight_layout(); fig.savefig(output / "efficient_frontier.png", dpi=160); plt.close(fig)

