# PAS Bubble Plot - Streamlit App

Interactive web app to generate PAS (polyadenylation site) bubble plots with manual data entry or file upload.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

✨ **3 Input Methods:**
- Paste data directly (CSV format)
- Upload 3 CSV files
- Use example SMARCE1 data

📊 **Interactive Plot:**
- Hover to see details
- Zoom and pan
- Download as HTML

⚙️ **Customizable:**
- Adjust PAS window size
- Reorder conditions
- Toggle labels
- Zoom to region

🎯 **Auto PAS Assignment:**
- Automatically assigns transcripts to nearest PAS
- Shows assignment summary

## Input Format

### 1. PAS Sites (CSV)
```
pas,coord
long,40624962
medium,40627710
short,40628724
```

### 2. Transcript Info (CSV)
```
tx_id,start
TX1,40628980
TX2,40627710
TX3,40624962
```

### 3. Expression Data (CSV)
```
tx_id,WT,KD
TX1,52.98,55.12
TX2,24.56,17.89
TX3,29.34,11.28
```

For **3+ conditions**, just add more columns:
```
tx_id,Control,Treatment_1h,Treatment_6h,Treatment_24h
TX1,50,48,42,35
```

## Deploy Online (Optional)

Share your app with others:

1. Create account at [Streamlit Cloud](https://streamlit.io/cloud)
2. Connect your GitHub repo
3. Deploy with one click

Free hosting for public apps!

## Usage Tips

- **Small datasets**: Use "Paste Data" - quick for 5-10 transcripts
- **Larger datasets**: Use "Upload CSV Files"
- **Testing**: Use "Example Data" to see the format
- **Multiple conditions**: App handles 2, 3, 4+ conditions automatically
- **PAS assignment**: Transcripts within the window get assigned to nearest PAS

## Screenshots

[App shows 3 tabs for data entry, interactive plot, and settings panel]

## Requirements

- Python 3.8+
- streamlit
- pandas
- plotly
- numpy
