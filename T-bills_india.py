import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page config
st.set_page_config(
    page_title="T-Bills India Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8fbfd;
        color: #1a4d7c;
        font-family: 'Arial', sans-serif;
    }
    .stApp > header {
        width: 100%;
        background-color: #ffffff;
        padding: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-top: -20px;
    }
    .stApp .main .block-container {
        width: 90%;
        max-width: 1200px;
        padding: 30px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-top: 20px;
        margin-bottom: 20px;
        margin-left: auto;
        margin-right: auto;
    }
    h1 {
        color: #1a4d7c;
        text-align: center;
        padding-top: 20px;
        padding-bottom: 10px;
        border-bottom: 4px solid #1a4d7c;
        margin-bottom: 45px;
        font-size: 2.5em;
        font-weight: 700;
    }
    h2, h3 {
        color: #1a4d7c;
        font-weight: 600;
    }
    hr {
        border: none;
        height: 2px;
        background-image: linear-gradient(to right, #a8d5f2, #e0e0e0, #a8d5f2);
        margin: 40px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Load Data ---
@st.cache_data
def load_data(file_path):
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

df = load_data("pd_dataframe_tbills.xlsx")

# --- Main Title ---
st.title("T-Bills India Yield Analysis")

if not df.empty:
    period_col = df.columns[0]
    df['Period_Datetime'] = pd.to_datetime(df[period_col], format='%b %y', errors='coerce')
    df = df.sort_values('Period_Datetime')
    tenor_cols = [col for col in df.columns if col not in [period_col, 'Period_Datetime']]

    long_df = df.melt(
        id_vars=[period_col, 'Period_Datetime'],
        value_vars=tenor_cols,
        var_name='Tenor',
        value_name='Yield'
    )

    # --- Time Series Plot ---
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly
    for i, tenor in enumerate(tenor_cols):
        temp = long_df[long_df['Tenor'] == tenor]
        fig.add_trace(go.Scatter(
            x=temp[period_col],
            y=temp['Yield'],
            mode='markers',
            name=tenor,
            marker=dict(size=7, opacity=0.8, color=colors[i % len(colors)]),
            line=dict(width=2, color=colors[i % len(colors)]),
            customdata=temp[period_col],
            hovertemplate=f'<b>{tenor}</b><br>Period: %{{customdata}}<br>Yield: %{{y:.2f}}%<extra></extra>'
        ))

    fig.update_layout(
        title=dict(text="T-Bill Rates Over Time by Tenor", x=0.01, xanchor="left", font=dict(size=24, color='#1a4d7c')),
        xaxis_title='Period', yaxis_title='Yield (%)',
        template='plotly_white',
        font=dict(family='Arial', size=12, color='#1a4d7c'),
        height=500,
        legend=dict(orientation="h", y=-0.3)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Slider Yield Curve ---
    st.subheader("Interactive T-Bill Yield Curve Evolution")
    tenor_order = ['7 Day', '14 Day', '1 Month', '2 Month', '3 Month', '4 Month', '5 Month',
                   '6 Month', '7 Month', '8 Month', '9 Month', '10 Month', '11 Month', '12 Month']

    all_periods = long_df[period_col].unique().tolist()
    selected = st.select_slider("Select Period:", options=all_periods, value=all_periods[-1])

    df_slider = long_df[long_df[period_col] == selected].copy()
    df_slider['Tenor'] = pd.Categorical(df_slider['Tenor'], categories=tenor_order, ordered=True)
    df_slider = df_slider.sort_values('Tenor')

    fig_curve = go.Figure(go.Scatter(
        x=df_slider['Tenor'], y=df_slider['Yield'],
        mode='lines+markers',
        line=dict(color='#1a4d7c', width=3),
        marker=dict(color='#1a4d7c', size=9, symbol='circle')
    ))
    fig_curve.update_layout(
        title=dict(text=f"T-Bill Yield Curve for {selected}", x=0.5, font=dict(size=20, color='#1a4d7c')),
        xaxis_title='Tenor', yaxis_title='Yield (%)',
        template='plotly_white',
        height=550,
        font=dict(family='Arial', size=12, color='#1a4d7c'),
        xaxis=dict(categoryorder='array', categoryarray=tenor_order)
    )
    st.plotly_chart(fig_curve, use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- 3D & Heatmap ---
    st.subheader("Yield Curve Dynamics (3D & Heatmap)")
    col1, col2 = st.columns(2)

    with col1:
        st.write("### 3D T-Bill Yield Surface")
        z_vals = df[tenor_cols].values
        fig3d = go.Figure(data=[go.Surface(
            z=z_vals,
            x=tenor_cols,
            y=df[period_col],
            colorscale='RdBu_r',
            showscale=False
        )])
        fig3d.update_layout(
            scene=dict(
                xaxis_title='Tenor', yaxis_title='Period', zaxis_title='Yield (%)',
                xaxis=dict(tickfont=dict(color='#1a4d7c')),
                yaxis=dict(tickfont=dict(color='#1a4d7c')),
                zaxis=dict(tickfont=dict(color='#1a4d7c'))
            ),
            height=650,
            font=dict(family='Arial', color='#1a4d7c')
        )
        st.plotly_chart(fig3d, use_container_width=True)

    with col2:
        st.write("### T-Bill Yield Heatmap")
        heatmap_df = df.copy()
        heatmap_df.set_index(period_col, inplace=True)
        heatmap_df = heatmap_df[tenor_cols]

        fig_heatmap = px.imshow(
            heatmap_df.values,
            x=tenor_cols,
            y=heatmap_df.index,
            labels=dict(x="Tenor", y="Period", color="Yield (%)"),
            color_continuous_scale='RdBu_r'
        )
        fig_heatmap.update_traces(
            hovertemplate='<b>Tenor:</b> %{x}<br><b>Period:</b> %{y}<br><b>Yield:</b> %{z:.2f}%<extra></extra>'
        )
        fig_heatmap.update_layout(
            font=dict(family="Arial", size=12, color='#1a4d7c'),
            xaxis=dict(tickangle=45, tickfont=dict(color='#1a4d7c')),
            yaxis=dict(tickfont=dict(color='#1a4d7c')),
            coloraxis_colorbar=dict(title='Yield (%)', titlefont=dict(color='#1a4d7c'), tickfont=dict(color='#1a4d7c')),
            height=650,
            template='plotly_white'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

else:
    st.info("No T-Bills data available. Please ensure the Excel file is present and correct.")

