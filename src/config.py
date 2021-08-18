from transformers import BertTokenizer
import torch

TRAINING_FILE = "../data/train.csv"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MAX_LEN = 160
TRAIN_BATCH_SIZE = 8
VALID_BATCH_SIZE = 8
LEARNING_RATE = 3e-5
DROPOUT = 0.2
BERT_DIM = 768
NUM_CLASSES = 1
EPOCHS = 10
ACCUMULATION_STEPS = 2
BERT_PATH = "C:/bert_base_uncased/"
MODEL_PATH = "../models/"
TOKENIZER = BertTokenizer.from_pretrained(BERT_PATH, do_lower_case=True)
