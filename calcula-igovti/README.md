# Calculadora iGovTI

Esta pasta contém a aplicação web `index.html`, uma calculadora e plataforma analítica client-side para processar respostas do questionário iGovTI, aplicar uma estrutura de índice definida em YAML e explorar estatisticamente os resultados.

A aplicação foi evoluída a partir de uma calculadora iGovTI existente. Ela preserva a importação de XLSX, aplicação de YAML, cálculo de agregados ponderados, árvore de cálculo, memória de cálculo, tabela de resultados, exportações e classificação de maturidade, e adiciona uma aba completa de análises estatísticas.

## Visão Geral

O arquivo `index.html` é autocontido e roda diretamente no navegador. Ele usa bibliotecas via CDN:

- `xlsx`: leitura de planilhas `.xlsx`/`.xls`.
- `js-yaml`: leitura e validação do YAML da estrutura do índice.
- `Plotly.js`: gráficos interativos e exportação visual.
- `simple-statistics`: dependência preparada para estatística, embora a página também implemente funções estatísticas locais.
- `tsne-js`: projeção t-SNE na aba analítica, com fallback para PCA 2D.
- `umap-js`: projeção UMAP quando selecionada, com fallback para PCA 2D.

A aplicação possui três abas principais:

1. **Calculadora**
   - edição/importação do YAML;
   - importação da planilha XLSX;
   - validação da estrutura;
   - cálculo do índice;
   - árvore interativa do índice;
   - memória de cálculo.

2. **Resultados**
   - tabela final por organização;
   - raiz do índice;
   - nível de maturidade;
   - agregados calculados.

3. **Análises Estatísticas**
   - estatística descritiva;
   - correlações e dependências;
   - PCA;
   - t-SNE/PCA 2D;
   - K-Means;
   - benchmarking;
   - outliers;
   - exploração individual;
   - distribuições;
   - insights automáticos.

## Fluxo de Uso

1. Abra `calcula-igovti/index.html` no navegador.
2. Revise ou importe o YAML da estrutura do índice.
3. Clique em **Aplicar**.
4. Importe a planilha de respostas XLSX exportada pelo LimeSurvey.
5. Verifique as validações.
6. Clique em **Calcular**.
7. Navegue entre:
   - árvore e memória de cálculo;
   - tabela de resultados;
   - análises estatísticas.

Antes de haver resultados calculados, a aba **Análises Estatísticas** exibe:

> Calcule os resultados antes de acessar as análises estatísticas.

Depois do cálculo, as análises são recalculadas automaticamente a partir de `state.results`.

## Estrutura de Dados

### Estado Principal

A aplicação mantém os dados em um objeto global `state`:

- `config`: YAML parseado.
- `rawRows`: linhas brutas importadas do XLSX.
- `processedRows`: linhas pré-processadas e normalizadas.
- `results`: resultados calculados.
- `idColumn`: coluna usada como identificador da organização.
- `availableQuestions`: conjunto de questões disponíveis após o pré-processamento.
- `selectedEntity`: organização selecionada na calculadora.
- `selectedNodeId`: nó selecionado na árvore.
- `collapsedNodes`: nós recolhidos no diagrama.
- `aggregateValidation`: mapa de validação de soma dos pesos.
- `showDetachedAggregates`: flag para renderizar agregados avulsos.
- `analytics`: objeto com todos os resultados estatísticos.
- `analyticsVariableScope`: escopo das variáveis analíticas.
- `clusterCount`: quantidade de clusters no K-Means.
- `embeddingMethod`: método de projeção 2D (`tsne` ou `pca`).
- `selectedAnalyticsEntity`: organização selecionada na aba analítica.
- `analyticsSearch`: filtro textual da aba analítica.

### Resultado Calculado

Cada item de `state.results` possui a forma:

```js
{
  id: "ORG",
  indice: "iGovTI",
  valor: 0.7345,
  nivel_maturidade: "Aprimorado",
  valores: {
    q1001: 1,
    GovernancaTI: 0.72,
    iGestTI: 0.68,
    iGovTI: 0.70
  },
  memoria: {
    iGovTI: [
      { id: "GovernancaTI", peso: 0.5, value: 0.72, contribution: 0.36 }
    ]
  }
}
```

As análises estatísticas usam principalmente `result.valores`.

## YAML do Índice

O YAML define:

- metadados do índice;
- categorias de resposta;
- níveis de maturidade;
- agregados;
- componentes;
- pesos.

Exemplo de estrutura:

```yaml
metadata:
  nome: iGovTI
  versao: "2026"
  raiz: iGovTI

preprocessamento:
  nao_se_aplica: parcial

categorias:
  naoad: 0
  adfor: 0.05
  admen: 0.15
  adpar: 0.5
  admai: 1
  naoap: 0.5
  sim: 1
  nao: 0

agregados:
  iGovTI:
    componentes:
      - id: GovernancaTI
        peso: 0.5
      - id: iGestTI
        peso: 0.5
```

### Categorias

A seção `categorias` converte respostas textuais ou códigos do LimeSurvey em valores numéricos normalizados.

Foram incluídos os códigos exportados pelo LimeSurvey para questões `[adoption]`:

- `naoad`: 0
- `adfor`: 0.05
- `admen`: 0.15
- `adpar`: 0.5
- `admai`: 1
- `naoap`: 0.5

Também foram incluídos códigos de escala sim/não:

- `sim`: 1
- `nao`: 0

Além dos códigos, o YAML embutido mantém rótulos longos como fallback para planilhas já decodificadas:

- `"Não adota"` e `"Não adota."`
- `"Há decisão formal ou plano aprovado para adotá-lo"`
- `"Adota em menor parte"`
- `"Adota parcialmente"`
- `"Não se aplica"`
- `"Adota em maior parte ou totalmente"`
- `"Sim"`
- `"Não"`
- `"Nao"`
- `"N/A"`

## Importação e Pré-Processamento

O XLSX é lido com `XLSX.read`. A primeira aba da planilha é convertida em JSON com:

```js
XLSX.utils.sheet_to_json(firstSheet, { defval: null })
```

Cada linha da planilha é convertida em uma linha processada contendo:

- `__id`: identificador da organização;
- `__raw`: linha original;
- `__normalized`: respostas normalizadas;
- `__questions`: questões pontuadas e aliases.

### Detecção da Coluna Identificadora

A aplicação tenta identificar a coluna da organização com os nomes:

- `firstname`
- `attribute_1`
- `orgao`
- `órgão`
- `entidade`
- `auditado`
- `name`
- `id`

Se nenhuma dessas existir, usa a primeira coluna da planilha.

O campo `firstname` é priorizado porque, nas exportações do LimeSurvey usadas neste fluxo, ele contém o nome legível da organização. O campo técnico `id` só é usado como fallback.

### Normalização de Colunas

A função `normalizeColumnName` remove pontos e preserva colchetes e o sufixo `ext`.

Isso é importante porque o LimeSurvey exporta subitens de questões no formato:

```text
q2501ext[A]
q2501ext[C]
```

Versões anteriores removiam `ext`, `[` e `]`, transformando `q2501ext[A]` em `q2501A`. Isso causava falso alerta de questão não encontrada quando o YAML referenciava `q2501ext[A]`.

### Colunas Ignoradas

A função `isQuestionColumn` considera apenas colunas com número de questão e ignora campos auxiliares:

- `lei`
- `est`
- `evi`
- `nsa`
- `raz`
- `SQ`

Assim, uploads, justificativas, evidências e campos textuais auxiliares não entram no cálculo numérico.

### Aliases de Questões

A função `questionIdAliases` cria aliases para compatibilidade entre formatos:

- `q2501ext[A]` gera alias `q2501A`;
- `q2501[A]` gera alias `q2501A`;
- `q2501A` gera aliases `q2501[A]` e `q2501ext[A]`.

Esses aliases são adicionados apenas ao mapa final de pontuações (`questionScores`) para permitir que YAMLs com grafias diferentes encontrem a questão correta. Eles não são usados para duplicar colunas no cálculo das questões base.

## Cálculo de Questões

Cada resposta é normalizada por `normalizeAnswer`:

1. valores vazios viram `0`;
2. números são preservados;
3. strings são buscadas em `config.categorias`;
4. se não houver categoria, tenta converter para número;
5. se não for número, mantém o valor bruto.

### Questões de Adoção com Subitens

Questões do tipo adoption possuem:

- uma resposta base, como `q2501`;
- subitens, como `q2501ext[A]`, `q2501ext[B]`, etc.

A função `calculateQuestion` aplica deflação quando a resposta base representa adoção parcial ou maior parte/total:

- adoção maior parte/total:
  - códigos reconhecidos: `admai`, `"Adota em maior parte ou totalmente"`, `"Adota em maior parte ou totalmente."`, `"Adota"`;
  - desconto máximo: `0.85`.

- adoção parcial:
  - códigos reconhecidos: `adpar`, `"Adota parcialmente"`, `"Adota parcialmente."`;
  - desconto máximo: `0.35`.

Fórmula:

```text
score = baseNumeric - ((missing * discountMax) / quantidade_de_subitens)
```

Onde:

```text
missing = soma(1 - valor_do_subitem)
```

O resultado é limitado ao intervalo `[0, 1]`.

Se a questão não tem subitens ou a resposta base não é uma adoção que exige deflação, o valor base é usado diretamente.

## Cálculo dos Agregados

A função `calculateAll` percorre todos os registros processados e calcula:

1. questões normalizadas;
2. agregados definidos no YAML;
3. raiz do índice;
4. nível de maturidade;
5. memória de cálculo.

Cada agregado é calculado por soma ponderada:

```text
agregado = soma(valor_componente * peso_componente)
```

O resultado é limitado a `[0, 1]`.

### Recursão

Agregados podem depender de:

- questões (`q1001`);
- subitens (`q2501ext[A]`);
- outros agregados (`GovernancaTI`, `iGestTI`).

A função `visit(id)` calcula recursivamente cada nó. Se encontrar um ciclo durante o cálculo, lança erro de ciclo.

### Memória de Cálculo

Para cada agregado, a memória registra:

- componente;
- peso;
- valor calculado;
- contribuição (`valor * peso`).

Essa memória alimenta:

- árvore textual;
- detalhes do nó;
- visualização do diagrama.

## Classificação de Maturidade

A função `classifyMaturity` usa os intervalos definidos em `niveis_maturidade`.

Cada nível pode definir:

- `min`
- `max`
- `inclui_min`
- `inclui_max`

Exemplo:

```yaml
- nome: Intermediário
  min: 0.4
  max: 0.7
  inclui_min: true
  inclui_max: false
```

Se nenhum intervalo corresponder, a classificação retornada é `"Sem classificação"`.

## Validações

A função `validateAndRender` valida a estrutura antes e depois da importação.

Validações implementadas:

- YAML ausente ou inválido;
- `metadata.raiz` obrigatório;
- `categorias` obrigatório;
- `niveis_maturidade` deve ser lista;
- `agregados` obrigatório;
- raiz deve existir em `agregados`;
- cada agregado deve ter componentes;
- pesos dos componentes devem ser números finitos;
- subagregados referenciados devem existir;
- questões referenciadas devem existir na planilha, quando já houver planilha importada;
- ciclos entre agregados;
- coerência dos níveis de maturidade;
- soma dos pesos de cada agregado deve ser `1`.

### Validação da Soma dos Pesos

Cada agregado é validado por `aggregateValidationMap`.

Se a soma dos pesos não for `1`, a aplicação:

- mostra erro no painel de validações;
- marca o nó da árvore textual com tom de alerta;
- marca o nó do diagrama com tom de alerta;
- mostra a mensagem no detalhe do nó.

A tolerância usada é:

```text
abs(soma - 1) <= 0.000001
```

## Diagrama da Árvore

A aplicação renderiza um diagrama SVG da estrutura do índice.

Recursos:

- nó raiz;
- agregados;
- questões;
- links entre componentes;
- seleção de nó;
- caminho ativo;
- expandir;
- recolher;
- centralizar;
- detalhe do nó selecionado;
- valores calculados após seleção de organização;
- pesos no pai;
- contribuição;
- validação do agregado.

### Colapso Inicial

Ao aplicar o YAML, a árvore é recolhida para o primeiro nível:

- raiz visível;
- filhos diretos visíveis;
- demais agregados recolhidos.

Isso evita que estruturas grandes abram ocupando toda a tela.

### Agregados Avulsos

A flag **Agregados avulsos** permite renderizar agregados que não estão conectados à raiz.

O processamento:

1. identifica agregados alcançáveis a partir da raiz;
2. identifica agregados não alcançáveis;
3. remove os que são filhos de outros agregados avulsos;
4. renderiza apenas as raízes avulsas;
5. desenha essas árvores desconectadas abaixo da árvore principal.

Isso permite documentar e visualizar cálculos auxiliares, pro forma ou comparativos sem conectá-los ao índice principal.

## Exportações

### YAML

Exporta o conteúdo atual do editor YAML como:

```text
estrutura-igovti.yaml
```

### Resultados JSON

Exporta `state.results` completo:

```text
resultado-igovti.json
```

Inclui:

- `id`;
- `indice`;
- `valor`;
- `nivel_maturidade`;
- `valores`;
- `memoria`.

### Resultados CSV

Exporta:

- `id`;
- raiz do índice;
- `nivel_maturidade`;
- agregados do YAML.

### Diagrama SVG

Exporta o SVG atual do diagrama da árvore.

A exportação inclui:

- namespace SVG;
- fundo branco;
- estilos básicos embutidos;
- links;
- nós;
- cores de seleção e alerta.

Nome do arquivo:

```text
arvore-{raiz}-{organizacao}.svg
```

### Diagrama PNG

A exportação PNG:

1. serializa o SVG atual;
2. cria um `Blob`;
3. carrega o SVG em uma imagem;
4. desenha em `canvas`;
5. exporta como PNG.

Nome do arquivo:

```text
arvore-{raiz}-{organizacao}.png
```

### Análise CSV

A aba estatística exporta:

- médias;
- desvios;
- correlações Pearson;
- clusters por organização.

Arquivo:

```text
analise-estatistica-igovti.csv
```

### Análise JSON

Exporta o objeto `state.analytics`, com dados estatísticos, correlações, PCA, clusters, benchmarks e insights.

Arquivo:

```text
analise-estatistica-igovti.json
```

## Aba Análises Estatísticas

A aba analítica transforma os resultados calculados em uma base exploratória.

Ela é atualizada automaticamente ao fim de `calculateAll`, por meio de:

```js
refreshAnalytics()
```

### Base Analítica

A função `buildAnalyticsDataset` cria uma matriz numérica a partir de `state.results`.

Por padrão, usa:

- raiz (`metadata.raiz`);
- agregados definidos no YAML.

Também há opção para usar:

- todas as variáveis numéricas de `result.valores`.

Uma variável entra na base se:

- possui valores numéricos finitos;
- valores estão no intervalo `[0, 1]`;
- pelo menos 75% das linhas têm valores numéricos válidos;
- há pelo menos 2 valores válidos.

Valores ausentes ou inválidos são imputados pela média da variável para fins de PCA e clustering.

### Controles

A aba possui controles para:

- escopo de variáveis:
  - `Agregados`;
  - `Tudo numérico`.
- seleção múltipla de variáveis.
- número de clusters:
  - mínimo `2`;
  - máximo `10`;
  - padrão `4`.
- algoritmo de clustering:
  - K-Means;
  - DBSCAN;
  - Hierárquico.
- parâmetros DBSCAN:
  - `eps`;
  - `minPts`.
- projeção:
  - `t-SNE`;
  - `UMAP`;
  - `PCA 2D`.
- modo da rede de dependências:
  - Pearson;
  - Spearman;
  - Mutual Information.
- filtro por nível de maturidade.
- filtro por cluster.
- organização selecionada;
- organização de comparação;
- busca textual por organização.

## Estatística Descritiva

A função `computeDescriptiveStats` calcula, para cada variável:

- `n`;
- média;
- mediana;
- primeiro quartil (`q1`);
- terceiro quartil (`q3`);
- mínimo;
- máximo;
- variância amostral;
- desvio padrão amostral;
- coeficiente de variação.

Fórmulas principais:

```text
média = soma(x) / n
variância = soma((x - média)^2) / (n - 1)
desvio padrão = sqrt(variância)
coeficiente de variação = desvio padrão / média
```

Quando a média é `0`, o coeficiente de variação retorna `0` para evitar divisão por zero.

## Correlações e Dependências

A aplicação calcula três matrizes:

1. Pearson;
2. Spearman;
3. Mutual Information.

### Pearson

A correlação de Pearson mede relação linear:

```text
r = cov(x, y) / (sd(x) * sd(y))
```

Valores próximos de:

- `1`: associação positiva forte;
- `-1`: associação negativa forte;
- `0`: ausência de associação linear.

### Spearman

A correlação de Spearman é calculada aplicando Pearson aos rankings das variáveis.

Fluxo:

1. transformar valores em posições ordenadas;
2. calcular Pearson sobre os rankings.

Isso mede associação monotônica, não apenas linear.

### Mutual Information

A informação mútua é calculada por discretização em 5 bins.

Fluxo:

1. cada valor é colocado em um bucket de 0 a 4;
2. calcula-se a distribuição marginal de cada variável;
3. calcula-se a distribuição conjunta;
4. soma-se:

```text
MI = soma p(x,y) * log2(p(x,y) / (p(x) * p(y)))
```

Ela captura dependências não necessariamente lineares.

### Classificação das Correlações

Os pares são classificados por `abs(Pearson)`:

- forte: `>= 0.7`;
- moderada: `>= 0.4` e `< 0.7`;
- fraca: `< 0.4`.

A aba exibe:

- heatmap de Pearson;
- tabela de pares ordenada por força;
- Spearman e Mutual Information por par;
- rede de dependências com pares `|r| >= 0.60`.

## PCA

A função `computePca` implementa PCA localmente.

Processamento:

1. centraliza as colunas;
2. calcula matriz de covariância;
3. extrai até 3 componentes por iteração de potência;
4. aplica deflação da matriz após cada componente;
5. calcula scores;
6. calcula loadings;
7. calcula variância explicada;
8. calcula variância acumulada.

### Centralização

Cada coluna é transformada em:

```text
x_centralizado = x - média_da_variável
```

### Matriz de Covariância

Para cada par de variáveis:

```text
cov(i,j) = soma(x_i * x_j) / (n - 1)
```

### Iteração de Potência

O autovetor dominante é aproximado por iterações sucessivas:

```text
v_next = A * v
v_next = v_next / ||v_next||
```

O autovalor é estimado por:

```text
lambda = v' * A * v
```

### Deflação

Após extrair um componente:

```text
A_next = A - lambda * v * v'
```

### Loadings

Para cada variável, são registrados:

- carga em PC1;
- carga em PC2;
- importância aproximada:

```text
abs(PC1) + abs(PC2)
```

A aba exibe:

- variância explicada por componente;
- variância acumulada;
- ranking de variáveis mais explicativas.

## Clustering

O motor analítico permite alternar entre K-Means, DBSCAN e clustering hierárquico.

### K-Means

A função `computeKMeans` implementa K-Means localmente.

Parâmetros:

- `k`: selecionado pelo usuário;
- mínimo `2`;
- máximo `10`;
- máximo de iterações: `60`.

### Inicialização

Os centroides iniciais são escolhidos de forma determinística, distribuídos ao longo da matriz:

```js
matrix[Math.floor((i * n) / k)]
```

Isso evita aleatoriedade e torna os resultados reproduzíveis.

### Atribuição

Cada organização é atribuída ao centroide mais próximo por distância euclidiana:

```text
distância = sqrt(soma((x_i - c_i)^2))
```

### Atualização dos Centroides

Cada centroide vira a média das organizações atribuídas ao cluster.

O processo para quando:

- nenhuma atribuição muda;
- ou chega a 60 iterações.

### Saídas

O clustering gera:

- quantidade efetiva de clusters;
- atribuição de cluster por organização;
- centroides;
- distância de cada organização ao centroide.

### DBSCAN

A função `computeDbscan` agrupa organizações por densidade usando:

- `eps`: distância máxima de vizinhança;
- `minPts`: quantidade mínima de vizinhos para formar núcleo.

Organizações classificadas como ruído recebem cluster `-1` e aparecem como ruído no filtro.

### Clustering Hierárquico

A função `computeHierarchicalClustering` executa aglomeração determinística por centroides e corta a árvore pelo número de clusters informado. Ela também gera uma sequência de fusões usada para renderizar o painel de dendrograma simplificado.

### Qualidade dos Clusters

A aplicação calcula uma métrica de silhouette aproximada por organização e resume:

- método selecionado;
- silhouette médio;
- distância média ao centroide;
- quantidade de ruídos no DBSCAN;
- resumo de média, mínimo e máximo por cluster.

## t-SNE e Projeção 2D

A aba permite escolher:

- `t-SNE`;
- `UMAP`;
- `PCA 2D`.

Quando `t-SNE` está selecionado e a biblioteca está disponível, a função `computeEmbedding` executa:

- dimensão: `2`;
- perplexity dinâmica:

```text
max(2, min(20, floor((n - 1) / 3)))
```

- `epsilon`: `10`;
- iterações: `250`.

Se `tsne-js` falhar ou não estiver carregado, a aplicação usa PCA 2D como fallback.

Quando `UMAP` está selecionado e `umap-js` está disponível, a aplicação usa UMAP com parâmetros conservadores (`nNeighbors` dinâmico e `minDist` 0.1). Se a biblioteca falhar ou não carregar, usa PCA 2D como fallback.

## Outliers

A função `computeOutliers` detecta organizações atípicas por múltiplos critérios.

### Outlier por IQR

Usa o valor raiz do índice:

```text
IQR = Q3 - Q1
```

Marca como outlier se:

```text
valor < Q1 - 1.5 * IQR
valor > Q3 + 1.5 * IQR
```

### Outlier por Distância ao Centróide

Usa a distância da organização ao centroide do cluster.

Calcula os quartis das distâncias e marca como outlier se:

```text
distância > Q3_distância + 1.5 * IQR_distância
```

Na visualização de clusters, outliers aparecem com marcador maior.

### Outlier por Desequilíbrio Interno

Cada organização recebe um desvio padrão interno entre suas variáveis analíticas. Valores altos indicam organizações com áreas muito fortes e muito fracas simultaneamente.

### Outliers por Variável

A função `computeVariableOutliers` aplica IQR por variável e lista organizações com valores extremos em dimensões específicas.

## Benchmarking

A função `computeBenchmarks` produz:

- ranking geral por valor raiz;
- top organizações;
- bottom organizações;
- ranking de variáveis por média;
- ranking de variáveis fortes;
- organizações equilibradas;
- organizações desbalanceadas;
- resumo por cluster;
- top quartil.

### Ranking Geral

Ordena organizações por `row.valor` de forma decrescente.

### Variáveis Críticas

Ordena variáveis por média crescente.

As menores médias são interpretadas como dimensões críticas ou gargalos sistêmicos.

### Benchmark por Cluster

Para cada cluster:

- conta organizações;
- calcula média do índice raiz.

### Top Quartil

Calcula o percentil 75 do índice raiz e seleciona organizações com valor maior ou igual a esse corte.

Esse grupo é usado na exploração individual como referência de excelência.

## Fragilidades Sistêmicas

O painel de fragilidades usa o ranking de médias das variáveis.

Ele exibe as dimensões com menor média, pois representam práticas, subíndices ou agregados com menor adoção média entre as organizações.

Essas dimensões ajudam a identificar:

- gargalos estruturais;
- capacidades frágeis;
- temas prioritários para melhoria;
- práticas com baixa adoção sistêmica.

## Exploração Individual

Ao selecionar uma organização ou clicar em rankings/scatterplots, a aba atualiza:

- radar chart;
- ranking da organização;
- valor raiz;
- nível de maturidade;
- cluster;
- tabela de gaps.
- comparação opcional com outra organização selecionada.

### Radar Chart

Mostra até 12 variáveis da base analítica.

Compara:

- organização selecionada;
- média geral;
- média do cluster;
- média do top quartil.

### Gaps

Para cada variável:

```text
gap = valor_da_organização - média_geral_da_variável
```

Valores negativos indicam fragilidades relativas.

Valores positivos indicam pontos fortes relativos.

## Distribuições Estatísticas

O painel de distribuições usa o valor raiz do índice e renderiza:

- histograma;
- boxplot;
- violin plot.

Essas visualizações permitem observar:

- concentração de organizações;
- dispersão;
- assimetria;
- extremos;
- presença de outliers.

## Insights Automáticos

A função `generateInsights` produz textos automáticos com:

- variável mais crítica;
- variável mais forte;
- dimensão mais homogênea;
- dimensão mais dispersa;
- maior correlação com a raiz;
- dependência não linear mais forte;
- variável mais estruturante;
- cluster mais crítico;
- qualidade média dos clusters;
- quantidade de organizações atípicas.

Critérios:

- variável crítica: menor média;
- variável forte: maior média;
- homogênea: menor desvio padrão;
- dispersa: maior coeficiente de variação;
- maior correlação com raiz: maior `abs(Pearson)` contra a raiz;
- dependência não linear mais forte: maior Mutual Information entre pares;
- variável estruturante: combinação ponderada de correlação com a raiz, correlação média, MI média e importância PCA;
- cluster crítico: menor média do índice raiz;
- atípicas: total de outliers por IQR ou distância ao centroide.

## Análise Temporal

A aplicação tenta detectar colunas de ciclo nas linhas brutas importadas:

- `ano`;
- `ciclo`;
- `year`;
- `survey_year`;
- `periodo`;
- `período`.

Se houver dois ou mais ciclos, o painel temporal mostra evolução média por ciclo. Se não houver, exibe mensagem explícita de indisponibilidade.

## Renderização Visual

A interface preserva a identidade da calculadora:

- cabeçalho escuro;
- destaque em `--accent`;
- painéis brancos;
- bordas discretas;
- cards com sombra leve;
- tabelas com cabeçalho fixo;
- grids responsivos.

A aba analítica adiciona:

- cards executivos;
- textos de ajuda em cada card, explicando a finalidade da análise e como interpretar os resultados;
- controles compactos;
- painéis em grid de 12 colunas;
- gráficos Plotly responsivos;
- tabelas avançadas;
- rede de dependências;
- radar comparativo;
- heatmaps;
- gráficos de distribuição.

## Responsividade

Em telas menores:

- a calculadora volta para uma coluna;
- os cards analíticos ocupam largura total;
- controles analíticos passam para 2 colunas;
- em telas muito estreitas, controles passam para 1 coluna;
- a barra de abas permite rolagem horizontal.

## Comportamento Sem Bibliotecas Externas

Se Plotly não estiver carregado, a aba estatística exibe mensagem de erro e não tenta desenhar gráficos.

Se `tsne-js` não estiver carregado ou falhar, a projeção não linear usa PCA 2D como fallback.

O cálculo principal do índice não depende de Plotly nem de t-SNE. Portanto, a calculadora continua funcionando mesmo que as bibliotecas analíticas não carreguem.

## Solicitações Implementadas

Durante a evolução desta página foram implementadas as seguintes solicitações:

### Diagrama de Árvore

Foi adicionado um diagrama SVG interativo da estrutura do índice:

- renderização da raiz;
- agregados;
- questões;
- links;
- seleção de nós;
- detalhe do nó;
- caminho ativo;
- expandir/recolher;
- centralizar.

### Exportação da Árvore

Foram adicionadas exportações:

- `.svg`;
- `.png`.

### Validação de Pesos

Cada agregado passou a ser validado para assegurar que a soma dos pesos seja `1`.

Se a soma divergir:

- o painel de validações mostra erro;
- o nó da árvore textual fica em alerta;
- o nó do diagrama fica em alerta;
- a mensagem detalhada informa a soma encontrada.

### Agregados Avulsos

Foi adicionada flag para renderizar agregados não conectados à raiz.

Eles são exibidos como árvores desconectadas da árvore principal.

### Correção de Identificadores `ext`

Foi corrigido o problema em que colunas como `q2501ext[A]` eram normalizadas para `q2501A`.

A aplicação agora preserva `ext[A]` e cria aliases compatíveis.

### Categorias LimeSurvey

A seção `categorias` do YAML embutido foi ajustada para aceitar códigos reais exportados pelo LimeSurvey:

- `naoad`;
- `adfor`;
- `admen`;
- `adpar`;
- `admai`;
- `naoap`;
- `sim`;
- `nao`.

### Deflação com Códigos LimeSurvey

A função `calculateQuestion` passou a reconhecer `admai` e `adpar` para aplicar corretamente a deflação por subitens.

### Sistema de Abas

Foi criado sistema de abas:

1. Calculadora;
2. Resultados;
3. Análises Estatísticas.

### Plataforma Analítica

Foi adicionada a aba **Análises Estatísticas**, com:

- estatística descritiva;
- correlações;
- Mutual Information;
- PCA;
- K-Means;
- DBSCAN;
- clustering hierárquico;
- t-SNE;
- UMAP;
- benchmarking;
- outliers;
- outliers por variável;
- análise de desequilíbrio interno;
- exploração individual;
- comparação entre organizações;
- radar chart;
- distribuições;
- densidade;
- análise temporal condicional;
- insights automáticos;
- exportações CSV/JSON.

## Limitações Conhecidas

- A aplicação é client-side; planilhas muito grandes podem consumir memória e deixar o navegador lento.
- O t-SNE roda no navegador e pode ser custoso em bases grandes.
- Mutual Information usa discretização simples em 5 bins.
- O K-Means usa inicialização determinística simples, não K-Means++.
- A PCA implementada usa iteração de potência e extrai até 3 componentes, suficiente para visualização e explicabilidade inicial.
- A análise usa por padrão agregados e raiz; questões detalhadas entram apenas quando o usuário seleciona “Tudo numérico”.

## Validações Realizadas

Foram feitas validações com Chrome em modo headless:

- carregamento do HTML sem `TypeError`, `ReferenceError` ou `SyntaxError`;
- renderização inicial das abas;
- manutenção do grid original da calculadora;
- renderização da aba estatística com dados sintéticos;
- geração de gráficos Plotly;
- renderização de cards, insights, heatmap, rede, ranking e PCA.

## Arquivo Principal

Toda a aplicação está em:

```text
calcula-igovti/index.html
```

Este README documenta o comportamento implementado nessa página.
