import flask
import config
import torch
from flask import Flask, request
from model import BERTBaseUncased

app = Flask(__name__)

MODEL = None
DEVICE = config.DEVICE


def sentence_prediction(sentence):
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


@app.route("/predict")
def predict():
    sentence = request.args.get("sentence")
    positive_prediction = sentence_prediction(sentence)
    negative_prediction = 1 - positive_prediction
    print(sentence)
    response = {
        "positive": str(positive_prediction),
        "negative": str(negative_prediction),
        "sentence": str(sentence),
    }
    return flask.jsonify(response)


if __name__ == "__main__":
    MODEL = BERTBaseUncased().to(DEVICE)
    MODEL.load_state_dict(torch.load(config.MODEL_PATH + "/model.bin"))
    MODEL.eval()
    app.run(debug=True)
