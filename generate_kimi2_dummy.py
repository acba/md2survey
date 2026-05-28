#!/usr/bin/env python3
"""Generate 100+ diverse dummy respondents for iGovTI 2026 survey."""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Load template to get exact column structure
df_template = pd.read_excel('/home/acba/workspace/md2survey/results-survey585912.xlsx')
columns = df_template.columns.tolist()

# Define adoption scale values
ADOPTION_VALUES = [
    "Não adota.",
    "Há decisão formal ou plano aprovado para adotá-lo.",
    "Adota em menor parte.",
    "Adota parcialmente.",
    "Adota em maior parte ou totalmente.",
    "Não se aplica."
]

ADOPTION_WEIGHTS_PROFILES = {
    "very_low":  [0.50, 0.25, 0.15, 0.08, 0.02, 0.00],  # mostly Não adota
    "low":       [0.30, 0.25, 0.25, 0.12, 0.06, 0.02],
    "medium_low":[0.15, 0.20, 0.30, 0.20, 0.12, 0.03],
    "medium":    [0.08, 0.12, 0.25, 0.30, 0.20, 0.05],
    "medium_high":[0.03, 0.08, 0.15, 0.30, 0.32, 0.12],
    "high":      [0.00, 0.03, 0.08, 0.20, 0.42, 0.27],  # mostly Adota em maior parte
}

# Single choice questions and their options
SINGLE_CHOICES = {
    "q0101": {
        "A": "a) Centralizada Interna: Há uma área de TI centralizada e formal que atende toda a organização, utilizando equipe técnica majoritariamente própria (servidores).",
        "B": "b) Centralizada Terceirizada: Há uma área de TI centralizada e formal que faz a gestão, mas a execução operacional/técnica é predominantemente terceirizada (ex: fábricas de software, service desk).",
        "C": "c) Centralizada Externa: Os serviços de TI são prestados predominantemente por um órgão, entidade ou estrutura central externa à organização (ex: empresa pública de processamento de dados estadual ou municipal).",
        "D": "d) Descentralizada: Diferentes secretarias, unidades ou setores possuem autonomia e mantêm suas próprias equipes, contratos ou infraestruturas de TI de forma independente.",
        "E": "e) Híbrida: Existe uma TI central formal para diretrizes e infraestrutura corporativa, mas as áreas de negócio possuem equipes próprias para sustentar sistemas específicos.",
        "F": "f) Inexistente / Informal: Não há área de TI formalmente instituída no organograma da organização.",
    },
    "q0102": {
        "A": "a) a área de TI reporta-se diretamente ao dirigente máximo da organização",
        "B": "b) a área de TI está subordinada a secretaria, subsecretaria, diretoria-geral ou estrutura equivalente de nível estratégico",
        "C": "c) a área de TI está subordinada a área administrativa, financeira ou área meio equivalente",
        "D": "d) a área de TI está subordinada a unidade operacional ou setorial sem atuação corporativa relevante",
        "E": "e) não há área de TI formalmente instituída ou não há posicionamento hierárquico formal definido para a área de TI",
    },
    "q0104": {
        "A": "a) Independente da TI: Há unidade, área ou gestor de segurança da informação formalmente separado da área de TI.",
        "B": "b) Integrada à TI: A área, equipe ou responsável por segurança da informação integra a estrutura da área de tecnologia da informação.",
        "C": "c) Gerida por Comitê: Não há uma unidade administrativa exclusiva para SI, mas a função é coordenada por comitê, comissão ou instância colegiada formal.",
        "D": "d) Responsável designado: Há responsável formalmente designado para segurança da informação, mas sem unidade, equipe ou comitê específico.",
        "E": "e) Inexistente / Informal: Não há área, função, gestor ou comitê de Segurança da Informação formalmente instituído na organização.",
    },
}

# Adoption questions (main + ext + nsa/lei/est/raz + evi)
ADOPTION_QUESTIONS = [
    "q1001", "q1002", "q1003", "q1004",
    "q2101", "q2102",
    "q2201", "q2202", "q2203", "q2204",
    "q2301", "q2302", "q2303",
    "q2401", "q2402", "q2403", "q2404",
    "q2501", "q2502", "q2503", "q2504", "q2505",
    "q2601", "q2602",
    "q2701", "q2702", "q2703", "q2704", "q2705", "q2706", "q2707",
    "q2801", "q2802", "q2803",
    "q3001", "q3002", "q3005",
]

# Extension counts for each adoption question
EXT_COUNTS = {
    "q1001": 9, "q1002": 4, "q1003": 2, "q1004": 7,
    "q2101": 4, "q2102": 5,
    "q2201": 5, "q2202": 6, "q2203": 3, "q2204": 6,
    "q2301": 3, "q2302": 4, "q2303": 4,
    "q2401": 5, "q2402": 4, "q2403": 6, "q2404": 7,
    "q2501": 6, "q2502": 5, "q2503": 6, "q2504": 11, "q2505": 4,
    "q2601": 6, "q2602": 4,
    "q2701": 4, "q2702": 4, "q2703": 4, "q2704": 4, "q2705": 4, "q2706": 4, "q2707": 5,
    "q2801": 7, "q2802": 5, "q2803": 7,
    "q3001": 6, "q3002": 7, "q3005": 4,
}

# Sim/Nao questions (array)
SIM_NAO_QUESTIONS = {
    "q2708": ["A", "B", "C", "D"],
    "q2804": ["A", "B", "C", "D", "E"],
    "q2805": ["A", "B"],
    "q3003": ["A", "B", "C"],
}

# Multi questions
MULTI_QUESTIONS = {
    "q0103": ["A", "B", "C", "D", "E", "F", "G"],
    "q3004": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"],
}


def pick_adoption(profile):
    """Pick an adoption value based on profile weights."""
    weights = ADOPTION_WEIGHTS_PROFILES[profile]
    return np.random.choice(ADOPTION_VALUES, p=weights)


def generate_respondent(row_id, profile):
    """Generate one respondent's answers."""
    row = {}

    # Metadata
    row['id'] = row_id
    row['submitdate'] = (datetime(2026, 5, 13) + timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S.000')
    row['lastpage'] = 46
    row['startlanguage'] = 'pt-BR'
    row['seed'] = random.randint(100000000, 999999999)
    row['token'] = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    row['startdate'] = row['submitdate']
    row['datestamp'] = row['submitdate']

    # Profile determines q0101 (structure)
    if profile in ["very_low", "low"]:
        q0101_choice = random.choices(["F", "D", "C"], weights=[0.6, 0.3, 0.1])[0]
    elif profile in ["medium_low", "medium"]:
        q0101_choice = random.choices(["B", "C", "D", "E"], weights=[0.3, 0.3, 0.2, 0.2])[0]
    else:
        q0101_choice = random.choices(["A", "B", "E"], weights=[0.4, 0.4, 0.2])[0]

    row['q0101'] = SINGLE_CHOICES["q0101"][q0101_choice]
    row['q0101evi'] = np.nan
    row['q0101evi[filecount]'] = np.nan

    # q0102 (positioning) - must be consistent with q0101
    if q0101_choice == "F":
        row['q0102'] = SINGLE_CHOICES["q0102"]["E"]
    elif profile in ["very_low", "low"]:
        row['q0102'] = SINGLE_CHOICES["q0102"][random.choices(["C", "D"], weights=[0.5, 0.5])[0]]
    elif profile in ["medium_low", "medium"]:
        row['q0102'] = SINGLE_CHOICES["q0102"][random.choices(["B", "C"], weights=[0.4, 0.6])[0]]
    else:
        row['q0102'] = SINGLE_CHOICES["q0102"][random.choices(["A", "B"], weights=[0.6, 0.4])[0]]
    row['q0102evi'] = np.nan
    row['q0102evi[filecount]'] = np.nan

    # q0103 (multi) - attributions
    if q0101_choice == "F":
        # No TI area
        for opt in MULTI_QUESTIONS["q0103"]:
            row[f'q0103[{opt}]'] = np.nan
        row['q0103[G]'] = "Sim"  # No attributions defined
    else:
        if profile in ["very_low", "low"]:
            # Only basic attributions
            has = random.sample(["A", "B"], k=random.randint(0, 2))
        elif profile in ["medium_low", "medium"]:
            has = random.sample(["A", "B", "C", "D"], k=random.randint(2, 4))
        else:
            has = random.sample(["A", "B", "C", "D", "E", "F"], k=random.randint(4, 6))

        for opt in MULTI_QUESTIONS["q0103"]:
            row[f'q0103[{opt}]'] = "Sim" if opt in has else np.nan
    row['q0103evi'] = np.nan
    row['q0103evi[filecount]'] = np.nan

    # q0104 (SI positioning)
    if profile in ["very_low", "low"]:
        q0104_choice = random.choices(["E", "D"], weights=[0.7, 0.3])[0]
    elif profile in ["medium_low", "medium"]:
        q0104_choice = random.choices(["D", "B", "C"], weights=[0.4, 0.4, 0.2])[0]
    else:
        q0104_choice = random.choices(["A", "B", "C"], weights=[0.4, 0.4, 0.2])[0]
    row['q0104'] = SINGLE_CHOICES["q0104"][q0104_choice]
    row['q0104evi'] = np.nan
    row['q0104evi[filecount]'] = np.nan

    # q0105 (array_numbers) - workforce
    if q0101_choice == "F":
        # No TI = all zeros
        for area in ["TI", "SI"]:
            for tipo in ["efetivos", "comissionados", "terceirizados", "cedidos", "temporarios", "estagiarios"]:
                row[f'q0105[{area}_{tipo}]'] = 0.0
    else:
        # Generate realistic workforce numbers
        if profile in ["very_low", "low"]:
            ti_total = random.randint(1, 8)
            si_total = random.randint(0, 2)
        elif profile in ["medium_low", "medium"]:
            ti_total = random.randint(8, 30)
            si_total = random.randint(1, 5)
        else:
            ti_total = random.randint(25, 80)
            si_total = random.randint(3, 15)

        # Distribute by type
        for area, total in [("TI", ti_total), ("SI", si_total)]:
            efetivos = int(total * random.uniform(0.3, 0.7))
            terceirizados = int(total * random.uniform(0.1, 0.4))
            comissionados = int(total * random.uniform(0.0, 0.2))
            cedidos = int(total * random.uniform(0.0, 0.1))
            temporarios = int(total * random.uniform(0.0, 0.1))
            estagiarios = int(total * random.uniform(0.0, 0.15))

            # Adjust to match total approximately
            total_calc = efetivos + terceirizados + comissionados + cedidos + temporarios + estagiarios
            if total_calc < total:
                efetivos += (total - total_calc)

            row[f'q0105[{area}_efetivos]'] = float(efetivos)
            row[f'q0105[{area}_comissionados]'] = float(comissionados)
            row[f'q0105[{area}_terceirizados]'] = float(terceirizados)
            row[f'q0105[{area}_cedidos]'] = float(cedidos)
            row[f'q0105[{area}_temporarios]'] = float(temporarios)
            row[f'q0105[{area}_estagiarios]'] = float(estagiarios)

    # qg2000ciencia
    row['qg2000ciencia[ciente]'] = "Sim"

    # Adoption questions
    for q in ADOPTION_QUESTIONS:
        val = pick_adoption(profile)
        row[q] = val

        # Não se aplica reason columns
        if val == "Não se aplica.":
            row[f'{q}nsa'] = random.choice(["A", "B", "C"])
            row[f'{q}lei'] = np.nan
            row[f'{q}est'] = np.nan
            row[f'{q}raz'] = np.nan
        else:
            row[f'{q}nsa'] = np.nan
            row[f'{q}lei'] = np.nan
            row[f'{q}est'] = np.nan
            row[f'{q}raz'] = np.nan

        # Extension columns
        n_ext = EXT_COUNTS.get(q, 0)
        if val in ["Não adota.", "Há decisão formal ou plano aprovado para adotá-lo.", "Não se aplica."]:
            # No extensions checked
            for i in range(1, n_ext + 1):
                row[f'{q}ext[{chr(64+i)}]'] = np.nan
        else:
            # Some extensions checked based on profile
            n_checked = 0
            if profile == "very_low":
                n_checked = random.randint(0, max(1, n_ext // 4))
            elif profile == "low":
                n_checked = random.randint(0, max(1, n_ext // 3))
            elif profile == "medium_low":
                n_checked = random.randint(1, max(2, n_ext // 2))
            elif profile == "medium":
                n_checked = random.randint(max(1, n_ext // 3), max(2, n_ext * 2 // 3))
            elif profile == "medium_high":
                n_checked = random.randint(max(2, n_ext // 2), max(3, n_ext * 3 // 4))
            else:
                n_checked = random.randint(max(2, n_ext * 2 // 3), n_ext)

            checked = set(random.sample(range(1, n_ext + 1), min(n_checked, n_ext)))
            for i in range(1, n_ext + 1):
                row[f'{q}ext[{chr(64+i)}]'] = "Sim" if i in checked else np.nan

        row[f'{q}evi'] = np.nan
        row[f'{q}evi[filecount]'] = np.nan

    # Sim/Nao questions
    for q, opts in SIM_NAO_QUESTIONS.items():
        for opt in opts:
            if q == "q2708":
                # Cargos específicos
                if profile in ["very_low", "low"]:
                    val = "Não"
                elif profile in ["medium_low", "medium"]:
                    val = random.choice(["Sim", "Não"])
                else:
                    val = "Sim"
            elif q == "q2804":
                # Práticas de governança nas contratações
                if profile in ["very_low", "low"]:
                    val = random.choices(["Sim", "Não"], weights=[0.2, 0.8])[0]
                elif profile in ["medium_low", "medium"]:
                    val = random.choices(["Sim", "Não"], weights=[0.5, 0.5])[0]
                else:
                    val = random.choices(["Sim", "Não"], weights=[0.8, 0.2])[0]
            elif q == "q2805":
                # Notas técnicas TCE-RJ
                if profile in ["very_low", "low", "medium_low"]:
                    val = random.choices(["Sim", "Não"], weights=[0.3, 0.7])[0]
                else:
                    val = random.choices(["Sim", "Não"], weights=[0.7, 0.3])[0]
            elif q == "q3003":
                # Contratação de IA
                if profile in ["very_low", "low", "medium_low", "medium"]:
                    val = "Não"
                else:
                    val = random.choices(["Sim", "Não"], weights=[0.3, 0.7])[0]
            else:
                val = random.choice(["Sim", "Não"])
            row[f'{q}[{opt}]'] = val

        if q == "q2804":
            row['q2804eviA'] = np.nan
            row['q2804eviA[filecount]'] = np.nan
        else:
            row[f'{q}evi'] = np.nan
            row[f'{q}evi[filecount]'] = np.nan

    # Multi questions
    for q, opts in MULTI_QUESTIONS.items():
        if q == "q3004":
            # Only visible if q3003 has Sim
            q3003_has_sim = any(row.get(f'q3003[{opt}]', "Não") == "Sim" for opt in SIM_NAO_QUESTIONS["q3003"])
            if not q3003_has_sim:
                for opt in opts:
                    row[f'{q}[{opt}]'] = np.nan
            else:
                n_checked = random.randint(1, len(opts))
                checked = set(random.sample(range(len(opts)), n_checked))
                for i, opt in enumerate(opts):
                    row[f'{q}[{opt}]'] = "Sim" if i in checked else np.nan

    # q3006 (long text)
    if row.get('q3001') in ["Adota parcialmente.", "Adota em maior parte ou totalmente."]:
        row['q3006'] = random.choice([
            "Utilizamos IA para análise de dados e atendimento ao cidadão.",
            "A organização desenvolveu chatbots para atendimento virtual.",
            "IA generativa é utilizada para apoio à redação de documentos.",
            "Não há uso significativo de IA na organização.",
            "",
        ])
    else:
        row['q3006'] = np.nan

    # Final fields
    row['qcomentario'] = np.nan
    row['qciencia[SQ001]'] = "Sim"
    row['firstname'] = f"ORG_{row_id:03d}"
    row['lastname'] = f"Respondente {row_id}"
    row['email'] = f"respondente{row_id}@org.gov.br"

    # Ensure all columns exist
    for col in columns:
        if col not in row:
            row[col] = np.nan

    return row


# Generate respondents
n_respondents = 120  # At least 100
profiles = ["very_low"] * 20 + ["low"] * 20 + ["medium_low"] * 20 + ["medium"] * 20 + ["medium_high"] * 20 + ["high"] * 20
random.shuffle(profiles)

new_rows = []
start_id = int(df_template['id'].max()) + 1

for i, profile in enumerate(profiles):
    row = generate_respondent(start_id + i, profile)
    new_rows.append(row)

# Create DataFrame
df_new = pd.DataFrame(new_rows)
df_new = df_new[columns]  # Ensure same column order

# Combine with template (only keep template structure, don't include old rows unless desired)
# Actually, the user said "gere pelo menos mais 100 conjunto de respostas", so just the new ones
df_combined = pd.concat([df_template, df_new], ignore_index=True)

# Save
output_path = '/home/acba/workspace/md2survey/kimi2_dummy.xlsx'
df_combined.to_excel(output_path, index=False)

print(f"Generated {len(df_new)} new respondents")
print(f"Total rows in file: {len(df_combined)}")
print(f"Saved to: {output_path}")
print(f"Shape: {df_combined.shape}")
