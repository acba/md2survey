#!/usr/bin/env python3
"""
Análise Estatística iGovTI 2026 — Metodologia iGG/TCU
Baseado em "Estrutura para a compreensão dos dados do iGG 2018"
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from factor_analyzer.factor_analyzer import calculate_kmo
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
import warnings
warnings.filterwarnings('ignore')

# Implementação manual de Cronbach's Alpha
def cronbach_alpha(data):
    """Calcula o Coeficiente Alfa de Cronbach."""
    items = data.shape[1]
    variances = data.var(axis=0, ddof=1)
    total_var = data.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return 0.0, None
    alpha = (items / (items - 1)) * (1 - variances.sum() / total_var)
    
    # Intervalo de confiança bootstrap simples
    n_boot = 100
    alphas = []
    for _ in range(n_boot):
        idx = np.random.choice(data.index, size=len(data), replace=True)
        boot_data = data.loc[idx]
        boot_var = boot_data.var(axis=0, ddof=1)
        boot_total = boot_data.sum(axis=1).var(ddof=1)
        if boot_total > 0:
            a = (items / (items - 1)) * (1 - boot_var.sum() / boot_total)
            alphas.append(a)
    
    ci = (np.percentile(alphas, 2.5), np.percentile(alphas, 97.5)) if alphas else None
    return alpha, ci

# ── Configuração visual ────────────────────────────────────────────────
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 120

# ── Carregar dados ─────────────────────────────────────────────────────
print("Carregando dados...")
df = pd.read_excel('/home/acba/workspace/md2survey/kimi_dummy.xlsx',
                   sheet_name='Fiscalização TCE-RJ nº 18202')
print(f"Dados: {df.shape[0]} linhas × {df.shape[1]} colunas")

# ── Identificar colunas ────────────────────────────────────────────────
# Perguntas principais de adoção (sem sufixos)
adoption_main = sorted([c for c in df.columns if c.startswith('q') and
    any(c.startswith(p) for p in ['q1001','q1002','q1003','q1004',
                                   'q2101','q2102','q2201','q2202','q2203','q2204',
                                   'q2301','q2302','q2303','q2401','q2402','q2403','q2404',
                                   'q2501','q2502','q2503','q2504','q2505',
                                   'q2601','q2602','q2701','q2702','q2703','q2704',
                                   'q2705','q2706','q2707','q2801','q2802','q2803',
                                   'q3001','q3002','q3005']) and
    not any(s in c for s in ['nsa','lei','est','raz','ext','evi','filecount'])])

# Perguntas de existência (tipo E) — no iGovTI 2026 não há distinção M/A/E na escala,
# mas mantemos a mesma escala numérica

# Detalhamento TipoX (ext) para cada pergunta de adoção
ext_map = {}
for q in adoption_main:
    ext_cols = [c for c in df.columns if c.startswith(f'{q}ext[')]
    if ext_cols:
        ext_map[q] = sorted(ext_cols)

print(f"Perguntas de adoção: {len(adoption_main)}")
print(f"Perguntas com TipoX: {len(ext_map)}")

# ── Mapeamento numérico conforme Figura 1 do PDF ─────────────────────────
# Escala do iGG 2018 / iGovTI 2026 (valores entre 0 e 1):
#   Não adota = 0
#   Há decisão formal/plano aprovado = 0,05
#   Adota em menor parte = 0,15
#   Adota parcialmente = 0,50
#   Adota em maior parte ou totalmente = 1,00
#   Não se aplica = tratado separadamente (NaN, depois ajustado)

ADOPTION_VALUES = {
    'naoad': 0.00,
    'adfor': 0.05,
    'admen': 0.15,
    'adpar': 0.50,
    'admai': 1.00,
    'naoap': np.nan,  # tratado separadamente
}

# ── Construir matriz de adoção com TipoX ───────────────────────────────
print("\nConstruindo matriz de valores numéricos...")

score_df = pd.DataFrame(index=df.index)

for q in adoption_main:
    # Valor base da pergunta principal
    base = df[q].map(ADOPTION_VALUES)
    
    # Verificar TipoX (ext) quando aplicável
    tipo_x_cols = ext_map.get(q, [])
    if tipo_x_cols:
        # Contar quantos TipoX foram marcados (Y) vs total disponíveis
        tx = df[tipo_x_cols].map(lambda x: 1 if x == 'Y' else 0)
        tx_count = tx.sum(axis=1)
        tx_total = len(tipo_x_cols)
        tx_prop = tx_count / tx_total  # proporção de TipoX marcados
        
        # Aplicar deflação conforme regra do iGG (simplificada):
        #   - valor 1.00 (admai): desconto 0 a 0,85
        #   - valor 0.50 (adpar): desconto 0 a 0,35
        #   - valor <=0.15: desconto 0
        # A fórmula: valor_final = valor_base - desconto_max * (1 - tx_prop)
        deflator = pd.Series(0.0, index=df.index)
        
        mask_admai = (base == 1.00)
        mask_adpar = (base == 0.50)
        
        deflator[mask_admai] = 0.85 * (1 - tx_prop[mask_admai])
        deflator[mask_adpar] = 0.35 * (1 - tx_prop[mask_adpar])
        # admen, adfor, naoad, naoap → deflator 0
        
        score_df[q] = base - deflator
    else:
        score_df[q] = base

# Preencher NaN (naoap) com a média da coluna para fins de análise fatorial
score_filled = score_df.fillna(score_df.mean())

print(f"Matriz de escores: {score_filled.shape}")
print(f"Estatísticas descritivas (primeiras 5):\n{score_filled.describe().iloc[:, :5]}")

# ── Índices Estatísticos Globais ──────────────────────────────────────
print("\n" + "="*65)
print("ÍNDICES ESTATÍSTICOS GLOBAIS")
print("="*65)

valid_responses = score_filled.shape[0]
num_questions = score_filled.shape[1]
print(f"\n1. Quantidade de respostas válidas: {valid_responses}")
print(f"   Número de itens de verificação: {num_questions}")
print(f"   Razão respostas/itens: {valid_responses/num_questions:.2f}")

# 2. Alfa de Cronbach
alpha, alpha_ci = cronbach_alpha(score_filled)
print(f"\n2. Coeficiente Alfa de Cronbach: {alpha:.4f}")
if alpha_ci is not None:
    print(f"   Intervalo de confiança 95%: [{alpha_ci[0]:.4f}, {alpha_ci[1]:.4f}]")
if alpha >= 0.9:
    print("   → Excelente confiabilidade interna (> 0,90)")
elif alpha >= 0.8:
    print("   → Boa confiabilidade interna (0,80–0,90)")
elif alpha >= 0.7:
    print("   → Aceitável confiabilidade interna (0,70–0,80)")
else:
    print("   → Confiabilidade interna baixa (< 0,70)")

# 3. Teste de Bartlett
bartlett_chi, bartlett_p = calculate_bartlett_sphericity(score_filled)
print(f"\n3. Teste de Esfericidade de Bartlett:")
print(f"   Estatística χ²: {bartlett_chi:.3f}")
print(f"   Valor-p: {bartlett_p:.6f}")
if bartlett_p < 0.05:
    print("   → Correlações significativas entre itens (p < 0,05)")
else:
    print("   → Correlações podem não ser significativas (p >= 0,05)")

# 4. KMO
kmo_all, kmo_model = calculate_kmo(score_filled)
print(f"\n4. Medida KMO (Kaiser-Meyer-Olkin):")
print(f"   KMO Global (MSA): {kmo_model:.4f}")
if kmo_model >= 0.9:
    print("   → Maravilhosa adequação da amostra (> 0,90)")
elif kmo_model >= 0.8:
    print("   → Meritória adequação da amostra (0,80–0,90)")
elif kmo_model >= 0.7:
    print("   → Média adequação da amostra (0,70–0,80)")
elif kmo_model >= 0.6:
    print("   → Mediana adequação da amostra (0,60–0,70)")
else:
    print("   → Inaceitável adequação da amostra (< 0,60)")

# KMO individual
print(f"\n   KMO por item (top 10 mais baixos):")
kmo_series = pd.Series(kmo_all, index=score_filled.columns)
for item, val in kmo_series.sort_values().head(10).items():
    print(f"      {item}: {val:.4f}")

# ── Análise de Componentes Principais (ACP) por prática ────────────────
print("\n" + "="*65)
print("ANÁLISE DE COMPONENTES PRINCIPAIS (ACP) POR PRÁTICA")
print("="*65)

# Agrupar questões por prática/tema (conforme estrutura do questionário)
praticas = {
    'g1000_Governanca':     ['q1001', 'q1002', 'q1003', 'q1004'],
    'g2100_Planejamento':   ['q2101', 'q2102'],
    'g2200_Servicos':       ['q2201', 'q2202', 'q2203', 'q2204'],
    'g2300_Riscos':         ['q2301', 'q2302', 'q2303'],
    'g2400_EstruturaSI':    ['q2401', 'q2402', 'q2403', 'q2404'],
    'g2500_ProcessosSI':    ['q2501', 'q2502', 'q2503', 'q2504', 'q2505'],
    'g2600_Solucoes':       ['q2601', 'q2602'],
    'g2700_Pessoas':        ['q2701', 'q2702', 'q2703', 'q2704', 'q2705', 'q2706', 'q2707'],
    'g2800_Contratacoes':   ['q2801', 'q2802', 'q2803'],
    'g3000_IA':             ['q3001', 'q3002', 'q3005'],
}

pca_results = {}
print(f"\n{'Prática':<25} {'Itens':>5} {'PC1%':>8} {'PC2%':>8} {'Kaiser':>7} {'Adequado':>10}")
print("-" * 75)

for nome_pratica, itens in praticas.items():
    itens_presentes = [c for c in itens if c in score_filled.columns]
    if len(itens_presentes) < 2:
        continue
    
    dados_pratica = score_filled[itens_presentes]
    
    # Padronizar
    scaler = StandardScaler()
    X_std = scaler.fit_transform(dados_pratica)
    
    # PCA completo
    pca_local = PCA()
    pca_local.fit(X_std)
    
    var_pc1 = pca_local.explained_variance_ratio_[0] * 100
    var_pc2 = pca_local.explained_variance_ratio_[1] * 100 if len(pca_local.explained_variance_ratio_) > 1 else 0
    eigenvalues = pca_local.explained_variance_
    n_kaiser = sum(eigenvalues > 1)
    
    adequado = "SIM" if (var_pc1 > 50 and n_kaiser == 1) else "PARCIAL" if var_pc1 > 50 else "NÃO"
    
    print(f"{nome_pratica:<25} {len(itens_presentes):>5} {var_pc1:>7.1f}% {var_pc2:>7.1f}% {n_kaiser:>7} {adequado:>10}")
    
    pca_results[nome_pratica] = {
        'itens': itens_presentes,
        'pca': pca_local,
        'var_pc1': var_pc1,
        'var_pc2': var_pc2,
        'n_kaiser': n_kaiser,
        'adequado': adequado,
        'X_std': X_std,
        'loadings': pca_local.components_[0],
        'scores': pca_local.transform(X_std)[:, 0],
    }

# ── Cálculo dos Indicadores (scores do primeiro PC) ────────────────────
print("\n" + "="*65)
print("INDICADORES POR PRÁTICA (Primeiro Componente Principal)")
print("="*65)

indicadores = pd.DataFrame(index=df.index)
for nome, res in pca_results.items():
    indicadores[nome] = res['scores']

print(f"\nEstatísticas dos indicadores:\n{indicadores.describe().round(3)}")

# ── Classificação em Estágios de Capacidade ────────────────────────────
# Conforme Figura 2 do PDF:
#   Inexpressivo: 0% – 15%
#   Iniciando:    15% – 40%
#   Intermediário: 40% – 70%
#   Aprimorado:   70% – 100%
print("\n" + "="*65)
print("CLASSIFICAÇÃO EM ESTÁGIOS DE CAPACIDADE")
print("="*65)

# Normalizar indicadores para 0-1 (min-max por indicador)
indicadores_norm = indicadores.copy()
for col in indicadores_norm.columns:
    mn, mx = indicadores_norm[col].min(), indicadores_norm[col].max()
    if mx > mn:
        indicadores_norm[col] = (indicadores_norm[col] - mn) / (mx - mn)
    else:
        indicadores_norm[col] = 0

# Classificar cada prática de cada organização
estagios = pd.DataFrame(index=df.index)
for col in indicadores_norm.columns:
    vals = indicadores_norm[col]
    estagios[col] = pd.cut(vals,
        bins=[-0.01, 0.15, 0.40, 0.70, 1.01],
        labels=['Inexpressivo', 'Iniciando', 'Intermediário', 'Aprimorado'],
        include_lowest=True)

print("\nDistribuição de estágios por prática:")
for col in estagios.columns:
    counts = estagios[col].value_counts().sort_index()
    pct = (counts / len(estagios) * 100).round(1)
    print(f"\n  {col}:")
    for cat in ['Inexpressivo', 'Iniciando', 'Intermediário', 'Aprimorado']:
        if cat in counts:
            print(f"    {cat:<15}: {counts[cat]:>3} ({pct[cat]:>5.1f}%)")

# Média geral (iGovTI)
iGovTI = indicadores_norm.mean(axis=1)
estagio_geral = pd.cut(iGovTI,
    bins=[-0.01, 0.15, 0.40, 0.70, 1.01],
    labels=['Inexpressivo', 'Iniciando', 'Intermediário', 'Aprimorado'],
    include_lowest=True)

print(f"\n{'='*65}")
print("iGovTI GERAL (média de todos os indicadores)")
print(f"{'='*65}")
print(f"Média geral: {iGovTI.mean():.4f}")
print(f"Desvio padrão: {iGovTI.std():.4f}")
print(f"Mínimo: {iGovTI.min():.4f}")
print(f"Máximo: {iGovTI.max():.4f}")
print(f"\nDistribuição dos estágios gerais:")
for cat in ['Inexpressivo', 'Iniciando', 'Intermediário', 'Aprimorado']:
    count = (estagio_geral == cat).sum()
    pct = count / len(estagio_geral) * 100
    print(f"  {cat:<15}: {count:>3} ({pct:>5.1f}%)")

# ── Salvar resultados numéricos ─────────────────────────────────────────
print("\nSalvando resultados...")
results_text = f"""
RESULTADOS DA ANÁLISE ESTATÍSTICA iGovTI 2026
=============================================
Metodologia baseada em: Estrutura para a compreensão dos dados do iGG 2018 (TCU)

AMOSTRA:
- Respostas válidas: {valid_responses}
- Itens de verificação: {num_questions}
- Razão respostas/itens: {valid_responses/num_questions:.2f}

ÍNDICES ESTATÍSTICOS:
1. Coeficiente Alfa de Cronbach: {alpha:.4f}
   Intervalo 95%: [{alpha_ci[0]:.4f}, {alpha_ci[1]:.4f}]
2. Teste de Esfericidade de Bartlett: χ² = {bartlett_chi:.3f}, p = {bartlett_p:.6f}
3. Medida KMO (MSA): {kmo_model:.4f}

ANÁLISE DE COMPONENTES PRINCIPAIS (ACP) POR PRÁTICA:
"""
for nome, res in pca_results.items():
    results_text += f"\n{nome}:\n"
    results_text += f"  Itens: {res['itens']}\n"
    results_text += f"  Variância PC1: {res['var_pc1']:.1f}%\n"
    results_text += f"  Componentes com autovalor > 1: {res['n_kaiser']}\n"
    results_text += f"  Adequado (>50% e Kaiser=1): {res['adequado']}\n"
    results_text += f"  Loadings PC1:\n"
    for item, loading in zip(res['itens'], res['loadings']):
        results_text += f"    {item}: {loading:.3f}\n"

results_text += f"\n\nINDICADOR iGovTI GERAL:\n"
results_text += f"  Média: {iGovTI.mean():.4f}\n"
results_text += f"  Desvio padrão: {iGovTI.std():.4f}\n"
results_text += f"  Mínimo: {iGovTI.min():.4f}\n"
results_text += f"  Máximo: {iGovTI.max():.4f}\n"
results_text += f"\n  Distribuição de estágios:\n"
for cat in ['Inexpressivo', 'Iniciando', 'Intermediário', 'Aprimorado']:
    count = (estagio_geral == cat).sum()
    pct = count / len(estagio_geral) * 100
    results_text += f"    {cat}: {count} ({pct:.1f}%)\n"

with open('/home/acba/workspace/md2survey/resultados_estatisticos.txt', 'w') as f:
    f.write(results_text)

# ── Gráficos ───────────────────────────────────────────────────────────
print("Gerando gráficos...")
fig_count = 0

# 1. Distribuição dos níveis de adoção (bruta)
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Distribuição dos Níveis de Adoção (Escala 0–1)', fontsize=14, fontweight='bold')

# Frequência global
all_scores = score_filled.values.flatten()
all_scores = all_scores[~np.isnan(all_scores)]
axes[0, 0].hist(all_scores, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
axes[0, 0].axvline(x=all_scores.mean(), color='red', linestyle='--', linewidth=2, label=f'Média: {all_scores.mean():.3f}')
axes[0, 0].set_xlabel('Valor de Adoção')
axes[0, 0].set_ylabel('Frequência')
axes[0, 0].set_title('Distribuição Global dos Escores')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3, axis='y')

# Boxplot por prática
bp_data = []
bp_labels = []
for nome, res in pca_results.items():
    bp_data.append(score_filled[res['itens']].values.flatten())
    bp_labels.append(nome.replace('g', '').replace('_', ' '))

axes[0, 1].boxplot(bp_data, labels=bp_labels)
axes[0, 1].set_title('Dispersão dos Escores por Prática')
axes[0, 1].set_ylabel('Valor de Adoção (0–1)')
axes[0, 1].tick_params(axis='x', rotation=45, labelsize=8)
axes[0, 1].grid(True, alpha=0.3, axis='y')

# Média por prática
medias = {nome: score_filled[res['itens']].mean().mean() for nome, res in pca_results.items()}
axes[1, 0].barh(list(medias.keys()), list(medias.values()), color='steelblue')
axes[1, 0].set_xlabel('Média do Valor de Adoção')
axes[1, 0].set_title('Média de Adoção por Prática')
axes[1, 0].axvline(x=0.5, color='red', linestyle='--', alpha=0.7, label='Limite Parcial/Adiantado')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3, axis='x')

# Matriz de correlação (amostra)
corr_sample = score_filled[list(pca_results.values())[0]['itens'] + list(pca_results.values())[1]['itens']].corr()
im = axes[1, 1].imshow(corr_sample, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
axes[1, 1].set_title('Matriz de Correlações (Amostra de Práticas)')
axes[1, 1].set_xticks(range(len(corr_sample.columns)))
axes[1, 1].set_yticks(range(len(corr_sample.columns)))
axes[1, 1].set_xticklabels([c.replace('q', '') for c in corr_sample.columns], rotation=90, fontsize=8)
axes[1, 1].set_yticklabels([c.replace('q', '') for c in corr_sample.columns], fontsize=8)
plt.colorbar(im, ax=axes[1, 1])

plt.tight_layout()
plt.savefig('/home/acba/workspace/md2survey/fig01_distribuicao_geral.png', bbox_inches='tight')
plt.close()
fig_count += 1

# 2. Matriz de correlação completa
print("  Matriz de correlação...")
plt.figure(figsize=(16, 14))
corr_full = score_filled.corr()
mask = np.triu(np.ones_like(corr_full, dtype=bool), k=1)
sns.heatmap(corr_full, mask=mask, cmap='RdYlGn', center=0, vmin=-1, vmax=1,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
            xticklabels=[c.replace('q', '') for c in corr_full.columns],
            yticklabels=[c.replace('q', '') for c in corr_full.columns])
plt.title('Matriz de Correlações entre os Itens de Verificação\n(iGovTI 2026)', fontsize=14, fontweight='bold')
plt.xticks(rotation=90, fontsize=8)
plt.yticks(fontsize=8)
plt.tight_layout()
plt.savefig('/home/acba/workspace/md2survey/fig02_matriz_correlacao.png', bbox_inches='tight')
plt.close()
fig_count += 1

# 3. Scree plots por prática
print("  Scree plots...")
n_praticas = len(pca_results)
ncols = 3
nrows = (n_praticas + ncols - 1) // ncols
fig, axes = plt.subplots(nrows, ncols, figsize=(15, 4*nrows))
axes = axes.flatten() if nrows > 1 else [axes] if ncols == 1 else axes.flatten()

for idx, (nome, res) in enumerate(pca_results.items()):
    ax = axes[idx]
    ev = res['pca'].explained_variance_ratio_ * 100
    ax.bar(range(1, len(ev)+1), ev, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axhline(y=100/len(ev), color='red', linestyle='--', alpha=0.7, label='Média')
    ax.set_xlabel('Componente')
    ax.set_ylabel('% Variância')
    ax.set_title(f"{nome.replace('g', '').replace('_', ' ')}\nPC1: {ev[0]:.1f}%")
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend()

# Hide extra subplots
for idx in range(len(pca_results), len(axes)):
    axes[idx].set_visible(False)

plt.tight_layout()
plt.savefig('/home/acba/workspace/md2survey/fig03_scree_por_pratica.png', bbox_inches='tight')
plt.close()
fig_count += 1

# 4. Loadings (cargas fatoriais) por prática
print("  Loadings...")
fig, axes = plt.subplots(nrows, ncols, figsize=(15, 4*nrows))
axes = axes.flatten() if nrows > 1 else [axes] if ncols == 1 else axes.flatten()

for idx, (nome, res) in enumerate(pca_results.items()):
    ax = axes[idx]
    loadings = res['loadings']
    itens_labels = [c.replace('q', '') for c in res['itens']]
    y_pos = np.arange(len(itens_labels))
    colors = ['green' if l > 0.5 else 'orange' if l > 0.3 else 'red' for l in loadings]
    ax.barh(y_pos, loadings, color=colors, alpha=0.7, edgecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(itens_labels, fontsize=9)
    ax.set_xlabel('Carga Fatorial (Loading)')
    ax.set_title(f"Cargas Fatoriais - PC1\n{nome.replace('g', '').replace('_', ' ')}")
    ax.axvline(x=0, color='black', linewidth=0.5)
    ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3, axis='x')

for idx in range(len(pca_results), len(axes)):
    axes[idx].set_visible(False)

plt.tight_layout()
plt.savefig('/home/acba/workspace/md2survey/fig04_loadings_por_pratica.png', bbox_inches='tight')
plt.close()
fig_count += 1

# 5. Scores (indicadores) por prática
print("  Indicadores por prática...")
fig, axes = plt.subplots(nrows, ncols, figsize=(15, 4*nrows))
axes = axes.flatten() if nrows > 1 else [axes] if ncols == 1 else axes.flatten()

for idx, (nome, res) in enumerate(pca_results.items()):
    ax = axes[idx]
    scores = res['scores']
    ax.hist(scores, bins=15, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axvline(x=scores.mean(), color='red', linestyle='--', linewidth=2, label=f'Média: {scores.mean():.2f}')
    ax.set_xlabel('Score (Primeiro PC)')
    ax.set_ylabel('Frequência')
    ax.set_title(f"Indicador - {nome.replace('g', '').replace('_', ' ')}")
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

for idx in range(len(pca_results), len(axes)):
    axes[idx].set_visible(False)

plt.tight_layout()
plt.savefig('/home/acba/workspace/md2survey/fig05_scores_por_pratica.png', bbox_inches='tight')
plt.close()
fig_count += 1

# 6. Radar dos indicadores (média por prática)
print("  Radar chart...")
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

medias_ind = indicadores_norm.mean()
categories = [c.replace('g', '').replace('_', ' ') for c in medias_ind.index]
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

values = medias_ind.values.tolist()
values += values[:1]

ax.plot(angles, values, 'o-', linewidth=2, color='steelblue')
ax.fill(angles, values, alpha=0.25, color='steelblue')
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=10)
ax.set_ylim(0, 1)
ax.set_title('Média dos Indicadores por Prática\n(iGovTI 2026)', fontsize=14, fontweight='bold', pad=20)
ax.grid(True)

plt.tight_layout()
plt.savefig('/home/acba/workspace/md2survey/fig06_radar_indicadores.png', bbox_inches='tight')
plt.close()
fig_count += 1

# 7. Estágios de capacidade (stacked bar)
print("  Estágios de capacidade...")
fig, ax = plt.subplots(figsize=(12, 8))

estagio_counts = pd.DataFrame()
for col in estagios.columns:
    counts = estagios[col].value_counts().reindex(['Inexpressivo', 'Iniciando', 'Intermediário', 'Aprimorado'], fill_value=0)
    estagio_counts[col.replace('g', '').replace('_', ' ')] = counts

estagio_counts.T.plot(kind='barh', stacked=True, ax=ax,
                       color=['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c'])
ax.set_xlabel('Número de Organizações')
ax.set_title('Classificação em Estágios de Capacidade por Prática', fontsize=14, fontweight='bold')
ax.legend(title='Estágio', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('/home/acba/workspace/md2survey/fig07_estagios_capacidade.png', bbox_inches='tight')
plt.close()
fig_count += 1

# 8. iGovTI Geral
print("  iGovTI geral...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histograma iGovTI
axes[0].hist(iGovTI, bins=15, color='steelblue', alpha=0.7, edgecolor='black')
axes[0].axvline(x=iGovTI.mean(), color='red', linestyle='--', linewidth=2, label=f'Média: {iGovTI.mean():.3f}')
axes[0].axvline(x=0.40, color='orange', linestyle='--', alpha=0.7, label='Limite Intermediário')
axes[0].axvline(x=0.70, color='green', linestyle='--', alpha=0.7, label='Limite Aprimorado')
axes[0].set_xlabel('iGovTI (média normalizada)')
axes[0].set_ylabel('Frequência')
axes[0].set_title('Distribuição do Indicador iGovTI Geral')
axes[0].legend()
axes[0].grid(True, alpha=0.3, axis='y')

# Estágios gerais
geral_counts = estagio_geral.value_counts().reindex(['Inexpressivo', 'Iniciando', 'Intermediário', 'Aprimorado'], fill_value=0)
colors_est = ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c']
axes[1].bar(geral_counts.index, geral_counts.values, color=colors_est, alpha=0.7, edgecolor='black')
axes[1].set_ylabel('Número de Organizações')
axes[1].set_title('Estágio de Capacidade Geral (iGovTI)')
for i, v in enumerate(geral_counts.values):
    axes[1].text(i, v + 0.5, f'{v}\n({v/len(estagio_geral)*100:.1f}%)', ha='center', fontweight='bold')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/acba/workspace/md2survey/fig08_igovti_geral.png', bbox_inches='tight')
plt.close()
fig_count += 1

# 9. Heatmap de organizações × práticas (scores normalizados)
print("  Heatmap organizações...")
plt.figure(figsize=(14, 10))
sample_idx = np.random.choice(indicadores_norm.index, min(25, len(indicadores_norm)), replace=False)
heatmap_data = indicadores_norm.loc[sample_idx].T

sns.heatmap(heatmap_data, cmap='RdYlGn', vmin=0, vmax=1, linewidths=0.5,
            xticklabels=[f'Org{i+1}' for i in range(len(sample_idx))],
            yticklabels=[c.replace('g', '').replace('_', ' ') for c in heatmap_data.index],
            cbar_kws={'label': 'Score Normalizado (0–1)'})
plt.title('Mapa de Calor - Scores por Prática e Organização\n(Amostra de 25 organizações)',
          fontsize=14, fontweight='bold')
plt.xlabel('Organizações')
plt.ylabel('Práticas')
plt.tight_layout()
plt.savefig('/home/acba/workspace/md2survey/fig09_heatmap_organizacoes.png', bbox_inches='tight')
plt.close()
fig_count += 1

# 10. Correlações implícitas entre práticas
print("  Correlações entre práticas...")
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Relações entre Domínios (Médias das Práticas por Organização)', fontsize=14, fontweight='bold')

pares = [
    ('g1000_Governanca', 'g2200_Servicos', 'Governança vs Serviços'),
    ('g2100_Planejamento', 'g2300_Riscos', 'Planejamento vs Riscos'),
    ('g2700_Pessoas', 'g2600_Solucoes', 'Pessoas vs Soluções'),
    ('g2400_EstruturaSI', 'g2800_Contratacoes', 'Segurança vs Contratações'),
]

for ax, (p1, p2, titulo) in zip(axes.flat, pares):
    if p1 in indicadores_norm.columns and p2 in indicadores_norm.columns:
        x = indicadores_norm[p1]
        y = indicadores_norm[p2]
        ax.scatter(x, y, s=80, alpha=0.6, c='steelblue', edgecolors='black')
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(sorted(x), p(sorted(x)), "r--", alpha=0.8)
        corr = np.corrcoef(x, y)[0, 1]
        ax.set_title(f'{titulo}\n(r = {corr:.3f})')
        ax.set_xlabel(p1.replace('g', '').replace('_', ' '))
        ax.set_ylabel(p2.replace('g', '').replace('_', ' '))
        ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/acba/workspace/md2survey/fig10_correlacoes_implicitas.png', bbox_inches='tight')
plt.close()
fig_count += 1

print(f"\n{'='*65}")
print(f"ANÁLISE CONCLUÍDA - {fig_count} gráficos gerados")
print(f"{'='*65}")
print("Arquivos gerados:")
print("  - resultados_estatisticos.txt")
for i in range(1, fig_count + 1):
    print(f"  - fig{i:02d}_*.png")
