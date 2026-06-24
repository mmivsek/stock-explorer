# Stock Explorer

A Streamlit app for exploring and comparing normalized stock price growth, with a "what if I invested $1,000?" calculator.

**Live app:** https://mivsekstocks.streamlit.app/

## Architecture

```mermaid
flowchart LR
    A[Plotly built-in stock dataset] --> B[app.py<br/>Streamlit app]
    B --> C[GitHub repository]
    C --> D[Streamlit Community Cloud]
    D --> E[User's browser]
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
