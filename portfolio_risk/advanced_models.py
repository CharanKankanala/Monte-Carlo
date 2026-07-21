"""GARCH, regime-switching, and heavy-tail copula models."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm, rankdata, t


@dataclass(frozen=True)
class GarchFit:
    omega: float
    alpha: float
    beta: float
    conditional_variance: np.ndarray


def fit_garch11(series: np.ndarray) -> GarchFit:
    """Fit zero-mean Gaussian GARCH(1,1) by constrained maximum likelihood."""
    x = np.asarray(series, float) - np.mean(series)
    base = max(float(np.var(x)), 1e-10)

    def variance(theta: np.ndarray) -> np.ndarray:
        omega, alpha, beta = theta
        h = np.empty(len(x)); h[0] = base
        for i in range(1, len(x)):
            h[i] = omega + alpha * x[i - 1] ** 2 + beta * h[i - 1]
        return np.maximum(h, 1e-12)

    def objective(theta: np.ndarray) -> float:
        h = variance(theta)
        return float(.5 * np.sum(np.log(h) + x * x / h))

    bounds = [(base * 1e-6, base), (1e-5, .4), (1e-5, .999)]
    constraint = {"type": "ineq", "fun": lambda z: .999 - z[1] - z[2]}
    result = minimize(objective, [base * .02, .08, .88], method="SLSQP",
                      bounds=bounds, constraints=constraint,
                      options={"maxiter": 200, "ftol": 1e-8})
    theta = result.x if result.success else np.array([base * .02, .08, .88])
    return GarchFit(*map(float, theta), variance(theta))


@dataclass(frozen=True)
class RegimeFit:
    means: np.ndarray
    variances: np.ndarray
    transition: np.ndarray
    probabilities: np.ndarray


def fit_two_state_regime(series: np.ndarray, iterations: int = 100) -> RegimeFit:
    """Fit a two-state Gaussian hidden Markov model using scaled EM."""
    x = np.asarray(series, float)
    means = np.quantile(x, [.3, .7])
    variances = np.full(2, max(np.var(x), 1e-8))
    trans = np.array([[.96, .04], [.08, .92]])
    gamma = np.full((len(x), 2), .5)
    for _ in range(iterations):
        emit = np.column_stack([norm.pdf(x, means[j], np.sqrt(variances[j])) for j in range(2)]) + 1e-300
        # Scaling prevents a long forward-backward recursion from underflowing
        # to zero while leaving the EM state probabilities unchanged.
        alpha = np.empty_like(emit); scale = np.empty(len(x))
        alpha[0] = .5 * emit[0]; scale[0] = alpha[0].sum(); alpha[0] /= scale[0]
        for i in range(1, len(x)):
            alpha[i] = (alpha[i - 1] @ trans) * emit[i]
            scale[i] = alpha[i].sum(); alpha[i] /= scale[i]
        beta = np.ones_like(emit)
        for i in range(len(x) - 2, -1, -1):
            beta[i] = trans @ (emit[i + 1] * beta[i + 1]) / scale[i + 1]
        gamma = alpha * beta; gamma /= gamma.sum(axis=1, keepdims=True)
        xi = np.zeros((2, 2))
        for i in range(len(x) - 1):
            z = alpha[i, :, None] * trans * (emit[i + 1] * beta[i + 1])[None, :]
            xi += z / z.sum()
        trans = xi / xi.sum(axis=1, keepdims=True)
        means = (gamma * x[:, None]).sum(axis=0) / gamma.sum(axis=0)
        variances = (gamma * (x[:, None] - means) ** 2).sum(axis=0) / gamma.sum(axis=0)
        variances = np.maximum(variances, 1e-10)
    order = np.argsort(variances)
    return RegimeFit(means[order], variances[order], trans[np.ix_(order, order)], gamma[:, order])


def rank_copula_correlation(returns: pd.DataFrame) -> np.ndarray:
    """Estimate dependence after removing marginal shapes with rank transforms."""
    n = len(returns)
    uniforms = np.column_stack([rankdata(returns[c]) / (n + 1) for c in returns])
    gaussian_scores = norm.ppf(uniforms)
    corr = np.corrcoef(gaussian_scores, rowvar=False)
    eigval, eigvec = np.linalg.eigh(corr)
    corr = (eigvec * np.maximum(eigval, 1e-6)) @ eigvec.T
    d = np.sqrt(np.diag(corr))
    return corr / np.outer(d, d)


def simulate_garch_regime_copula(returns: pd.DataFrame, weights: np.ndarray,
                                  paths: int = 10_000, horizon: int = 252,
                                  seed: int = 42, initial_value: float = 100_000,
                                  degrees_freedom: int = 6) -> np.ndarray:
    """Simulate a portfolio with dynamic GARCH variance, latent regimes, and t-copula shocks."""
    # The default of six t degrees of freedom gives heavier joint tails than a
    # Gaussian while retaining finite variance and stable calibration here.
    rng = np.random.default_rng(seed)
    x = returns.to_numpy(); n_assets = x.shape[1]
    fits = [fit_garch11(x[:, j]) for j in range(n_assets)]
    regime = fit_two_state_regime(x @ weights)
    corr = rank_copula_correlation(returns)
    chol = np.linalg.cholesky(corr)
    state = rng.choice(2, paths, p=regime.probabilities[-1])
    h = np.tile([f.conditional_variance[-1] for f in fits], (paths, 1))
    omega = np.array([f.omega for f in fits]); alpha = np.array([f.alpha for f in fits]); beta = np.array([f.beta for f in fits])
    asset_means = x.mean(axis=0)
    previous = np.zeros((paths, n_assets))
    values = np.empty((paths, horizon + 1)); values[:, 0] = initial_value
    for day in range(horizon):
        move = rng.random(paths)
        state = np.where(move < regime.transition[state, 1], 1, 0)
        z = (rng.standard_t(degrees_freedom, (paths, n_assets)) @ chol.T) / np.sqrt(degrees_freedom / (degrees_freedom - 2))
        h = omega + alpha * previous ** 2 + beta * h
        market_shift = regime.means[state] - np.dot(asset_means, weights)
        shock = asset_means + market_shift[:, None] + np.sqrt(h) * z
        previous = shock - asset_means
        values[:, day + 1] = values[:, day] * np.exp(shock @ weights)
    return values
