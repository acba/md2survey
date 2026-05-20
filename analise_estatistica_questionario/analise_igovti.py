#!/usr/bin/env python3
"""
Análise Estatística iGovTI 2026 — Módulo Reutilizável
Metodologia baseada no iGG/TCU (Estrutura para compreensão dos dados 2018)
Retorna dict com métricas, dados para Plotly.js e figuras base64 do Matplotlib.
"""

import io
import base64
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ── Estilo matplotlib ────────────────────────────────────────────────
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 120

# ── Paleta TCE-RJ ──────────────────────────────────────────────────────
TCERJ_NAVY = '#1a3a5c'
TCERJ_CYAN = '#0088bb'
TCERJ_LIME = '#7cb342'
TCERJ_LIGHT = '#e8f4f8'
TCERJ_WHITE = '#ffffff'

# ── Escala numérica iGG ──────────────────────────────────────────────
ADOPTION_VALUES = {
    'naoad': 0.00,
    'adfor': 0.05,
    'admen': 0.15,
    'adpar': 0.50,
    'admai': 1.00,
    'naoap': np.nan,
}

ESTAGIOS_BINS = [-0.01, 0.15, 0.40, 0.70, 1.01]
ESTAGIOS_LABELS = ['Inexpressivo', 'Iniciando', 'Intermediário', 'Aprimorado']

# ── Cronbach's Alpha ─────────────────────────────────────────────────
def cronbach_alpha(data):
    items = data.shape[1]
    variances = data.var(axis=0, ddof=1)
    total_var = data.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return 0.0, None
    alpha = (items / (items - 1)) * (1 - variances.sum() / total_var)
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
    ci = (float(np.percentile(alphas, 2.5)), float(np.percentile(alphas, 97.5))) if alphas else None
    return float(alpha), ci

# ── Bartlett ──────────────────────────────────────────────────────────
def bartlett_test(data):
    n = data.shape[0]
    p = data.shape[1]
    corr = np.corrcoef(data.values.T)
    try:
        det_corr = np.linalg.det(corr)
        if det_corr <= 0 or np.isnan(det_corr):
            eigenvalues = np.linalg.eigvalsh(corr)
            log_det = np.sum(np.log(eigenvalues[eigenvalues > 1e-10]))
            statistic = -log_det * (n - 1 - (2*p + 5)/6)
        else:
            statistic = -np.log(det_corr) * (n - 1 - (2*p + 5)/6)
        df_bartlett = p * (p - 1) / 2
        p_value = 1 - stats.chi2.cdf(statistic, df_bartlett)
        return float(statistic), float(p_value)
    except:
        return None, None

# ── KMO ──────────────────────────────────────────────────────────────
def kmo_test(data):
    corr = np.corrcoef(data.values.T)
    corr = corr + np.eye(corr.shape[0]) * 1e-10
    try:
        corr_inv = np.linalg.pinv(corr)
        diag_inv = np.diag(corr_inv)
        diag_inv = np.where(diag_inv > 0, diag_inv, 1e-10)
        partial_corr = -corr_inv / np.sqrt(np.outer(diag_inv, diag_inv))
        np.fill_diagonal(partial_corr, 1)
        kmo_i = np.zeros(corr.shape[0])
        for i in range(corr.shape[0]):
            sum_sq_corr = np.sum(corr[i, :] ** 2) - 1
            sum_sq_partial = np.sum(partial_corr[i, :] ** 2) - 1
            if (sum_sq_corr + sum_sq_partial) > 0:
                kmo_i[i] = sum_sq_corr / (sum_sq_corr + sum_sq_partial)
        sum_sq_corr = np.sum(corr ** 2) - corr.shape[0]
        sum_sq_partial = np.sum(partial_corr ** 2) - corr.shape[0]
        kmo_total = sum_sq_corr / (sum_sq_corr + sum_sq_partial) if (sum_sq_corr + sum_sq_partial) > 0 else 0
        return float(kmo_total), kmo_i.tolist()
    except:
        return 0.0, []

# ── Função auxiliar: figura → base64 ─────────────────────────────────
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"

# ── Função principal ─────────────────────────────────────────────────
def analisar_questionario(caminho_xlsx: str) -> dict:
    print(f"[analise] Carregando {caminho_xlsx}...")
    df = pd.read_excel(caminho_xlsx, sheet_name='Fiscalização TCE-RJ nº 18202')
    print(f"[analise] Dados: {df.shape[0]} × {df.shape[1]}")

    # Identificar colunas principais de adoção
    adoption_main = sorted([c for c in df.columns if c.startswith('q') and
        any(c.startswith(p) for p in ['q1001','q1002','q1003','q1004',
                                       'q2101','q2102','q2201','q2202','q2203','q2204',
                                       'q2301','q2302','q2303','q2401','q2402','q2403','q2404',
                                       'q2501','q2502','q2503','q2504','q2505',
                                       'q2601','q2602','q2701','q2702','q2703','q2704',
                                       'q2705','q2706','q2707','q2801','q2802','q2803',
                                       'q3001','q3002','q3005']) and
        not any(s in c for s in ['nsa','lei','est','raz','ext','evi','filecount'])])

    # Mapear extensões TipoX
    ext_map = {}
    for q in adoption_main:
        ext_cols = [c for c in df.columns if c.startswith(f'{q}ext[')]
        if ext_cols:
            ext_map[q] = sorted(ext_cols)

    print(f"[analise] {len(adoption_main)} perguntas principais, {len(ext_map)} com TipoX")

    # ── Matriz de escores ──────────────────────────────────────────
    score_df = pd.DataFrame(index=df.index)
    for q in adoption_main:
        base = df[q].map(ADOPTION_VALUES)
        tipo_x_cols = ext_map.get(q, [])
        if tipo_x_cols:
            tx = df[tipo_x_cols].map(lambda x: 1 if x == 'Y' else 0)
            tx_count = tx.sum(axis=1)
            tx_total = len(tipo_x_cols)
            tx_prop = tx_count / tx_total
            deflator = pd.Series(0.0, index=df.index)
            mask_admai = (base == 1.00)
            mask_adpar = (base == 0.50)
            deflator[mask_admai] = 0.85 * (1 - tx_prop[mask_admai])
            deflator[mask_adpar] = 0.35 * (1 - tx_prop[mask_adpar])
            score_df[q] = base - deflator
        else:
            score_df[q] = base

    score_filled = score_df.fillna(score_df.mean())
    score_filled = score_filled.loc[:, score_filled.var() > 0]

    print(f"[analise] Matriz final: {score_filled.shape}")

    # ── Índices estatísticos ──────────────────────────────────────
    alpha, alpha_ci = cronbach_alpha(score_filled)
    bartlett_chi, bartlett_p = bartlett_test(score_filled)
    kmo_global, kmo_individual = kmo_test(score_filled)

    metricas = {
        "n_orgs": int(score_filled.shape[0]),
        "n_itens": int(score_filled.shape[1]),
        "cronbach": round(alpha, 4),
        "cronbach_ci": [round(alpha_ci[0], 4), round(alpha_ci[1], 4)] if alpha_ci else None,
        "bartlett_chi": round(bartlett_chi, 3) if bartlett_chi else None,
        "bartlett_p": round(bartlett_p, 6) if bartlett_p else None,
        "kmo": round(kmo_global, 4),
    }

    # ── Práticas / agregadores ───────────────────────────────────
    praticas = {
        'Governança':     ['q1001', 'q1002', 'q1003', 'q1004'],
        'Planejamento':   ['q2101', 'q2102'],
        'Serviços':       ['q2201', 'q2202', 'q2203', 'q2204'],
        'Riscos':         ['q2301', 'q2302', 'q2303'],
        'Estrutura SI':   ['q2401', 'q2402', 'q2403', 'q2404'],
        'Processos SI':   ['q2501', 'q2502', 'q2503', 'q2504', 'q2505'],
        'Soluções':       ['q2601', 'q2602'],
        'Pessoas':        ['q2701', 'q2702', 'q2703', 'q2704', 'q2705', 'q2706', 'q2707'],
        'Contratações':   ['q2801', 'q2802', 'q2803'],
        'IA':             ['q3001', 'q3002', 'q3005'],
    }

    pca_results = {}
    indicadores = pd.DataFrame(index=score_filled.index)

    for nome_pratica, itens in praticas.items():
        itens_presentes = [c for c in itens if c in score_filled.columns]
        if len(itens_presentes) < 2:
            continue
        dados_pratica = score_filled[itens_presentes]
        scaler = StandardScaler()
        X_std = scaler.fit_transform(dados_pratica)
        pca_local = PCA()
        pca_local.fit(X_std)
        var_pc1 = float(pca_local.explained_variance_ratio_[0] * 100)
        var_pc2 = float(pca_local.explained_variance_ratio_[1] * 100) if len(pca_local.explained_variance_ratio_) > 1 else 0.0
        eigenvalues = pca_local.explained_variance_
        n_kaiser = int(sum(eigenvalues > 1))
        adequado = bool(var_pc1 > 50 and n_kaiser == 1)
        loadings = pca_local.components_[0]
        scores = pca_local.transform(X_std)[:, 0]

        pca_results[nome_pratica] = {
            'itens': itens_presentes,
            'var_pc1': round(var_pc1, 1),
            'var_pc2': round(var_pc2, 1),
            'n_kaiser': n_kaiser,
            'adequado': adequado,
            'loadings': {item: round(float(ld), 3) for item, ld in zip(itens_presentes, loadings)},
            'scores': scores.tolist(),
            'autovalores': eigenvalues.tolist(),
        }
        indicadores[nome_pratica] = scores

    # ── Normalizar e classificar estágios ─────────────────────────
    indicadores_norm = indicadores.copy()
    for col in indicadores_norm.columns:
        mn, mx = indicadores_norm[col].min(), indicadores_norm[col].max()
        if mx > mn:
            indicadores_norm[col] = (indicadores_norm[col] - mn) / (mx - mn)
        else:
            indicadores_norm[col] = 0.0

    estagios = pd.DataFrame(index=score_filled.index)
    estagios_praticas_dict = {}
    for col in indicadores_norm.columns:
        vals = indicadores_norm[col]
        est = pd.cut(vals, bins=ESTAGIOS_BINS, labels=ESTAGIOS_LABELS, include_lowest=True)
        estagios[col] = est
        counts = est.value_counts().reindex(ESTAGIOS_LABELS, fill_value=0)
        estagios_praticas_dict[col] = {k: int(v) for k, v in counts.items()}

    iGovTI = indicadores_norm.mean(axis=1)
    estagio_geral = pd.cut(iGovTI, bins=ESTAGIOS_BINS, labels=ESTAGIOS_LABELS, include_lowest=True)
    estagios_geral_dict = {}
    for cat in ESTAGIOS_LABELS:
        count = int((estagio_geral == cat).sum())
        estagios_geral_dict[cat] = count

    metricas["igovti_mean"] = round(float(iGovTI.mean()), 4)
    metricas["igovti_std"] = round(float(iGovTI.std()), 4)
    metricas["igovti_min"] = round(float(iGovTI.min()), 4)
    metricas["igovti_max"] = round(float(iGovTI.max()), 4)

    # ── Correlações implícitas ────────────────────────────────────
    pares_nomes = [
        ('Governança', 'Serviços', 'Governança vs Serviços'),
        ('Planejamento', 'Riscos', 'Planejamento vs Riscos'),
        ('Pessoas', 'Soluções', 'Pessoas vs Soluções'),
        ('Estrutura SI', 'Contratações', 'Segurança vs Contratações'),
    ]
    correlacoes_implicitas = {}
    for p1, p2, titulo in pares_nomes:
        if p1 in indicadores_norm.columns and p2 in indicadores_norm.columns:
            x = indicadores_norm[p1].values.tolist()
            y = indicadores_norm[p2].values.tolist()
            corr = float(np.corrcoef(x, y)[0, 1])
            correlacoes_implicitas[titulo] = {"x": x, "y": y, "corr": round(corr, 3)}

    # ── Dados para heatmaps (Plotly.js) ───────────────────────────
    corr_full = score_filled.corr()
    matriz_correlacao = {
        "z": corr_full.values.tolist(),
        "x": [c.replace('q', '') for c in corr_full.columns],
        "y": [c.replace('q', '') for c in corr_full.index],
    }

    sample_idx = np.random.choice(indicadores_norm.index, min(25, len(indicadores_norm)), replace=False)
    heatmap_org = indicadores_norm.loc[sample_idx].T
    heatmap_organizacoes = {
        "z": heatmap_org.values.tolist(),
        "x": [f"Org {i+1}" for i in range(len(sample_idx))],
        "y": list(heatmap_org.index),
    }

    # ── Figuras base64 (Matplotlib) ──────────────────────────────
    print("[analise] Gerando figuras base64...")
    figuras_base64 = {}

    # 1. Distribuição geral
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Distribuição dos Níveis de Adoção (Escala 0–1)', fontsize=14, fontweight='bold', color=TCERJ_NAVY)
    all_scores = score_filled.values.flatten()
    all_scores = all_scores[~np.isnan(all_scores)]
    axes[0,0].hist(all_scores, bins=20, color=TCERJ_CYAN, alpha=0.7, edgecolor='black')
    axes[0,0].axvline(x=all_scores.mean(), color=TCERJ_LIME, linestyle='--', linewidth=2, label=f'Média: {all_scores.mean():.3f}')
    axes[0,0].set_title('Distribuição Global dos Escores')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3, axis='y')

    bp_data, bp_labels = [], []
    for nome, res in pca_results.items():
        bp_data.append(score_filled[res['itens']].values.flatten())
        bp_labels.append(nome)
    axes[0,1].boxplot(bp_data, labels=bp_labels)
    axes[0,1].set_title('Dispersão por Prática')
    axes[0,1].tick_params(axis='x', rotation=45, labelsize=8)
    axes[0,1].grid(True, alpha=0.3, axis='y')

    medias = {nome: float(score_filled[res['itens']].mean().mean()) for nome, res in pca_results.items()}
    axes[1,0].barh(list(medias.keys()), list(medias.values()), color=TCERJ_CYAN)
    axes[1,0].axvline(x=0.5, color=TCERJ_LIME, linestyle='--', alpha=0.7)
    axes[1,0].set_title('Média de Adoção por Prática')
    axes[1,0].grid(True, alpha=0.3, axis='x')

    corr_sample = score_filled[list(pca_results.values())[0]['itens'] + list(pca_results.values())[1]['itens']].corr()
    im = axes[1,1].imshow(corr_sample, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
    axes[1,1].set_title('Matriz de Correlações (Amostra)')
    plt.colorbar(im, ax=axes[1,1])
    figuras_base64['distribuicao'] = fig_to_base64(fig)

    # 2. Scree plots por prática
    n_praticas = len(pca_results)
    ncols, nrows = 3, (n_praticas + 2) // 3
    fig, axes = plt.subplots(nrows, ncols, figsize=(15, 4*nrows))
    axes = axes.flatten() if nrows > 1 else [axes] if ncols == 1 else axes.flatten()
    fig.suptitle('Variância Explicada por Componente (Scree Plot)', fontsize=14, fontweight='bold', color=TCERJ_NAVY)
    for idx, (nome, res) in enumerate(pca_results.items()):
        ax = axes[idx]
        ev = res['autovalores']
        ax.bar(range(1, len(ev)+1), ev, color=TCERJ_CYAN, alpha=0.7, edgecolor='black')
        ax.axhline(y=1, color=TCERJ_LIME, linestyle='--', alpha=0.7, label='Kaiser (λ=1)')
        ax.set_title(f"{nome}\nPC1: {res['var_pc1']:.1f}%")
        ax.set_xlabel('Componente')
        ax.set_ylabel('Autovalor')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, axis='y')
    for idx in range(len(pca_results), len(axes)):
        axes[idx].set_visible(False)
    figuras_base64['scree'] = fig_to_base64(fig)

    # 3. Estágios de capacidade
    fig, ax = plt.subplots(figsize=(12, 7))
    estagio_counts = pd.DataFrame()
    for col in estagios.columns:
        counts = estagios[col].value_counts().reindex(ESTAGIOS_LABELS, fill_value=0)
        estagio_counts[col] = counts
    estagio_counts.T.plot(kind='barh', stacked=True, ax=ax,
                          color=['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c'])
    ax.set_xlabel('Número de Organizações')
    ax.set_title('Classificação em Estágios de Capacidade por Prática', fontsize=14, fontweight='bold', color=TCERJ_NAVY)
    ax.legend(title='Estágio', bbox_to_anchor=(1.05, 1), loc='upper left')
    figuras_base64['estagios'] = fig_to_base64(fig)

    # 4. iGovTI geral
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Indicador iGovTI Geral', fontsize=14, fontweight='bold', color=TCERJ_NAVY)
    axes[0].hist(iGovTI, bins=15, color=TCERJ_CYAN, alpha=0.7, edgecolor='black')
    axes[0].axvline(x=iGovTI.mean(), color=TCERJ_LIME, linestyle='--', linewidth=2, label=f'Média: {iGovTI.mean():.3f}')
    axes[0].axvline(x=0.40, color='orange', linestyle='--', alpha=0.7, label='Limite Intermediário')
    axes[0].axvline(x=0.70, color='green', linestyle='--', alpha=0.7, label='Limite Aprimorado')
    axes[0].set_xlabel('iGovTI (média normalizada)')
    axes[0].set_ylabel('Frequência')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')

    geral_counts = estagio_geral.value_counts().reindex(ESTAGIOS_LABELS, fill_value=0)
    colors_est = ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c']
    axes[1].bar(geral_counts.index, geral_counts.values, color=colors_est, alpha=0.7, edgecolor='black')
    axes[1].set_ylabel('Número de Organizações')
    axes[1].set_title('Estágio de Capacidade Geral')
    for i, v in enumerate(geral_counts.values):
        axes[1].text(i, v + 0.5, f'{v}\n({v/len(estagio_geral)*100:.1f}%)', ha='center', fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    figuras_base64['igovti_geral'] = fig_to_base64(fig)

    print("[analise] Análise concluída.")

    return {
        "metricas": metricas,
        "estagios_geral": estagios_geral_dict,
        "estagios_praticas": estagios_praticas_dict,
        "pca_por_pratica": pca_results,
        "correlacoes_implicitas": correlacoes_implicitas,
        "matriz_correlacao": matriz_correlacao,
        "heatmap_organizacoes": heatmap_organizacoes,
        "figuras_base64": figuras_base64,
    }


# ── Teste standalone ─────────────────────────────────────────────────
if __name__ == "__main__":
    resultado = analisar_questionario("sample_data/kimi_dummy.xlsx")
    print("\n--- Resultado ---")
    print(f"Cronbach: {resultado['metricas']['cronbach']}")
    print(f"KMO: {resultado['metricas']['kmo']}")
    print(f"Figuras: {list(resultado['figuras_base64'].keys())}")
