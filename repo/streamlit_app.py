import streamlit as st
import pandas as pd
import plotly.express as px
from src.get_reg_data import get_reg_data

# Configuração da página
st.set_page_config(
    page_title="Case MT2 Data - Emplacamentos",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

# Função para calcular previsões ajustadas
def calculate_forecast(data: pd.DataFrame, adjustments: dict) -> pd.DataFrame:
    adjusted_data = data.copy()
    for key, value in adjustments.items():
        if value is not None:
            adjusted_data.loc[adjusted_data['CALC'], key] = value
    return adjusted_data

# Leitura e preparação dos dados
BASE_SARIMAX_PATH = 'data/base_sarimax.csv'
PROJ_EXOG_PATH = 'data/proj_exog_fut.csv'
data = get_reg_data(BASE_SARIMAX_PATH, PROJ_EXOG_PATH)

# Barra lateral para navegação
st.sidebar.title("Navegação")
page = st.sidebar.radio("Selecione uma página:", ["Séries Históricas", "Simulação What If"])

# ------------------------------------------------------------------------
# Página: Séries Históricas
# ------------------------------------------------------------------------
if page == "Séries Históricas":
    st.header("Séries Históricas")
    st.markdown(
        """
        Visualize as séries históricas de emplacamentos reais e as variáveis macroeconômicas, separando dados históricos de previstos.
        """
    )

    # Gráfico da série temporal de emplacamentos
    st.subheader("Emplacamentos Reais")
    st.line_chart(
        data.set_index("mes_ano")[["licen"]],
        use_container_width=True,
    )

    # Gráfico de variáveis macroeconômicas
    st.subheader("Variáveis Macroeconômicas")
    macro_var = st.selectbox(
        "Selecione uma variável macroeconômica para visualizar:",
        ["pib", "selic", "tx_cambio", "prod_ind", "infl"],
    )

    # Combinar dados históricos e previstos para o gráfico
    historical_data = data[data['CALC'] == False][["mes_ano", macro_var]].copy()
    historical_data['Tipo'] = "Histórico"

    forecast_data = data[data['CALC'] == True][["mes_ano", macro_var]].copy()
    forecast_data['Tipo'] = "Previsto"

    combined_data = pd.concat([historical_data, forecast_data])
    combined_data.rename(columns={macro_var: "Valor", "mes_ano": "Data"}, inplace=True)

    # Gráfico com Plotly
    fig = px.line(
        combined_data,
        x="Data",
        y="Valor",
        color="Tipo",
        labels={"Valor": macro_var, "Data": "Mês/Ano", "Tipo": "Tipo de Dado"},
        title=f"{macro_var}: Histórico vs Previsto",
    )

    st.plotly_chart(fig, use_container_width=True)

# Página: Simulação What If
elif page == "Simulação What If":
    st.header("Simulação 'What If'")

    # Coeficientes extraídos diretamente do modelo - HTML
    coefficients = {
        # "ar1":0.9543,
        "intercept": -11849.278,
        "pib": 0.0207,
        "selic": 2313.385,
        "tx_cambio": -215.8352,
        "prod_ind": 4.2921,
        "infl": -69.0663,
    }

    # Dados históricos
    historical_data = data[data["CALC"] == False].copy()
    last_historical = historical_data.iloc[-1]

    # Layout em colunas para os parâmetros de entrada
    col1, col2, col3 = st.columns(3)
    with col1:
        pib_proximo = st.number_input("PIB (Próximo Período):", value=float(last_historical["pib"]))
        prod_ind_proximo = st.number_input("Produção Industrial (Próximo Período):", value=float(last_historical["prod_ind"]))
    with col2:
        selic_proximo = st.number_input("Selic (Próximo Período):", value=float(last_historical["selic"]))
        infl_proximo = st.number_input("Inflação (Próximo Período):", value=float(last_historical["infl"]))
    with col3:
        tx_cambio_proximo = st.number_input("Câmbio (Próximo Período):", value=float(last_historical["tx_cambio"]))

    # Calcular o licenciamento previsto para o próximo período
    licen_previsto = (
        coefficients["intercept"]
        # + (last_historical["licen"] * coefficients["ar1"])
        + (pib_proximo * coefficients["pib"])
        + (selic_proximo * coefficients["selic"])
        + (tx_cambio_proximo * coefficients["tx_cambio"])
        + (prod_ind_proximo * coefficients["prod_ind"])
        + (infl_proximo * coefficients["infl"])
    )

    # Dados do próximo período
    proximo_periodo = {
        "mes_ano": pd.to_datetime(last_historical["mes_ano"]) + pd.DateOffset(months=1),
        "pib": pib_proximo,
        "selic": selic_proximo,
        "tx_cambio": tx_cambio_proximo,
        "prod_ind": prod_ind_proximo,
        "infl": infl_proximo,
        "licen_previsto": licen_previsto,
    }

    # Combinar os dados históricos e o próximo período para o gráfico
    combined_data = historical_data[["mes_ano", "licen"]].copy()
    combined_data.rename(columns={"licen": "Valor"}, inplace=True)
    combined_data["Tipo"] = "Histórico"

    proximo_df = pd.DataFrame([proximo_periodo])
    proximo_df = proximo_df[["mes_ano", "licen_previsto"]].rename(columns={"licen_previsto": "Valor"})
    proximo_df["Tipo"] = "Previsão"

    combined_data = pd.concat([combined_data, proximo_df], ignore_index=True)

    # Gráfico com Plotly
    fig = px.line(
        combined_data,
        x="mes_ano",
        y="Valor",
        color="Tipo",
        labels={"Valor": "Emplacamentos", "mes_ano": "Mês/Ano", "Tipo": "Tipo de Dado"},
        title="Emplacamentos: Histórico e Previsão",
    )

    # Adicionar destaque para o ponto previsto
    fig.add_scatter(
        x=proximo_df["mes_ano"],
        y=proximo_df["Valor"],
        mode="markers",
        marker=dict(size=12, symbol="star", color="red"),
        name="Previsão",
    )

    # Adicionar anotação sem seta no gráfico para o ponto previsto
    fig.add_annotation(
        x=proximo_df["mes_ano"].iloc[0],
        y=proximo_df["Valor"].iloc[0] + (proximo_df["Valor"].iloc[0] * 0.1),  # Posição acima do ponto
        text=f"{licen_previsto:,.0f}",
        showarrow=False,  # Sem seta
        font=dict(size=12, color="red"),  # Texto vermelho
    )

    st.plotly_chart(fig, use_container_width=True)

    # Exportação do Resultado
    st.subheader("Exportação de Resultados")
    combined_csv = pd.concat([historical_data, proximo_df])
    csv = combined_csv.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Baixar Previsão em CSV",
        data=csv,
        file_name="previsao_proximo_periodo.csv",
        mime="text/csv",
    )