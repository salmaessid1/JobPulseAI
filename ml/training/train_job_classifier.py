import pandas as pd
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer
)
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
import joblib
from torch.utils.data import Dataset

MODEL_NAME = "distilbert-base-uncased"
MAX_LEN = 128

# ============ DATASET ============
class JobDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            str(self.texts[idx]),
            truncation=True,
            padding="max_length",
            max_length=MAX_LEN,
            return_tensors="pt"
        )
        return {
            "input_ids": enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long)
        }

# ============ CHARGEMENT ============
train_df = pd.read_csv("data/processed/train_classification.csv")
test_df = pd.read_csv("data/processed/test_classification.csv")

le = LabelEncoder()
train_labels = le.fit_transform(train_df["sector"])
test_labels = le.transform(test_df["sector"])

print(f"Classes: {list(le.classes_)}")
print(f"Train: {len(train_df)} | Test: {len(test_df)}")

# ============ TOKENIZER + MODEL ============
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(le.classes_)
)

train_dataset = JobDataset(train_df["description"].values, train_labels, tokenizer)
test_dataset = JobDataset(test_df["description"].values, test_labels, tokenizer)

# ============ MÉTRIQUES ============
def compute_metrics(eval_pred):
    preds = np.argmax(eval_pred.predictions, axis=1)
    return {
        "accuracy": accuracy_score(eval_pred.label_ids, preds),
        "f1": f1_score(eval_pred.label_ids, preds, average="weighted")
    }

# ============ TRAINING ============
args = TrainingArguments(
    output_dir="ml/models/job_classifier",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir="ml/models/job_classifier/logs",
    logging_steps=50,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

# ============ SAUVEGARDE ============
model.save_pretrained("ml/models/job_classifier")
tokenizer.save_pretrained("ml/models/job_classifier")
joblib.dump(le, "ml/models/job_classifier/label_encoder.pkl")

print("✅ Modèle sauvegardé dans ml/models/job_classifier/")