import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt


# 1. Page config - MUST be the very first Streamlit command
st.set_page_config(
    page_title="T-Bills India Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling and Centering ---
st.markdown(
    """
    <style>
    /* General app styling for background and font */
    .stApp {
        background-color: #f8fbfd;
        color: #1a4d7c;
        font-family: 'Arial', sans-serif;
    }

    /* Adjust the header position */
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

    /* Style for the main page title */
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

    /* Styling for subheaders (H2) */
    h2 {
        color: #1a4d7c;
        margin-top: 25px;
        margin-bottom: 15px;
        font-weight: 600;
        /* Unified font size for section headers for consistency. */
        font-size: 24px;
    }

    /* Styling for H3 (titles for 3D and Heatmap sections) */
    h3 {
        color: #1a4d7c;
        margin-top: 0;
        margin-bottom: 0;
        font-weight: 600;
        text-align: left;
        width: 100%;
        font-size: 20px;
    }

    /* Improve Streamlit select slider appearance */
    .st-emotion-cache-1yr0343 {
        background-color: #d1e2f3 !important;
        height: 8px;
        border-radius: 4px;
    }
    .st-emotion-cache-1yr0343 > div {
        background-color: #1a4d7c !important;
        border: 2px solid #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }

    /* Enhance Plotly chart containers */
    .streamlit-plotly-container {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 30px;
        background-color: #ffffff;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        transition: transform 0.2s ease-in-out;
    }
    .streamlit-plotly-container:hover {
        transform: translateY(-5px);
    }

    /* Horizontal rule for section separation */
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
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while loading the file '{file_path}': {e}")
        return pd.DataFrame()

tbill_data_df = load_data("pd_dataframe_tbills.xlsx")

# --- Main Title ---
st.title("T-Bills India Yield Analysis")

# --- Historical T-Bill Rates by Tenor ---
if not tbill_data_df.empty:
    plot_df = tbill_data_df.copy()
    period_column_name = plot_df.columns[0]
    
    try:
        plot_df['Period_Datetime'] = pd.to_datetime(plot_df[period_column_name], format='%b %y')
    except ValueError:
        st.warning(f"Could not parse '{period_column_name}' as 'Mon YY'. Attempting general parse.")
        plot_df['Period_Datetime'] = pd.to_datetime(plot_df[period_column_name])

    tenor_cols = [col for col in plot_df.columns if col not in [period_column_name, 'Period_Datetime']]
    long_df = plot_df.melt(
        id_vars=[period_column_name, 'Period_Datetime'],
        value_vars=tenor_cols,
        var_name='Tenor',
        value_name='Yield'
    )

    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for i, tenor in enumerate(tenor_cols):
        df_tenor = long_df[long_df['Tenor'] == tenor].sort_values(by='Period_Datetime')
        fig.add_trace(go.Scatter(
            x=df_tenor[period_column_name],
            y=df_tenor['Yield'],
            mode='markers',
            name=tenor,
            marker=dict(size=7, opacity=0.8, color=colors[i % len(colors)]),
            line=dict(width=2, color=colors[i % len(colors)]),
            customdata=df_tenor[period_column_name],
            hovertemplate=f'<b>{tenor}</b><br>Period: %{{customdata}}<br>Yield: %{{y:.2f}}%<extra></extra>',
            showlegend=True
        ))

    fig.update_layout(
        title={
            'text': 'T-Bill Rates Over Time by Tenor',
            'x': 0.01,
            'xanchor': 'left',
            'y': 0.95,
            'yanchor': 'top',
            # Unified font size for chart title to match section headers.
            'font': dict(size=24, color='#1a4d7c')
        },
        xaxis_title='Period',
        yaxis_title='Yield (%)',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef', gridwidth=1, tickangle=-45, tickfont=dict(size=11, color='#1a4d7c')),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef', gridwidth=1, tickfont=dict(size=11, color='#1a4d7c')),
        template='plotly_white',
        font=dict(family='Arial, sans-serif', size=12, color='#1a4d7c'),
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="right", x=1),
        updatemenus=[dict(
            type="buttons",
            direction="right",
            active=1,
            x=0.01,
            y=1.18,
            xanchor="left",
            yanchor="top",
            buttons=list([
                dict(label="Show Lines", method="update", args=[{"mode": ["markers+lines"] * len(fig.data)}]),
                dict(label="Hide Lines", method="update", args=[{"mode": ["markers"] * len(fig.data)}])
            ]),
        )]
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Interactive T-Bill Yield Curve Evolution ---
    st.subheader("Interactive T-Bill Yield Curve Evolution")

    tenor_order = ['7 Day', '14 Day', '1 Month', '2 Month', '3 Month', '4 Month', '5 Month', '6 Month', '7 Month', '8 Month', '9 Month', '10 Month', '11 Month', '12 Month']
    long_df_chronological = long_df.sort_values(by='Period_Datetime')
    all_periods = long_df_chronological[period_column_name].unique().tolist()
    
    # FIX: Added columns to center the slider and reduce its length.
    sl_col1, sl_col2, sl_col3 = st.columns([0.15, 0.7, 0.15]) # 15% margin on left/right

    with sl_col2:
        selected_period = st.select_slider(
            label='Drag to select a **Period** to view its Yield Curve:',
            options=all_periods,
            value=all_periods[-1],
            help="Drag the slider to observe how the T-Bill yield curve changes over time."
        )

    filtered_df_for_slider = long_df_chronological[long_df_chronological[period_column_name] == selected_period].copy()
    filtered_df_for_slider['Tenor'] = pd.Categorical(filtered_df_for_slider['Tenor'], categories=tenor_order, ordered=True)
    filtered_df_for_slider = filtered_df_for_slider.sort_values(by='Tenor')
    
    min_yield_current = filtered_df_for_slider['Yield'].min()
    max_yield_current = filtered_df_for_slider['Yield'].max()
    y_axis_min = min_yield_current - 0.2 if min_yield_current - 0.2 >= 0 else 0
    y_axis_max = max_yield_current + 0.2

    fig_time_series = go.Figure(
        data=[go.Scatter(
            x=filtered_df_for_slider['Tenor'],
            y=filtered_df_for_slider['Yield'],
            mode='lines+markers',
            line=dict(color='#1a4d7c', width=3),
            marker=dict(color='#1a4d7c', size=9, symbol='circle', line=dict(width=1, color='DarkSlateGrey'))
        )]
    )

    fig_time_series.update_layout(
        title={
            'text': f'T-Bill Yield Curve for {selected_period}',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=20, color='#1a4d7c')
        },
        xaxis_title='Tenor (Maturity)',
        yaxis_title='Yield (%)',
        xaxis={'categoryorder': 'array', 'categoryarray': tenor_order, 'tickangle': 0, 'tickfont': dict(size=11, color='#1a4d7c')},
        yaxis=dict(range=[y_axis_min, y_axis_max], showgrid=True, gridcolor='#e9ecef', tickfont=dict(size=11, color='#1a4d7c')),
        height=550,
        font=dict(family="Arial, sans-serif", size=12, color='#1a4d7c'),
        template='plotly_white',
        hovermode="x unified"
    )

    st.plotly_chart(fig_time_series, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- 3D Graph and Heatmap ---
    st.subheader("Yield Curve Dynamics (3D & Heatmap)")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### 3D T-Bill Yield Surface")
        plot_df_sorted = plot_df.sort_values(by='Period_Datetime')
        dates_for_3d = plot_df_sorted[period_column_name].unique().tolist()
        z_values_3d = plot_df_sorted[tenor_cols].values

        fig_3d = go.Figure(data=[go.Surface(
            z=z_values_3d,
            x=tenor_cols,
            y=dates_for_3d,
            colorscale='RdBu_r',
            showscale=False
        )])

        fig_3d.update_layout(
            scene=dict(
                xaxis=dict(title=dict(text='Tenor', font=dict(size=14, color='#1a4d7c')), tickfont=dict(size=10, color='#1a4d7c')),
                yaxis=dict(title=dict(text='Period', font=dict(size=14, color='#1a4d7c')), tickfont=dict(size=10, color='#1a4d7c')),
                zaxis=dict(title=dict(text='Yield (%)', font=dict(size=14, color='#1a4d7c')), tickfont=dict(size=10, color='#1a4d7c'))
            ),
            margin=dict(l=25, r=50, b=65, t=50),
            height=650,
            font=dict(family="Arial, sans-serif", size=12, color='#1a4d7c')
        )
        st.plotly_chart(fig_3d, use_container_width=True)


    with col2:
    st.write("### T-Bill Yield Heatmap")

    heatmap_df = tbill_data_df.copy()
    heatmap_df['Period_Datetime'] = pd.to_datetime(heatmap_df[period_column_name], format='%b %y', errors='coerce')
    heatmap_df = heatmap_df.sort_values(by='Period_Datetime')
    heatmap_df.set_index(period_column_name, inplace=True)
    if 'Period_Datetime' in heatmap_df.columns:
        heatmap_df = heatmap_df.drop(columns=['Period_Datetime'])

    fig_heatmap = px.imshow(
        heatmap_df[tenor_cols],
        labels=dict(x="Tenor", y="Period", color="Yield (%)"),
        color_continuous_scale="RdBu_r",
        aspect="auto"
    )

    fig_heatmap.update_layout(
        title="Yield Heatmap",
        xaxis=dict(
            title="Tenor",
            tickangle=45,
            tickfont=dict(size=10, color='#1a4d7c')
        ),
        yaxis=dict(
            title="Period",
            tickfont=dict(size=10, color='#1a4d7c')
        ),
        coloraxis_colorbar=dict(
            title="Yield (%)",
            tickfont=dict(color='#1a4d7c'),
            titlefont=dict(size=12, color='#1a4d7c')
        ),
        font=dict(family="Arial, sans-serif", size=12, color='#1a4d7c'),
        height=650,
        margin=dict(t=50, b=50, l=50, r=50),
        template='plotly_white'
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

else:
    st.info("No T-Bills data available. Please ensure 'pd_dataframe_tbills.xlsx' exists and is correctly formatted.")
