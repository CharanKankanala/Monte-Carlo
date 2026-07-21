# Market Dataset Card

## Purpose

This dataset supports a common-date, multi-asset backtest and two competing Monte Carlo models. The committed cache fixes the exact input behind the published dashboard so a later vendor correction cannot silently change the reported numbers.

## Universe

| Ticker | Research role |
|---|---|
| SPY | US large-cap equity and equity benchmark |
| QQQ | US technology growth exposure |
| IWM | US small-cap equity |
| EFA | Developed equity outside the US |
| IEF | Intermediate Treasuries and 60/40 bond sleeve |
| TLT | Long-duration Treasuries |
| GLD | Gold |
| VNQ | US listed real estate |
| DBC | Broad commodities |

## Source and processing

`portfolio_risk/data.py` requests daily Yahoo Finance prices with corporate-action adjustment. The pipeline sorts the dates, keeps the nine named columns, and uses the intersection of complete observations. Log returns feed the simulation models; simple total returns feed the walk-forward backtest.

## Coverage and refresh

The cache begins in January 2014 and contains more than 3,100 aligned sessions. `.github/workflows/refresh-research.yml` can refresh the prices and dashboard payload together each week. The workflow commits only when the source data changes.

## Data-specific caveats

Yahoo Finance can revise historical observations and does not provide an institutional service-level guarantee. ETF returns also mix asset-class behavior with fund fees, tracking error, and product design. Finally, requiring a complete nine-asset row removes dates with an isolated missing quote; this improves matrix consistency but is not a neutral choice for every study.
