
# Aplicativo de Previsão de Emplacamentos

Este aplicativo foi desenvolvido para realizar previsões de emplacamentos de veículos com base em variáveis macroeconômicas. Ele utiliza Streamlit para a interface web e realiza cálculos baseados em coeficientes fornecidos pelo modelo econométrico.

## Funcionalidades

- Visualização de séries históricas de emplacamentos reais.
- Previsão do próximo período com base em variáveis macroeconômicas ajustáveis.
- Destaque da previsão no gráfico com um ícone especial.
- Exportação dos dados históricos e da previsão para CSV.

---

## Estrutura de Pastas

```
.
├── data/               # Dados de entrada
├── src/                # Código fonte principal
│   ├── get_reg_data.py # Função para carregar e processar os dados
├── streamlit_app.py    # Aplicativo principal
├── requirements.txt    # Dependências do projeto
```

---

## Configuração do Ambiente

### 1. Criar o Ambiente Virtual

Para garantir que as dependências do projeto não interfiram em outras instalações, crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual:
- **Windows**:
  ```bash
  .venv\Scripts\activate
  ```
- **Linux/MacOS**:
  ```bash
  source .venv/bin/activate
  ```

### 2. Instalar Dependências

Com o ambiente virtual ativo, instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

---

## Executar o Aplicativo

Após configurar o ambiente, inicie o aplicativo Streamlit:

```bash
streamlit run streamlit_app.py
```

Abra o navegador no endereço exibido para acessar o aplicativo (geralmente `http://localhost:8501`).

---

## Sobre o Aplicativo

Este aplicativo é utilizado para prever os emplacamentos de veículos com base em variáveis como PIB, Selic, câmbio, produção industrial e inflação. Ele também permite ajustar as variáveis para realizar simulações e exportar os resultados.

---

