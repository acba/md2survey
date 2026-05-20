library(readxl)
library(tidyr)
library(dplyr)
library(psych)
library(stringr)
library(writexl)

gera_modelos <- function(){
  iGG2021_resultados_TCU <- read_excel("dados/iGG2021_resultados_TCU.xlsx")
  
  df_agregados <- tibble(
    
    ResultadoTI = list(c('2123', '3132', '3133')),
    ModeloTI = list(c('2133')),
    MonitorAvaliaTI = list(c('2153', '3142D', '3142E')),
    PessoasTI = list(c('4121', '4122', '4131', '4151', '4172')),
    PlanejamentoTI = list(c('4211', '4212')),
    iGestServicosTI = list(c('4221', '4222', '4223', '4224')),
    iGestNiveisServicoTI = list(c('4231')),
    iGestRiscosTI = list(c('4241', '4242', '2111', '2112', '2113', '2114', '2115')),
    EstruturaSegInfo = list(c('4251', '4252', '4253')),
    ProcessoSegInfo = list(c('4261', '4262', '4263', '4264', '4265', '4266')),
    ProcessoSoftware = list(c('4271')),
    iGestProjetosTI = list(c('4281')),
    iGestContratosTI = list(c('4352', '4361A', '4362A')),
    GovernancaTI = list(c('ModeloTI',	'MonitorAvaliaTI',	'ResultadoTI')),
    iGestSegInfo = list(c('EstruturaSegInfo',	'ProcessoSegInfo', '2115', '4242', '4271F', '3142E')),
    ProcessosTI = list(c('iGestServicosTI', 'iGestNiveisServicoTI',
                         'iGestRiscosTI', 'iGestSegInfo', 'ProcessoSoftware',
                         'iGestProjetosTI', 'iGestContratosTI')),
    iGestTI = list(c('PlanejamentoTI', 'PessoasTI', 'ProcessosTI')),
    iGovTI = list(c('GovernancaTI', 'iGestTI'))
  )
  
  modelos <- list()
  agregados <- names(df_agregados)
  for(i in 1:length(agregados)){
    
    agregado_nome <- agregados[i]
    agregado_vars <- unlist(df_agregados[[i]])
    
    mat_dados_agregados <- iGG2021_resultados_TCU %>%
      select(matches(paste0('^', as.character(agregado_vars), '$'))) %>% 
      as.matrix()
    
    modelo_pca <- principal(mat_dados_agregados)
    
    modelo <- tibble(
      variaveis = agregado_vars,
      media = colMeans(mat_dados_agregados),
      carga = as.numeric(modelo_pca$loadings),
      peso = carga/sum(carga)
    )
    
    attr(modelo, 'nome') <- agregado_nome
    attr(modelo, 'var_total_explicada') <- modelo_pca$Vaccounted[2]
    
    modelos[[as.name(agregado_nome)]] <- modelo
  }
  
  return(modelos)
}

conversao_nomenclatura_tcerj_tcu <- function(df_dados){
  df_conversao <- tribble(
    ~tcu, ~tce,
    #PlanejamentoTI
    4211, 2111,
    4212, 2112,
    #PessoasTI
    4121, 2211,
    4122, 2212,
    4123, 2213,
    4131, 2221,
    4151, 2231,
    4172, 2241,
    #iGestServicosTI
    4221, 2121,
    4222, 2122,
    4223, 2123,
    4224, 2124, 
    #iGestNiveisServicosTI
    4231, 2131,
    #iGestRiscosTI
    4241, 2141,
    4242, 2142,
    2111, 2146,
    2112, 2147,
    2113, 2143,
    2114, 2144,
    2115, 2145,
    #EstruturaSegInfo
    4251, 2151,
    4252, 2152,
    4253, 2153,
    #ProcessoSegInfo
    4261, 2161,
    4262, 2162,
    4263, 2163,
    4264, 2164,
    4265, 2165,
    4266, 2166,
    #ProcessoSoftware
    4271, 2171,
    #iGestProjetosTI
    4281, 2181,
    #iGestContratosTI
    4352, 2311,
    4361, 2321,
    4362, 2322,
    #ModeloTI
    2133, 1111,
    #MonitoraAvaliaTI
    2153, 1121,
    3142, 1122,
    #ResultadoTI
    2123, 1133,
    3132, 1131,
    3133, 1132
  )
  
  df_dados <- df_dados %>% 
    select(matches("\\d{4}")) %>% 
    select(-matches("lei")) %>% 
    select(-matches("est")) %>% 
    select(-matches("evi")) %>% 
    select(-matches("nsa")) %>% 
    select(-matches("raz")) %>% 
    rename_with(function(x){gsub("\\.", "", x)}) %>% 
    rename_with(function(x){gsub("\\[", "", x)}) %>%
    rename_with(function(x){gsub("\\]", "", x)}) %>% 
    rename_with(function(x){gsub("ext", "", x)})
  
  
  for(i in 1:nrow(df_conversao)){
    df_dados <- df_dados %>% 
      rename_with(function(x){
        gsub(pattern = as.character(paste0('q',df_conversao$tce[i])),
             replacement = as.character(df_conversao$tcu[i]),
             x = as.character(x))})
  }

  df_dados[df_dados == 'N/A'] <- '0'
  df_dados[df_dados == 'Nao'] <- '0'
  df_dados[df_dados == 'Não'] <- '0'
  df_dados[df_dados == 'Sim'] <- '1'
  df_dados <- df_dados %>%
    mutate_at(vars(matches("[A-Z]", ignore.case = F)), as.numeric)

  return(df_dados)
}


calcula_valor_questao <- function(id_questao, df_todas_questoes){
  
  if(id_questao == '3142'){
    a <- 0
    print('aaaaa')
  }
  df_dados_questao <- df_todas_questoes %>% 
    select(contains(as.character(id_questao)))
  
  
  # Obs1.: remove os pontos finais, caso existam, da coluna dddd (1ª col.) para que correspondam aos valores
  # do vetor `niveis`, definido abaixo.
  
  df_dados_questao <- df_dados_questao %>% 
    mutate_at(vars(matches(paste0('^', id_questao, "$"))), function(x){str_replace_all(x, '\\.', '')})  # operação descrita em Obs1.
  
  niveis <- c("Não adota" = 0.00,
              "Há decisão formal ou plano aprovado para adotá-lo" = 0.05,
              "Adota em menor parte" = 0.15,
              "Adota parcialmente" = 0.50,
              #"Nao se aplica" = 1.00001, # Não se aplica ajustado para não fazer a deflação
              "Não se aplica" = 0.5000001, # adota-se a opção conservadora de se considerar consistente a justificativa
              
              #"Nao se aplica" = 0.50, # adota-se a opção conservadora de se considerar consistente a justificativa
              # dada para a não aplicabilidade,
              "Adota" = 1.00,
              "Adota em maior parte ou totalmente" = 1.00)
  
  # cria uma coluna `valor` com o valor inicial da questão, de acordo com os valores definidos no vetor `niveis`
  df_dados_questao <- df_dados_questao %>% 
    mutate_at(vars(matches(paste0('^', id_questao, "$"))), function(x){niveis[.[[1]]]})
  
  num_questoes_adicionais <- sum(grepl('[A-Z]$', names(df_dados_questao)))
  
  if(num_questoes_adicionais > 0){
    
    # Obs2.: uma questão adicional "nenhuma das opções acima se adequam" foi incluída, por segurança", para se
    # assegurar de que o jurisdicionado não iria, despercebidamente, deixar as questões adicionais em branco
    # por isso ela deve ser retirada. 
    
    df_dados_questao <- df_dados_questao %>% 
      select(-matches(paste0(LETTERS[num_questoes_adicionais+1], "$"))) # operação descrita em Obs2.
    
    
    # função que aplica a deflação ao valor inicial, de acordo com as respostas às questões adicionais
    desconta_valor <- function(questoes_adicionais, desconto_total){
      
      num_questoes_adicionais <- length(questoes_adicionais)
      questoes_adicionais_inv = 1 - questoes_adicionais
      
      desconto_por_questao_adicional <- desconto_total/num_questoes_adicionais
      
      sum(questoes_adicionais_inv) * desconto_por_questao_adicional
    }
    
    df_dados_questao <- df_dados_questao %>%
      rowwise() %>%
      mutate_at(vars(matches(paste0('^', id_questao, "$"))), function(x){case_when(
        (x == 0.5000001) ~ 0.5, #Converte a pontuação do "Não se aplica" para 0.5 e não aplica deflação
        (x == 1.00) ~ x + desconta_valor(c_across(matches('[A-Z]')), -0.85),
        (x == 0.50) ~ x + desconta_valor(c_across(matches('[A-Z]')), -0.35),
        T ~ x)})
    
    # df_dados_questao <- df_dados_questao %>%
    #   rowwise() %>%
    #   mutate_at(vars(matches(paste0('^', id_questao, "$"))), function(x){x-1})
  }
  
  return(df_dados_questao)
}


calcula_agregacoes <- function(modelos, dados){
  
  agregacoes <- list()
  pesos <- list()
  cargas <- list()
  medias <- list()
  
  for(i in 1:length(modelos)){
    modelo <- modelos[[i]]
    
    nome_agregacao <- attr(modelo, 'nome')
    variaveis_agregadas <- modelo$variaveis
    
    mat_dados_agregacao <- dados %>%
      select(matches(paste0('^', as.character(variaveis_agregadas), '$'))) %>% 
      as.matrix()
    
    valor <- mat_dados_agregacao %*% modelo$peso
   
    dados[nome_agregacao] <- valor
    
    # agregacao <- dados %>% 
    #   select(matches(paste0('^', c('Jurisdicionado', nome_agregacao, variaveis_agregadas), '$'))) %>% 
    #   gather(key = 'nome', value = 'valor', -Jurisdicionado) %>% 
    #   mutate(nivel = cut(valor,
    #                      c(0.00, 0.15, 0.40, 0.70, 1.00),
    #                      c('INE', 'INI', 'INT', 'APR'),
    #                      include.lowest = T,
    #                      right = F),
    #          nome = factor(nome, 
    #                        levels = c(nome_agregacao, variaveis_agregadas),
    #                        ordered = T))
    # 
    # 
    # 
    # agregacoes[[as.name(nome_agregacao)]] <- agregacao
    pesos[[as.name(nome_agregacao)]] <- modelo$peso
    medias[[as.name(nome_agregacao)]] <- modelo$media
    cargas[[as.name(nome_agregacao)]] <- modelo$carga
  }
  
  list(dados = dados, agregacoes = agregacoes,
       pesos = pesos, medias = medias, cargas = cargas)
}
