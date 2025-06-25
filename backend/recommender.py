import numpy as np
import pandas as pd
import gzip
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing import FunctionTransformer


class TabularSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X['tabular']


class TextSelector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X['text']


class AutoMLRecommender:
    def __init__(self, param_grid=None, use_tabular=True, use_text=True):
        self.use_tabular = use_tabular
        self.use_text = use_text
        self.param_grid = param_grid or {
            'features__tabular__kbest__k': [2, 4],
            'features__text__tfidf__max_features': [50, 100],
            'nn__n_neighbors': [5, 10],
        }
        self.pipeline = None
        self.best_params_ = None
        self.nn = None
        self.X_ = None

    def fit(self, tabular, text, y, n_neighbors=6):
        X = {'tabular': tabular, 'text': text}
        features_list = []
        if self.use_tabular:
            features_list.append(
                ('tabular', Pipeline([
                    ('selector', TabularSelector()),
                    ('scaler', StandardScaler()),
                    ('kbest', SelectKBest(f_classif, k=4)),
                ]))
            )
        if self.use_text:
            features_list.append(
                ('text', Pipeline([
                    ('selector', TextSelector()),
                    ('tfidf', TfidfVectorizer(max_features=100)),
                ]))
            )
        if not features_list:
            raise ValueError(
                'At least one of use_tabular or use_text must be True')
        features = FeatureUnion(features_list)
        pipe = Pipeline([
            ('features', features),
            ('norm', FunctionTransformer(normalize)),
            ('nn', NearestNeighbors(n_neighbors=n_neighbors, metric='cosine'))
        ])
        pipe.fit(X, y)
        self.pipeline = pipe
        self.best_params_ = None
        self.nn = self.pipeline.named_steps['nn']
        self.X_ = self.pipeline.named_steps['features'].transform(X)

    def recommend(self, idx, k=5):
        d, inds = self.nn.kneighbors(self.X_[idx:idx+1], n_neighbors=k+1)
        return inds[0][1:]

    def precision_at_k(self, y_true, neighbors_idx, k=5):
        return precision_at_k(y_true, neighbors_idx, k)

    def recall_at_k(self, y_true, neighbors_idx, k=5):
        return recall_at_k(y_true, neighbors_idx, k)

    def map_at_k(self, y_true, neighbors_idx, k=5):
        return map_at_k(y_true, neighbors_idx, k)

    def mrr_at_k(self, y_true, neighbors_idx, k=5):
        return mrr_at_k(y_true, neighbors_idx, k)

    def diversity_at_k(self, neighbors_idx, k=5):
        return diversity_at_k(neighbors_idx, k)


def precision_at_k(y_true, neighbors_idx, k=5):
    return np.mean([
        np.mean(y_true[neighbors_idx[i]] == y_true[i])
        for i in range(len(y_true))
    ])


def recall_at_k(y_true, neighbors_idx, k=5):
    return np.mean([
        np.any(y_true[neighbors_idx[i]] == y_true[i])
        for i in range(len(y_true))
    ])


def map_at_k(y_true, neighbors_idx, k=5):
    ap_list = []
    for i in range(len(y_true)):
        hits = 0
        sum_prec = 0
        for j in range(k):
            if y_true[neighbors_idx[i][j]] == y_true[i]:
                hits += 1
                sum_prec += hits / (j + 1)
        ap = sum_prec / k
        ap_list.append(ap)
    return np.mean(ap_list)


def mrr_at_k(y_true, neighbors_idx, k=5):
    rr_list = []
    for i in range(len(y_true)):
        rr = 0
        for j in range(k):
            if y_true[neighbors_idx[i][j]] == y_true[i]:
                rr = 1 / (j + 1)
                break
        rr_list.append(rr)
    return np.mean(rr_list)


def diversity_at_k(neighbors_idx, k=5):
    all_recs = neighbors_idx.flatten()
    return len(np.unique(all_recs)) / all_recs.size


def load_off_dataset_light(jsonl_path, n_samples=100):
    usecols = ['product_name', 'ingredients_text', 'nutriments', 'categories']
    records = []
    with gzip.open(jsonl_path, 'rt', encoding='utf-8') as f:
        for line in f:
            if len(records) >= n_samples:
                break
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if all(col in rec and rec[col] for col in usecols):
                records.append({col: rec[col] for col in usecols})
    df = pd.DataFrame(records)
    tab = np.vstack([
        [
            r.get('nutriments', {}).get('energy_100g', 0),
            r.get('nutriments', {}).get('fat_100g', 0),
            r.get('nutriments', {}).get('proteins_100g', 0),
            r.get('nutriments', {}).get('carbohydrates_100g', 0)
        ]
        for r in records
    ])
    text = (df['product_name'] + '. ' + df['ingredients_text']).tolist()
    df['main_category'] = df['categories'].str.split(',').str[0]
    labels = df['main_category'].astype('category').cat.codes.values
    return tab, text, labels, df
