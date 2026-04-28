import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

TRADING_DAYS = 252
INITIAL_PORTFOLIO_VALUE = 100000

ASSETS = {
    "Equity": {"mu": 0.09, "sigma": 0.22},
    "Bond": {"mu": 0.04, "sigma": 0.08},
    "Gold": {"mu": 0.05, "sigma": 0.15},
}

STRATEGIES = {
    "Conservative": np.array([0.25, 0.60, 0.15]),
    "Balanced": np.array([0.50, 0.30, 0.20]),
    "Aggressive": np.array([0.70, 0.15, 0.15]),
}

VOL_SCENARIOS = {
    "Very Low Vol": 0.70,
    "Low Vol": 0.85,
    "Base Vol": 1.00,
    "High Vol": 1.20,
    "Very High Vol": 1.40,
}

RETURN_ASSUMPTIONS = {
    "Bearish": -0.02,
    "Neutral": 0.00,
    "Bullish": 0.02,
}

CORR = np.array([
    [1.00, 0.25, 0.10],
    [0.25, 1.00, -0.05],
    [0.10, -0.05, 1.00],
])

def annual_to_daily(mu_annual, sigma_annual):
    return mu_annual / TRADING_DAYS, sigma_annual / np.sqrt(TRADING_DAYS)

def simulate_returns(mu_annual, sigma_annual, days, paths, seed):
    rng = np.random.default_rng(seed)
    n_assets = len(mu_annual)
    mu_d, sig_d = annual_to_daily(mu_annual, sigma_annual)
    L = np.linalg.cholesky(CORR)
    z = rng.standard_normal((paths, days, n_assets))
    zc = np.einsum("pda,ab->pdb", z, L)
    log_r = (mu_d - 0.5 * sig_d**2)[None, None, :] + sig_d[None, None, :] * zc
    return np.exp(log_r) - 1

def max_drawdown(path_values):
    peaks = np.maximum.accumulate(path_values, axis=1)
    dd = (path_values - peaks) / peaks
    return dd.min(axis=1)

def summarize(terminal_values, total_returns, mdd, alpha=0.95):
    var = np.percentile(total_returns, (1-alpha)*100)
    cvar = total_returns[total_returns <= var].mean()
    ci_low, ci_high = np.percentile(total_returns, [2.5, 97.5])
    return {
        "Expected Return (%)": total_returns.mean()*100,
        "95% VaR (%)": var*100,
        "95% CVaR (%)": cvar*100,
        "Average Max Drawdown (%)": mdd.mean()*100,
        "Worst Max Drawdown (%)": mdd.min()*100,
        "95% CI Lower Return (%)": ci_low*100,
        "95% CI Upper Return (%)": ci_high*100,
        "Expected Terminal Value": terminal_values.mean(),
    }

def run(paths, days, seed, out):
    out.mkdir(parents=True, exist_ok=True)
    base_mu = np.array([ASSETS[a]["mu"] for a in ["Equity","Bond","Gold"]], dtype=float)
    base_sigma = np.array([ASSETS[a]["sigma"] for a in ["Equity","Bond","Gold"]], dtype=float)

    rows = []
    s = seed
    for ret_name, ret_shift in RETURN_ASSUMPTIONS.items():
        for vol_name, vol_mult in VOL_SCENARIOS.items():
            mu = base_mu + ret_shift
            sigma = base_sigma * vol_mult
            asset_ret = simulate_returns(mu, sigma, days, paths, s)
            s += 1
            for strat_name, w in STRATEGIES.items():
                p_ret = asset_ret @ w
                p_val = np.empty((paths, days+1), dtype=float)
                p_val[:,0] = INITIAL_PORTFOLIO_VALUE
                p_val[:,1:] = INITIAL_PORTFOLIO_VALUE * np.cumprod(1+p_ret, axis=1)

                terminal = p_val[:,-1]
                total_ret = terminal / INITIAL_PORTFOLIO_VALUE - 1
                mdd = max_drawdown(p_val)

                m = summarize(terminal, total_ret, mdd)
                m.update({
                    "Return Assumption": ret_name,
                    "Scenario": vol_name,
                    "Strategy": strat_name,
                    "Paths": paths,
                    "Horizon (days)": days
                })
                rows.append(m)

    df = pd.DataFrame(rows)
    df.to_csv(out / "monte_carlo_metrics.csv", index=False)

    neutral = df[df["Return Assumption"]=="Neutral"]
    neutral.pivot(index="Scenario", columns="Strategy", values="Expected Return (%)").plot(kind="bar", figsize=(10,5))
    plt.title("Expected Return (%) by Volatility Scenario (Neutral)")
    plt.tight_layout()
    plt.savefig(out / "expected_return_by_scenario.png", dpi=160)
    plt.close()

    neutral.pivot(index="Scenario", columns="Strategy", values="95% VaR (%)").plot(kind="bar", figsize=(10,5))
    plt.title("95% VaR (%) by Volatility Scenario (Neutral)")
    plt.tight_layout()
    plt.savefig(out / "var95_by_scenario.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8,6))
    for strat in df["Strategy"].unique():
        sub = df[df["Strategy"]==strat]
        plt.scatter(sub["95% VaR (%)"], sub["Expected Return (%)"], label=strat, alpha=0.8)
    plt.xlabel("95% VaR (%)")
    plt.ylabel("Expected Return (%)")
    plt.title("Risk-Return Scatter")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "risk_return_scatter.png", dpi=160)
    plt.close()

    print("Done. Output:", out.resolve())
    print("Rows:", len(df), "(expected 45)")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--paths", type=int, default=10000)
    p.add_argument("--days", type=int, default=252)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=Path("outputs"))
    a = p.parse_args()
    run(a.paths, a.days, a.seed, a.out)
