import random

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Stock Explorer", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, rgba(144, 238, 144, 0.15), rgba(34, 139, 34, 0.06));
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📈 Stock Price Explorer")

FUN_FACTS = [
    "Netflix started as a DVD-by-mail rental service charging per rental, before switching to its now-famous monthly subscription model in September 1999.",
    "Steve Jobs and Steve Wozniak financed Apple's first computer by selling personal possessions — Jobs his Volkswagen Bus, Wozniak his HP-65 calculator — raising $1,300 to build the Apple I.",
    "A year before founding Microsoft, childhood friends Bill Gates and Paul Allen built Traf-O-Data, a system that analyzed automobile traffic data.",
    "Google was originally nicknamed \"BackRub\" because its search algorithm ranked sites by checking their backlinks.",
    "Jeff Bezos once considered naming his company Relentless — the domain relentless.com still redirects to Amazon's homepage today.",
    "Facebook's original motto was \"Move fast and break things,\" until the company swapped it for \"Move fast with stable infrastructure\" in 2014.",
]

@st.cache_data
def load_data():
    # This stock dataset is built into plotly — no file to download or push!
    df = px.data.stocks()              # columns: date + 6 big tech stocks
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()
tickers = [c for c in df.columns if c != "date"]

# Sidebar: pick which stocks to compare
chosen = st.sidebar.multiselect("Choose stocks", tickers, default=["AAPL", "MSFT", "GOOG"])
if not chosen:
    st.warning("Pick at least one stock from the sidebar.")
    st.stop()

st.caption("Prices are indexed to 1.00 at the start, so each line shows growth since Jan 2018.")

if "fun_fact" not in st.session_state:
    st.session_state.fun_fact = random.choice(FUN_FACTS)

fact_col, button_col = st.columns([6, 1])
with fact_col:
    st.info(f"Did you know? {st.session_state.fun_fact}")
with button_col:
    if st.button("🔄 New fact"):
        st.session_state.fun_fact = random.choice(FUN_FACTS)
        st.rerun()

# Key numbers: total growth for each chosen stock
cols = st.columns(len(chosen))
for col, t in zip(cols, chosen):
    growth = (df[t].iloc[-1] - 1) * 100
    col.metric(t, f"{df[t].iloc[-1]:.2f}x", f"{growth:+.1f}%")

# Top performer among the chosen stocks
growths = {t: (df[t].iloc[-1] - 1) * 100 for t in chosen}
best_ticker = max(growths, key=growths.get)
st.metric("🏆 Best performer", best_ticker, f"{growths[best_ticker]:+.1f}%")

# Line chart comparing the chosen stocks over time
fig = px.line(df, x="date", y=chosen, title="Normalized price over time")
st.plotly_chart(fig, width="stretch")

# "What if I invested $1,000?" calculator
st.divider()
st.subheader("💰 What if I invested $1,000?")
invest_ticker = st.selectbox("Pick a stock", chosen)
amount = st.number_input("Investment amount ($)", min_value=1, value=1000, step=100)
invest_date = st.date_input(
    "Investment date",
    value=df["date"].min(),
    min_value=df["date"].min(),
    max_value=df["date"].max(),
)

# Snap to the closest trading date we actually have data for
closest_idx = (df["date"] - pd.Timestamp(invest_date)).abs().idxmin()
actual_date = df.loc[closest_idx, "date"]
price_then = df.loc[closest_idx, invest_ticker]
price_now = df[invest_ticker].iloc[-1]

final_value = amount * (price_now / price_then)
profit = final_value - amount
st.caption(f"Based on the closest available price on {actual_date.date()}.")
st.metric(
    f"Value today of ${amount:,.0f} invested in {invest_ticker} on {actual_date.date()}",
    f"${final_value:,.2f}",
    f"{profit:+,.2f}",
)
