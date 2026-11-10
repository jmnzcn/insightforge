/* InsightForge: render validated YAML-driven analytics in the browser. */
const COLORS = ['#7e90ff', '#44d9c1', '#f3b96b', '#c58bff', '#f47e9d'];
const FORMAT = { currency: v => '$' + Math.round(v).toLocaleString('en-US'), integer: v => Math.round(v).toLocaleString('en-US') };
const layoutBase = { paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { color: '#91a3bf', family: 'DM Sans, sans-serif', size: 11 }, margin: { l: 55, r: 20, t: 22, b: 50 }, xaxis: { gridcolor: '#26344c', zerolinecolor: '#26344c' }, yaxis: { gridcolor: '#26344c', zerolinecolor: '#26344c' }, showlegend: false };
const plotOptions = { responsive: true, displayModeBar: false };
let bundle;
function el(tag, className, text) { const n = document.createElement(tag); if (className) n.className = className; if (text !== undefined) n.textContent = text; return n; }
function aggregate(rows, field, key) { const map = new Map(); rows.forEach(r => map.set(r[key], (map.get(r[key]) || 0) + Number(r[field]))); return [...map.entries()].sort((a,b) => String(a[0]).localeCompare(String(b[0]))); }
function render() {
  const config = bundle.config;
  const region = document.getElementById('region').value, category = document.getElementById('category').value;
  const rows = bundle.rows.filter(r => (!region || r.region === region) && (!category || r.category === category));
  document.getElementById('records').textContent = rows.length + ' / ' + bundle.row_count + ' records';
  const kpis = document.getElementById('kpis'); kpis.replaceChildren();
  config.metrics.forEach((metric, i) => {
    const total = rows.reduce((sum, r) => sum + Number(r[metric.column]), 0);
    const card = el('article', 'kpi');
    card.append(el('div', 'kpi-label', metric.label), el('div', 'kpi-value', (FORMAT[metric.format] || FORMAT.integer)(total)), el('div', 'kpi-foot', 'Aggregated from validated data'));
    kpis.append(card);
  });
  const charts = document.getElementById('charts'); charts.replaceChildren();
  config.charts.forEach((chart, i) => {
    const metric = config.metrics.find(m => m.id === chart.metric);
    const values = aggregate(rows, metric.column, chart.x);
    const card = el('article', 'chart-card');
    card.append(el('div', 'chart-title', chart.title), el('div', 'chart-desc', 'Interactive · filter-aware'));
    const plot = el('div', 'plot'); card.append(plot); charts.append(card);
    let trace, layout = structuredClone(layoutBase);
    if (chart.type === 'line') {
      trace = { x: values.map(v => v[0]), y: values.map(v => v[1]), type: 'scatter', mode: 'lines+markers', line: { color: COLORS[0], width: 3, shape: 'spline' }, marker: { color: '#a7b2ff', size: 8 }, fill: 'tozeroy', fillcolor: 'rgba(126,144,255,.09)', hovertemplate: '%{x}<br>%{y:,.0f}<extra></extra>' };
    } else if (chart.type === 'bar') {
      trace = { x: values.map(v => v[0]), y: values.map(v => v[1]), type: 'bar', marker: { color: COLORS.slice(0, values.length), cornerradius: 5 }, hovertemplate: '%{x}<br>%{y:,.0f}<extra></extra>' };
    } else {
      trace = { labels: values.map(v => v[0]), values: values.map(v => v[1]), type: 'pie', hole: .65, marker: { colors: COLORS }, textinfo: 'percent', textfont: { color: '#e8ecf7' }, hovertemplate: '%{label}<br>%{value:,.0f}<extra></extra>' };
      layout.margin = { l: 20, r: 20, t: 20, b: 20 };
      layout.showlegend = true; layout.legend = { orientation: 'h', x: .5, xanchor: 'center', y: -.05 };
    }
    Plotly.newPlot(plot, [trace], layout, plotOptions);
  });
}
async function start() {
  try {
    const response = await fetch('./dashboard.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('Dashboard bundle unavailable');
    bundle = await response.json();
    document.getElementById('title').textContent = bundle.config.title;
    document.getElementById('subtitle').textContent = bundle.config.subtitle || '';
    for (const dimension of bundle.config.dimensions) {
      const select = document.getElementById(dimension);
      if (!select) continue;
      [...new Set(bundle.rows.map(r => r[dimension]))].sort().forEach(value => { const option = el('option', '', value); option.value = value; select.append(option); });
      select.addEventListener('change', render);
    }
    document.getElementById('reset').addEventListener('click', () => { for (const dimension of bundle.config.dimensions) { const select = document.getElementById(dimension); if (select) select.value = ''; } render(); });
    render();
  } catch (error) {
    document.getElementById('subtitle').textContent = 'Unable to load dashboard: ' + error.message;
    console.error(error);
  }
}
document.addEventListener('DOMContentLoaded', start);
