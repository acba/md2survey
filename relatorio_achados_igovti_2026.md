# Relatório de Análise: Mapeamento de Achados Potenciais no iGovTI 2026

## 1. Introdução

O presente relatório tem por objetivo comparar os possíveis achados levantados para a fiscalização TCE-RJ nº 18/2026 com as questões e trilhas lógicas do questionário iGovTI 2026, bem como com a matriz consolidada de avaliação de riscos. Busca-se identificar a cobertura do instrumento de coleta de dados (questionário) em relação aos achados esperados e avaliar a necessidade de adicionar ou modificar questões de auditoria.

## 2. Mapeamento dos Achados no Questionário iGovTI 2026

### 2.1 Ausência de normatização da área de TIC

**Achado:** Não há área de TI formalmente instituída no organograma da organização.

**Cobertura no iGovTI 2026:**
- **q0101** (opção F — Inexistente/Informal): identifica diretamente a ausência de área de TI formal.
- **q0102** (opção E — não há área de TI formalmente instituída): confirma o posicionamento hierárquico inexistente.
- **q0103** (opção G — não há atribuições ou competências da área de TI formalmente definidas): verifica a formalização das competências.

**Avaliação:** O questionário cobre adequadamente este achado por meio das questões de estrutura organizacional (grupo g0100). As trilhas lógicas da matriz consolidada (C12 — Estrutura formal de TI inexistente) também o capturam.

---

### 2.2 Área de TIC sem atribuições de planejamento, coordenação, gestão e controle

**Achado:** A área de TI possui atribuições limitadas ou não possui competências formalizadas para planejamento, coordenação e gestão.

**Cobertura no iGovTI 2026:**
- **q0103** (opções A a F): verifica se as atribuições foram formalizadas (infraestrutura, sistemas, segurança, governança/planejamento, contratos, dados/IA).
- **q1001** (detalhamento C, D, E): verifica se a organização define papéis, responsabilidades e comitê de TI.

**Avaliação:** O questionário captura a existência formal das atribuições, mas não avalia diretamente a efetividade do exercício dessas competências. A matriz consolidada (C12, C14, C25) trata da estrutura e governança, mas a análise de riscos aponta que "governança sem monitoramento é falha relevante".

---

### 2.3 Posicionamento organizacional inadequado da área de TIC

**Achado:** A área de TI está subordinada a unidade operacional, administrativa ou financeira, sem atuação estratégica.

**Cobertura no iGovTI 2026:**
- **q0102** (opções C e D): identifica subordinação a área administrativa/financeira ou unidade operacional/setorial.
- **q0102** (opção B): identifica subordinação a secretaria/diretoria-geral (nível intermediário).

**Avaliação:** O questionário mapeia o posicionamento hierárquico, mas não estabelece critérios de adequação. A matriz consolidada (C25 — TI distante da alta administração) trata o tema como risco médio, desde que haja evidência de efeito.

---

### 2.4 Ausência de instituição formal do Comitê de TIC

**Achado:** Não há comitê de TI formalmente instituído.

**Cobertura no iGovTI 2026:**
- **q1001** (detalhamento E): verifica se existe comitê de TI composto por representantes de áreas relevantes.
- **q1001** (detalhamento F): verifica se o comitê realiza atividades previstas em ato constitutivo.

**Avaliação:** O questionário identifica a existência formal do comitê e sua atuação. No entanto, não diferencia "ato de criação sem reuniões" (comitê inerte) de "comitê atuante". A matriz consolidada (C14) destaca essa distinção: "Comitê criado sem reuniões ou deliberações é forte evidência de governança formalista".

---

### 2.5 Atuação meramente formal do Comitê de TIC

**Achado:** O comitê existe formalmente, mas não realiza reuniões, não produz deliberações ou não monitora indicadores.

**Cobertura no iGovTI 2026:**
- **q1001** (detalhamento F): o comitê realiza as atividades previstas em ato constitutivo.
- **q1001** (detalhamento H): a organização estabeleceu objetivos, indicadores e metas para a gestão de TI.
- **q1002** (detalhamento D): relatórios de medição de desempenho estão disponíveis à liderança.

**Avaliação:** As questões capturam indiretamente a atuação formal do comitê, mas não perguntam especificamente sobre a periodicidade de reuniões, a existência de atas ou deliberações. A matriz de riscos (C14) indica que este é um achado frequente e de alta materialidade.

---

### 2.6 Inexistência ou desatualização do planejamento de TIC

**Achado:** Não há plano de TI vigente ou o plano está desatualizado.

**Cobertura no iGovTI 2026:**
- **q2101** (adoption): processo de planejamento de TI.
- **q2102** (adoption): plano de TI vigente, com detalhamentos sobre aprovação (A), publicação (B), vínculo orçamentário (C), alinhamento institucional (D) e acompanhamento (E).

**Avaliação:** O questionário cobre o ciclo completo do planejamento. No entanto, não pergunta diretamente sobre a data de vigência ou a última revisão do plano. A matriz consolidada (C13) destaca que "plano sem acompanhamento ou revisão" é risco de alta materialidade.

---

### 2.7 Inexistência ou desatualização do catálogo de serviços de TIC

**Achado:** Não há catálogo de serviços de TI formalizado ou atualizado.

**Cobertura no iGovTI 2026:**
- **q2201** (adoption): catálogo de serviços e monitoramento de níveis de serviço, com detalhamentos sobre metas (A), atualização (B), acessibilidade (C), ANS (D) e monitoramento (E).

**Avaliação:** O questionário cobre o tema de forma adequada, incluindo a atualização e o monitoramento. A matriz consolidada (C20) classifica este risco como médio.

---

### 2.8 Inexistência de Acordos de Níveis de Serviço formalmente definidos

**Achado:** Não há ANS estabelecidos entre a área de TI e as áreas de negócio.

**Cobertura no iGovTI 2026:**
- **q2201** (detalhamento D): ANS contendo metas de nível de serviço acordadas.
- **q2804** (detalhamento D): TR preveem Níveis Mínimos de Serviço (NMS) vinculando pagamento a resultados.

**Avaliação:** Cobertura adequada. O questionário vincula o tema à gestão de serviços e às contratações.

---

### 2.9 Inexistência ou fragilidade do inventário de ativos de TIC

**Achado:** Não há inventário atualizado de ativos de TI.

**Cobertura no iGovTI 2026:**
- **q2203** (adoption): gestão de configuração e ativos, com detalhamento sobre base de dados consolidada (A) e uso para planejamento de mudanças (B).
- **q2501** (adoption): gestão de ativos associados à informação, com detalhamento sobre inventário (A), responsáveis (B) e informações críticas (C).

**Avaliação:** O questionário cobre o inventário tanto sob a ótica de serviços (ITSM) quanto de segurança da informação. A matriz consolidada (C18) reforça a importância do tema.

---

### 2.10 Ausência de processo formal de gestão de configuração

**Achado:** Não há processo formal de gestão de configuração (CMDB).

**Cobertura no iGovTI 2026:**
- **q2203** (adoption): gestão de configuração e ativos.
- **q2203** (detalhamento C): processo formalizado.

**Avaliação:** Cobertura adequada. O detalhamento C exige formalização do processo.

---

### 2.11 Inexistência de processo formal de gestão de incidentes de TIC

**Achado:** Não há processo formal de gestão de incidentes de TI.

**Cobertura no iGovTI 2026:**
- **q2204** (adoption): gestão de incidentes de serviços de TI e de segurança da informação, com regras de priorização (A), níveis de serviço (B), base de conhecimento (C), formalização (D), notificação de incidentes de segurança (E) e análise de causa raiz (F).

**Avaliação:** Cobertura adequada e detalhada. A matriz consolidada (C06) reforça a importância da análise de causa raiz e da comunicação.

---

### 2.12 Ausência de registro sistemático dos incidentes de TIC

**Achado:** Os incidentes não são registrados em ferramenta ou sistema adequado.

**Cobertura no iGovTI 2026:**
- **q2204** (detalhamento A): regras de priorização e escalamento (implica registro).
- **q2204** (detalhamento E): procedimentos de notificação e tratamento de incidentes de segurança.
- **q2204** (detalhamento F): análise de causas raízes e ações corretivas (requer registro histórico).

**Avaliação:** O questionário aborda indiretamente o registro, mas não pergunta explicitamente se existe "ferramenta ou sistema de registro de incidentes". A questão q2204 assume que o processo existe, mas não investiga a existência de ferramenta. Este é um ponto de fragilidade.

## 3. Análise Comparativa com a Matriz Consolidada de Riscos

A matriz consolidada de avaliação de riscos (CONSOLIDADO_AVALIACAO_RISCO.md) identifica 26 riscos prioritários. Os 12 achados propostos pelo usuário mapeiam-se parcialmente nos riscos consolidados:

| Achado do Usuário | Risco Consolidado Equivalente | Grau de Cobertura |
|---|---|---|
| Ausência de normatização da área de TIC | C12 — Estrutura formal de TI inexistente | Alta |
| Área de TIC sem atribuições de planejamento, coordenação, gestão e controle | C12 — Estrutura formal de TI inexistente / C14 — Governança pró-forma | Média |
| Posicionamento organizacional inadequado | C25 — TI distante da alta administração | Baixa (indireta) |
| Ausência de instituição formal do Comitê de TIC | C14 — Governança pró-forma | Alta |
| Atuação meramente formal do Comitê de TIC | C14 — Governança pró-forma | Média (falta detalhamento) |
| Inexistência ou desatualização do planejamento de TIC | C13 — Planejamento de TI sem plano vigente | Alta |
| Inexistência ou desatualização do catálogo de serviços | C20 — Catálogo de serviços e ANS inexistentes | Alta |
| Inexistência de ANS formalmente definidos | C20 — Catálogo de serviços e ANS inexistentes | Alta |
| Inexistência ou fragilidade do inventário de ativos | C18 — Gestão de ativos sem inventário | Alta |
| Ausência de processo formal de gestão de configuração | C15 — Gestão de mudanças e configuração | Alta |
| Inexistência de processo formal de gestão de incidentes | C06 — Resposta a incidentes inexistente | Alta |
| Ausência de registro sistemático dos incidentes | C06 — Resposta a incidentes inexistente | Baixa (indireta) |

**Observação:** Três achados possuem cobertura baixa ou indireta no questionário:
1. **Posicionamento organizacional inadequado**: o questionário mapeia a posição, mas não avalia a adequação.
2. **Atuação meramente formal do Comitê**: o questionário verifica a existência do comitê e seus detalhamentos, mas não pergunta sobre reuniões, atas ou deliberações específicas.
3. **Registro sistemático de incidentes**: o questionário pressupõe o processo, mas não investiga a existência de ferramenta ou sistema de registro.

## 4. Avaliação das Questões de Auditoria Propostas

### Questão 1: Planejamento de TIC como instrumento de governança (COBIT 2019)

**Subquestões:**
- Comitê de TIC formalmente instituído por ato normativo vigente?
- Comitê de TIC reúne-se com periodicidade mínima e produz atas?
- Planejamento de TIC formalmente instituído e aprovado?
- Planejamento de TIC é revisto e atualizado periodicamente?

**Avaliação:** As subquestões estão adequadas e alinhadas ao iGovTI 2026 (q1001, q2101, q2102). No entanto, o questionário não pergunta explicitamente sobre "ato normativo vigente" do comitê (q1001 pergunta sobre ato constitutivo, mas não sobre vigência). Também não pergunta sobre "periodicidade mínima de reuniões" ou "produção de atas". A subquestão sobre revisão do planejamento está parcialmente coberta (q2102 detalhamento E), mas não pergunta sobre a data da última revisão.

**Recomendação:** Adicionar questão específica sobre vigência do ato constitutivo do comitê, periodicidade de reuniões e existência de atas registradas.

---

### Questão 2: Gestão de serviços de TIC alinhada a COBIT 2019 e ITIL 4

**Subquestões:**
- Catálogo de serviços formalmente instituído, atualizado e acessível?
- Catálogo é periodicamente revisado e atualizado?
- ANS formalmente definidos com monitoramento contínuo?
- Inventário atualizado de ativos de TIC?
- Processo formal de gestão de configuração com ICs definidos?
- Processo formal de gestão de incidentes com papéis e fluxos definidos?
- Incidentes registrados em ferramenta ou sistema com rastreabilidade?

**Avaliação:** A questão está bem estruturada e cobre os achados 7 a 12. As subquestões sobre catálogo, ANS, inventário, gestão de configuração e gestão de incidentes estão alinhadas ao iGovTI 2026 (q2201, q2203, q2204, q2501).

**Fragilidade identificada:** A subquestão sobre "incidentes registrados em ferramenta ou sistema" não tem correspondente direto no iGovTI 2026. O questionário pressupõe que o processo existe (q2204), mas não investiga a infraestrutura de registro. A matriz consolidada (C06) destaca que "avaliar incidentes reais recentes é essencial para confirmar efetividade".

**Recomendação:** Adicionar questão específica sobre existência de ferramenta ou sistema de registro de incidentes, e solicitar evidência de registros recentes.

---

### Questão 3: Contratações de soluções de TIC alinhadas ao COBIT 2019

**Subquestões:**
- Fluxo decisório formalizado para contratações de TI?
- Papéis e responsabilidades formalmente definidos?
- Modelos padronizados para artefatos de contratação?
- Manuais ou normativos orientativos para elaboração de artefatos?

**Avaliação:** A questão está alinhada ao grupo g2800 do iGovTI 2026 (q2801, q2802, q2803, q2804, q2805). As subquestões sobre fluxo decisório, papéis e modelos padronizados estão cobertas.

**Observação:** A questão não aborda especificamente os critérios de segurança da informação e proteção de dados (LGPD) nas contratações, que é um ponto crítico destacado na matriz consolidada (C09 — Contratações de TI sem governança técnica e requisitos de SI/LGPD). O iGovTI 2026 já cobre isso em q2804 (detalhamento E), mas a questão de auditoria proposta não o menciona.

**Recomendação:** Incluir subquestão sobre requisitos de segurança da informação e adequação à LGPD nas contratações de TI.

## 5. Recomendações para Adição ou Modificação de Questões

### 5.1 Adicionar questão sobre atuação efetiva do Comitê de TIC

**Justificativa:** O iGovTI 2026 identifica a existência do comitê (q1001), mas não avalia sua efetividade. A matriz consolidada (C14) e os achados propostos (4 e 5) destacam que a mera existência formal do comitê não garante governança efetiva.

**Questão sugerida:**
> "O Comitê de TIC reúne-se com periodicidade mínima definida, produz atas registradas de suas deliberações e monitora o cumprimento das decisões tomadas?"

**Evidência solicitada:** Atas de reuniões do comitê de TI dos últimos 12 meses, cronograma de reuniões e relatório de acompanhamento de deliberações.

---

### 5.2 Adicionar questão sobre ferramenta de registro de incidentes

**Justificativa:** O iGovTI 2026 avalia o processo de gestão de incidentes (q2204), mas não investiga se existe ferramenta ou sistema de registro. O achado 12 (ausência de registro sistemático) e a matriz consolidada (C06) indicam que a rastreabilidade é essencial.

**Questão sugerida:**
> "A organização utiliza ferramenta ou sistema informatizado para registro, acompanhamento e análise de incidentes de TI e de segurança da informação, garantindo rastreabilidade e histórico?"

**Evidência solicitada:** Nome da ferramenta, capturas de tela do sistema, relatório de incidentes registrados nos últimos 12 meses.

---

### 5.3 Adicionar questão sobre adequação do posicionamento hierárquico da TI

**Justificativa:** O iGovTI 2026 mapeia o posicionamento (q0102), mas não estabelece critérios de adequação. O achado 3 (posicionamento inadequado) e a matriz consolidada (C25) indicam que o posicionamento afeta a capacidade estratégica.

**Questão sugerida:**
> "Considerando o porte, a complexidade e a criticidade dos serviços de TI da organização, o posicionamento hierárquico da área de TI é compatível com sua atuação estratégica e de governança?"

**Evidência solicitada:** Organograma institucional, descrição da atuação estratégica da TI, justificativa do posicionamento adotado.

---

### 5.4 Modificar a Questão 2 de Auditoria para incluir requisitos de segurança nas contratações

**Justificativa:** A matriz consolidada (C09) e o iGovTI 2026 (q2804, detalhamento E) destacam a importância dos requisitos de segurança da informação e de proteção de dados nas contratações.

**Subquestão sugerida (adição à Questão 3):**
> "As contratações de soluções de TIC incluem análise expressa de requisitos de segurança da informação e de adequação à Lei Geral de Proteção de Dados (LGPD), com definição de responsabilidades do fornecedor quanto à proteção de dados pessoais e sigilosos?"

**Evidência solicitada:** TR ou ETP de contratações de TI com cláusulas de segurança e LGPD, termos de confidencialidade, relatórios de avaliação de riscos de proteção de dados.

---

### 5.5 Adicionar questão sobre testes de continuidade e recuperação de desastres

**Justificativa:** A matriz consolidada (C08) classifica como risco crítico a ausência de testes de continuidade. O iGovTI 2026 aborda continuidade em q2303, mas não investiga a efetividade dos testes.

**Questão sugerida:**
> "A organização realiza testes periódicos de recuperação de desastres e de continuidade de serviços críticos de TI, com evidências de execução e análise de resultados?"

**Evidência solicitada:** Relatórios de testes de continuidade/DR dos últimos 24 meses, cronograma de testes, plano de ações corretivas identificadas.

---

### 5.6 Adicionar questão sobre uso de IA generativa não autorizada (Shadow AI)

**Justificativa:** A matriz consolidada (C01) classifica como risco crítico o uso de IA generativa sem governança. O iGovTI 2026 já possui questões sobre IA (q3001 a q3006), mas a questão q3005 foca em controles técnicos. Seria útil investigar a efetividade desses controles.

**Questão sugerida:**
> "A organização realiza auditorias ou levantamentos periódicos para identificar o uso não autorizado de ferramentas de inteligência artificial generativa (shadow AI) em sua rede corporativa?"

**Evidência solicitada:** Relatórios de levantamento de uso de IA, logs de proxy/firewall, norma de uso de IA, registros de campanhas de conscientização.

## 6. Conclusão

O questionário iGovTI 2026 apresenta cobertura **adequada a alta** para a maioria dos 12 achados propostos, especialmente em relação à estrutura organizacional, planejamento, gestão de serviços, segurança da informação e contratações. As trilhas lógicas do questionário permitem inferir a existência de fragilidades nos controles.

No entanto, identificam-se **três lacunas principais** que justificam a adição ou modificação de questões:

1. **Efetividade da governança:** o questionário identifica a existência formal do comitê de TI, planejamento e processos, mas não avalia se essas estruturas operam de forma efetiva (reuniões, atas, deliberações, testes, revisões).

2. **Infraestrutura de suporte:** o questionário pressupõe que processos como gestão de incidentes possuem ferramentas de suporte, mas não investiga diretamente a existência de sistemas, registros operacionais ou evidências de efetividade.

3. **Critérios de adequação:** o questionário mapeia posicionamento hierárquico e estrutura, mas não estabelece parâmetros para avaliar se a configuração adotada é adequada ao contexto da organização.

As **questões de auditoria propostas** pelo usuário estão bem formuladas e alinhadas aos achados. Recomenda-se:
- **Adicionar** subquestões sobre vigência do ato constitutivo do comitê, periodicidade de reuniões e produção de atas;
- **Adicionar** subquestão sobre existência de ferramenta de registro de incidentes;
- **Adicionar** subquestão sobre requisitos de segurança e LGPD nas contratações de TI;
- **Considerar** a inclusão de questões sobre testes de continuidade, shadow AI e adequação do posicionamento hierárquico da TI.

A matriz consolidada de riscos deve ser utilizada como insumo de planejamento, orientando a priorização dos procedimentos de auditoria, mas não como conclusão automática de achado. Cada risco identificado deve ser confirmado por evidência documental, entrevista ou teste substantivo.
