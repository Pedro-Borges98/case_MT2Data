import pandas as pd
from pathlib import Path

def get_reg_data(base_sarimax_path: str, proj_exog_path: str) -> pd.DataFrame:
    """
    Carrega as bases de dados, combina-as e adiciona uma variável CALC para indicar se os dados são calculados.

    Args:
        base_sarimax_path (str): Caminho para a base SARIMAX.
        proj_exog_path (str): Caminho para a base de projeções exógenas.

    Returns:
        pd.DataFrame: DataFrame combinado com a coluna CALC.
    """
    # Carregar as bases de dados com vírgula como separador decimal
    base_sarimax = pd.read_csv(base_sarimax_path, sep=';', decimal=',')
    proj_exog = pd.read_csv(proj_exog_path, sep=';', decimal=',')
    
    # Renomear colunas da base de projeções exógenas para manter o padrão da base SARIMAX
    proj_exog = proj_exog.rename(columns={
        "data": "mes_ano",
        "sel": "selic",
        "cam": "tx_cambio",
        "ind": "prod_ind",
        "inf": "infl"
    })
    
    # Adicionar a coluna CALC para identificar as projeções exógenas
    base_sarimax['CALC'] = False
    proj_exog['CALC'] = True
    
    # Combinar as bases
    combined_df = pd.concat([base_sarimax, proj_exog], ignore_index=True)
    
    # Garantir que as colunas numéricas sejam float
    numeric_columns = ["pib", "selic", "tx_cambio", "prod_ind", "infl"]
    combined_df[numeric_columns] = combined_df[numeric_columns].apply(pd.to_numeric, errors="coerce")

    # Ordenar por mes_ano
    combined_df = combined_df.sort_values(by='mes_ano').reset_index(drop=True)
    
    return combined_df
