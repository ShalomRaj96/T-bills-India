import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="T-Bills India Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
.stApp {
    background-color: #f8fbfd;
    color: #1a4d7c;
    font-family: 'Arial', sans-serif;
}
h1, h2, h3 {
    color: #1a4d7c;
}
h1 {
    text-align: center;
    font-size: 2.5em;
    padding-bottom: 10px;
    border-bottom: 4px solid #1a4d7c;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(path):
    try:
        return pd.read_excel(path)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data("pd_dataframe_tbills.xlsx")

st.title("T-Bills India Yield Analysis")

if not df.empty:
    period_col = df.columns[0]
    df['Period_Datetime'] = pd.to_datetime(df[period_col], format='%b %y', errors='coerce')
    tenor_cols = [col for col in df.columns if col not in [period_col, 'Period_Datetime']]
    long_df = df.melt(id_vars=[period_col, 'Period_Datetime'], value_vars=tenor_cols,
                      var_name='Tenor', value_name='Yield')

    # --- Historical Line Chart ---
    fig = go.Figure()
    for i, tenor in enumerate(tenor_cols):
        sub_df = long_df[long_df['Tenor'] == tenor].sort_values('Period_Datetime')
        fig.add_trace(go.Scatter(
            x=sub_df[period_col], y=sub_df['Yield'],
            mode='markers+lines',
            name=tenor,
            line=dict(color=px.colors.qualitative.Plotly[i % 10]),
            marker=dict(size=6)
        ))

    fig.update_layout(
        title="T-Bill Rates Over Time by Tenor",
        xaxis_title="Period",
        yaxis_title="Yield (%)",
        template="plotly_white",
        font=dict(color='#1a4d7c'),
        xaxis=dict(tickangle=45)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Interactive Yield Curve ---
    st.subheader("Interactive T-Bill Yield Curve Evolution")
    tenor_order = ['7 Day', '14 Day', '1 Month', '2 Month', '3 Month', '4 Month',
                   '5 Month', '6 Month', '7 Month', '8 Month', '9 Month',
                   '10 Month', '11 Month', '12 Month']

    periods = long_df[period_col].dropna().unique().tolist()
    selected_period = st.select_slider("Select Period", options=periods, value=periods[-1])
    filtered = long_df[long_df[period_col] == selected_period]
    filtered['Tenor'] = pd.Categorical(filtered['Tenor'], categories=tenor_order, ordered=True)
    filtered = filtered.sort_values('Tenor')

    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scatter(
        x=filtered['Tenor'], y=filtered['Yield'],
        mode='lines+markers',
        line=dict(color='#1a4d7c', width=3),
        marker=dict(size=8)
    ))
    fig_curve.update_layout(
        title=f"T-Bill Yield Curve for {selected_period}",
        xaxis_title="Tenor",
        yaxis_title="Yield (%)",
        template="plotly_white",
        font=dict(color='#1a4d7c')
    )
    st.plotly_chart(fig_curve, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- 3D Surface Plot ---
    st.subheader("Yield Curve Dynamics (3D & Heatmap)")
    col1, col2 = st.columns(2)

    with col1:
        st.write("### 3D T-Bill Yield Surface")
        z = df.sort_values('Period_Datetime')[tenor_cols].values
        y = df.sort_values('Period_Datetime')[period_col]
        x = tenor_cols

        fig3d = go.Figure(data=[go.Surface(z=z, x=x, y=y, colorscale='RdBu_r')])
        fig3d.update_layout(
            scene=dict(
                xaxis_title='Tenor',
                yaxis_title='Period',
                zaxis_title='Yield (%)'
            ),
            height=600,
            margin=dict(l=10, r=10, b=10, t=30)
        )
        st.plotly_chart(fig3d, use_container_width=True)

    # --- Plotly Heatmap (Replaces seaborn) ---
    with col2:
        st.write("### T-Bill Yield Heatmap")
        heat_df = df.copy()
        heat_df['Period_Datetime'] = pd.to_datetime(heat_df[period_col], format='%b %y', errors='coerce')
        heat_df = heat_df.sort_values('Period_Datetime')
        heat_df = heat_df.set_index(period_col)

        fig_hm = px.imshow(
            heat_df[tenor_cols],
            labels=dict(x="Tenor", y="Period", color="Yield (%)"),
            aspect="auto",
            color_continuous_scale="RdBu_r"
        )
        fig_hm.update_layout(
            font=dict(color="#1a4d7c"),
            xaxis=dict(tickangle=45),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_hm, use_container_width=True)

else:
    st.warning("Data file not found or is empty.")



