#!/usr/bin/env python3
"""Gera um HTML standalone com os dados do upload para teste visual."""
import requests, json, base64, html
from pathlib import Path

# 1. Faz upload
url = "http://127.0.0.1:5000/upload"
file_path = Path(__file__).parent / "sample_data" / "kimi_dummy.xlsx"

with open(file_path, "rb") as f:
    resp = requests.post(url, files={"file": f})

data = resp.json()

# 2. Gera HTML standalone
html_out = Path(__file__).parent / "standalone_dashboard.html"

# Embute CSS
with open(Path(__file__).parent / "assets/css/tcerj-theme.css") as f:
    css = f.read()

# Template simplificado do dashboard
html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard iGovTI 2026 - Standalone Test</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
{css}
</style>
</head>
<body>
<header>
    <div class="logo-container">
        <div class="logo-text">
            <span class="logo-main">TCE-RJ</span>
            <span class="logo-sub">Tribunal de Contas do Estado do Rio de Janeiro</span>
        </div>
    </div>
    <h1>Dashboard iGovTI 2026</h1>
    <p class="subtitle">Análise Estatística do Questionário de Governança de TI</p>
</header>

<div class="container">
    <!-- Resumo Executivo -->
    <section class="summary-cards">
        <div class="card">
            <div class="card-title">Organizações</div>
            <div class="card-value">{data['metricas']['n_organizacoes']}</div>
            <div class="card-subtitle">Amostra analisada</div>
        </div>
        <div class="card">
            <div class="card-title">Alfa de Cronbach</div>
            <div class="card-value">{data['metricas']['cronbach']:.3f}</div>
            <div class="card-subtitle">Consistência interna</div>
        </div>
        <div class="card">
            <div class="card-title">KMO</div>
            <div class="card-value">{data['metricas']['kmo']:.3f}</div>
            <div class="card-subtitle">Adequação amostral</div>
        </div>
        <div class="card">
            <div class="card-title">iGovTI Médio</div>
            <div class="card-value">{data['metricas']['igovti_geral']:.3f}</div>
            <div class="card-subtitle">Índice geral</div>
        </div>
        <div class="card">
            <div class="card-title">Bartlett</div>
            <div class="card-value">{'Significante' if data['metricas']['bartlett']['significativo'] else 'Não sig.'}</div>
            <div class="card-subtitle">χ² = {data['metricas']['bartlett']['qui_quadrado']:.1f}</div>
        </div>
    </section>

    <!-- Estágios de Capacidade -->
    <section class="chart-section">
        <h2>Estágios de Capacidade de TI</h2>
        <div id="estagios-chart" style="height: 450px;"></div>
    </section>

    <!-- Figuras base64 -->
    <section class="chart-section">
        <h2>Distribuição Geral do iGovTI</h2>
        <img src="data:image/png;base64,{data['figuras_base64']['distribuicao']}" alt="Distribuição" style="width: 100%; max-width: 900px;">
    </section>

    <section class="chart-section">
        <h2>Scree Plot por Prática</h2>
        <img src="data:image/png;base64,{data['figuras_base64']['scree']}" alt="Scree" style="width: 100%; max-width: 900px;">
    </section>

    <section class="chart-section">
        <h2>iGovTI Geral</h2>
        <img src="data:image/png;base64,{data['figuras_base64']['igovti_geral']}" alt="iGovTI Geral" style="width: 100%; max-width: 900px;">
    </section>

    <!-- Tabela de Práticas -->
    <section class="table-section">
        <h2>Indicadores por Prática</h2>
        <table class="data-table">
            <thead>
                <tr><th>Prática</th><th>Eigenvalue</th><th>% Variância</th><th>Kaiser OK</th></tr>
            </thead>
            <tbody>
"""

for p in data['praticas']:
    html_content += f"                <tr><td>{html.escape(p['nome'])}</td><td>{p['eigenvalue']:.2f}</td><td>{p['variancia']:.1f}%</td><td>{'Sim' if p['adequado'] else 'Não'}</td></tr>\n"

html_content += """            </tbody>
        </table>
    </section>
</div>

<script>
// Estágios de Capacidade - Donut Chart
var estagiosData = """ + json.dumps(data['estagios_capacidade']) + """;
var labels = Object.keys(estagiosData);
var values = Object.values(estagiosData);

var pieData = [{
    values: values,
    labels: labels,
    type: 'pie',
    hole: 0.45,
    marker: {
        colors: ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
    },
    textinfo: 'label+percent',
    textposition: 'outside'
}];

var pieLayout = {
    showlegend: true,
    legend: { orientation: 'h', y: -0.1 },
    margin: { t: 30, b: 60 }
};

Plotly.newPlot('estagios-chart', pieData, pieLayout, {responsive: true});
</script>
</body>
</html>
"""

html_out.write_text(html_content, encoding="utf-8")
print(f"✓ HTML standalone gerado: {html_out}")
print(f"  Tamanho: {html_out.stat().st_size:,} bytes")
print(f"  Organizações: {data['metricas']['n_organizacoes']}")
print(f"  Cronbach: {data['metricas']['cronbach']:.4f}")
print(f"  Práticas: {len(data['praticas'])}")
