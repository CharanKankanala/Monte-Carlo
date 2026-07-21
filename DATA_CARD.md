# Market Dataset Card

## Universe

SPY, QQQ, IWM, EFA, IEF, TLT, GLD, VNQ, and DBC represent US large-cap, technology and small-cap equities; developed international equity; intermediate and long Treasuries; gold; US real estate; and broad commodities.

## Source and transformation

The pipeline downloads daily Yahoo Finance prices with automatic corporate-action adjustment and inner-aligns assets to complete common trading dates. Log returns drive simulation; simple total returns drive implementable backtests.

## Coverage and reproducibility

The committed production cache begins in January 2014 and contains more than 3,100 aligned observations. `data/market_prices.csv` is the immutable input for the reported results. The scheduled workflow refreshes that cache and the dashboard payload together.

## Known limitations

The data is not a licensed institutional feed and may contain provider corrections. ETF selection introduces proxy and survivorship bias. The common-date intersection omits dates on which any selected instrument lacks an observation.

