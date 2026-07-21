import numpy as np
import pandas as pd
from portfolio_risk.core import (SimulationConfig, calculate_metrics,
                                 maximum_drawdown, optimize_weights, simulate_paths)


def sample_returns():
    rng = np.random.default_rng(1)
    return pd.DataFrame(rng.normal([.0004, .0002, .0001], [.012, .008, .003], (400, 3)), columns=list("ABC"))


def test_drawdown_known_values():
    paths = np.array([[100., 120., 90., 108.]])
    assert np.allclose(maximum_drawdown(paths), [-.25])


def test_allocations_long_only_and_invested():
    for w in optimize_weights(sample_returns()).values():
        assert np.isclose(w.sum(), 1) and np.all(w >= -1e-10)


def test_minimum_variance_is_no_worse_than_equal_weight():
    r = sample_returns(); weights = optimize_weights(r); cov = r.cov().to_numpy()
    assert weights["minimum_variance"] @ cov @ weights["minimum_variance"] <= weights["equal_weight"] @ cov @ weights["equal_weight"] + 1e-12


def test_simulation_reproducible_and_sized():
    r = sample_returns(); w = np.ones(3) / 3; cfg = SimulationConfig(paths=100, horizon=20)
    a = simulate_paths(r, w, cfg); b = simulate_paths(r, w, cfg)
    assert a.shape == (100, 21) and np.array_equal(a, b)


def test_cvar_not_less_than_var():
    r = sample_returns(); paths = simulate_paths(r, np.ones(3) / 3, SimulationConfig(paths=500, horizon=30))
    m = calculate_metrics(paths)
    assert m["cvar_95"] >= m["var_95"]

