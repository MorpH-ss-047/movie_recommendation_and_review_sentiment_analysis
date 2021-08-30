import flask
import config
import torch
from flask import Flask, request
from model import BERTBaseUncased
import scrape_reviews

app = Flask(__name__)

MODEL = None
DEVICE = config.DEVICE


def get_sentiment(sentence):
    tokenizer = config.TOKENIZER
    max_len = config.MAX_LEN
    sentence = str(sentence)
    sentence = " ".join(sentence.split())

    inputs = tokenizer.encode_plus(
        sentence,
        None,
        add_special_tokens=True,
        max_length=max_len,
        truncation=True,
        padding="max_length",
        return_tensors="pt",
    ).to(DEVICE)

    outputs = MODEL(**inputs)
    outputs = torch.sigmoid(outputs).cpu().detach().numpy()[0][0]
    return outputs


@app.route("/")
def predict():
    movie_name = request.args.get("movie_name")
    review_list = scrape_reviews.get_reviews(movie_name)
    pos_list = []
    neg_list = []
    for sentence in review_list:
        prediction = get_sentiment(sentence)
        positive_prediction = prediction
        negative_prediction = 1 - positive_prediction
        pos_list.append(positive_prediction)
        neg_list.append(negative_prediction)
    positive_score = sum(pos_list) / len(pos_list)
    negative_score = sum(neg_list) / len(neg_list)
    response = {
        "Verdict": "Positive" if positive_score > negative_score else "Negative",
        "movie_name": str(movie_name),
        "negative": str(negative_score),
        "positive": str(positive_score),
    }
    return flask.jsonify(response)


@app.route("/predict")
def predict_sentence():
    sentence = request.args.get("sentence")
    positive_prediction = get_sentiment(sentence)
    negative_prediction = 1 - positive_prediction
    print(sentence)
    response = {
        "Verdict": "Positive" if positive_prediction > negative_prediction else "Negative",
        "positive": str(positive_prediction),
        "negative": str(negative_prediction),
        "sentence": str(sentence),
    }
    return flask.jsonify(response)


if __name__ == "__main__":
    MODEL = BERTBaseUncased().to(DEVICE)
    MODEL.load_state_dict(torch.load(config.MODEL_PATH + "bert_model_2.bin"))
    MODEL.eval()
    app.run(debug=True)
