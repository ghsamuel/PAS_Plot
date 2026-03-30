import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO
import numpy as np

st.set_page_config(page_title="PAS Bubble Plot Generator", layout="wide")

st.title("🧬 PAS Bubble Plot Generator")
st.markdown("Create bubble plots showing transcript 3' ends relative to polyadenylation sites")

# Sidebar for input method
st.sidebar.header("Input Method")
input_method = st.sidebar.radio(
    "Choose how to input your data:",
    ["Paste Data", "Upload CSV Files", "Use Example Data"]
)

# Initialize session state
if 'pas_df' not in st.session_state:
    st.session_state.pas_df = None
if 'tx_df' not in st.session_state:
    st.session_state.tx_df = None
if 'expr_df' not in st.session_state:
    st.session_state.expr_df = None

# ============================================================================
# INPUT SECTION
# ============================================================================

if input_method == "Use Example Data":
    st.info("Using example SMARCE1 data")
    
    st.session_state.pas_df = pd.DataFrame({
        'pas': ['long', 'medium', 'short'],
        'coord': [40624962, 40627710, 40628724]
    })
    
    st.session_state.tx_df = pd.DataFrame({
        'tx_id': ['ENST00000431889.6', 'ENST00000646448.1', 'ENST00000450046.7',
                  'ENST00000618765.5', 'ENST00000494549.5', 'ENST00000482308.5'],
        'start': [40628980, 40628724, 40627710, 40627652, 40625006, 40624962]
    })
    
    st.session_state.expr_df = pd.DataFrame({
        'tx_id': ['ENST00000431889.6', 'ENST00000646448.1', 'ENST00000450046.7',
                  'ENST00000618765.5', 'ENST00000494549.5', 'ENST00000482308.5'],
        'WT': [52.98, 14.75, 24.56, 19.87, 29.34, 27.65],
        'KD': [55.12, 16.23, 17.89, 13.45, 11.28, 9.87]
    })

elif input_method == "Paste Data":
    st.header("📋 Paste Your Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. PAS Sites")
        st.markdown("Format: `pas,coord`")
        pas_input = st.text_area(
            "Paste PAS data (CSV format)",
            "pas,coord\nlong,40624962\nmedium,40627710\nshort,40628724",
            height=150
        )
        if pas_input:
            st.session_state.pas_df = pd.read_csv(StringIO(pas_input))
    
    with col2:
        st.subheader("2. Transcript Info")
        st.markdown("Format: `tx_id,start`")
        tx_input = st.text_area(
            "Paste transcript data (CSV format)",
            "tx_id,start\nTX1,40628980\nTX2,40627710\nTX3,40624962",
            height=150
        )
        if tx_input:
            st.session_state.tx_df = pd.read_csv(StringIO(tx_input))
    
    with col3:
        st.subheader("3. Expression Data")
        st.markdown("Format: `tx_id,WT,KD,...`")
        expr_input = st.text_area(
            "Paste expression data (CSV format)",
            "tx_id,WT,KD\nTX1,52.98,55.12\nTX2,24.56,17.89\nTX3,29.34,11.28",
            height=150
        )
        if expr_input:
            st.session_state.expr_df = pd.read_csv(StringIO(expr_input))

else:  # Upload CSV Files
    st.header("📁 Upload CSV Files")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. PAS Sites")
        pas_file = st.file_uploader("Upload PAS CSV", type=['csv'], key='pas')
        if pas_file:
            st.session_state.pas_df = pd.read_csv(pas_file)
    
    with col2:
        st.subheader("2. Transcript Info")
        tx_file = st.file_uploader("Upload Transcript CSV", type=['csv'], key='tx')
        if tx_file:
            st.session_state.tx_df = pd.read_csv(tx_file)
    
    with col3:
        st.subheader("3. Expression Data")
        expr_file = st.file_uploader("Upload Expression CSV", type=['csv'], key='expr')
        if expr_file:
            st.session_state.expr_df = pd.read_csv(expr_file)

# ============================================================================
# PREVIEW DATA
# ============================================================================

if st.session_state.pas_df is not None:
    with st.expander("📊 Preview Data", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**PAS Sites:**")
            st.dataframe(st.session_state.pas_df, use_container_width=True)
        with col2:
            st.write("**Transcript Info:**")
            st.dataframe(st.session_state.tx_df, use_container_width=True)
        with col3:
            st.write("**Expression Data:**")
            st.dataframe(st.session_state.expr_df, use_container_width=True)

# ============================================================================
# SETTINGS
# ============================================================================

st.sidebar.header("⚙️ Plot Settings")

pas_window = st.sidebar.number_input("PAS Window (bp)", value=100, min_value=10, step=10)

# Get condition names from expression data
if st.session_state.expr_df is not None:
    conditions = [col for col in st.session_state.expr_df.columns if col != 'tx_id']
    condition_order = st.sidebar.multiselect(
        "Condition Order (top to bottom)",
        conditions,
        default=conditions
    )
else:
    condition_order = ['WT', 'KD']

show_labels = st.sidebar.checkbox("Show transcript labels", value=True)
if show_labels and condition_order:
    label_condition = st.sidebar.selectbox("Label which condition", condition_order)
else:
    label_condition = condition_order[0] if condition_order else 'WT'

zoom_start = st.sidebar.number_input("Zoom Start (optional)", value=0, step=1000)
zoom_end = st.sidebar.number_input("Zoom End (optional)", value=0, step=1000)

plot_title = st.sidebar.text_input("Plot Title", "Transcript 3' ends relative to PAS sites")

# Color palette
color_map = {
    'long': '#2A9D8F',
    'medium': '#E76F51',
    'short': '#4A90D9',
    'unassigned': 'grey'
}

# ============================================================================
# GENERATE PLOT
# ============================================================================

if st.button("🎨 Generate Plot", type="primary"):
    if all([st.session_state.pas_df is not None, 
            st.session_state.tx_df is not None, 
            st.session_state.expr_df is not None]):
        
        with st.spinner("Generating plot..."):
            # Auto-assign PAS
            tx_df = st.session_state.tx_df.copy()
            pas_df = st.session_state.pas_df.copy()
            expr_df = st.session_state.expr_df.copy()
            
            tx_df['nearest_pas'] = 'unassigned'
            tx_df['min_dist'] = np.inf
            
            for i, tx_row in tx_df.iterrows():
                for j, pas_row in pas_df.iterrows():
                    dist = abs(tx_row['start'] - pas_row['coord'])
                    if dist < tx_df.loc[i, 'min_dist']:
                        tx_df.loc[i, 'min_dist'] = dist
                        if dist <= pas_window:
                            tx_df.loc[i, 'nearest_pas'] = pas_row['pas']
            
            st.success(f"✓ Assigned {sum(tx_df['nearest_pas'] != 'unassigned')} transcripts")
            if sum(tx_df['nearest_pas'] == 'unassigned') > 0:
                st.warning(f"⚠ {sum(tx_df['nearest_pas'] == 'unassigned')} transcripts unassigned")
            
            # Merge data
            plot_data = tx_df.merge(expr_df, on='tx_id')
            
            # Reshape to long format
            plot_data_long = pd.melt(
                plot_data,
                id_vars=['tx_id', 'start', 'nearest_pas'],
                value_vars=condition_order,
                var_name='condition',
                value_name='TPM'
            )
            
            # Add y position
            plot_data_long['y_pos'] = plot_data_long['condition'].map(
                {cond: i for i, cond in enumerate(condition_order)}
            )
            
            # Apply zoom
            if zoom_start > 0 and zoom_end > zoom_start:
                plot_data_long = plot_data_long[
                    (plot_data_long['start'] >= zoom_start) & 
                    (plot_data_long['start'] <= zoom_end)
                ]
            
            # Create Plotly figure
            fig = go.Figure()
            
            # Add PAS shaded regions
            for _, pas_row in pas_df.iterrows():
                fig.add_vrect(
                    x0=pas_row['coord'] - pas_window,
                    x1=pas_row['coord'] + pas_window,
                    fillcolor=color_map.get(pas_row['pas'], 'grey'),
                    opacity=0.1,
                    line_width=0
                )
            
            # Add PAS vertical lines
            for _, pas_row in pas_df.iterrows():
                fig.add_vline(
                    x=pas_row['coord'],
                    line_dash="dash",
                    line_color=color_map.get(pas_row['pas'], 'grey'),
                    line_width=2
                )
                
                # Add PAS labels
                fig.add_annotation(
                    x=pas_row['coord'],
                    y=len(condition_order) - 0.4,
                    text=pas_row['pas'],
                    showarrow=False,
                    font=dict(size=12, color=color_map.get(pas_row['pas'], 'grey'), family="Arial Black")
                )
            
            # Add bubbles by PAS class
            for pas_class in plot_data_long['nearest_pas'].unique():
                subset = plot_data_long[plot_data_long['nearest_pas'] == pas_class]
                
                fig.add_trace(go.Scatter(
                    x=subset['start'],
                    y=subset['y_pos'],
                    mode='markers',
                    marker=dict(
                        size=subset['TPM'],
                        sizemode='diameter',
                        sizeref=subset['TPM'].max() / 100,
                        color=color_map.get(pas_class, 'grey'),
                        opacity=0.8,
                        line=dict(width=1, color='white')
                    ),
                    text=subset['tx_id'],
                    hovertemplate='<b>%{text}</b><br>Coord: %{x}<br>TPM: %{marker.size:.1f}<extra></extra>',
                    name=pas_class,
                    showlegend=True
                ))
            
            # Add labels if requested
            if show_labels:
                label_data = plot_data_long[plot_data_long['condition'] == label_condition]
                for _, row in label_data.iterrows():
                    fig.add_annotation(
                        x=row['start'],
                        y=row['y_pos'],
                        text=row['tx_id'],
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=1,
                        arrowcolor='grey',
                        ax=20,
                        ay=-30,
                        font=dict(size=9)
                    )
            
            # Update layout
            fig.update_layout(
                title=dict(text=plot_title, font=dict(size=16)),
                xaxis=dict(
                    title="Genomic coordinate",
                    showgrid=True,
                    gridcolor='lightgrey'
                ),
                yaxis=dict(
                    title="",
                    tickmode='array',
                    tickvals=list(range(len(condition_order))),
                    ticktext=condition_order,
                    showgrid=False
                ),
                plot_bgcolor='white',
                hovermode='closest',
                height=500,
                legend=dict(title="PAS class")
            )
            
            # Display plot
            st.plotly_chart(fig, use_container_width=True)
            
            # Download button
            fig.write_html("pas_bubble_plot.html")
            with open("pas_bubble_plot.html", "rb") as f:
                st.download_button(
                    label="📥 Download Interactive Plot (HTML)",
                    data=f,
                    file_name="pas_bubble_plot.html",
                    mime="text/html"
                )
    else:
        st.error("❌ Please provide all three datasets (PAS sites, Transcript info, Expression data)")

# ============================================================================
# INSTRUCTIONS
# ============================================================================

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown("""
    ### How to Use
    
    **Required Data:**
    1. **PAS Sites** - Polyadenylation site coordinates
       - Columns: `pas` (name), `coord` (coordinate)
       
    2. **Transcript Info** - Transcript 3' end positions
       - Columns: `tx_id` (identifier), `start` (3' end coordinate)
       
    3. **Expression Data** - TPM values per condition
       - Columns: `tx_id`, then one column per condition (e.g., `WT`, `KD`)
    
    **Input Methods:**
    - **Paste Data**: Copy-paste CSV formatted data directly
    - **Upload Files**: Upload 3 separate CSV files
    - **Example Data**: Load SMARCE1 example to see format
    
    **PAS Assignment:**
    - Transcripts are automatically assigned to nearest PAS within the window size
    - Adjust "PAS Window" to change assignment threshold
    
    **Plot Controls:**
    - Reorder conditions to change vertical stacking
    - Toggle labels on/off
    - Zoom to specific region by setting start/end coordinates
    """)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit | PAS Bubble Plot Generator*")
