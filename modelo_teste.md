---
title: "Questionário de Governança e Gestão de TI - 2026"
language: "pt-BR"
sid: 489123
target: municipal, estadual
admin: Coordenadoria de Auditoria em TI
adminemail: "auditoriati@tcerj.tc.br"
format: G
template: vanilla
expires: "2026-06-01 23:59:59"
endtext: |
  <p style="margin-bottom:12pt;text-align:justify;margin:0cm 0cm 10pt;"><span style="font-size:11pt;"><span style="line-height:normal;"><span style="font-family:Calibri, sans-serif;"><span style="font-size:12pt;"><span style="font-family:Arial, sans-serif;">Agradecemos o preenchimento do questionário de Governança e Gestão de Tecnologia da Informação. Assim que as respostas forem validadas, você e o dirigente máximo da organização receberão e-mail com as respostas </span></span></span></span></span><span style="font-size:12pt;"><span style="line-height:115%;"><span style="font-family:Arial, sans-serif;">fornecidas ao questionário, que deverá ser guardado e mantido </span></span></span><span style="font-size:12pt;"><span style="line-height:115%;"><span style="font-family:Arial, sans-serif;">à disposição do TCE-RJ, juntamente com as evidências documentais que dão suporte às mesmas, </span></span></span><span style="font-size:12pt;"><span style="line-height:115%;"><span style="font-family:Arial, sans-serif;">para </span></span></span><span style="font-size:12pt;"><span style="line-height:115%;"><span style="font-family:Arial, sans-serif;">futura verificação de consistência.</span></span></span></p>
  
  <h2 style="font-style:italic;text-align:center;">FIM</h2>
welcome: |
  <p style="color:#000000;">O TCE-RJ, por meio da Coordenadoria Setorial de Auditoria em Políticas de Tecnologia da Informação (CAS-TI), está realizando auditoria para verificar os aspectos das políticas de Governança e Gestão de Tecnologia da Informação como norteadores das contratações de TI no Executivo Estadual no âmbito do Sistema Estadual de Tecnologia da Informação e Comunicação – SETIC, que foi estruturado pelo Decreto Estadual nº 47.278/2020.</p>
  
  <p style="color:#000000;">O Questionário em tela é um instrumento de coleta de dados para mapear o cenário atual das práticas de governança e gestão de tecnologia da informação adotadas pelas organizações do nível setorial do SETIC e seus Setores de TI (assessorias de informática), assim como suas percepções acerca do Sistema SETIC.</p>
  
  <p style="color:#000000;">Recomenda-se que o servidor responsável pelo preenchimento reúna previamente todas as informações necessárias junto aos diversos setores da organização (Jurídico, Controle Interno, Gestão de Pessoal, Gestão de TI, etc.) antes de iniciar o preenchimento on-line.</p>
  
  <p style="color:#000000;">As evidências documentais que suportam as respostas dadas deverão ser reunidas e mantidas à disposição do TCE-RJ para futura verificação de consistência.</p>
---

# Questionário de Governança e Gestão de TI - 2026

## Escala: adoption
type: single
- naoad | Não adota.
- adfor | Há decisão formal ou plano aprovado para adotá-lo.
- admen | Adota em menor parte.
- adpar | Adota parcialmente.
- admai | Adota em maior parte ou totalmente.
- naoap | Não se aplica.

## Escala: justificativa_nsa
type: single
- A | Não se aplica porque há lei e/ou norma externa à organização que impede a implementação desta prática.
- B | Não se aplica porque há estudos que demonstram que o custo de implementação supera o benefício esperado.
- C | Não se aplica por outras razões.

## Escala: sim_nao
type: single
- sim | Sim
- nao | Não

## Grupo: g001 | Dados do servidor responsável pelo preenchimento do questionário

### qnome [short]
mandatory: true

**Nome Completo:**

### qmatricula [short]
mandatory: true

**Matrícula:**

### qcargo [short]
mandatory: true

**Cargo:**

### qorgao [short]
mandatory: true

**Órgão:**

## Grupo: g1000 | Sistema Estadual de Tecnologia da Informação e Comunicação - SETIC
> De acordo com o Decreto Estadual nº 47.278 de 17 de setembro de 2020, o Sistema Estadual de Tecnologia da Informação e Comunicação - SETIC, configura-se como o conjunto de recursos humanos, tecnológicos e de equipamentos voltados para o estabelecimento e a implementação de políticas para a informação e a comunicação pública, sendo estruturado em dois níveis de atuação: I - Direção Geral, representado pelo PRODERJ; e II – Setorial, representado pelas Assessorias de Informática, ou setores equivalentes, de todos os órgãos da administração direta e indireta do estado do Rio de Janeiro, assim chamadas de NSTIC/RJ.
> Alinhando-se a essa estrutura apresentada, nessa seção será avaliada a percepção do gestor de TI da organização, pessoa responsável pela assessoria de informática (Setor de TI) da organização, podendo, também, ser denominado como o principal responsável pelo NSTIC/RJ, nos termos do Art. 4º do Anexo C da Portaria PRODERJ/PRE nº 825/2021.

### q1011 [single]
mandatory: true
scale: sim_nao
subgroup: 1010 Informações do Setor de TI
help: O Setor de TI é a unidade responsável pelo planejamento, supervisão, coordenação e controle da tecnologia da informação da organização.

<strong>1011. A organização possui Setor de TI próprio.</strong>

### q1011sim [multi_text]
mandatory: true
visible_if: q1011 == sim
help: O Gestor de TI é a pessoa responsável pelo Setor de TI da organização.

<strong>Forneça o nome e contato do Gestor de TI da organização.</strong>

subquestions:
- SQ001 | Nome
- SQ002 | E-mail
- SQ003 | Telefone

### q1011nao [long]
mandatory: true
visible_if: q1011 == nao

<strong>A organização não necessita de TI? Existe um responsável externo à organização? Qual? Está formalizado? Justifique a situação.</strong>

## Grupo: g1020 | Normativos do SETIC
> Nesta seção são avaliados conhecimento e atendimento a normativos expedidos pelo PRODERJ.

### q1021 [single]
mandatory: true
scale: sim_nao
visible_if: q1011 == sim
help: Conforme o Decreto Estadual nº 47.278/2020, compete ao PRODERJ disciplinar diretrizes técnicas e procedimentais de TIC.

<strong>1021. A organização tem conhecimento dos normativos expedidos pelo Diretor Geral do SETIC (PRODERJ).</strong>

### q1021ext [multi]
mandatory: true
visible_if: q1021 == sim
min_answers: 1
hide_tip: true

<strong>Visando explicitar melhor o grau de conhecimento, marque abaixo uma ou mais opções que caracterizam sua resposta.</strong>

subquestions:
- A | a) Portaria PRODERJ/PRE nº 825/2021, que institui a PGTIC/RJ, a EGTIC/RJ e as normas para elaboração do PEDTIC.
- B | b) Instrução Normativa PRODERJ/PRE nº 01/2021, sobre contratação e celebração de acordos envolvendo soluções de TIC.
- C | c) Instrução Normativa PRODERJ/PRE nº 02/2022, sobre procedimentos de segurança da informação.
- D | d) Instrução Normativa PRODERJ/PRE nº 03/2022, sobre sites e portais de internet hospedados no PRODERJ.

### q1021raznao [long]
mandatory: true
visible_if: q1021 == nao

Expresse o motivo.

### q1022 [adoption]
mandatory: true
visible_if: q1011 == sim
help: A Portaria PRODERJ/PRE nº 825/2021 institui a Política de Governança de Tecnologia da Informação e Comunicação do Estado do Rio de Janeiro – PGTIC/RJ, a EGTIC/RJ e normas para elaboração do PEDTIC.

<strong>1022. A organização atende à Portaria PRODERJ/PRE nº 825/2021 expedida pelo Diretor Geral do SETIC (PRODERJ).</strong>

detail_options:
- A | a) a organização constituiu seu Comitê Permanente do PEDTIC.
- B | b) o Comitê Permanente do PEDTIC é composto pelo principal responsável do NSTIC/RJ.
- C | c) a organização elabora seu PEDTIC.
- D | d) a organização aprovou formalmente o PEDTIC.


### q1022extAevi [upload]
mandatory: true
visible_if: q1022ext.A == Y
allowed_filetypes: pdf, docx, zip
min_files: 1
max_files: 1

Anexe evidência documental que comprove a constituição do Comitê Permanente do PEDTIC.

### q1022extDevi [upload]
mandatory: true
visible_if: q1022ext.D == Y
allowed_filetypes: doc, pdf, docx, zip
min_files: 1
max_files: 3

Anexe evidência documental que comprove a aprovação formal do PEDTIC.

### q1023 [adoption]
mandatory: true
target: estadual
visible_if: q1011 == sim
help: A Portaria PRODERJ/PRE nº 825/2021 institui a Política de Governança de Tecnologia da Informação e Comunicação do Estado do Rio de Janeiro – PGTIC/RJ, a EGTIC/RJ e normas para elaboração do PEDTIC.

<strong>1023. XPTO.</strong>

detail_options:
- A | a) a organização constituiu seu Comitê Permanente do PEDTIC.
- B | b) o Comitê Permanente do PEDTIC é composto pelo principal responsável do NSTIC/RJ.
