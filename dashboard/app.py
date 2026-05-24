import os
import pandas as pd
from flask import Flask, render_template, jsonify

app = Flask(__name__)

DATA_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
)
SUBSETS = ['FD001', 'FD002', 'FD003', 'FD004']


def _csv(name):
    return os.path.join(DATA_DIR, name)


def load_summary():
    return pd.read_csv(_csv('dualmixer_summary.csv'))


def load_lastcycle(subset):
    df = pd.read_csv(_csv(f'dualmixer_{subset}_lastcycle.csv'))
    df['eid'] = df['eid'].astype(int)
    return df


def load_predictions(subset):
    df = pd.read_csv(_csv(f'dualmixer_{subset}_predictions.csv'))
    df['eid'] = df['eid'].astype(int)
    return df


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/engines/<subset>')
def api_engines(subset):
    if subset not in SUBSETS:
        return jsonify({'error': 'Invalid subset'}), 400
    df = load_lastcycle(subset)
    return jsonify({'engines': sorted(df['eid'].tolist())})


@app.route('/api/trajectory/<subset>/<int:eid>')
def api_trajectory(subset, eid):
    if subset not in SUBSETS:
        return jsonify({'error': 'Invalid subset'}), 400
    df = load_predictions(subset)
    edf = df[df['eid'] == eid].reset_index(drop=True)
    if edf.empty:
        return jsonify({'error': 'Engine not found'}), 404
    return jsonify({
        'cycles': list(range(1, len(edf) + 1)),
        'true_rul': edf['true'].round(2).tolist(),
        'pred_rul': edf['pred'].round(2).tolist(),
    })


@app.route('/api/scatter/<subset>')
def api_scatter(subset):
    if subset not in SUBSETS:
        return jsonify({'error': 'Invalid subset'}), 400
    df = load_lastcycle(subset)
    return jsonify({
        'true_rul': df['true'].round(2).tolist(),
        'pred_rul': df['pred'].round(2).tolist(),
        'engine_ids': df['eid'].tolist(),
    })


@app.route('/api/performance')
def api_performance():
    df = load_summary()
    return jsonify({'data': df.to_dict(orient='records')})


@app.route('/api/health/<subset>/<int:eid>')
def api_health(subset, eid):
    if subset not in SUBSETS:
        return jsonify({'error': 'Invalid subset'}), 400
    df = load_lastcycle(subset)
    row = df[df['eid'] == eid]
    if row.empty:
        return jsonify({'error': 'Engine not found'}), 404
    pred = float(row['pred'].iloc[0])
    true_val = float(row['true'].iloc[0])
    if pred > 80:
        status, level = 'Healthy', 'healthy'
    elif pred >= 30:
        status, level = 'Warning', 'warning'
    else:
        status, level = 'Critical', 'critical'
    return jsonify({
        'engine_id': eid,
        'pred_rul': round(pred, 2),
        'true_rul': round(true_val, 2),
        'error': round(pred - true_val, 2),
        'status': status,
        'level': level,
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
