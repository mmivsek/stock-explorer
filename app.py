import random

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Stock Explorer", layout="wide")

st.markdown(
    """
    <style>
    html, body, .stApp, [class*="css"] {
        font-family: "Times New Roman", Times, serif;
    }
    .stApp {
        background-image:
            linear-gradient(135deg, rgba(144, 238, 144, 0.18), rgba(46, 139, 87, 0.12)),
            url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%22120%22%20height%3D%22120%22%3E%3Ctext%20x%3D%228%22%20y%3D%2238%22%20font-size%3D%2234%22%20font-family%3D%22Arial%2C%20sans-serif%22%20fill%3D%22rgba%280%2C90%2C0%2C0.10%29%22%3E%24%3C/text%3E%3Ctext%20x%3D%2260%22%20y%3D%2295%22%20font-size%3D%2234%22%20font-family%3D%22Arial%2C%20sans-serif%22%20fill%3D%22rgba%280%2C90%2C0%2C0.10%29%22%3E%E2%82%AC%3C/text%3E%3C/svg%3E");
        background-size: cover, 120px 120px;
        background-attachment: fixed, fixed;
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

# Most volatile: largest swings in week-over-week % change
volatility = {t: df[t].pct_change().std() * 100 for t in chosen}
most_volatile = max(volatility, key=volatility.get)

vol_col1, vol_col2 = st.columns(2)
vol_col1.metric("🏆 Best performer", best_ticker, f"{growths[best_ticker]:+.1f}%")
vol_col2.metric("🎢 Most volatile", most_volatile, f"±{volatility[most_volatile]:.2f}% weekly swing")

# Line chart comparing the chosen stocks over time
fig = px.line(df, x="date", y=chosen, title="Normalized price over time")
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, width="stretch")

# Correlation heatmap: do the chosen stocks move together?
if len(chosen) > 1:
    st.subheader("🔗 How closely do these stocks move together?")
    corr = df[chosen].corr()
    heatmap = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdYlGn",
        zmin=-1,
        zmax=1,
        title="Correlation between selected stocks",
    )
    heatmap.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(heatmap, width="stretch")
    st.caption("1.0 = always move together, -1.0 = always move oppositely, 0 = no relationship.")

# "What if I invested $1,000?" calculator
st.divider()
st.subheader("💰 What if I invested $1,000?")
dataset_end = df["date"].max().date()
st.caption(
    f"⚠️ This demo dataset only covers {df['date'].min().date()} to {dataset_end}. "
    "\"Today\" below means the last date in the dataset, not the real current date — "
    "so this is not a live, up-to-date return."
)
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
    f"Value on {dataset_end} of ${amount:,.0f} invested in {invest_ticker} on {actual_date.date()}",
    f"${final_value:,.2f}",
    f"{profit:+,.2f}",
)
