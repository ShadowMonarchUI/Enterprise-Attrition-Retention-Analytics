import sys
import asyncio

# 1. Windows Fix: Prevents the WinError 10054 console disconnect bug
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# Set the page layout to wide
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Dynamic Light/Dark Mode ---
st.markdown("""
<style>
    /* Use Streamlit's dynamic theme variables instead of hardcoded hex colors */
    .stApp {
        background-color: var(--secondary-background-color);
    }
    
    /* Dynamic background, border, and shadow for KPI metric cards */
    div[data-testid="metric-container"] {
        background-color: var(--background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Dynamic background for Plotly charts */
    div.stPlotlyChart {
        background-color: var(--background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Styling for the floating Insight Cards */
    .insight-card {
        background-color: var(--background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-left: 5px solid #118DFF; /* Power BI Blue Accent */
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
        font-size: 15px;
    }
    
    /* Highlight class for key numbers */
    .highlight {
        background-color: #FFE066;
        color: #B30000;
        font-weight: 800;
        padding: 2px 6px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Power BI Color Palette
PBI_COLORS = {'Churned': '#E66C37', 'Retained': '#118DFF'}

# Helper function: Removed "plotly_white" so Streamlit can auto-invert colors in Dark Mode
def apply_pbi_theme(fig):
    fig.update_layout(
        margin=dict(t=40, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text=''
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='rgba(128, 128, 128, 0.2)', zerolinecolor='rgba(128, 128, 128, 0.2)')
    return fig

# Cache the data extraction
@st.cache_data(show_spinner="Extracting enterprise data...")
def load_data():
    try:
        conn = sqlite3.connect('churn_project.db')
        # Data Extraction: Strictly utilizing nested subqueries (No Joins)
        query = """
            SELECT CustomerID, Age, Gender, Tenure, Total_Spend, Payment_Delay, Churn
            FROM customer_data
            WHERE CustomerID IN (
                SELECT CustomerID FROM customer_data 
                WHERE Payment_Delay > (SELECT AVG(Payment_Delay) FROM customer_data)
            )
            AND Total_Spend > (SELECT AVG(Total_Spend) FROM customer_data);
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Format Labels for Power BI Visuals
        df['Churn_Label'] = df['Churn'].map({1: 'Churned', 0: 'Retained'})
        
        # Create Tenure Bins for Proportional Stacked Charts
        df['Tenure_Group'] = pd.cut(
            df['Tenure'], 
            bins=[0, 12, 24, 36, 48, 100], 
            labels=['0-1 Yr', '1-2 Yrs', '2-3 Yrs', '3-4 Yrs', '4+ Yrs']
        )
        return df
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data found in SQLite. Please run your database extraction script first.")
    st.stop()

# ==========================================
# SIDEBAR: ADVANCED FILTERS
# ==========================================
st.sidebar.title("🎛️ Data Filters")
st.sidebar.markdown("Slice the dataset to update the dashboard dynamically.")

selected_gender = st.sidebar.multiselect(
    "1. Demographics (Gender):",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

min_age, max_age = int(df["Age"].min()), int(df["Age"].max())
selected_age = st.sidebar.slider(
    "2. Demographics (Age Range):",
    min_value=min_age, max_value=max_age, value=(min_age, max_age)
)

min_tenure, max_tenure = int(df["Tenure"].min()), int(df["Tenure"].max())
selected_tenure = st.sidebar.slider(
    "3. Lifecycle (Tenure in Months):",
    min_value=min_tenure, max_value=max_tenure, value=(min_tenure, max_tenure)
)

min_spend, max_spend = float(df["Total_Spend"].min()), float(df["Total_Spend"].max())
selected_spend = st.sidebar.slider(
    "4. Financials (Total Spend Range):",
    min_value=min_spend, max_value=max_spend, value=(min_spend, max_spend)
)

# Apply filters
filtered_df = df[
    (df["Gender"].isin(selected_gender)) &
    (df["Age"] >= selected_age[0]) & (df["Age"] <= selected_age[1]) &
    (df["Tenure"] >= selected_tenure[0]) & (df["Tenure"] <= selected_tenure[1]) &
    (df["Total_Spend"] >= selected_spend[0]) & (df["Total_Spend"] <= selected_spend[1])
]

# ==========================================
# MAIN CANVAS: ENTERPRISE GRID LAYOUT
# ==========================================
st.title("📊 Enterprise Attrition & Retention Analytics")
st.markdown("---")

total_customers = len(filtered_df)
if total_customers == 0:
    st.info("No customers match the current filter settings. Adjust the sidebar sliders.")
    st.stop()

# --- ROW 1: TOP-LEVEL KPI BANNER ---
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

churn_rate = (filtered_df["Churn"].mean() * 100)
avg_delay = filtered_df["Payment_Delay"].mean()
avg_spend = filtered_df["Total_Spend"].mean()
avg_tenure = filtered_df["Tenure"].mean()

kpi1.metric("Volume", f"{total_customers:,}")
kpi2.metric("Attrition Rate", f"{churn_rate:.2f}%")
kpi3.metric("Avg Payment Delay", f"{avg_delay:.1f} Days")
kpi4.metric("Avg LTV (Spend)", f"${avg_spend:.0f}")
kpi5.metric("Avg Tenure", f"{avg_tenure:.1f} Mos")

st.markdown("<br>", unsafe_allow_html=True)

CHART_HEIGHT = 280

# --- ROW 2: PRIMARY DIAGNOSTICS (Ratio 1:2) ---
row2_col1, row2_col2 = st.columns([1, 2])

with row2_col1:
    churn_counts = filtered_df['Churn_Label'].value_counts().reset_index()
    churn_counts.columns = ['Status', 'Count']
    fig_donut = px.pie(
        churn_counts, values='Count', names='Status', hole=0.6,
        title="<b>Cohort Attrition Ratio</b>",
        color='Status', color_discrete_map=PBI_COLORS
    )
    fig_donut = apply_pbi_theme(fig_donut)
    fig_donut.update_layout(height=CHART_HEIGHT)
    st.plotly_chart(fig_donut, use_container_width=True)

with row2_col2:
    fig_bar_stack = px.histogram(
        filtered_df, x="Tenure_Group", color="Churn_Label", barmode="relative", barnorm="percent",
        title="<b>Attrition Proportion by Lifecycle Stage (%)</b>",
        color_discrete_map=PBI_COLORS,
        labels={"Tenure_Group": "Tenure Segment"}
    )
    fig_bar_stack = apply_pbi_theme(fig_bar_stack)
    fig_bar_stack.update_layout(height=CHART_HEIGHT, yaxis_title="Percentage (%)")
    st.plotly_chart(fig_bar_stack, use_container_width=True)

# --- ROW 3: FINANCIAL & BEHAVIORAL CHARTS (Ratio 1:2) ---
row3_col1, row3_col2 = st.columns([1, 2])

with row3_col1:
    fig_box = px.box(
        filtered_df, x="Churn_Label", y="Payment_Delay", color="Churn_Label",
        title="<b>Payment Delay Variance</b>",
        color_discrete_map=PBI_COLORS
    )
    fig_box = apply_pbi_theme(fig_box)
    fig_box.update_layout(height=CHART_HEIGHT, showlegend=False, xaxis_title="")
    st.plotly_chart(fig_box, use_container_width=True)

with row3_col2:
    fig_scatter = px.scatter(
        filtered_df, x="Age", y="Total_Spend", color="Churn_Label", opacity=0.7,
        title="<b>Financial Health: Spend vs Age Matrix</b>",
        color_discrete_map=PBI_COLORS
    )
    fig_scatter = apply_pbi_theme(fig_scatter)
    fig_scatter.update_layout(height=CHART_HEIGHT)
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- ROW 4: DEMOGRAPHIC SEGMENTATION (Ratio 1:1) ---
row4_col1, row4_col2 = st.columns(2)

with row4_col1:
    fig_gender = px.histogram(
        filtered_df, x="Gender", color="Churn_Label", barmode="group",
        title="<b>Attrition Volume by Demographic (Gender)</b>",
        color_discrete_map=PBI_COLORS
    )
    fig_gender = apply_pbi_theme(fig_gender)
    fig_gender.update_layout(height=CHART_HEIGHT, xaxis_title="")
    st.plotly_chart(fig_gender, use_container_width=True)

with row4_col2:
    fig_violin = px.violin(
        filtered_df, x="Churn_Label", y="Age", color="Churn_Label", box=True,
        title="<b>Age Distribution Density by Status</b>",
        color_discrete_map=PBI_COLORS
    )
    fig_violin = apply_pbi_theme(fig_violin)
    fig_violin.update_layout(height=CHART_HEIGHT, showlegend=False, xaxis_title="")
    st.plotly_chart(fig_violin, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# AUTOMATED ANALYTICAL INSIGHT CARDS
# ==========================================
st.subheader("🧠 Automated Diagnostic Insights")

churned_df = filtered_df[filtered_df['Churn'] == 1]
retained_df = filtered_df[filtered_df['Churn'] == 0]

insight1, insight2, insight3 = st.columns(3)

with insight1:
    if not churned_df.empty and not retained_df.empty:
        delay_diff = churned_df['Payment_Delay'].mean() - retained_df['Payment_Delay'].mean()
        if delay_diff > 0:
            text = f"<b>Delinquency Impact:</b> Churned accounts delay payments by an average of <span class='highlight'>{delay_diff:.1f} days more</span> than retained accounts. Strict intervention protocols should trigger before this threshold."
        else:
            text = "<b>Delinquency Impact:</b> In this specific view, payment delays are evenly distributed between active and churned users."
    else:
        text = "Insufficient variance to calculate delinquency impact."
    st.markdown(f"<div class='insight-card'>{text}</div>", unsafe_allow_html=True)

with insight2:
    if not churned_df.empty:
        peak_churn_tenure = churned_df['Tenure'].mode()[0]
        text = f"<b>Lifecycle Risk Zone:</b> The highest concentration of absolute attrition volume occurs at <span class='highlight'>month {peak_churn_tenure}</span>. The retention team should deploy engagement campaigns at month {max(1, peak_churn_tenure-1)}."
    else:
        text = "No churned users in this current filter view to calculate lifecycle risk."
    st.markdown(f"<div class='insight-card'>{text}</div>", unsafe_allow_html=True)

with insight3:
    if not churned_df.empty:
        lost_revenue = churned_df['Total_Spend'].sum()
        text = f"<b>Revenue At-Risk:</b> The total historical value of churned accounts in this filtered segment is <span class='highlight'>${lost_revenue:,.2f}</span>. Prioritizing this specific demographic is critical for revenue preservation."
    else:
        text = "Zero revenue lost to attrition in this specific demographic view."
    st.markdown(f"<div class='insight-card'>{text}</div>", unsafe_allow_html=True)