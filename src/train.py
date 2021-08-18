import config
import dataset
import engine

import torch
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
from model import BERTBaseUncased
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from transformers import AdamW, get_linear_schedule_with_warmup

# Removing html tags
def removehtml(text):
    soup = bs(text, "lxml")
    return soup.get_text()


def run():
    df = pd.read_csv(config.TRAINING_FILE)
    # Encoding target variable
    df.sentiment = df.sentiment.apply(lambda x: 1 if x == "positive" else 0)
    # Removing html tags
    df["review"] = df.review.apply(removehtml)

    # Splitting data into training and validation
    df_train, df_valid = train_test_split(
        df, test_size=0.1, random_state=42, stratify=df.sentiment.values
    )

    # resetting index because DataLoader will use the indexes to pass
    # batches of data to model
    df_train = df_train.reset_index(drop=True)
    df_valid = df_valid.reset_index(drop=True)

    train_dataset = dataset.BERTDataset(
        review=df_train.review.values, target=df_train.sentiment.values,
    )

    train_data_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=config.TRAIN_BATCH_SIZE, num_workers=4,
    )

    valid_dataset = dataset.BERTDataset(
        review=df_valid.review.values, target=df_valid.sentiment.values,
    )

    valid_data_loader = torch.utils.data.DataLoader(
        valid_dataset, batch_size=config.VALID_BATCH_SIZE, num_workers=4,
    )

    # Initialising model
    model = BERTBaseUncased().to(config.DEVICE)

    param_optimizer = list(model.named_parameters())
    no_decay = ["bias", "LayerNorm.bias", "LayerNorm.weight"]
    mizer_parameters = [
        {
            "params": [
                p for n, p in param_optimizer if not any(nd in n for nd in no_decay)
            ],
            "weight_decay": 0.001,
        },
        {
            "params": [
                p for n, p in param_optimizer if any(nd in n for nd in no_decay)
            ],
            "weight_decay": 0.0,
        },
    ]
    num_train_steps = int(len(df_train)) / config.TRAIN_BATCH_SIZE * config.EPOCHS
    optimizer = AdamW(mizer_parameters, lr=config.LEARNING_RATE)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=0, num_training_steps=num_train_steps,
    )

    best_accuracy = 0.0
    for epoch in range(config.EPOCHS):
        engine.train_fn(
            data_loader=train_data_loader,
            model=model,
            optimizer=optimizer,
            device=config.DEVICE,
            accumulation_steps=config.ACCUMULATION_STEPS,
            scheduler=scheduler,
        )
        targets, outputs = engine.eval_fn(valid_data_loader, model, config.DEVICE)
        outputs = np.array(outputs) >= 0.5
        accuracy = accuracy_score(targets, outputs)
        print(f"Epoch {epoch}, accuracy: {accuracy}")
        if accuracy > best_accuracy:
            torch.save(model.state_dict(), config.MODEL_PATH+f"bert_model_{epoch}.bin")
            best_accuracy = accuracy


if __name__ == "__main__":
    run()
