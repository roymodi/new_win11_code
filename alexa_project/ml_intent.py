import json, os, pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

DATA_FILE = "data/intent_train.json"
MODEL_FILE = "data/intent_model.pkl"


def load_training_data():
    try:
        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists(DATA_FILE):
            return [], []

        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        texts = [d["text"] for d in data]
        labels = [d["intent"] for d in data]
        return texts, labels

    except:
        return [], []


def train_model():
    texts, labels = load_training_data()
    if len(texts) < 10:
        return None

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X = vectorizer.fit_transform(texts)

    clf = LogisticRegression(max_iter=200)
    clf.fit(X, labels)

    with open(MODEL_FILE, "wb") as f:
        pickle.dump((vectorizer, clf), f)

    return True


def predict_intent(text):
    if not os.path.exists(MODEL_FILE):
        return None

    try:
        with open(MODEL_FILE, "rb") as f:
            vectorizer, clf = pickle.load(f)

        X = vectorizer.transform([text])
        return clf.predict(X)[0]

    except:
        return None
