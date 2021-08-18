import config
from transformers import BertModel
import torch.nn as nn


class BERTBaseUncased(nn.Module):
    def __init__(self):
        super(BERTBaseUncased, self).__init__()
        self.bert = BertModel.from_pretrained(config.BERT_PATH, return_dict=False)
        self.bert_drop = nn.Dropout(config.DROPOUT)
        self.out = nn.Linear(config.BERT_DIM, config.NUM_CLASSES)

    def forward(self, input_ids, attention_mask, token_type_ids):
        _, pooled_output = self.bert(
            input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids
        )
        drop_output = self.bert_drop(pooled_output)
        output = self.out(drop_output)
        return output
