# Consolidação da Avaliação de Riscos

## 1. Síntese executiva

Foram analisadas integralmente as avaliações de risco produzidas por DeepSeek, Gemini, GPT e Kimi. Em conjunto, elas cobrem governança de TI, segurança da informação, gestão de serviços, riscos e continuidade, processos de segurança, desenvolvimento, projetos, pessoas, contratações e inteligência artificial. A consolidação não adotou média automática: riscos semanticamente equivalentes foram agrupados, e a probabilidade/impacto consolidados foram definidos por julgamento técnico, considerando materialidade, causalidade, plausibilidade e utilidade para a auditoria.

Os riscos que merecem maior atenção imediata são:

- uso de IA generativa e IA institucional sem governança, controle de dados, avaliação de riscos, validação e supervisão humana;
- controle de acesso frágil, especialmente sem privilégio mínimo e revisão periódica;
- segurança técnica insuficiente em ativos críticos, incluindo vulnerabilidades, logs, malware, backup e testes de recuperação;
- ausência ou fragilidade da função de segurança da informação, da resposta a incidentes e da gestão de continuidade;
- contratações de TI sem crivo técnico, sem requisitos de segurança/LGPD, sem vinculação de pagamento a resultados ou sem aderência ao planejamento;
- gestão de riscos de TI/SI meramente formal, sem identificação em processos críticos, responsável, tratamento ou continuidade correspondente.

Os riscos com maior incerteza são aqueles dependentes de informações quantitativas ou contextuais não presentes nas avaliações, como força de trabalho real (`q0105`), dependência de terceirizados, criticidade dos sistemas, orçamento, histórico de incidentes e materialidade das contratações. Eles devem orientar procedimentos adicionais, mas não devem ser usados isoladamente para concluir pela existência de achado.

Os riscos com maior potencial de impactar os objetivos da auditoria são os que combinam baixa maturidade institucional com efeitos transversais: SI inexistente, IA sem governança, controles técnicos frágeis, riscos/continuidade sem tratamento, e contratações de TI sem governança. Esses pontos afetam diretamente economicidade, eficiência, conformidade, proteção de dados, continuidade dos serviços e capacidade da alta administração de dirigir e supervisionar a TI.

## 2. Metodologia de consolidação

As avaliações foram analisadas em quatro etapas:

1. Extração das linhas de tabela de cada arquivo, preservando fonte, ID, nome, descrição, expressão lógica, probabilidade, impacto, nível de risco e justificativa.
2. Agrupamento semântico por tema e causa de risco, e não apenas por texto ou expressão. Por exemplo, "IA generativa sem controle", "Shadow IT de IA Generativa" e "IA sem regras sobre dados sensíveis em prompts" foram avaliados como riscos correlatos, mas separados quando a causa e o procedimento de auditoria eram distintos.
3. Arbitragem técnica das divergências. Foram considerados: gravidade do efeito, amplitude do controle ausente, probabilidade plausível em órgãos públicos, granularidade da expressão, vínculo causal com o achado e materialidade para auditoria.
4. Consolidação em uma matriz única, eliminando redundâncias, preservando rastreabilidade e registrando necessidade de aprofundamento.

Critérios usados:

- Riscos repetidos foram consolidados quando expressavam a mesma falha de controle ou a mesma consequência auditável.
- Riscos específicos foram mantidos separados quando geravam procedimentos de auditoria distintos. Exemplo: "controle de acesso" e "classificação de informação" são correlatos, mas requerem evidências e testes diferentes.
- Divergências de P/I/R foram resolvidas por julgamento técnico. Ausência total de controle ou combinação de controles críticos ausentes recebeu maior prioridade do que falha parcial isolada.
- Riscos com expressão incompleta, genérica ou abreviada foram aproveitados apenas quando o conceito era tecnicamente válido.
- Lacunas foram registradas quando os modelos deixaram de considerar materialidade, evidência, compensações de controle, histórico de incidentes ou dependências entre domínios.

Limitações:

- As avaliações analisadas se baseiam nas trilhas lógicas do questionário, não em respostas reais de uma organização auditada.
- Algumas expressões originais usam abreviações, `ADOTA(q)` ou reticências, o que reduz a operacionalização direta.
- Há riscos que dependem de `q0105` e de quantitativos, mas os arquivos analisados não trazem dados preenchidos.
- O nível de risco consolidado é uma priorização para planejamento de auditoria, não uma conclusão de achado.

## 3. Avaliação crítica das análises por modelo

### DeepSeek

Pontos fortes:

- Cobertura mais ampla: 98 trilhas, incluindo riscos estruturais, operacionais, contratuais, pessoas, IA e cruzamentos entre domínios.
- Boa granularidade em controles específicos, como backup sem teste, vulnerabilidades, logs, causa raiz, NMS, PNCP e dependência de terceirizados.
- Inclui exemplos concretos de materialização, úteis para desenhar procedimentos de auditoria.

Fragilidades:

- Alta redundância semântica. Muitos riscos são subitens de riscos maiores e poderiam ser agregados.
- Mistura riscos críticos com riscos de baixa materialidade em uma mesma lógica, o que pode dispersar foco da equipe.
- Algumas trilhas cruzadas são interessantes, mas dependem de premissas contextuais não verificadas. Exemplo: descentralização/hibridismo de TI não é necessariamente negativo se houver governança eficaz.
- Algumas avaliações parecem subestimar riscos estruturais ao atribuir probabilidade baixa demais, ou superestimar impacto em controles isolados.

Síntese crítica: é a fonte mais rica para mineração de riscos, mas exige forte curadoria para evitar matriz excessivamente longa e redundante.

### Gemini

Pontos fortes:

- Sintético e orientado a riscos de alta materialidade.
- Boa capacidade de agrupar riscos correlatos em achados mais executivos.
- Identificou temas centrais: SI básica, IA generativa, acessos, continuidade, contratação órfã, NMS e governança pró-forma.

Fragilidades:

- Expressões lógicas usam reticências e abreviações, o que prejudica a rastreabilidade operacional.
- Algumas formulações são amplas demais, combinando controles distintos em um único achado. Isso pode dificultar teste de auditoria e responsabilização.
- Tendência a linguagem alarmista em alguns riscos, com menor nuance entre ausência total e falha parcial.
- Cobertura limitada: 17 trilhas, deixando lacunas relevantes em riscos, classificação da informação, ativos, projetos, pessoas e transparência.

Síntese crítica: útil para visão executiva e priorização, mas insuficiente como matriz completa de planejamento.

### GPT

Pontos fortes:

- Boa estrutura metodológica, com 52 trilhas e justificativas relativamente consistentes.
- Consolida riscos por famílias relevantes, preservando expressões lógicas completas na maior parte dos casos.
- Melhor equilíbrio entre visão agregada e trilhas cruzadas, especialmente em IA, SI, riscos, continuidade e contratações.

Fragilidades:

- Algumas trilhas amplas recebem risco 25 mesmo quando a condição pode representar apenas lacuna parcial, o que pode superestimar situações intermediárias.
- Certas expressões misturam ausência de adoção com detalhamento ausente; isso é útil para triagem, mas exige cuidado para não interpretar `None` de detalhamento como falso.
- Algumas trilhas cruzadas foram incorporadas a partir do DeepSeek e poderiam ser mais explicitamente diferenciadas entre causa, condição e consequência.

Síntese crítica: é a base mais equilibrada para consolidação, mas precisou de ajuste de materialidade e separação entre falhas totais e parciais.

### Kimi

Pontos fortes:

- Boa formulação técnica de riscos específicos e auditáveis.
- Forte foco em controles críticos: gestão de riscos formalizada, continuidade testada, revisão de acessos, segurança no ciclo de software, IA generativa, CMDB, projetos de alta materialidade e incidentes.
- Expressões geralmente mais precisas que as do Gemini.

Fragilidades:

- Tendência a classificar como 25 alguns controles específicos, como formalização de gestão de riscos, que isoladamente nem sempre justificam probabilidade e impacto máximos.
- Algumas trilhas pressupõem materialidade elevada sem distinguir porte da organização, criticidade dos sistemas ou compensações existentes.
- A análise é menos abrangente que DeepSeek e GPT, embora mais focada que Gemini.

Síntese crítica: boa fonte para identificar riscos técnicos prioritários, mas suas notas de probabilidade/impacto precisaram ser calibradas em alguns casos.

## 4. Matriz consolidada de riscos

| ID | Risco consolidado | Achado/tema relacionado | Fontes consideradas | Express?o l?gica consolidada | Probabilidade consolidada | Impacto consolidado | Nível de risco consolidado | Prioridade de auditoria | Necessidade de aprofundamento | Grau de confiança da consolidação | Justificativa da consolidação | Observações |
|---|---|---|---|---|---:|---:|---:|---|---|---|---|---|
| C01 | IA generativa sem mapeamento, regras para prompts ou controle técnico | Inteligência artificial, proteção de dados, shadow IT | DeepSeek T75, T70; Gemini T02; GPT T02, T50; Kimi TR005, TR013 | `q3005 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q3005 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q3005extA or !q3005extB or !q3005extC or !q3005extD)) or (q3002 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and !q3002extB)` | 5 | 5 | 25 | Crítica | Alta: verificar inventário de ferramentas, logs/proxy, normas, bloqueios, termos de uso e orientação aos servidores | Alto | Há convergência forte entre os modelos quanto à probabilidade elevada de uso descentralizado de IA generativa e impacto relevante sobre sigilo, LGPD e reputação. A posição consolidada eleva impacto a 5 porque o uso de prompts com dados reais pode causar exposição imediata e de difícil reversão. | Risco deve ser tratado como prioritário mesmo quando a organização ainda não reconhece uso institucional de IA. |
| C02 | Controle de acesso sem privilégio mínimo, revisão periódica ou política formal | Segurança da informação, IAM, proteção de dados | DeepSeek T42, T43, T82; Gemini T03; GPT T05; Kimi TR003 | `q2502 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2502 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2502extB or !q2502extD or !q2502extE))` | 5 | 5 | 25 | Crítica | Alta: testar amostras de concessão, revisão, desligamento, perfis privilegiados e segregação de funções | Alto | A ausência de revisão e privilégio mínimo é vetor recorrente de fraude, vazamento e movimentação lateral. Os modelos convergem no impacto alto; a probabilidade consolidada foi mantida em 5 pela recorrência de acúmulo de privilégios e contas não revisadas. | Deve ser testado com dados reais de usuários, não apenas por entrevista. |
| C03 | Segurança técnica insuficiente em ativos críticos | Vulnerabilidades, logs, malware, backup, perímetro e testes | DeepSeek T46, T47, T48, T49; Gemini T09; GPT T03, T44; Kimi TR010 | `q2504 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2504 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2504extC or !q2504extD or !q2504extE or !q2504extG or !q2504extI or !q2504extJ or !q2504extK))` | 5 | 5 | 25 | Crítica | Alta: verificar inventário, hardening, varreduras, logs, EDR/antimalware, backups e testes de restauração | Alto | A falta combinada de controles técnicos amplia tanto a chance de incidente quanto o dano. A avaliação consolidada considera o conjunto dos controles, não apenas um item isolado, justificando nível máximo. | Quando apenas um controle específico faltar, a classificação deve ser recalibrada no achado concreto. |
| C04 | IA institucional ou em produção sem diretrizes, avaliação de riscos, validação ou supervisão humana | Governança de IA, ética, LGPD, automação decisória | DeepSeek T69, T71, T72, T73, T78, T83; Gemini T05, T16; GPT T01, T32, T49, T51, T52; Kimi TR027 | `q3001 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (q3002 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or !q3002extA or !q3002extD or !q3002extE or !q3002extF)` | 4 | 5 | 20 | Crítica | Alta: levantar casos de uso, modelos em produção, contratos, dados tratados, critérios de decisão, validações e revisão humana | Alto | A divergência principal foi entre GPT (mais severo) e Kimi/Gemini (mais moderados em alguns itens). A posição consolidada adota impacto 5, mas probabilidade 4, pois a existência de IA em produção depende do órgão avaliado. | Pode gerar achados de alto impacto jurídico quando a IA afetar direitos de cidadãos. |
| C05 | Função de segurança da informação inexistente ou sem governança efetiva | Estrutura de SI, política, gestor, comitê, ETIR | DeepSeek T84, T02, T31, T79, T97; Gemini T01; GPT T07, T17, T18, T34, T42; Kimi TR008, TR016, TR029, TR032 | `q0104 == 'E' or q2401 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or q2403 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or q2404 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte']` | 4 | 5 | 20 | Crítica | Alta: verificar organograma, portarias, política, comitê, gestor, equipe, responsabilidades e recursos | Alto | Gemini superestima todas as combinações como 25, enquanto DeepSeek e GPT distinguem ausência total e fragilidade. A consolidação mantém impacto máximo, mas probabilidade 4 para refletir que ausência total não é universal. | Se `q0105` indicar zero profissionais de SI, elevar prioridade de procedimentos. |
| C06 | Resposta a incidentes inexistente, reativa ou sem aprendizagem | Gestão de incidentes, ETIR, comunicação, causa raiz | DeepSeek T23, T24, T38, T80; Gemini T17; GPT T04, T10; Kimi TR012, TR017, TR024 | `q2204 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2204 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2204extA or !q2204extD or !q2204extE or !q2204extF)) or (q2404 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and !q2404extG)` | 4 | 5 | 20 | Crítica | Alta: examinar procedimentos, registros de incidentes, escalamento, notificação, comunicação e análise pós-incidente | Alto | Gemini avaliou causa raiz isolada como risco 8, mas GPT tratou ausência estrutural como 25. A consolidação separa o escopo amplo de resposta a incidentes e fixa 20: impacto é máximo, mas a probabilidade depende da maturidade operacional. | Avaliar incidentes reais recentes é essencial para confirmar efetividade. |
| C07 | Gestão de riscos de TI/SI meramente formal ou sem tratamento | Riscos de TI, riscos de SI, responsável, plano de tratamento | DeepSeek T25, T26, T27, T30, T79, T81; Gemini T13; GPT T07, T08, T39, T40; Kimi TR001, TR008, TR021 | `q2301 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2301 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2301extA or !q2301extB or !q2301extC)) or q2302 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2302 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2302extB or !q2302extC or !q2302extD))` | 4 | 5 | 20 | Crítica | Alta: revisar matriz de riscos, vínculo com processos críticos, planos de tratamento, responsáveis, prazos e monitoramento | Alto | Kimi atribuiu 25 à falta de formalização; isso foi considerado superestimado quando isolado. O risco consolidado foca identificação e tratamento, que têm vínculo causal mais forte com eventos críticos, justificando 20. | Formalização é evidência importante, mas não substitui tratamento efetivo. |
| C08 | Continuidade de serviços de TI sem BIA, testes ou revisão periódica | Continuidade, resiliência, recuperação de desastres | DeepSeek T28, T29, T81; Gemini T04; GPT T06, T41; Kimi TR002 | `q2303 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2303 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2303extB or !q2303extC or !q2303extD))` | 4 | 5 | 20 | Crítica | Alta: verificar PCN/DRP, BIA/AIN, RTO/RPO, resultados de testes e evidências de revisão | Alto | Kimi classificou como 25; DeepSeek variou entre 12 e 15 em itens isolados. A consolidação adota 20 porque o impacto é máximo, mas a probabilidade 5 só se justificaria com histórico de indisponibilidade ou ausência completa de plano. | Plano nunca testado deve ser tratado como evidência forte de fragilidade. |
| C09 | Contratações de TI sem governança técnica, planejamento, NMS ou requisitos de SI/LGPD | Contratações de TI, PCA, planejamento, fiscalização contratual | DeepSeek T61, T62, T63, T65, T66, T89; Gemini T06, T07, T08; GPT T11, T12, T47, T48; Kimi TR020, TR023 | `q2801 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or q2804.A == 'nao' or q2804.B == 'nao' or q2804.C == 'nao' or q2804.D == 'nao' or q2804.E == 'nao'` | 4 | 5 | 20 | Crítica | Alta: testar processos, ETP/TR, PCA, aprovação técnica, NMS, fiscalização, requisitos de segurança e proteção de dados | Alto | Há forte convergência de que contratações sem crivo técnico e requisitos de segurança geram desperdício e exposição jurídica. A consolidação mantém impacto 5 por envolver recursos públicos, continuidade e LGPD. | Separar achados por etapa: planejamento, seleção, gestão contratual e transparência. |
| C10 | Desenvolvimento ou aquisição de software sem segurança desde a concepção | Processo de software, segurança, qualidade, requisitos | DeepSeek T51, T52, T53, T95; GPT T23, T45; Kimi TR004, TR026 | `q2601 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2601 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2601extA or !q2601extB or !q2601extC or !q2601extE or !q2601extF))` | 4 | 5 | 20 | Alta | Alta: verificar SDLC, requisitos de segurança, testes, acessibilidade, participação da área de negócio e aceite | Alto | Kimi avaliou ausência de segurança no ciclo de vida como 25; a consolidação adota 20, pois o impacto é alto, mas a probabilidade máxima depende da existência e criticidade dos sistemas desenvolvidos. | Acessibilidade e direitos de uso são subtemas relevantes, mas secundários frente à segurança. |
| C11 | Classificação e tratamento de informações insuficientes, especialmente dados pessoais | LGPD, LAI, classificação, rotulagem e tratamento de dados | DeepSeek T44, T45; GPT T21, T43; Kimi TR009 | `q2503 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2503 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2503extA or !q2503extB or !q2503extC or !q2503extD or !q2503extE or !q2503extF))` | 4 | 5 | 20 | Alta | Alta: verificar inventário de dados, hipóteses legais, rotulagem, publicação de tratamento, controles e normas | Médio | Há convergência sobre impacto alto, mas divergência sobre probabilidade: DeepSeek considerou identificação de dados pessoais menos provável como omissão total. A consolidação usa probabilidade 4 por ser comum haver tratamento parcial e descentralizado. | Exige cruzamento com encarregado/DPO, bases de dados e políticas de privacidade. |
| C12 | Estrutura formal de TI inexistente, mal posicionada ou sem atribuições definidas | Estrutura organizacional de TI, governança básica | DeepSeek T01, T03, T04, T92; GPT T33; Kimi TR006, TR031 | `q0101 == 'F' or q0102 in ['D','E'] or q0103.G == 1` | 4 | 5 | 20 | Alta | Média: verificar organograma, normativos, atribuições, subordinação, papéis e aderência entre norma e prática | Médio | A ausência total de TI é menos provável, mas quando ocorre tem impacto muito alto. A consolidação amplia a formulação para incluir informalidade e atribuições indefinidas, tornando o risco mais auditável. | Em órgãos pequenos, considerar arranjos compartilhados ou centralizados externos antes de concluir fragilidade. |
| C13 | Planejamento de TI sem plano vigente, alinhamento, orçamento ou acompanhamento | Planejamento de TI, PDTI/PEDTIC, orçamento, PCA | DeepSeek T12, T13, T14, T15, T16, T85, T86; Gemini T06, T12; GPT T13, T14, T37, T38; Kimi TR014, TR022, TR034 | `q2101 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or q2102 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2102 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2102extC or !q2102extD or !q2102extE))` | 4 | 4 | 16 | Alta | Alta: verificar vigência, aprovação, publicação, vínculo com orçamento/PCA, participação das áreas e monitoramento | Alto | Risco recorrente em todos os modelos. Impacto consolidado 4 porque afeta eficiência e alinhamento, mas não necessariamente causa dano imediato se houver controles compensatórios. | Pode subir para impacto 5 quando contratações relevantes estiverem fora do plano. |
| C14 | Governança de TI pró-forma, sem comitê atuante, indicadores ou monitoramento | Governança de TI, comitê, metas, indicadores, alta administração | DeepSeek T05, T06, T07, T08, T09, T96; Gemini T11; GPT T15, T16, T35, T36; Kimi TR025, TR033 | `q1001 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q1001 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q1001extE or !q1001extF or !q1001extH)) or q1002 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or !q1002extC or !q1002extD` | 4 | 4 | 16 | Alta | Média: verificar atas, indicadores, metas, relatórios, deliberações e evidência de atuação da alta administração | Alto | A consolidação reconhece que governança sem monitoramento é falha relevante, mas não adota impacto 5 automaticamente porque o efeito depende da criticidade das decisões de TI afetadas. | Comitê criado sem reuniões ou deliberações é forte evidência de governança formalista. |
| C15 | Gestão de mudanças e configuração sem base confiável, testes ou rastreabilidade | ITSM, mudanças, CMDB, ativos, rastreabilidade | DeepSeek T19, T20, T21, T76, T88; Gemini T15; GPT T09, T19; Kimi TR007, TR015 | `q2202 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2202 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2202extC or !q2202extD or !q2202extE or !q2202extF)) or q2203 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2203 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2203extA or !q2203extB))` | 4 | 4 | 16 | Alta | Alta: amostrar mudanças, aprovações, testes, comunicação, ativos afetados, CMDB e pós-implementação | Alto | DeepSeek e Kimi trouxeram componentes específicos; GPT agregou de forma ampla. A consolidação une mudanças e configuração porque a ausência de CMDB reduz a qualidade da análise de impacto das mudanças. | Se mudanças afetarem sistemas críticos, impacto pode subir para 5. |
| C16 | Gestão de projetos de TI sem riscos, escopo, custos, prazos ou portfólio | Projetos de TI, materialidade, governança de projetos | DeepSeek T54, T55; GPT T24; Kimi TR011 | `q2602 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2602 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2602extA or !q2602extB or !q2602extC or !q2602extD))` | 4 | 4 | 16 | Alta | Média: verificar portfólio, projetos críticos, cronograma, orçamento, riscos, mudanças de escopo e benefícios | Médio | Kimi elevou probabilidade para 5 em projetos de alta materialidade; a consolidação usa 4 por depender do volume e criticidade dos projetos. Impacto 4 é adequado para atrasos, custos e falhas de entrega. | Procedimentos devem focar projetos de maior materialidade. |
| C17 | Força de trabalho, competências e capacitação insuficientes em TI/SI | Pessoas, competências, dimensionamento, dependência de terceiros | DeepSeek T56, T57, T58, T60, T77, T84, T90, T98; Gemini T10; GPT T27, T28, T29, T31, T46; Kimi TR019, TR028 | `q2708.A == 'nao' and q2708.B == 'nao' and q2708.C == 'nao' and q2708.D == 'nao' or q2705 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or q2706 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q0105.TI.terceirizados > (3 * q0105.TI.efetivos) and q0105.TI.efetivos < 3)` | 4 | 4 | 16 | Alta | Alta: analisar `q0105`, perfis, cargos, contratos, capacitações, lacunas e tratamento | Médio | Os modelos convergem na relevância, mas variam entre impacto 3 e 5. A consolidação adota 16 porque a materialidade depende do porte, terceirização e criticidade dos serviços sustentados. | Zero profissionais de SI ou dependência extrema de terceiros deve ser destacado como subachado crítico. |
| C18 | Gestão de ativos de informação sem inventário, responsáveis ou integração com controles | Ativos de informação, accountability, controles de proteção | DeepSeek T40, T41, T82; GPT T22; Kimi TR018 | `q2501 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2501 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2501extA or !q2501extB or !q2501extC or !q2501extD or !q2501extF))` | 4 | 4 | 16 | Alta | Média: verificar inventário de ativos, responsáveis, classificação, controles aplicados e integração com acesso/continuidade | Médio | Risco importante, mas normalmente se materializa por meio de outros riscos, como acesso indevido, classificação deficiente ou continuidade. Por isso impacto consolidado 4, não 5. | Pode ser testado em conjunto com LGPD e controle de acesso. |
| C19 | Transparência e planejamento anual de contratações insuficientes | PNCP, PCA, transparência ativa, controle social | DeepSeek T67, T68; GPT T25, T26; Kimi TR030 | `q2802 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or !q2802extE or q2803 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2803 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2803extA or !q2803extB or !q2803extC or !q2803extD or !q2803extE or !q2803extF or !q2803extG))` | 4 | 4 | 16 | Alta | Média: verificar PCA, PNCP, publicações de ETP/TR/editais/contratos/aditivos e exceções de sigilo | Alto | Os modelos tratam PNCP às vezes como risco moderado, mas a consolidação mantém 16 por envolver conformidade legal e transparência de contratações públicas. | Não confundir falha de publicação isolada com ausência sistêmica de transparência. |
| C20 | Catálogo de serviços e ANS inexistentes ou não monitorados | Gestão de serviços de TI, níveis de serviço, atendimento | DeepSeek T17, T18; GPT T20; Kimi TR035 | `q2201 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2201 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2201extA or !q2201extB or !q2201extC or !q2201extD or !q2201extE))` | 4 | 3 | 12 | Média | Média: verificar catálogo, ANS, metas, acessibilidade aos usuários e monitoramento de cumprimento | Alto | Risco relevante para qualidade de serviço, mas impacto normalmente menor que incidentes, continuidade ou segurança. A consolidação adota 12, salvo se envolver serviços críticos. | Pode apoiar achados sobre satisfação e desempenho de TI. |
| C21 | Auditoria interna sem cobertura de TI e segurança da informação | Terceira linha, governança, assurance | DeepSeek T10; Gemini T14; GPT T30 | `q1003 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q1003 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q1003extA or !q1003extB))` | 3 | 4 | 12 | Média | Média: revisar PAINT, relatórios, competências da auditoria interna e comunicação à alta administração | Alto | Há convergência entre três fontes. Impacto 4 porque a ausência de auditoria não causa diretamente o incidente, mas reduz detecção independente e supervisão. | Pode orientar entrevistas com auditoria interna e alta administração. |
| C22 | Capacitação e conscientização em segurança sem programa permanente | Cultura de segurança, pessoas, phishing, uso aceitável | DeepSeek T37, T50, T90; GPT T31; Kimi TR028 | `q2505 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2505 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2505extA or !q2505extC or !q2505extD))` | 3 | 4 | 12 | Média | Média: verificar plano, campanhas, registros, público-alvo, periodicidade e avaliações | Médio | Kimi atribui probabilidade 5 e impacto 3; GPT usa 3/4. A consolidação adota 3/4 por reconhecer impacto relevante, mas dependente de outros controles técnicos e organizacionais. | Pode ser testado com evidências de campanhas e participação. |
| C23 | Perfis e escolha de gestores de TI/SI frágeis | Governança de pessoas, integridade, liderança técnica | DeepSeek T59, T87; GPT T29 | `q2701 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q2701 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2701extA or !q2701extC)) or q2704 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or !q2704extA or !q2704extB` | 3 | 4 | 12 | Média | Média: verificar perfis, critérios de seleção, impedimentos, currículos e transparência | Médio | Aparece em menos fontes, mas tem vínculo relevante com capacidade de governança e integridade. Mantido como risco consolidado secundário de planejamento. | Não deve competir com riscos técnicos críticos, mas pode explicar causas estruturais. |
| C24 | Processo de software sem acessibilidade, usabilidade ou direitos de uso bem definidos | Qualidade de software, inclusão digital, propriedade intelectual | DeepSeek T52, T53; GPT T23; Kimi TR026 | `q2601 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q2601extC or !q2601extD)` | 3 | 3 | 9 | Média | Baixa a média: verificar quando houver desenvolvimento/aquisição de sistemas voltados ao cidadão | Médio | Risco tecnicamente válido, mas de menor criticidade que segurança no ciclo de vida. A consolidação reduz prioridade para evitar inflar riscos de qualidade como se fossem riscos cibernéticos críticos. | Pode ser relevante em serviços digitais de alto uso público. |
| C25 | TI distante da alta administração e com baixa capacidade de influência estratégica | Posicionamento hierárquico, governança institucional | DeepSeek T04; Kimi TR031 | `q0102 in ['C','D'] and (q1001 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or !q1001extE or !q1001extH)` | 3 | 3 | 9 | Média | Baixa a média: verificar organograma e participação em decisões estratégicas | Médio | Risco pouco abordado e dependente de contexto. O posicionamento hierárquico não é achado por si só, mas pode explicar baixa governança, planejamento fraco e contratações desalinhadas. | Tratar como causa contextual, não como achado autônomo salvo evidência de efeito. |
| C26 | Metas de simplificação e digitalização de serviços insuficientes | Serviços públicos digitais, experiência do usuário | DeepSeek T11 | `q1004 in ['N?o adota','H? decis?o formal ou plano aprovado para adot?-lo','Adota em menor parte'] or (q1004 in ['Adota parcialmente','Adota em maior parte ou totalmente'] and (!q1004extA or !q1004extC or !q1004extG))` | 2 | 3 | 6 | Baixa | Baixa: aprofundar apenas se o escopo incluir transformação digital e atendimento ao cidadão | Baixo | Apareceu apenas no DeepSeek e tem materialidade menor frente aos riscos de segurança, continuidade, contratações e governança. Mantido como lacuna secundária. | Não deve orientar o escopo principal salvo diretriz específica da fiscalização. |

## 5. Análise crítica das divergências

| Caso | Entendimentos conflitantes | Posição consolidada adotada | Justificativa técnica |
|---|---|---|---|---|
| IA generativa | GPT e Kimi tratam como risco máximo em algumas trilhas; DeepSeek/Gemini variam entre 16 e 20. | C01 com P5, I5, risco 25. | A facilidade de acesso e o potencial de exposição de dados em prompts justificam prioridade máxima. O risco é plausível mesmo sem contratação formal, porque decorre de uso difuso por servidores. |
| IA institucional em produção | GPT tende a 25; DeepSeek e Kimi avaliam subcontroles como 12 a 15; Gemini usa 16 e 10 em supervisão. | C04 com P4, I5, risco 20. | O impacto é máximo quando há decisão ou serviço apoiado por IA, mas a probabilidade depende de a organização realmente ter IA em produção e de sua materialidade. |
| Continuidade | Kimi atribui 25 à falta de testes; GPT/Gemini tratam o conjunto como 20; DeepSeek avalia BIA/teste isoladamente como 12 a 15. | C08 com P4, I5, risco 20. | Testes e BIA são críticos, mas probabilidade 5 só é defensável com histórico de indisponibilidade ou ausência completa de plano. |
| Controle de acesso | GPT e Kimi chegam a 25; Gemini usa 20; DeepSeek avalia subcomponentes como 9 a 12. | C02 com P5, I5, risco 25. | A combinação de privilégio mínimo ausente, revisão inexistente e política frágil é uma das maiores causas de incidentes e fraudes. A consolidação considera o conjunto de falhas, não um subitem isolado. |
| Gestão de riscos | Kimi classificou formalização como 25; DeepSeek e GPT variaram conforme identificação/tratamento/responsável. | C07 com P4, I5, risco 20. | Formalização isolada não deve receber risco máximo. A consolidação foca a ausência de identificação em processos críticos, responsável e plano de tratamento, que têm causalidade mais forte. |
| Incidentes | GPT elevou a ausência de resposta estruturada a 25; Gemini classificou análise de causa raiz isolada como 8. | C06 com P4, I5, risco 20. | A divergência decorre do escopo. Causa raiz isolada é subcontrole; ausência de processo, escalamento e comunicação é risco crítico. |
| Contratações de TI | DeepSeek avaliou NMS e LGPD como 12; GPT tratou o conjunto como 20; Gemini focou crivo técnico e body shop com 16. | C09 com P4, I5, risco 20. | A falha combinada em planejamento, crivo técnico, NMS e LGPD afeta recursos públicos, conformidade e continuidade. O conjunto merece prioridade crítica. |
| Força de trabalho | Gemini atribui alta probabilidade e impacto 3; GPT/DeepSeek distinguem cargos, lacunas e dependência de terceiros. | C17 com P4, I4, risco 16. | O risco é relevante, mas sua criticidade depende do porte, quantitativo real e grau de terceirização. Deve ser aprofundado com `q0105`. |
| Transparência/PNCP | DeepSeek tende a moderado; GPT considera mais amplo; Kimi usa 12 para PCA não divulgado. | C19 com P4, I4, risco 16. | Transparência de contratações é tema legal e de controle social. Falhas sistêmicas merecem alta prioridade, mas falha isolada de publicação deve ser calibrada. |

## 6. Riscos subestimados, superestimados ou mal formulados

| Classificação | Fonte/risco | Avaliação crítica | Ajuste proposto na consolidação |
|---|---|---|---|---|
| Superestimado | Kimi TR001, gestão de riscos sem formalização como P5/I5 | A falta de formalização é grave, mas isoladamente não equivale à ausência de identificação ou tratamento dos riscos. | Consolidado em C07 com foco em identificação, responsável e tratamento, P4/I5. |
| Superestimado | GPT T03, T04, T05 quando qualquer lacuna parcial dispara risco 25 | As trilhas são úteis, mas podem superestimar organizações que adotam controles principais e deixam lacunas pontuais. | Mantido risco máximo apenas para conjuntos de controles críticos em C02 e C03. |
| Subestimado | DeepSeek T44, classificação sem identificação de dados pessoais com risco 10 | A materialização pode envolver LGPD e dados sensíveis, com impacto institucional alto. | Consolidado em C11 com P4/I5. |
| Subestimado | Gemini T17, incidente sem causa raiz com risco 8 | A nota é adequada para causa raiz isolada, mas não para fragilidade ampla de resposta a incidentes. | C06 diferencia processo amplo de subcontrole específico. |
| Mal formulado | Gemini expressões com reticências e abreviações | Expressões como `['Não adota', 'Há decisão...']` são úteis para leitura, mas não são executáveis nem plenamente rastreáveis. | Conceitos aproveitados; expressões não foram copiadas como fonte operacional. |
| Mal formulado | Riscos que usam descentralização/hibridismo de TI como negativo em si | TI descentralizada ou híbrida não é necessariamente achado se houver governança, padrões e coordenação. | Tratado apenas como contexto em C25, não como risco crítico autônomo. |
| Genérico | "Governança de TI pró-forma" sem evidência específica | Formulação executiva útil, mas precisa de evidências: atas, indicadores, metas, relatórios e deliberações. | Consolidado em C14 com procedimentos de aprofundamento. |
| Duplicado semanticamente | Backup sem teste, segurança técnica insuficiente, falsa sensação de segurança | Mesma família de controles técnicos de segurança, com backup como subcontrole crítico. | Consolidado em C03, com atenção específica a backup. |
| Duplicado semanticamente | IA sem diretrizes, IA contratada sem governança, IA em produção sem supervisão | Riscos correlatos, mas nem todos são idênticos. | Separados em C01 (IA generativa/shadow) e C04 (IA institucional/produção). |
| Baixa materialidade relativa | Metas de simplificação sem digitalização | Relevante para transformação digital, mas secundário frente a segurança, continuidade, contratações e IA. | Mantido em C26 com prioridade baixa. |

## 7. Lacunas identificadas

1. As avaliações não incorporam dados reais de respostas, evidências anexadas ou qualidade documental. A matriz indica trilhas, não achados confirmados.
2. A materialidade financeira de contratações, projetos e serviços não foi considerada. Um mesmo risco pode ser secundário em contrato pequeno e crítico em contrato de sustentação essencial.
3. A criticidade dos sistemas suportados pela TI não foi diferenciada. Sistemas finalísticos, arrecadação, saúde, folha ou processo eletrônico deveriam ter peso maior.
4. O histórico de incidentes, indisponibilidades, glosas, sanções LGPD ou auditorias anteriores não foi utilizado, embora seja decisivo para probabilidade.
5. A dependência de terceiros e a capacidade interna aparecem, mas exigem análise quantitativa com `q0105` e contratos de terceirização.
6. Poucas avaliações tratam de controles compensatórios. Por exemplo, ausência de área formal de SI pode ser parcialmente mitigada por serviço compartilhado, órgão central ou contrato especializado, desde que comprovado.
7. O tratamento de `Não se aplica` não foi discutido com rigor. Essa opção deve ser validada criticamente para evitar uso indevido como fuga de controles.
8. Faltou amarração direta com critérios normativos específicos, como LGPD, Lei 14.133/2021, PNCP, normativos de segurança, boas práticas de continuidade e frameworks de gestão de serviços.
9. Riscos de dados em nuvem, transferência internacional, logs de IA, retenção de prompts e treinamento de modelos por fornecedores foram apenas parcialmente capturados.
10. Poucas trilhas tratam de segregação de funções em contratações, fiscalização contratual e administração de acessos privilegiados de fornecedores.

## 8. Opinião final sobre os riscos

O conjunto de avaliações aponta um perfil de risco dominado por quatro frentes: segurança da informação, continuidade/resiliência, contratações de TI e inteligência artificial. Esses temas têm maior potencial de impacto institucional porque combinam exposição legal, proteção de dados, continuidade de serviços públicos, gasto público e tomada de decisão automatizada.

Devem ser priorizados na matriz de planejamento:

- IA generativa e IA institucional sem governança, com foco em dados pessoais/sigilosos, prompts, validação e supervisão humana;
- controle de acesso, privilégios e revisão de contas;
- segurança técnica de ativos críticos, incluindo vulnerabilidades, logs, antimalware, backup e restauração;
- resposta a incidentes e continuidade testada;
- gestão de riscos de TI/SI com tratamento e responsáveis;
- contratações de TI com crivo técnico, NMS, requisitos de SI/LGPD e aderência ao planejamento;
- estrutura e capacidade de SI/TI, especialmente quando houver zero profissionais, dependência excessiva de terceiros ou ausência de atribuições formais.

Exigem aprofundamento adicional:

- riscos baseados em quantitativos de pessoal (`q0105`);
- riscos de planejamento/contratações que dependem de materialidade financeira;
- riscos de IA que dependem da existência real de modelos em produção ou contratação de serviços;
- riscos de continuidade que dependem da criticidade dos serviços e resultados de testes;
- riscos de transparência/PNCP, distinguindo falhas pontuais de omissão sistêmica.

Podem ser tratados como secundários no planejamento inicial, salvo orientação específica do escopo:

- metas de simplificação e digitalização de serviços;
- acessibilidade/usabilidade de software, quando não houver sistema finalístico relevante;
- posicionamento hierárquico da TI, quando houver evidência de governança compensatória;
- falhas pontuais de comunicação de política sem indícios de descumprimento relevante.

Os pontos que devem orientar a estratégia de fiscalização são:

- selecionar amostras de sistemas e contratos críticos, não apenas documentos declaratórios;
- testar a efetividade de controles, especialmente acessos, backup, incidentes e mudanças;
- cruzar respostas do questionário com evidências anexadas, normativos, atas, registros e dados extraídos de sistemas;
- priorizar trilhas que combinem ausência de controle com alta materialidade ou exposição de dados pessoais;
- tratar IA e contratações como temas transversais, pois dependem simultaneamente de governança, segurança, dados, pessoas e fiscalização contratual.

## 9. Recomendações para uso pela equipe de auditoria

1. Use a matriz consolidada como insumo de planejamento, não como conclusão automática. Cada risco deve ser confirmado por evidência.
2. Para cada organização auditada, reordene os riscos considerando materialidade, criticidade dos sistemas, volume de dados pessoais, orçamento de TI e histórico de incidentes.
3. Priorize procedimentos substantivos para riscos C01 a C12. Eles concentram maior impacto institucional e maior convergência entre avaliações.
4. Em IA, combine entrevistas, análise documental, contratos, logs/proxy e inventário de ferramentas. Perguntas declaratórias tendem a subcapturar shadow AI.
5. Em segurança técnica, não aceite apenas norma ou política. Verifique evidências operacionais: relatórios de vulnerabilidade, logs, backup restaurado, inventário e tickets.
6. Em continuidade, peça evidências de teste e revisão. Plano sem teste deve ser considerado controle de baixa confiabilidade.
7. Em contratações, teste a cadeia completa: PCA, demanda, ETP, TR, aprovação técnica, requisitos de SI/LGPD, NMS, fiscalização e publicação no PNCP.
8. Em riscos e governança, verifique se há dono, prazo, tratamento e monitoramento. Matriz de riscos genérica sem plano de tratamento não deve ser considerada suficiente.
9. Use as divergências registradas para orientar discussões internas de julgamento profissional, especialmente quando uma trilha específica tiver sido classificada de forma muito diferente pelos modelos.
10. Documente limitações e incertezas no papel de trabalho, principalmente quando a resposta do questionário permitir detalhamentos `None` ou quando a expressão lógica depender de interpretação de adoção parcial.
