import numpy as np
import pandas as pd
from portfolio_risk.advanced_models import fit_garch11, fit_two_state_regime, rank_copula_correlation, simulate_garch_regime_copula
from portfolio_risk.backtesting import performance_metrics, walk_forward_backtest
from portfolio_risk.validation import kupiec_test


def returns(rows=700, assets=3):
    rng = np.random.default_rng(8)
    return pd.DataFrame(rng.normal(.0002, .01, (rows, assets)), columns=[f"A{i}" for i in range(assets)])


def test_garch_is_stationary_and_positive():
    fit = fit_garch11(returns()["A0"].to_numpy())
    assert fit.alpha + fit.beta < 1 and np.all(fit.conditional_variance > 0)


def test_regime_probabilities_and_transition_are_valid():
    fit = fit_two_state_regime(returns()["A0"].to_numpy(), iterations=20)
    assert np.allclose(fit.probabilities.sum(axis=1), 1)
    assert np.allclose(fit.transition.sum(axis=1), 1)
    assert fit.variances[0] <= fit.variances[1]


def test_rank_copula_correlation_is_psd():
    corr = rank_copula_correlation(returns())
    assert np.linalg.eigvalsh(corr).min() > -1e-8 and np.allclose(np.diag(corr), 1)


def test_advanced_simulation_dimensions_and_reproducibility():
    r = returns(); w = np.ones(3) / 3
    a = simulate_garch_regime_copula(r, w, paths=40, horizon=15, seed=2)
    b = simulate_garch_regime_copula(r, w, paths=40, horizon=15, seed=2)
    assert a.shape == (40, 16) and np.array_equal(a, b) and np.all(a > 0)


def test_walk_forward_has_benchmarks_and_costs():
    r = returns(800, 4); prices = 100 * np.exp(r.cumsum())
    prices.columns = ["SPY", "IEF", "X", "Y"]
    daily, weights, costs = walk_forward_backtest(prices, lookback=252)
    assert {"SP500", "SIXTY_FORTY", "risk_parity"}.issubset(daily.columns)
    assert not weights.empty and costs.trading_cost.sum() > 0


def test_performance_and_kupiec_metrics_are_finite():
    r = pd.Series(returns()["A0"])
    assert all(np.isfinite(list(performance_metrics(r).values())))
    assert 0 <= kupiec_test(r, .02)["kupiec_pvalue"] <= 1
