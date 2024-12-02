#' =============================================================================
#' PROJETO: TCC - Machine learning em criacao de contrafactual
#' 
#' AUTOR: Pedro Borges de Melo Filho
#' 
#' DATA: 27/11/2024
#' 
#' MODIFICACOES:
#' =============================================================================

rm(list = ls())

# ==============================================================================


# ==============================================================================
# Lista de pacotes a serem carregados
packages <- c('dplyr',"stringr", "readxl",'janitor')

# checando se os pacotes estao instalados e baixando-os, caso nao estajam
for (package in packages) {
  if (!require(package, character.only = TRUE)) {
    install.packages(package)
    require(package,character.only = TRUE)
  }
}

rm(package, packages)

# lendo dados ==================================================================

# Define o caminho para a pasta onde os dados brutos estão armazenados
caminho <- "G:/Meu Drive/Cases/case_MT2-Data/dados/dados_brutos/" 

# Lendo dados de licenciamento
# Lê o arquivo "SeriesTemporais_Autoveiculos.xlsm" e armazena na variável 'licen'
licen <- read_xlsx(paste0(caminho, "SeriesTemporais_Autoveiculos.xlsm")) 

# Lendo series macro
# Cria uma lista chamada 'series_macro' contendo os dados macroeconômicos
series_macro <- list(
  'pib'       = read.csv2( paste0(caminho, "pib.csv")        ),
  'selic'     = read.csv2( paste0(caminho, "selic.csv")      ),
  'tx_cambio' = read.csv2( paste0(caminho, "tx_cambio.csv")  ),
  'prod_ind'  = read.csv2( paste0(caminho, "prod_indus.csv") ),
  'infl'      = read.csv2( paste0(caminho, "igp-m.csv")      ) 
)


# Aplica uma função a cada dataframe na lista 'series_macro'
series_macro <- lapply(series_macro, function(df) {
  
  # Remove colunas vazias do dataframe
  df <- remove_empty(df, which = 'cols') %>% 
    
    # Filtra os dados para o período entre 2014 e setembro de 2024
    filter( (Data >= 2014)  & (Data <= 2024.09) ) %>% 
    
    # Renomeia a segunda coluna do dataframe para 'valor'
    rename(valor = names(df)[2])
})


# corrigindo inflacao ---------------------------
# obtendo valor da inflacao
infl <- series_macro[['infl']]$valor / 100

# tranformando as taxas mensais negativas em deflacao calculavel
infla_calculo <- ifelse(infl < 0, 1/(abs(infl) + 1) ,1 + infl)

# obetendo o valor de deflação comparado ao ultimo mes da obs 2024.09
infla_cum_2024_09 <- rev(cumprod( rev(infla_calculo) ))

# aplicando deflacao no pib
series_macro[["pib"]]$valor <- infla_cum_2024_09 * series_macro[["pib"]]$valor


# modificando a de licenciamento --------------------------
# Manipula o dataframe 'licen'
base <- licen %>% 
  
  # Filtra os dados para o período a partir de janeiro de 2014
  filter(mes_ano >= '2014-01-01') %>% 
  
  # Renomeia a coluna 'Licenciamento Total' para 'licen'
  rename(licen = `Licenciamento Total`) %>% 
  
  # Seleciona apenas as colunas 'mes_ano' e 'licen'
  select(mes_ano,licen) %>% 
  
  # Adiciona as var macro ao dataframe
  mutate( 
    pib        = series_macro[['pib']]$valor,      
    selic      = series_macro[['selic']]$valor,    
    tx_cambio = series_macro[['tx_cambio']]$valor, 
    prod_ind  = series_macro[['prod_ind']]$valor,  
    infl      = series_macro[['infl']]$valor,
    
    # Var de tempo em formato de data
    mes_ano   = as.Date(mes_ano)
  ) 

# Aplicando o teste KPSS com a hipótese nula de estacionariedade em torno de uma tendência
library(tseries)
# Objeto ts com seus dados, definindo a frequência
serie_licen <- ts(base$licen, frequency = 12, start = c(2014, 1))
kpss.test(serie_licen, null = "Trend")









