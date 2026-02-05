import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="Debt Dynamics Simulator", layout="wide")

st.title("📉 National Debt Dynamics Simulator")
st.markdown("""
This tool simulates the evolution of the **Debt-to-GDP ratio** over time based on the standard 
government budget constraint formula. Adjust the economic levers in the sidebar to see if the debt 
is sustainable.
""")

# --- Sidebar Inputs ---
st.sidebar.header("Economic Levers")

def user_input_features():
    # Initial State
    d_0 = st.sidebar.number_input("Initial Debt-to-GDP Ratio (%)", min_value=0.0, value=98.0, step=1.0)
    
    st.sidebar.markdown("---")
    
    # Rates (User inputs in %, converted to decimals for math)
    i = st.sidebar.slider("Nominal Interest Rate (i)", 0.0, 15.0, 4.5, 0.1)
    g = st.sidebar.slider("Real GDP Growth Rate (g)", -5.0, 10.0, 2.0, 0.1)
    pi = st.sidebar.slider("Inflation Rate (π)", -2.0, 15.0, 2.5, 0.1)
    
    st.sidebar.markdown("---")
    
    # Fiscal Policy
    tax = st.sidebar.slider("Tax Rate (Revenue % of GDP) (τ)", 10.0, 60.0, 30.0, 0.5)
    spending = st.sidebar.slider("Gov Spending (Non-Interest % of GDP) (s)", 10.0, 60.0, 32.0, 0.5)
    
    return d_0, i, g, pi, tax, spending

d_0_pct, i_pct, g_pct, pi_pct, tax_pct, s_pct = user_input_features()

# --- Calculations ---

# Convert percentages to decimals
d_0 = d_0_pct / 100
i = i_pct / 100
g = g_pct / 100
pi = pi_pct / 100
tau = tax_pct / 100
s = s_pct / 100

# Projection Years
years = 20
debt_trajectory = [d_0]
years_list = list(range(0, years + 1))

# The Loop: Calculating year-over-year change
current_d = d_0
for year in range(1, years + 1):
    # The Exact Formula: d_t = [(1+i) / ((1+g)(1+pi))] * d_{t-1} + (s - tau)
    numerator = 1 + i
    denominator = (1 + g) * (1 + pi)
    
    # Primary Deficit (Spending - Tax)
    primary_deficit = s - tau
    
    next_d = (numerator / denominator) * current_d + primary_deficit
    debt_trajectory.append(next_d)
    current_d = next_d

# Create DataFrame for plotting
df = pd.DataFrame({
    "Year": years_list,
    "Debt Ratio": [x * 100 for x in debt_trajectory] # Convert back to % for display
})

# --- Visualization ---

# 1. Main Chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["Year"], 
    y=df["Debt Ratio"],
    mode='lines+markers',
    name='Debt Ratio',
    line=dict(color='#FF4B4B', width=3),
    fill='tozeroy'
))

fig.update_layout(
    title="Projected Debt-to-GDP Ratio (20 Years)",
    xaxis_title="Years into the Future",
    yaxis_title="Debt to GDP (%)",
    hovermode="x unified",
    height=500
)

# 2. Key Metrics Columns
col1, col2, col3 = st.columns(3)

final_debt = df["Debt Ratio"].iloc[-1]
start_debt = df["Debt Ratio"].iloc[0]
delta = final_debt - start_debt

with col1:
    st.metric(label="Final Debt-to-GDP (Year 20)", value=f"{final_debt:.1f}%", delta=f"{delta:.1f}%", delta_color="inverse")

with col2:
    # r - g calculation (Real Interest Rate - Growth)
    # Approximation: r ≈ i - pi
    r_real = i_pct - pi_pct
    r_minus_g = r_real - g_pct
    
    status = "⚠️ Unfavorable (r > g)" if r_minus_g > 0 else "✅ Favorable (g > r)"
    st.metric(label="Interest-Growth Differential (r - g)", value=f"{r_minus_g:.2f}%", delta=status, delta_color="off")

with col3:
    primary_bal = tax_pct - s_pct
    bal_label = "Primary Surplus" if primary_bal > 0 else "Primary Deficit"
    color = "normal" if primary_bal > 0 else "inverse"
    st.metric(label=f"Annual {bal_label}", value=f"{abs(primary_bal):.1f}% of GDP")

st.plotly_chart(fig, use_container_width=True)

# --- Analysis & Explanation ---
st.subheader("Analysis")

st.markdown(f"""
**Scenario Summary:**
* You start with a debt ratio of **{d_0_pct}%**.
* The government spends **{s_pct}%** of GDP but collects **{tax_pct}%** in taxes.
* The economy grows at **{g_pct}%** while nominal interest rates are **{i_pct}%**.
""")

if final_debt > 150:
    st.error("🚨 **Crisis Warning:** The debt is spiraling out of control. The debt ratio exceeds 150% in 20 years. Consider raising taxes, cutting spending, or hoping for higher growth.")
elif final_debt > start_debt:
    st.warning("⚠️ **Rising Debt:** The debt ratio is increasing over time. While not immediately catastrophic, this trend may be unsustainable in the long run.")
else:
    st.success("✅ **Sustainable:** The debt ratio is decreasing. The economy is outgrowing the debt, or the government is running a sufficient surplus.")

st.latex(r'''
d_t = \frac{1 + i}{(1 + g)(1 + \pi)} d_{t-1} + (s - \tau)
''')
