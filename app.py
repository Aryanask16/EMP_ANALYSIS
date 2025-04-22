import streamlit as st
import pandas as pd
import plotly.express as px
import json

# --- Page Configuration & Theme Setup ---
st.set_page_config(page_title="Unemployment Analysis", layout="wide")
st.sidebar.title("Theme")
theme = st.sidebar.radio("Select theme", ["Light", "Dark"], index=0)

# Define colors and template based on theme
if theme == "Dark":
    bg_color = "#111111"
    text_color = "#EEEEEE"
    plotly_template = "plotly_dark"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    plotly_template = "plotly_white"

# Apply custom CSS for background & text
st.markdown(f"""
<style>
body, .block-container {{ background-color: {bg_color}; color: {text_color}; }}
.sidebar .sidebar-content {{ background-color: {bg_color}; color: {text_color}; }}
</style>
""", unsafe_allow_html=True)

# --- Filters ---
st.sidebar.title("Filters")

df = pd.read_csv("data/processed/state_data.csv")
states = sorted(df["State"].unique())
state = st.sidebar.selectbox("State", states)
years = sorted(df["Year"].unique())
year_range = st.sidebar.slider("Year Range", min_value=years[0], max_value=years[-1], value=(years[0], years[-1]))

# Filter data for selections
target_year = year_range[1]
sub = df[(df["State"] == state) & df["Year"].between(year_range[0], year_range[1])]
all_latest = df[df["Year"] == target_year]

# --- 1) Unemployment Rate ---
st.header(f"Unemployment Rate in {state}")
fig1 = px.line(sub, x="Year", y="UnemploymentRate",
                 title="Unemployment Rate Over Time",
                 template=plotly_template)
st.plotly_chart(fig1, use_container_width=True)

# --- 2) Worker Participation Ratio (WPR) ---
st.header("Worker Participation Ratio (WPR)")
fig2 = px.bar(sub, x="Year", y="WPR",
                title="WPR Over Time",
                template=plotly_template)
st.plotly_chart(fig2, use_container_width=True)

# --- 3) State Comparison (All States): Bar Chart ---
st.header(f"State Comparison in {target_year} (Bar)")
fig3_bar = px.bar(
    all_latest.sort_values("UnemploymentRate", ascending=False),
    x="UnemploymentRate", y="State",
    orientation="h",
    title=f"Unemployment Rate by State ({target_year})",
    template=plotly_template
)
fig3_bar.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig3_bar, use_container_width=True)

# --- 4) State Comparison: Heatmap ---
st.header("Unemployment Rate Heatmap (States vs Years)")
pivot = df.pivot(index="State", columns="Year", values="UnemploymentRate")
fig3_heat = px.imshow(
    pivot,
    aspect="auto",
    labels={'x':'Year','y':'State','color':'Unemp Rate'},
    title="Heatmap of Unemployment Rate Over Years",
    template=plotly_template
)
st.plotly_chart(fig3_heat, use_container_width=True)

# --- 5) Urban vs Rural Employment Share ---
st.header("Urban vs Rural Employment Share")
latest_sub = all_latest[all_latest["State"] == state]
if not latest_sub.empty:
    rural = latest_sub["RuralEmployment"].iloc[0]
    urban = latest_sub["UrbanEmployment"].iloc[0]
    fig4 = px.pie(
        names=["Rural Employment", "Urban Employment"],
        values=[rural, urban],
        title=f"Urban vs Rural Employment in {state} ({target_year})",
        template=plotly_template
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info(f"No employment data for {state} in {target_year}.")