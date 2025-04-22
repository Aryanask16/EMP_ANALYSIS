# etl.py
import os
import pandas as pd

# ─── Paths ────────────────────────────────────────────
RAW_CSV   = "data/raw/Unemployment in India.csv"
OUT_DIR   = "data/processed"
OUT_FILE  = os.path.join(OUT_DIR, "state_data.csv")
os.makedirs(OUT_DIR, exist_ok=True)

# ─── 1) Load & Clean ───────────────────────────────────
df = pd.read_csv(RAW_CSV)
df.columns = df.columns.str.strip()

# Parse dates & drop bad rows
df["Date"] = pd.to_datetime(df["Date"].astype(str).str.strip(),
                            format="%d-%m-%Y",
                            errors="coerce")
df = df[df["Region"].notna() & df["Date"].notna()]

# Extract Year & normalize Area
df["Year"] = df["Date"].dt.year.astype(int)
df["Area"] = df["Area"].fillna("Total").str.strip()

# Rename for clarity
df.rename(columns={
    "Region": "State",
    "Estimated Unemployment Rate (%)":       "UnempRate",
    "Estimated Labour Participation Rate (%)":"LP_Rate",
    "Estimated Employed":                    "Employed"
}, inplace=True)

# ─── 2) Aggregate by State / Year / Area ──────────────
grp = df.groupby(["State","Year","Area"], as_index=False).agg({
    "UnempRate":"mean",
    "LP_Rate":"mean",
    "Employed":"mean"
})

# Pivot rural vs urban vs total
pu = grp.pivot(index=["State","Year"], columns="Area", values="UnempRate")
pl = grp.pivot(index=["State","Year"], columns="Area", values="LP_Rate")
pe = grp.pivot(index=["State","Year"], columns="Area", values="Employed")

# ─── 3) Build tidy output ──────────────────────────────
out = pd.DataFrame({
    "State": pu.index.get_level_values(0),
    "Year":  pu.index.get_level_values(1),
    "Unemp_Rural": pu.get("Rural"),
    "Unemp_Urban": pu.get("Urban"),
    # Total unemployment rate = simple average of Rural & Urban
    "UnemploymentRate": (pu.get("Rural") + pu.get("Urban")) / 2,

    "LP_Rural":    pl.get("Rural"),
    "LP_Urban":    pl.get("Urban"),
    # WPR  = labour participation rate averaged
    "WPR":         (pl.get("Rural") + pl.get("Urban")) / 2,

    "RuralEmployment": pe.get("Rural"),
    "UrbanEmployment": pe.get("Urban"),
})

# Keep only the 6 columns the app needs:
out = out[[
    "State","Year",
    "UnemploymentRate","WPR",
    "RuralEmployment","UrbanEmployment"
]]

# ─── 4) Write CSV ──────────────────────────────────────
out.to_csv(OUT_FILE, index=False)
print("✅ state_data.csv written to", OUT_FILE)
