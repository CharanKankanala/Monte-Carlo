"""Statistical diagnostics and model-comparison tests."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2, jarque_bera, kstest, norm, ttest_1samp


def kupiec_test(returns: pd.Series, var_forecast: float, alpha: float = .05) -> dict[str, float]:
    violations = int((returns < -var_forecast).sum()); n = int(returns.count())
    rate = violations / max(n, 1); p = min(max(rate, 1e-12), 1 - 1e-12)
    ll_null = (n - violations) * np.log(1 - alpha) + violations * np.log(alpha)
    ll_alt = (n - violations) * np.log(1 - p) + violations * np.log(p)
    statistic = max(0.0, -2 * (ll_null - ll_alt))
    return {"violations": violations, "violation_rate": rate,
            "kupiec_lr": statistic, "kupiec_pvalue": float(chi2.sf(statistic, 1))}


def diagnostics(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name in returns:
        r = returns[name].dropna(); standardized = (r - r.mean()) / r.std(ddof=1)
        jb = jarque_bera(r); ks = kstest(standardized, "norm")
        lag1 = float(r.autocorr(1)); squared_lag1 = float((r * r).autocorr(1))
        rows.append({"series": name, "observations": len(r), "skew": r.skew(),
                     "excess_kurtosis": r.kurtosis(), "jarque_bera_pvalue": jb.pvalue,
                     "normal_ks_pvalue": ks.pvalue, "return_autocorrelation_lag1": lag1,
                     "squared_return_autocorrelation_lag1": squared_lag1})
    return pd.DataFrame(rows)


def benchmark_tests(backtest_returns: pd.DataFrame, benchmark: str = "SIXTY_FORTY") -> pd.DataFrame:
    rows = []
    for name in backtest_returns.columns:
        if name == benchmark: continue
        excess = backtest_returns[name] - backtest_returns[benchmark]
        test = ttest_1samp(excess, 0, nan_policy="omit")
        rows.append({"strategy": name, "benchmark": benchmark,
                     "annualized_excess_return": float(excess.mean() * 252),
                     "tracking_error": float(excess.std(ddof=1) * np.sqrt(252)),
                     "information_ratio": float(excess.mean() / excess.std(ddof=1) * np.sqrt(252)),
                     "mean_difference_tstat": float(test.statistic), "mean_difference_pvalue": float(test.pvalue)})
    return pd.DataFrame(rows)
