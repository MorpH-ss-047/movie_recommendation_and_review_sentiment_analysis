import torch
import torch.nn as nn
from tqdm import tqdm


def loss_fn(outputs, targets):
    return nn.BCEWithLogitsLoss()(outputs, targets.view(-1, 1))


def train_fn(data_loader, model, optimizer, device, accumulation_steps, scheduler):
    model.train()

    for bi, d in tqdm(enumerate(data_loader), total=len(data_loader)):
        ids = d["ids"].to(device)
        token_type_ids = d["token_type_ids"].to(device)
        mask = d["mask"].to(device)
        targets = d["targets"].to(device)

        optimizer.zero_grad()
        outputs = model(ids=ids, token_type_ids=token_type_ids, mask=mask,)
        loss = loss_fn(outputs, targets)
        loss.backward()
        if (bi + 1) % accumulation_steps == 0:
            optimizer.step()
            scheduler.step()


def eval_fn(data_loader, model, device):
    model.eval()
    fin_targets = []
    fin_outputs = []
    with torch.no_grad():
        for bi, d in tqdm(enumerate(data_loader), total=len(data_loader)):
            ids = d["ids"].to(device)
            token_type_ids = d["token_type_ids"].to(device)
            mask = d["mask"].to(device)
            targets = d["targets"].to(device)

            outputs = model(ids=ids, token_type_ids=token_type_ids, mask=mask,)
            fin_targets.extend(targets.cpu().detach().numpy().tolist())
            fin_outputs.extend(torch.sigmoid(outputs).cpu().detach().numpy().tolist())
    return fin_targets, fin_outputs
