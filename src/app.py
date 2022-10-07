import flask
import config
import torch
from flask import Flask, request, render_template, redirect, url_for
from model import BERTBaseUncased
from scraper.review_scraper import MovieNotFound, ReviewScraper

app = Flask(__name__)

MODEL = None
DEVICE = config.DEVICE
TOKENIZER = config.TOKENIZER
MAX_LEN = config.MAX_LEN


def get_sentiment(review):
    review = str(review)
    review = " ".join(review.split())

    inputs = TOKENIZER.encode_plus(
        review,
        None,
        add_special_tokens=True,
        max_length=MAX_LEN,
        truncation=True,
        padding="max_length",
        return_tensors="pt",
    ).to(DEVICE)

    outputs = MODEL(**inputs)
    outputs = torch.sigmoid(outputs).cpu().detach().numpy()[0][0]
    return outputs


def get_sentiment_of_reviews(movie_name: str):
    try:
        scraper = ReviewScraper(movie_name=movie_name, review_count=100)
    except MovieNotFound:
        redirect(url_for("home_page"))
    
    review_list = scraper.get_reviews()
    pos_list = []
    neg_list = []
    for i, review in enumerate(review_list):
        print("[INFO] Predicting review:", i, "...")
        positive_prediction = get_sentiment(review)
        negative_prediction = 1 - positive_prediction
        pos_list.append(positive_prediction)
        neg_list.append(negative_prediction)
    print(f"[INFO] Prediction from model finished for all {i+1} reviews")
    positive_score = sum(pos_list) / len(pos_list)
    negative_score = sum(neg_list) / len(neg_list)

    return positive_score, negative_score


# home page
@app.route("/", methods=["GET", "POST"])
def home_page():
    return render_template("index.html")


# predict page
@app.route("/predict", methods=["GET", "POST"])
def predict():
    movie_name = request.form.get("movie")
    # movie_name = movie_name['movie']    
    positive_score, negative_score = get_sentiment_of_reviews(movie_name)
    response = {
        "Verdict": "Positive" if positive_score > negative_score else "Negative",
        "movie_name": str(movie_name),
        "negative": str(negative_score),
        "positive": str(positive_score),
    }
    return render_template("predict.html", response=response)


# api response(JSON) of the sentiment of reviews of the given movie 
@app.route("/api/predict-sentiment")
def api_response():
    movie_name = request.args.get("movie_name")
    positive_score, negative_score = get_sentiment(movie_name)
    response = {
        "Verdict": "Positive" if positive_score > negative_score else "Negative",
        "movie_name": str(movie_name),
        "negative": str(negative_score),
        "positive": str(positive_score),
    }
    return flask.jsonify(response)


# api response(JSON) of the sentiment of a given review
@app.route("/api/get-sentiment-of-custom-input")
def predict_sentence():
    sentence = request.args.get("sentence")
    positive_score = get_sentiment(sentence)
    negative_score = 1 - positive_score
    response = {
        "Verdict": "Positive" if positive_score > negative_score else "Negative",
        "positive": str(positive_score),
        "negative": str(negative_score),
        "sentence": str(sentence),
    }
    return flask.jsonify(response)


if __name__ == "__main__":
    MODEL = BERTBaseUncased().to(DEVICE)
    MODEL.load_state_dict(torch.load(config.MODEL_PATH + "bert_model_2.bin"))
    MODEL.eval()
    app.run(debug=True)
