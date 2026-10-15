"""
Bot-Like Comment Detection - Model Training Script
Dataset : YouTube Spam Comments (UCI-style)
Model   : TF-IDF weights + Multinomial Naive Bayes (pure numpy, no scipy/sklearn)
"""

import os
import re
import string
import math
import pickle

import numpy as np
import pandas as pd
import nltk

nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords

STOP_WORDS = set(stopwords.words('english'))
DATA_PATH  = os.path.join(os.path.dirname(__file__), 'data', 'youtube_spam.csv')
MODEL_DIR  = os.path.join(os.path.dirname(__file__), 'model')

# ── Text helpers ──────────────────────────────────────────────────────────────

def preprocess(text: str) -> list[str]:
    text = str(text).lower()
    text = re.sub(r'http\S+|www\.\S+', ' url ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    return [w for w in text.split() if w not in STOP_WORDS and len(w) > 1]


def build_vocab(docs: list[list[str]], max_features: int = 3000) -> dict:
    """Build vocabulary of the top-N most frequent tokens (+ bigrams)."""
    freq = {}
    for tokens in docs:
        # unigrams
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        # bigrams
        for a, b in zip(tokens, tokens[1:]):
            bg = f"{a}__{b}"
            freq[bg] = freq.get(bg, 0) + 1
    # sort by frequency, take top max_features
    sorted_vocab = sorted(freq, key=freq.get, reverse=True)[:max_features]
    return {w: i for i, w in enumerate(sorted_vocab)}


def tfidf_matrix(docs: list[list[str]], vocab: dict) -> np.ndarray:
    """Compute TF-IDF matrix (n_docs × vocab_size)."""
    n     = len(docs)
    V     = len(vocab)
    mat   = np.zeros((n, V), dtype=np.float32)

    # TF
    for i, tokens in enumerate(docs):
        grams = list(tokens) + [f"{a}__{b}" for a, b in zip(tokens, tokens[1:])]
        for g in grams:
            if g in vocab:
                mat[i, vocab[g]] += 1
        total = mat[i].sum()
        if total > 0:
            mat[i] /= total

    # IDF
    df  = (mat > 0).sum(axis=0)          # document frequency per term
    idf = np.log((n + 1) / (df + 1)) + 1  # smoothed IDF
    mat *= idf
    return mat


def extract_rule_features(texts: list[str]) -> np.ndarray:
    """10 hand-crafted bot-signal features."""
    spam_keywords = [
        'free','click','win','subscribe','sub','earn','money','cash',
        'gift','prize','visit','check','followers','likes','views',
        'profit','guaranteed','bitcoin','crypto','investment','opportunity'
    ]
    rows = []
    for text in texts:
        t = str(text)
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
        avg_wl  = np.mean([len(w) for w in words]) if words else 0

        rows.append([clen, len(words), upper_r, has_url,
                     excl, rep, kw_cnt, punct_r, dig_r, avg_wl])
    return np.array(rows, dtype=np.float32)


# ── Naive Bayes (pure numpy) ──────────────────────────────────────────────────

class NaiveBayesClassifier:
    """Gaussian NB for combined TF-IDF + rule features."""

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.classes_  = np.unique(y)
        self.class_prior_ = {}
        self.theta_    = {}   # mean per class
        self.sigma_    = {}   # variance per class

        for c in self.classes_:
            Xc = X[y == c]
            self.class_prior_[c] = len(Xc) / len(X)
            self.theta_[c]       = Xc.mean(axis=0)
            self.sigma_[c]       = Xc.var(axis=0) + 1e-9   # smoothing

        return self

    def _log_likelihood(self, X: np.ndarray, c: int) -> np.ndarray:
        mu  = self.theta_[c]
        var = self.sigma_[c]
        # log of Gaussian pdf, summed across features
        ll = -0.5 * np.sum(np.log(2 * math.pi * var) + ((X - mu) ** 2) / var, axis=1)
        return ll + math.log(self.class_prior_[c])

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        log_probs = np.column_stack([self._log_likelihood(X, c) for c in self.classes_])
        # softmax for probabilities
        log_probs -= log_probs.max(axis=1, keepdims=True)
        probs = np.exp(log_probs)
        probs /= probs.sum(axis=1, keepdims=True)
        return probs

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.classes_[self.predict_proba(X).argmax(axis=1)]


# ── Training pipeline ─────────────────────────────────────────────────────────

def train():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    df.dropna(subset=['CONTENT', 'CLASS'], inplace=True)
    df['CLASS'] = df['CLASS'].astype(int)

    print(f"  Total  : {len(df)}")
    print(f"  Spam   : {df['CLASS'].sum()}")
    print(f"  Ham    : {(df['CLASS'] == 0).sum()}")

    texts  = df['CONTENT'].tolist()
    labels = df['CLASS'].values

    # Tokenise
    tokenised = [preprocess(t) for t in texts]

    # Build vocab & TF-IDF
    vocab  = build_vocab(tokenised, max_features=3000)
    X_tfidf = tfidf_matrix(tokenised, vocab)

    # Rule features
    X_rules = extract_rule_features(texts)

    # Normalise rule features (min-max per column)
    r_min  = X_rules.min(axis=0)
    r_max  = X_rules.max(axis=0)
    r_range = np.where(r_max - r_min == 0, 1, r_max - r_min)
    X_rules_norm = (X_rules - r_min) / r_range

    # Combine
    X = np.hstack([X_tfidf, X_rules_norm])
    y = labels

    # Train / test split (manual, 80 / 20)
    np.random.seed(42)
    idx   = np.random.permutation(len(X))
    split = int(0.8 * len(X))
    tr, te = idx[:split], idx[split:]
    X_train, X_test = X[tr], X[te]
    y_train, y_test = y[tr], y[te]

    print("\nTraining Naive Bayes classifier...")
    clf = NaiveBayesClassifier()
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    acc    = (y_pred == y_test).mean()
    print(f"Test Accuracy : {acc*100:.1f}%")

    # Detailed metrics
    for label, name in [(1, 'Bot'), (0, 'Human')]:
        tp = ((y_pred == label) & (y_test == label)).sum()
        fp = ((y_pred == label) & (y_test != label)).sum()
        fn = ((y_pred != label) & (y_test == label)).sum()
        prec = tp / max(tp + fp, 1)
        rec  = tp / max(tp + fn, 1)
        f1   = 2 * prec * rec / max(prec + rec, 1e-9)
        print(f"  {name:6s} — Precision: {prec:.2f}  Recall: {rec:.2f}  F1: {f1:.2f}")

    # Save artefacts
    os.makedirs(MODEL_DIR, exist_ok=True)
    artefacts = {
        'clf':      clf,
        'vocab':    vocab,
        'r_min':    r_min,
        'r_max':    r_max,
        'r_range':  r_range,
    }
    with open(os.path.join(MODEL_DIR, 'model.pkl'), 'wb') as f:
        pickle.dump(artefacts, f)

    print(f"\n✓ Model saved to {MODEL_DIR}/model.pkl")
    return artefacts


if __name__ == '__main__':
    train()
