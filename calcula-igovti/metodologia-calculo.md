# Metodologia de Calculo do iGovTI 2026

Este documento descreve, de forma autocontida, como é calculado o iGovTI 2026. Ele apresenta as regras de conversão das respostas, a árvore completa do índice, os pesos de cada componente, as fórmulas de agregação e os intervalos usados para classificar o nível de maturidade.

## Resumo

O iGovTI 2026 é um índice composto, calculado para cada organização a partir das respostas ao questionário. Cada resposta categórica é primeiro convertida para um valor numérico normalizado, em geral entre `0` e `1`. Em seguida, questões, subitens e agregados são combinados por somas ponderadas até chegar ao valor final do índice.

O índice final é formado por dois grandes componentes:

| Componente | Peso no iGovTI |
|---|---:|
| `GovernancaTI` | `0.477696299232863` |
| `iGestTI` | `0.522303700767137` |

`GovernancaTI` consolida quatro questões de governança. `iGestTI` consolida seis dimensões de gestão: planejamento, serviços, riscos de TI e segurança da informação, estrutura de segurança da informação, processo de segurança da informação e gestão de soluções de TI.

O resultado final do `iGovTI` varia de `0` a `1` e é classificado em quatro níveis de maturidade:

| Nível | Intervalo |
|---|---|
| `Inexpressivo` | `0 <= iGovTI < 0.15` |
| `Iniciando` | `0.15 <= iGovTI < 0.4` |
| `Intermediário` | `0.4 <= iGovTI < 0.7` |
| `Aprimorado` | `0.7 <= iGovTI <= 1` |

Em síntese, o cálculo segue esta sequência:

1. identificar a organização respondente;
2. selecionar as colunas que representam questões calculáveis;
3. converter respostas categóricas em valores numéricos;
4. recalcular questões com subitens quando houver regra de deflação;
5. calcular todos os agregados por soma ponderada;
6. calcular o `iGovTI`;
7. classificar o resultado em um nível de maturidade.

## Identificação do Índice

A raiz `iGovTI` é o resultado final calculado para cada organização. Todos os demais agregados e questões alimentam essa raiz por soma ponderada.

| Campo | Valor |
|---|---|
| Nome do índice | `iGovTI` |
| Ano/metodologia | `2026` |
| Raiz do cálculo | `iGovTI` |
| Regra de pontuação para "Não se aplica" | `0.5` |

## Visão Geral da Arvore do Índice

A árvore principal do iGovTI 2026 tem dois blocos:

```text
iGovTI
├── GovernancaTI
└── iGestTI
    ├── PlanejamentoTI
    ├── ServicosTI
    ├── RiscosTISegInfo
    ├── EstruturaSegInfo
    ├── ProcessoSegInfo
    └── GerirSoluçõesTI
```

O agregado `ProcessoSegInfo` possui agregados auxiliares intermediários para representar o cálculo especial de itens derivados da questão `q2501`:

```text
ProcessoSegInfo
├── _q4251(TCU)
│   ├── _q4251ext[A](TCU)
│   │   ├── q2501ext[A]
│   │   └── q2501ext[C]
│   └── q2502
├── q2503
└── q2504
```

## Conversão das Respostas em Valores Numericos

Antes do cálculo dos agregados, cada resposta do questionário é convertida para um valor numérico normalizado, normalmente no intervalo de `0` a `1`.

### Categorias de Adoção

| Código ou rótulo | Valor |
|---|---:|
| `naoad`, `Não adota`, `Não adota.` | `0` |
| `adfor`, `Há decisão formal ou plano aprovado para adotá-lo`, `Há decisão formal ou plano aprovado para adotá-lo.` | `0.05` |
| `admen`, `Adota em menor parte`, `Adota em menor parte.` | `0.15` |
| `adpar`, `Adota parcialmente`, `Adota parcialmente.` | `0.5` |
| `admai`, `Adota`, `Adota em maior parte ou totalmente`, `Adota em maior parte ou totalmente.` | `1` |
| `naoap`, `Não se aplica`, `Não se aplica.` | `0.5` |

### Categorias Sim/Não

| Código ou rótulo | Valor |
|---|---:|
| `sim`, `Sim` | `1` |
| `nao`, `Não`, `Nao` | `0` |
| `N/A` | `0` |

### Regras Gerais de Normalização

Para cada célula de resposta:

1. valor vazio, `null` ou ausente vira `0`;
2. número já informado na planilha é preservado;
3. texto ou código é procurado na tabela de categorias desta metodologia;
4. se o texto terminar com ponto final, a aplicação também tenta a versão sem ponto;
5. se não houver categoria correspondente, a aplicação tenta converter o texto para número;
6. se não for possível converter, o valor bruto é mantido, mas ele não deve alimentar agregados numéricos.

## Colunas Consideradas no Calculo

A aplicação considera como questão apenas colunas cujo nome contenha um número de quatro dígitos, por exemplo:

```text
q1001
q2501ext[A]
2501ext[C]
```

Campos auxiliares são ignorados mesmo quando contêm número de questão. São ignoradas colunas com os seguintes padrões:

| Padrão ignorado | Uso típico |
|---|---|
| `lei` | referência legal |
| `est` | estado/status auxiliar |
| `evi` | evidência anexada |
| `nsa` | justificativa de não se aplica |
| `raz` | razão/justificativa |
| `SQ` | metadados técnicos do LimeSurvey |

Assim, evidências, justificativas e textos auxiliares não entram diretamente no cálculo numérico do iGovTI.

## Identificação da Organização

Cada linha da planilha representa uma organização ou respondente. A calculadora tenta identificar a organização nesta ordem:

1. `firstname`
2. `attribute_1`
3. `orgao`
4. `órgão`
5. `entidade`
6. `auditado`
7. `name`
8. `id`
9. primeira coluna da planilha, se nenhuma das anteriores existir

No fluxo atual, `firstname` é priorizado porque tende a ser o identificador legível das organizações nas exportações usadas.

## Tratamento de Questões com Subitens

Algumas questões podem ter uma resposta base e subitens, por exemplo:

```text
q2501
q2501ext[A]
q2501ext[C]
```

Primeiro, todos os valores são normalizados. Depois, se uma questão base `qNNNN` possui subitens com o mesmo prefixo, a aplicação pode recalcular a pontuação da questão base.

### Quando Há Deflação

A deflação só ocorre se a questão base indicar:

| Situação da resposta base | Códigos ou rótulos reconhecidos | Desconto máximo |
|---|---|---:|
| Adoção em maior parte ou totalmente | `admai`, `Adota`, `Adota em maior parte ou totalmente`, `Adota em maior parte ou totalmente.` | `0.85` |
| Adoção parcial | `adpar`, `Adota parcialmente`, `Adota parcialmente.` | `0.35` |

Se a questão não tiver subitens, ou se a resposta base não for uma dessas situações, a pontuação da questão base é simplesmente o valor normalizado da própria resposta.

### Formula da Deflação

Para uma questão base com `n` subitens:

```text
missing = soma(1 - valor_do_subitem)
score = valor_base - ((missing * desconto_maximo) / n)
score_final = limitar(score, 0, 1)
```

Interpretação:

- subitem com valor `1` não reduz a pontuação;
- subitem com valor `0` reduz a pontuação;
- quanto mais subitens não atendidos, maior a deflação;
- a deflação máxima depende do grau de adoção declarado na questão base.

## Aliases de Questões

Para lidar com variações de nomenclatura nas exportações do LimeSurvey e na estrutura de cálculo, a aplicação cria aliases equivalentes:

| Forma original | Aliases possíveis |
|---|---|
| `q2501ext[A]` | `q2501A` |
| `q2501[A]` | `q2501A` |
| `q2501A` | `q2501[A]`, `q2501ext[A]` |

Isso permite que a estrutura de cálculo encontre a questão mesmo quando a planilha usa uma forma ligeiramente diferente. Os aliases servem apenas para localização do valor; eles não duplicam o peso da questão.

## Formula Geral dos Agregados

Todo agregado é calculado como soma ponderada de seus componentes:

```text
Agregado = soma(valor_componente_i * peso_i)
```

Depois da soma, o valor é limitado ao intervalo `[0, 1]`.

Os componentes podem ser:

- questões normalizadas, como `q1001`;
- subitens, como `q2501ext[A]`;
- agregados intermediários, como `GovernancaTI`;
- agregados auxiliares, como `_q4251(TCU)`.

Todos os pesos de cada agregado devem somar `1`, admitida apenas pequena tolerância numérica de ponto flutuante.

## Calculo da Governança de TI

`GovernancaTI` é calculado diretamente a partir de quatro questões.

| Componente | Peso |
|---|---:|
| `q1001` | `0.327403834851957` |
| `q1002` | `0.275682914168293` |
| `q1003` | `0.153597864756459` |
| `q1004` | `0.243315386223291` |

Fórmula:

```text
GovernancaTI =
  q1001 * 0.327403834851957
+ q1002 * 0.275682914168293
+ q1003 * 0.153597864756459
+ q1004 * 0.243315386223291
```

## Calculo dos Subagregados de Gestão de TI

### PlanejamentoTI

| Componente | Peso |
|---|---:|
| `q2101` | `0.502245016099551` |
| `q2102` | `0.497754983900449` |

```text
PlanejamentoTI =
  q2101 * 0.502245016099551
+ q2102 * 0.497754983900449
```

### ServicosTI

| Componente | Peso |
|---|---:|
| `q2201` | `0.243988021274905` |
| `q2202` | `0.241081341165387` |
| `q2203` | `0.262416152533095` |
| `q2204` | `0.252514485026613` |

```text
ServicosTI =
  q2201 * 0.243988021274905
+ q2202 * 0.241081341165387
+ q2203 * 0.262416152533095
+ q2204 * 0.252514485026613
```

### RiscosTISegInfo

| Componente | Peso |
|---|---:|
| `q2301` | `0.313583824988742` |
| `q2302` | `0.334855010417522` |
| `q2303` | `0.351561164593736` |

```text
RiscosTISegInfo =
  q2301 * 0.313583824988742
+ q2302 * 0.334855010417522
+ q2303 * 0.351561164593736
```

### EstruturaSegInfo

| Componente | Peso |
|---|---:|
| `q2401` | `0.352918884966675` |
| `q2402` | `0.314480446156258` |
| `q2403` | `0.332600668877067` |

```text
EstruturaSegInfo =
  q2401 * 0.352918884966675
+ q2402 * 0.314480446156258
+ q2403 * 0.332600668877067
```

### ProcessoSegInfo

`ProcessoSegInfo` usa dois agregados auxiliares antes da composição final.

Primeiro, calcula-se `_q4251ext[A](TCU)`:

| Componente | Peso |
|---|---:|
| `q2501ext[A]` | `0.5` |
| `q2501ext[C]` | `0.5` |

```text
_q4251ext[A](TCU) =
  q2501ext[A] * 0.5
+ q2501ext[C] * 0.5
```

Depois, calcula-se `_q4251(TCU)`:

| Componente | Peso |
|---|---:|
| `_q4251ext[A](TCU)` | `0.166666666666667` |
| `q2502` | `0.833333333333333` |

```text
_q4251(TCU) =
  _q4251ext[A](TCU) * 0.166666666666667
+ q2502 * 0.833333333333333
```

Por fim, calcula-se `ProcessoSegInfo`:

| Componente | Peso |
|---|---:|
| `_q4251(TCU)` | `0.375836866199098` |
| `q2503` | `0.301047566345608` |
| `q2504` | `0.323115567455294` |

```text
ProcessoSegInfo =
  _q4251(TCU) * 0.375836866199098
+ q2503 * 0.301047566345608
+ q2504 * 0.323115567455294
```

### GerirSoluçõesTI

| Componente | Peso |
|---|---:|
| `q2601` | `0.509278560342789` |
| `q2602` | `0.490721439657210` |

```text
GerirSoluçõesTI =
  q2601 * 0.509278560342789
+ q2602 * 0.490721439657210
```

## Calculo do iGestTI

`iGestTI` consolida os seis subagregados de gestão.

| Componente | Peso |
|---|---:|
| `PlanejamentoTI` | `0.153402950545233` |
| `ServicosTI` | `0.185165801954126` |
| `RiscosTISegInfo` | `0.163182752556826` |
| `EstruturaSegInfo` | `0.157769302046022` |
| `ProcessoSegInfo` | `0.182134616637340` |
| `GerirSoluçõesTI` | `0.158344576260455` |

Fórmula:

```text
iGestTI =
  PlanejamentoTI * 0.153402950545233
+ ServicosTI * 0.185165801954126
+ RiscosTISegInfo * 0.163182752556826
+ EstruturaSegInfo * 0.157769302046022
+ ProcessoSegInfo * 0.182134616637340
+ GerirSoluçõesTI * 0.158344576260455
```

## Calculo Final do iGovTI

O iGovTI 2026 combina governança e gestão com os seguintes pesos:

| Componente | Peso |
|---|---:|
| `GovernancaTI` | `0.477696299232863` |
| `iGestTI` | `0.522303700767137` |

Fórmula final:

```text
iGovTI =
  GovernancaTI * 0.477696299232863
+ iGestTI * 0.522303700767137
```

Como `GovernancaTI` e `iGestTI` também são resultados entre `0` e `1`, o `iGovTI` final também fica limitado ao intervalo `[0, 1]`.

## Classificação de Maturidade

Após calcular o valor final do `iGovTI`, a organização é classificada conforme os intervalos definidos nesta metodologia.

| Nível | Intervalo |
|---|---|
| `Inexpressivo` | `0 <= iGovTI < 0.15` |
| `Iniciando` | `0.15 <= iGovTI < 0.4` |
| `Intermediário` | `0.4 <= iGovTI < 0.7` |
| `Aprimorado` | `0.7 <= iGovTI <= 1` |

Se o valor não se enquadrar em nenhum intervalo, a aplicação retorna `Sem classificação`.

## Memoria de Calculo

Para cada organização, a aplicação produz uma memória de cálculo contendo, para cada agregado:

- identificador do componente;
- peso aplicado;
- valor do componente;
- contribuição ponderada (`valor * peso`).

Exemplo conceitual:

```json
{
  "iGovTI": [
    {
      "id": "GovernancaTI",
      "peso": 0.477696299232863,
      "value": 0.72,
      "contribution": 0.34394133544766136
    },
    {
      "id": "iGestTI",
      "peso": 0.522303700767137,
      "value": 0.68,
      "contribution": 0.35516651652165316
    }
  ]
}
```

Essa memória alimenta a árvore de cálculo, o diagrama visual e as exportações de resultados.

## Exemplo de Ordem de Processamento

Para cada linha da planilha:

1. identificar a organização;
2. selecionar colunas de questões válidas;
3. normalizar respostas categóricas e numéricas;
4. recalcular questões base que tenham subitens e exijam deflação;
5. criar aliases de questões para compatibilidade de nomes;
6. calcular recursivamente todos os agregados necessários;
7. calcular a raiz `iGovTI`;
8. classificar o nível de maturidade;
9. gravar os valores e a memória de cálculo.

## Observações Importantes

- Evidências anexadas e justificativas textuais não entram diretamente no cálculo do índice.
- O valor `Não se aplica` é convertido para `0.5`, conforme definido na tabela de categorias.
- A árvore do índice é definida pelos componentes e pesos descritos neste relatório; alterar componentes ou pesos altera o cálculo.
- Os nomes com acento, como `GerirSoluçõesTI`, devem ser preservados nos relatórios para evitar divergência entre identificadores.
- Agregados auxiliares iniciados por `_`, como `_q4251(TCU)`, são nós de cálculo intermediário e não níveis de maturidade independentes.
- Todos os agregados são calculados por soma ponderada e limitados ao intervalo `[0, 1]`.
