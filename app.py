"""
Bot-Like Comment Detection — Flask Web Application
Pure-numpy model (no scipy / sklearn DLL dependencies)
"""

import os
import re
import string
import pickle
import base64
import io
import math

import numpy as np
import pandas as pd
import nltk
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# ── NLTK ─────────────────────────────────────────────────────────────────────
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords
STOP_WORDS = set(stopwords.words('english'))

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(__file__)
MODEL_PATH  = os.path.join(BASE_DIR, 'model', 'model.pkl')
DATA_PATH   = os.path.join(BASE_DIR, 'data', 'youtube_spam.csv')
UPLOAD_DIR  = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'botdetect_secret_2024'
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'csv'}


# ── Load / train model ────────────────────────────────────────────────────────
# Import NaiveBayesClassifier into this namespace so pickle can resolve it
# regardless of whether it was saved from __main__ or train_model.
from train_model import NaiveBayesClassifier, train as _train_fn   # noqa: F401

def load_or_train():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            artefacts = pickle.load(f)
        print("✓ Model loaded from disk.")
        return artefacts
    print("⚙  Model not found — training now...")
    return _train_fn()

artefacts = load_or_train()
clf     = artefacts['clf']
vocab   = artefacts['vocab']
r_min   = artefacts['r_min']
r_max   = artefacts['r_max']
r_range = artefacts['r_range']


# ── Feature helpers (must mirror train_model.py exactly) ─────────────────────

def preprocess(text: str) -> list:
    text = str(text).lower()
    text = re.sub(r'http\S+|www\.\S+', ' url ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    return [w for w in text.split() if w not in STOP_WORDS and len(w) > 1]


def tfidf_single(tokens: list) -> np.ndarray:
    """TF-IDF vector for one comment."""
    V   = len(vocab)
    vec = np.zeros(V, dtype=np.float32)
    grams = list(tokens) + [f"{a}__{b}" for a, b in zip(tokens, tokens[1:])]
    for g in grams:
        if g in vocab:
            vec[vocab[g]] += 1
    total = vec.sum()
    if total > 0:
        vec /= total
    return vec


def rule_features_single(text: str) -> np.ndarray:
    spam_keywords = [
        'free','click','win','subscribe','sub','earn','money','cash',
        'gift','prize','visit','check','followers','likes','views',
        'profit','guaranteed','bitcoin','crypto','investment','opportunity'
    ]
    t     = str(text)
    words = t.split()
    clen  = len(t)

    upper_r = sum(1 for c in t if c.isupper()) / max(clen, 1)
    has_url = int(bool(re.search(r'http[s]?://|www\.', t, re.IGNORECASE)))
    excl    = t.count('!')

    if words:
        uniq = set(w.lower() for w in words)
        rep  = 1 - len(uniq) / len(words)
    else:
        rep = 0.0

    kw_cnt  = sum(1 for kw in spam_keywords if kw in t.lower())
    punct_r = sum(1 for c in t if c in string.punctuation) / max(clen, 1)
    dig_r   = sum(1 for c in t if c.isdigit()) / max(clen, 1)
    avg_wl  = float(np.mean([len(w) for w in words])) if words else 0.0

    raw = np.array([clen, len(words), upper_r, has_url,
                    excl, rep, kw_cnt, punct_r, dig_r, avg_wl], dtype=np.float32)
    return (raw - r_min) / r_range


def predict_comment(text: str) -> dict:
    tokens  = preprocess(text)
    tfidf_v = tfidf_single(tokens)
    rule_v  = rule_features_single(text)
    X       = np.hstack([tfidf_v, rule_v]).reshape(1, -1)

    proba      = clf.predict_proba(X)[0]          # [p_human, p_bot]
    pred       = int(clf.predict(X)[0])
    confidence = float(max(proba)) * 100

    # Human-readable signals
    signals = []
    t = str(text)
    if re.search(r'http[s]?://|www\.', t, re.IGNORECASE):
        signals.append("Contains URL / external link")
    if t.count('!') >= 2:
        signals.append(f"Excessive exclamation marks ({t.count('!')})")
    words = t.split()
    if words:
        uniq = set(w.lower() for w in words)
        rep  = 1 - len(uniq) / len(words)
        if rep > 0.3:
            signals.append(f"High word repetition ({rep*100:.0f}%)")
    upper_r = sum(1 for c in t if c.isupper()) / max(len(t), 1)
    if upper_r > 0.3:
        signals.append(f"High uppercase ratio ({upper_r*100:.0f}%)")
    spam_kw = ['free','click','win','subscribe','sub','earn','money',
               'cash','gift','prize','visit','followers','guaranteed']
    found = [kw for kw in spam_kw if kw in t.lower()]
    if found:
        signals.append(f"Spam keywords detected: {', '.join(found[:4])}")
    if len(t) < 20:
        signals.append("Very short comment (possible template)")

    return {
        'label':      'Bot' if pred == 1 else 'Human',
        'is_bot':     pred == 1,
        'confidence': round(confidence, 1),
        'bot_prob':   round(float(proba[1]) * 100, 1),
        'human_prob': round(float(proba[0]) * 100, 1),
        'signals':    signals,
        'comment':    text,
    }


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def make_chart_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return b64


def generate_bulk_charts(results: list) -> dict:
    bot_count   = sum(1 for r in results if r['is_bot'])
    human_count = len(results) - bot_count
    charts = {}

    # Pie chart
    fig, ax = plt.subplots(figsize=(5, 5))
    labels  = []
    values  = []
    colors  = []
    if bot_count:
        labels.append('Bot');   values.append(bot_count);   colors.append('#ef4444')
    if human_count:
        labels.append('Human'); values.append(human_count); colors.append('#22c55e')
    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors,
           startangle=140, textprops={'fontsize': 13, 'color': 'white'})
    ax.set_facecolor('#1e293b')
    fig.patch.set_facecolor('#1e293b')
    ax.set_title('Bot vs Human Distribution', color='white', fontsize=14, pad=15)
    charts['pie'] = make_chart_b64(fig)

    # Confidence histogram
    fig, ax = plt.subplots(figsize=(7, 4))
    bot_conf   = [r['confidence'] for r in results if r['is_bot']]
    human_conf = [r['confidence'] for r in results if not r['is_bot']]
    if bot_conf:
        ax.hist(bot_conf,   bins=10, color='#ef4444', alpha=0.8, label='Bot',   edgecolor='white')
    if human_conf:
        ax.hist(human_conf, bins=10, color='#22c55e', alpha=0.8, label='Human', edgecolor='white')
    ax.set_xlabel('Confidence (%)', color='white')
    ax.set_ylabel('Count',          color='white')
    ax.set_title('Confidence Score Distribution', color='white', fontsize=13)
    ax.tick_params(colors='white')
    ax.legend(facecolor='#334155', labelcolor='white')
    ax.set_facecolor('#1e293b')
    fig.patch.set_facecolor('#1e293b')
    for spine in ax.spines.values():
        spine.set_edgecolor('#475569')
    charts['hist'] = make_chart_b64(fig)

    return charts


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    comment = request.form.get('comment', '').strip()
    if not comment:
        flash('Please enter a comment to analyze.', 'warning')
        return redirect(url_for('index'))
    result = predict_comment(comment)
    return render_template('result.html', result=result)


@app.route('/bulk', methods=['GET', 'POST'])
def bulk():
    if request.method == 'GET':
        return render_template('bulk.html')

    if 'file' not in request.files:
        flash('No file selected.', 'warning')
        return redirect(url_for('bulk'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'warning')
        return redirect(url_for('bulk'))

    if not allowed_file(file.filename):
        flash('Only CSV files are supported.', 'danger')
        return redirect(url_for('bulk'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        df = pd.read_csv(filepath)
        col = None
        for candidate in ['CONTENT', 'content', 'comment', 'Comment', 'text', 'Text']:
            if candidate in df.columns:
                col = candidate
                break
        if col is None:
            col = df.columns[0]
        df = df[[col]].rename(columns={col: 'CONTENT'}).dropna().head(200)

        results = [predict_comment(row) for row in df['CONTENT']]
        charts  = generate_bulk_charts(results)

        bot_count = sum(1 for r in results if r['is_bot'])
        summary = {
            'total':       len(results),
            'bot_count':   bot_count,
            'human_count': len(results) - bot_count,
            'bot_pct':     round(bot_count / max(len(results), 1) * 100, 1),
            'avg_conf':    round(sum(r['confidence'] for r in results) / max(len(results), 1), 1),
        }
        return render_template('bulk.html', results=results, summary=summary, charts=charts)

    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'danger')
        return redirect(url_for('bulk'))

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    from flask import jsonify
    data = request.get_json(silent=True)
    if not data or 'comment' not in data:
        return jsonify({'error': 'Missing "comment" field'}), 400
    return jsonify(predict_comment(data['comment']))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
