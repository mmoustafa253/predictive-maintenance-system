# Dashboard Implementation — Dual-Scale Mixer Predictive Maintenance

## Project context
Bachelor thesis at the German University in Cairo, supervised by Dr. Tamer Mostafa. The dashboard demonstrates the Dual-Scale Mixer model's RUL predictions on the NASA C-MAPSS turbofan engine dataset (subsets FD001–FD004).

---

## Repository layout
```
dashboard_code/
├── notebooks/
│   ├── NB1_Transformer_NASA.ipynb
│   ├── NB2_Transformer_KAN_NASA.ipynb
│   ├── NB3_Transformer_KAN_BiLSTM_NASA.ipynb
│   ├── NB4_TFT_KAN_NASA.ipynb
│   ├── iTransformer1_final.ipynb
│   ├── Dual_Mixer_final.ipynb
│   └── XAI_DualMixer.ipynb
├── dashboard/
│   ├── app.py
│   ├── requirements.txt
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── style.css
├── results/                          ← all model outputs; also the dashboard's DATA_DIR
│   ├── transformer_summary.csv
│   ├── tkan_summary.csv
│   ├── tkanbilstm_summary.csv
│   ├── tftkan_summary.csv
│   ├── itransformer_summary.csv
│   ├── dualmixer_summary.csv
│   ├── dualmixer_FD001_predictions.csv
│   ├── dualmixer_FD001_lastcycle.csv
│   ├── dualmixer_FD002_predictions.csv
│   ├── dualmixer_FD002_lastcycle.csv
│   ├── dualmixer_FD003_predictions.csv
│   ├── dualmixer_FD003_lastcycle.csv
│   ├── dualmixer_FD004_predictions.csv
│   └── dualmixer_FD004_lastcycle.csv
├── xai/
│   └── xai_sensor_importance_summary.csv
├── README.md
├── CLAUDE.md
└── .gitignore                        ← excludes *.pt model weights
```

---

## Tech stack
| Layer | Technology | Notes |
|---|---|---|
| Backend | Python 3 · Flask | Serves routes and renders the Jinja2 template |
| Data | pandas | CSV loading only; no database |
| Frontend charts | Plotly.js (CDN) | `plotly-latest.min.js` loaded from `cdn.plot.ly` |
| Frontend layout | Plain HTML + CSS | No React, no Node, no build step |
| Fonts | Google Fonts CDN | Inter (UI) + JetBrains Mono (numbers) |

---

## Data file structure

**`results/dualmixer_summary.csv`** — one row per subset, columns: `Subset`, `Engines`, `RMSE`, `MAE`, `MAPE`, `NASA_Score`, `R2`, `Time_s`. MAPE is stored as a fraction (0.17 = 17%); multiply by 100 for display.

**`results/dualmixer_{subset}_lastcycle.csv`** — one row per engine, columns: `eid`, `true`, `pred`. Used for health status, scatter plot, and metrics.

**`results/dualmixer_{subset}_predictions.csv`** — one row per engine per cycle, columns: `eid`, `true`, `pred`. Used for the trajectory chart.

---

## Flask API routes (app.py)

| Route | Method | Description |
|---|---|---|
| `/` | GET | Renders `index.html` |
| `/api/engines/<subset>` | GET | Returns sorted list of engine IDs for the subset |
| `/api/trajectory/<subset>/<eid>` | GET | Returns `cycles`, `true_rul`, `pred_rul` arrays for one engine |
| `/api/scatter/<subset>` | GET | Returns `true_rul`, `pred_rul`, `engine_ids` for all engines |
| `/api/performance` | GET | Returns all rows of the summary CSV as JSON |
| `/api/health/<subset>/<eid>` | GET | Returns `pred_rul`, `true_rul`, `error`, `status`, `level` for one engine |

`DATA_DIR` in `app.py` resolves to `../results` relative to `dashboard/`.

Health thresholds: `pred_rul > 80` → Healthy, `30–80` → Warning, `< 30` → Critical.

---

## Frontend (index.html + style.css)

Single-page layout. All data is fetched via `fetch()` calls to the Flask API; the page never reloads.

**Components:**
- **Sticky navbar** — title, subtitle, GUC / supervisor metadata
- **Controls card** — Dataset Subset dropdown (FD001–FD004) + Engine ID dropdown (populated dynamically); spinner shown during loads
- **Health card** — animated coloured dot + status text; background gradient changes with health level
- **Three metric cards** — Predicted RUL, True RUL, Prediction Error (colour-coded positive/negative)
- **RUL Trajectory chart** — line chart of true vs predicted RUL over all cycles for the selected engine; dashed threshold lines at RUL = 80 (Warning) and RUL = 30 (Critical)
- **Scatter chart** — predicted vs true RUL for all engines in the subset; points coloured by health status; perfect-prediction diagonal reference line
- **Performance table** — all four subsets with RMSE, MAE, MAPE, NASA Score, R², Train Time; best value per metric highlighted in green

**Plotly configuration:** dark transparent background (`paper_bgcolor: 'transparent'`), shared `BASE` layout object reused across all charts, `displayModeBar: false`, `responsive: true`.

**CSS design system:** dark theme via CSS custom properties (`--bg: #0b1120`, `--surface: #111827`, `--accent: #60a5fa`, `--green: #22c55e`, `--amber: #f59e0b`, `--red: #ef4444`). Responsive grid breakpoints at 1100 px and 700 px.

---

## How to run
```bash
cd dashboard_code/dashboard
python app.py
# → http://localhost:5000
```
Requires: `pip install flask pandas plotly`
