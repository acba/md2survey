source('utils.R')

# Calcula os agregados e seus pesos
modelos <- gera_modelos()

df_municipios_tcerj_bruto <- read_excel("dados/resposta_questionario_municipios_tcerj.xlsx")
df_municipios_tcerj <- conversao_nomenclatura_tcerj_tcu(df_municipios_tcerj_bruto)

id_questoes <- str_extract_all(string = names(df_municipios_tcerj), '^\\d{4}$') %>%
  unlist() %>% 
  unique()

df_dados_processados <- NULL
for(id_questao in id_questoes){
  print(id_questao)
  df_dados_processados <- df_dados_processados %>% 
    bind_cols(calcula_valor_questao(id_questao, df_municipios_tcerj))
}

df_dados_processados <- cbind(Jurisdicionado = c('MARICA', 'RIO DAS OSTRAS', 'SAQUAREMA', 'VOLTA REDONDA'), df_dados_processados)

resultados <- calcula_agregacoes(modelos, df_dados_processados)

write_xlsx(resultados$dados,"igovti.xlsx")
