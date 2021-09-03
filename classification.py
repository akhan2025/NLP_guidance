from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from typing import List, Iterable
import numpy as np
import pandas as pd
import logging
import sys
import os

logger = logging.getLogger()
vectorizer = TfidfVectorizer(stop_words='english')


def create_lines() -> List[str]:

    all_lines = []
    for filename in os.listdir("dataverse_files/transcripts/AAPL"):
        with open(os.path.join("dataverse_files/transcripts/AAPL", filename), 'r') as f:
            data = f.read()
        sentences = data.split(".")
        for sentence in sentences:
            all_lines.append(sentence)
    logger.info(f"finished lines: {len(all_lines)}", extra={"length of lines":len(all_lines)})
    return all_lines


    

def create_kmeans(all_lines:list) -> KMeans:
    X = vectorizer.fit_transform(all_lines,)

    true_k = 200

    model = KMeans(n_clusters=true_k, max_iter=10000, n_init=10, verbose=1)
    model.fit(X)

    return model

def predict_sentence(model:KMeans) -> List[int]:
    print("\n")
    print("Prediction")
    X = vectorizer.transform(["Worldwide, 60% of Mac sales were first time buyers and switchers."])
    predicted = model.predict(X)
    logger.info(predicted)
    return predicted

def find_cluster(model:KMeans, predicted:int) -> None:
    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    print(f"cluster {predicted}"),
    for ind in order_centroids[predicted, :10]:
        print(terms[ind])

def setup_logging():
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def main():
    setup_logging()
    lines = create_lines()
    model = create_kmeans(all_lines=lines)
    predicted = predict_sentence(model=model)
    find_cluster(model, predicted[0])


if __name__ == "__main__":
    main()
