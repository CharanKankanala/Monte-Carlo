"use client";

import { useEffect, useMemo, useState } from "react";

type Performance = { strategy: string; cagr: number; annual_volatility: number; sharpe: number; max_drawdown: number; cagr_liquidity_stress: number };
type Model = { model: string; var_95: number; cvar_95: number; average_max_drawdown: number; expected_return: number };
type Wealth = { date: string; [key: string]: string | number };
type Results = { meta: { source: string; start: string; end: string; observations: number; paths: number; assets: Record<string,string> }; performance: Performance[]; models: Model[]; wealth: Wealth[]; regimes: {date:string; high_volatility:number}[]; garch: {asset:string; persistence:number; latest_annualized_volatility:number}[] };

const COLORS: Record<string, string> = { equal_weight: "#26d9a3", minimum_variance: "#70a7ff", momentum_tilt: "#f5c451", risk_parity: "#c897ff", SP500: "#ff6d73", SIXTY_FORTY: "#f4f5f7" };
const LABELS: Record<string, string> = { equal_weight: "Equal weight", minimum_variance: "Minimum variance", momentum_tilt: "Momentum tilt", risk_parity: "Risk parity", SP500: "S&P 500", SIXTY_FORTY: "60 / 40" };

const pct = (n: number, digits=1) => `${(n * 100).toFixed(digits)}%`;
const nice = (n: number) => Number.isFinite(n) ? n.toFixed(2) : "—";

function WealthChart({rows, active}:{rows:Wealth[]; active:string[]}) {
  if (!rows.length) return <div className="chart-empty">Loading research series…</div>;
  const width=1100, height=330, pad=28;
  const all = rows.flatMap(r => active.map(k => Number(r[k]))).filter(Number.isFinite);
  const lo=Math.min(...all)*.96, hi=Math.max(...all)*1.02;
  const points=(key:string)=>rows.map((r,i)=>`${pad+i/(rows.length-1)*(width-pad*2)},${height-pad-(Number(r[key])-lo)/(hi-lo)*(height-pad*2)}`).join(" ");
  return <div className="chart-wrap">
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Walk-forward wealth comparison">
      {[0,.25,.5,.75,1].map(v=><line key={v} x1={pad} x2={width-pad} y1={pad+v*(height-pad*2)} y2={pad+v*(height-pad*2)} className="gridline" />)}
      {active.map(k=><polyline key={k} points={points(k)} fill="none" stroke={COLORS[k]} strokeWidth={k==="SIXTY_FORTY"?3:2} vectorEffect="non-scaling-stroke" />)}
    </svg>
    <div className="chart-axis"><span>{rows[0].date.slice(0,4)}</span><span>Growth of $1, net of costs</span><span>{rows.at(-1)?.date.slice(0,4)}</span></div>
  </div>
}

export default function Home() {
  const [data,setData]=useState<Results|null>(null);
  const [active,setActive]=useState(["equal_weight","minimum_variance","risk_parity","SP500","SIXTY_FORTY"]);
  const [cost,setCost]=useState(10);
  const [view,setView]=useState<"performance"|"tail"|"diagnostics">("performance");
  useEffect(()=>{fetch("/results.json").then(r=>r.json()).then(setData)},[]);
  const ranked=useMemo(()=>data?.performance.slice().sort((a,b)=>b.sharpe-a.sharpe)??[],[data]);
  const leader=ranked[0];
  const toggle=(name:string)=>setActive(x=>x.includes(name)?(x.length>1?x.filter(v=>v!==name):x):[...x,name]);
  return <main>
    <header className="topbar"><a className="brand" href="#top"><span className="brand-mark">M</span><span>Multi-Asset Risk Lab</span></a><nav><a href="#research">Research</a><a href="#models">Models</a><a href="#methodology">Methodology</a></nav><span className="status"><i/> Research build</span></header>
    <section className="hero" id="top">
      <div><p className="eyebrow">QUANTITATIVE FINTECH RESEARCH</p><h1>Portfolio decisions,<br/><em>tested under pressure.</em></h1><p className="lede">An out-of-sample laboratory combining allocation research, implementation costs, volatility regimes and heavy-tail simulation across nine liquid asset-class ETFs.</p></div>
      <div className="hero-stat"><span>DATA WINDOW</span><strong>{data ? `${data.meta.start.slice(0,4)}—${data.meta.end.slice(0,4)}` : "2014—2026"}</strong><small>{data?.meta.observations.toLocaleString() ?? "3,000+"} trading days</small></div>
    </section>

    <section className="metric-strip" aria-label="research highlights">
      <div><span>Best risk-adjusted</span><strong>{leader ? LABELS[leader.strategy] : "60 / 40"}</strong><small>Sharpe {leader ? nice(leader.sharpe) : "—"}</small></div>
      <div><span>Lowest drawdown</span><strong>{ranked.length ? LABELS[ranked.slice().sort((a,b)=>b.max_drawdown-a.max_drawdown)[0].strategy] : "—"}</strong><small>Walk-forward, net of costs</small></div>
      <div><span>Scenario depth</span><strong>{data?.meta.paths.toLocaleString() ?? "10,000"} paths</strong><small>252-day horizon</small></div>
      <div><span>Model stack</span><strong>GARCH + HMM</strong><small>Heavy-tail rank copula</small></div>
    </section>

    <section className="panel" id="research">
      <div className="section-head"><div><p className="eyebrow">OUT-OF-SAMPLE EVIDENCE</p><h2>Walk-forward wealth</h2></div><div className="segmented"><button className={view==="performance"?"on":""} onClick={()=>setView("performance")}>Performance</button><button className={view==="tail"?"on":""} onClick={()=>setView("tail")}>Tail risk</button><button className={view==="diagnostics"?"on":""} onClick={()=>setView("diagnostics")}>Diagnostics</button></div></div>
      {view==="performance" && <><div className="strategy-picker">{data?.performance.map(p=><button key={p.strategy} onClick={()=>toggle(p.strategy)} className={active.includes(p.strategy)?"selected":""}><i style={{background:COLORS[p.strategy]}}/>{LABELS[p.strategy]}</button>)}</div><WealthChart rows={data?.wealth??[]} active={active}/></>}
      {view==="tail" && <div className="model-grid">{data?.models.map(m=><article key={m.model}><p>{m.model.replaceAll("_"," ")}</p><strong>{pct(m.cvar_95)}</strong><span>95% expected shortfall</span><div className="bar"><i style={{width:`${Math.min(100,m.cvar_95*800)}%`}}/></div><small>VaR {pct(m.var_95)} · Avg drawdown {pct(m.average_max_drawdown)}</small></article>)}</div>}
      {view==="diagnostics" && <div className="diagnostic-grid"><article><span>Volatility states</span><strong>2-state HMM</strong><p>Latent low- and high-volatility states are estimated with forward–backward EM, not labeled from future returns.</p></article><article><span>Dependence</span><strong>Rank copula</strong><p>Marginal shapes are removed before estimating cross-asset dependence; Student-t shocks preserve heavier tails.</p></article><article><span>Validation</span><strong>Coverage + tests</strong><p>VaR exceptions use Kupiec coverage while strategy differences report uncertainty and tracking error.</p></article></div>}
    </section>

    <section className="two-col" id="models">
      <div className="panel"><p className="eyebrow">IMPLEMENTATION REALISM</p><h2>Cost stress lab</h2><p className="muted">Explore a linear implementation-cost overlay. The production study uses 10 bps and separately validates a 35 bps stressed case.</p><label className="slider-label"><span>Assumed cost</span><strong>{cost} bps</strong></label><input type="range" min="0" max="75" value={cost} onChange={e=>setCost(Number(e.target.value))}/><div className="cost-table">{data?.performance.slice(0,4).map(p=>{const drag=(p.cagr-p.cagr_liquidity_stress)*(cost/35); return <div key={p.strategy}><span>{LABELS[p.strategy]}</span><b>{pct(p.cagr-drag)}</b><small>stress-adjusted CAGR</small></div>})}</div></div>
      <div className="panel"><p className="eyebrow">CONDITIONAL RISK</p><h2>GARCH persistence</h2><div className="garch-list">{data?.garch.map(g=><div key={g.asset}><span><b>{g.asset}</b><small>{data.meta.assets[g.asset]}</small></span><span className="persistence"><i style={{width:`${g.persistence*100}%`}}/></span><strong>{g.persistence.toFixed(3)}</strong></div>)}</div></div>
    </section>

    <section className="method" id="methodology"><div><p className="eyebrow">RESEARCH GOVERNANCE</p><h2>Designed to resist easy stories.</h2></div><div className="method-grid"><article><b>01</b><h3>Past-only estimation</h3><p>Every allocation uses a rolling 504-day window and is held out of sample for the following rebalance period.</p></article><article><b>02</b><h3>Friction-aware</h3><p>Turnover creates explicit trading costs; an additional liquidity-stress scenario tests strategy fragility.</p></article><article><b>03</b><h3>Competing distributions</h3><p>Historical block bootstrap is compared with a dynamic GARCH, regime and heavy-tail copula model.</p></article><article><b>04</b><h3>Benchmark honesty</h3><p>S&P 500 and 60/40 portfolios remain visible. Complexity is not treated as success unless evidence supports it.</p></article></div></section>
    <footer><div className="brand"><span className="brand-mark">M</span><span>Multi-Asset Risk Lab</span></div><p>Reproducible research · Data through {data?.meta.end ?? "latest cached run"}</p><p>Educational research, not investment advice.</p></footer>
  </main>
}
