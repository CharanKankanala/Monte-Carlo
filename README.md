# Monte Carlo Risk Simulation for Portfolio Forecasting  
### A Graduate-Level Study in Distributional Portfolio Risk, Tail Exposure, and Scenario Robustness

---

## Table of Contents

1. [Abstract](#abstract)  
2. [Motivation and Problem Statement](#motivation-and-problem-statement)  
3. [Research Questions](#research-questions)  
4. [Project Scope](#project-scope)  
5. [Methodological Framework](#methodological-framework)  
6. [Mathematical Formulation](#mathematical-formulation)  
7. [Portfolio Design](#portfolio-design)  
8. [Scenario and Sensitivity Design](#scenario-and-sensitivity-design)  
9. [Risk Metrics](#risk-metrics)  
10. [Implementation Architecture](#implementation-architecture)  
11. [Repository Structure](#repository-structure)  
12. [Reproducibility and Experiment Control](#reproducibility-and-experiment-control)  
13. [Installation](#installation)  
14. [Execution](#execution)  
15. [Outputs](#outputs)  
16. [How to Interpret Results](#how-to-interpret-results)  
17. [Validation Checklist](#validation-checklist)  
18. [Limitations](#limitations)  
19. [Future Work](#future-work)  
20. [Interview / Viva Defense Guide](#interview--viva-defense-guide)  
21. [Quick 60-Second Pitch](#quick-60-second-pitch)  
22. [License and Disclaimer](#license-and-disclaimer)

---

## Abstract

This project implements a Monte Carlo simulation framework to forecast one-year portfolio outcomes under uncertainty.  
The study models 10,000+ stochastic paths over a 252-trading-day horizon and compares three allocation policies (Conservative, Balanced, Aggressive) across volatility and return regimes.  
The framework emphasizes downside risk through 95% Value at Risk (VaR), 95% Conditional Value at Risk (CVaR), maximum drawdown behavior, and confidence intervals for terminal return distributions.  

Beyond basic simulation, this work is designed as an academically defensible mini-research system with explicit assumptions, reproducibility controls, scenario stress testing, and interview-ready narrative.

---

## Motivation and Problem Statement

Classical point forecasts of portfolio performance are often misleading under market uncertainty.  
Decision-making in finance requires distribution-aware estimates, especially for tail losses and path-dependent risk.

**Problem:**  
Given a set of strategic asset allocations, how do expected performance and downside risk evolve across plausible market regimes over a 1-year horizon?

---

## Research Questions

1. Which allocation strategy offers the highest expected terminal return?  
2. Which strategy offers strongest downside protection under stressed conditions?  
3. How sensitive are VaR/CVaR and drawdown behavior to volatility amplification and return shifts?  
4. Are conclusions stable across pessimistic, neutral, and optimistic assumptions?

---

## Project Scope

- Horizon: **252 trading days**  
- Simulation count: **10,000+ paths**  
- Assets: **Equity, Bond, Gold**  
- Strategies: **Conservative, Balanced, Aggressive**  
- Regimes:
  - **5 volatility scenarios**
  - **3 return assumptions**
- Core metrics:
  - Expected Return
  - 95% VaR
  - 95% CVaR
  - Maximum Drawdown
  - 95% Confidence Interval

Total strategy-scenario evaluations = **5 × 3 × 3 = 45**.

---

## Methodological Framework

1. Define baseline annual return and volatility assumptions per asset.
2. Convert annual assumptions to daily parameters.
3. Simulate correlated daily shocks via Cholesky decomposition.
4. Generate daily asset returns using GBM-like dynamics.
5. Aggregate asset returns to strategy-level portfolio returns using fixed weights.
6. Compound pathwise portfolio values from initial capital.
7. Compute terminal return distributions and pathwise drawdowns.
8. Estimate risk statistics (VaR, CVaR, CI, drawdown summaries).
9. Repeat across all regime combinations.
10. Export tabular and visual artifacts.

---

## Mathematical Formulation

For each asset \(i\) and day \(t\), log-return model:

\[
r_{i,t}^{(\log)} = \left(\mu_{i,d} - \frac{1}{2}\sigma_{i,d}^2\right) + \sigma_{i,d} z_{i,t}
\]

where \(z_t\) is sampled from a correlated multivariate normal distribution.

Simple return conversion:

\[
r_{i,t} = e^{r_{i,t}^{(\log)}} - 1
\]

Portfolio return per day:

\[
r_{p,t} = \sum_{i=1}^{N} w_i r_{i,t}
\]

Portfolio value path:

\[
V_t = V_0 \prod_{k=1}^{t}(1+r_{p,k})
\]

---

## Portfolio Design

### Assets and baseline annual assumptions

- Equity: return 9%, vol 22%  
- Bond: return 4%, vol 8%  
- Gold: return 5%, vol 15%

### Strategies

- **Conservative** = [0.25, 0.60, 0.15]  
- **Balanced** = [0.50, 0.30, 0.20]  
- **Aggressive** = [0.70, 0.15, 0.15]

### Correlation structure

A fixed positive-definite matrix is used to encode inter-asset dependence.

---

## Scenario and Sensitivity Design

### Volatility regimes

- Very Low Vol (0.70×)
- Low Vol (0.85×)
- Base Vol (1.00×)
- High Vol (1.20×)
- Very High Vol (1.40×)

### Return assumptions

- Bearish (-2%)
- Neutral (0%)
- Bullish (+2%)

This grid allows consistent stress-testing of risk-return tradeoffs.

---

## Risk Metrics

### Expected Return (%)
Mean terminal return across simulated paths.

### 95% VaR (%)
5th percentile of terminal return distribution (threshold loss quantile).

### 95% CVaR (%)
Average return of outcomes in the worst 5% tail (tail severity).

### Maximum Drawdown (%)
Largest peak-to-trough decline experienced along each path.

### 95% Confidence Interval
[2.5th, 97.5th] percentiles of terminal returns.

---

## Implementation Architecture

Current implementation is executable via a primary script.  
For full grad-level polish, modularization is recommended:

- `src/simulation.py` — path generation engine  
- `src/metrics.py` — VaR/CVaR/drawdown/CI estimators  
- `src/scenarios.py` — regime configuration layer  
- `src/plotting.py` — reporting visuals  
- `src/config.py` — assumptions and constants  
- `run_experiment.py` — CLI entrypoint  
- `tests/` — unit and integration tests

This project can be evolved into that structure with minimal logic changes.

---

## Repository Structure

```text
Monte-Carlo/
├── monte_carlo_portfolio.py
├── requirements.txt
├── README.md
├── ASSIGNMENT_CLARITY.md
└── outputs/
    ├── monte_carlo_metrics.csv
    ├── expected_return_by_scenario.png
    ├── var95_by_scenario.png
    ├── risk_return_scatter.png
    └── ...
