"""
Anode Cover Inspector — Quick Evaluation (Colab)
==================================================
Paste this entire cell into Google Colab and run it.
It will load your saved model and print the honest metrics.
"""

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# ===== LOAD YOUR SAVED MODEL =====
model_path = '/content/drive/MyDrive/CV_ACQI/anode_mobilenet_v2.keras'
print(f"Loading model from {model_path}...")
model = load_model(model_path)
print("Model loaded!\n")

# ===== LOAD TEST SET (same split as training) =====
data_dir = '/content/drive/MyDrive/CV_ACQI'

# Recreate the EXACT same test split using seed=42
full_train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.15,
    subset="training",
    seed=42,
    image_size=(224, 224),
    batch_size=16,
    label_mode='binary'
)

test_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.15,
    subset="validation",
    seed=42,
    image_size=(224, 224),
    batch_size=16,
    label_mode='binary'
)

# Count images per class
import os
for class_name in sorted(os.listdir(data_dir)):
    class_path = os.path.join(data_dir, class_name)
    if os.path.isdir(class_path):
        count = len([f for f in os.listdir(class_path)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
        print(f"  {class_name}: {count} images")

# ===== RUN PREDICTIONS ON TEST SET =====
print(f"\nEvaluating on test set ({len(test_ds)} batches)...")

test_loss, test_acc = model.evaluate(test_ds)

all_preds = []
all_labels = []

for images, labels in test_ds:
    preds = model.predict(images, verbose=0)
    all_preds.extend((preds.flatten() > 0.5).astype(int))
    all_labels.extend(labels.numpy().flatten().astype(int))

all_preds = np.array(all_preds)
all_labels = np.array(all_labels)

# ===== RESULTS =====
tp = np.sum((all_labels == 1) & (all_preds == 1))  # OK correct
tn = np.sum((all_labels == 0) & (all_preds == 0))  # NG correct
fp = np.sum((all_labels == 0) & (all_preds == 1))  # NG missed (DANGEROUS)
fn = np.sum((all_labels == 1) & (all_preds == 0))  # OK false alarm

total = len(all_labels)
ng_total = np.sum(all_labels == 0)
ok_total = np.sum(all_labels == 1)

# Per-class metrics
ng_precision = tn / (tn + fn) if (tn + fn) > 0 else 0
ng_recall    = tn / (tn + fp) if (tn + fp) > 0 else 0
ng_f1        = 2 * ng_precision * ng_recall / (ng_precision + ng_recall) if (ng_precision + ng_recall) > 0 else 0

ok_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
ok_recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
ok_f1        = 2 * ok_precision * ok_recall / (ok_precision + ok_recall) if (ok_precision + ok_recall) > 0 else 0

w_f1 = (ng_f1 * ng_total + ok_f1 * ok_total) / total

print(f"\n{'='*60}")
print(f"CONFUSION MATRIX")
print(f"{'='*60}")
print(f"                    Predicted NG    Predicted OK")
print(f"  Actual NG:        {tn:>8}        {fp:>8}")
print(f"  Actual OK:        {fn:>8}        {tp:>8}")

print(f"\n{'='*60}")
print(f"CLASSIFICATION REPORT")
print(f"{'='*60}")
print(f"              Precision    Recall    F1-Score    Support")
print(f"  NG           {ng_precision:>7.1%}   {ng_recall:>7.1%}     {ng_f1:>7.1%}       {int(ng_total)}")
print(f"  OK           {ok_precision:>7.1%}   {ok_recall:>7.1%}     {ok_f1:>7.1%}       {int(ok_total)}")
print(f"")
print(f"  Accuracy                                {test_acc:>7.1%}       {total}")
print(f"  Weighted F1  {w_f1:>7.1%}   ← USE THIS instead of accuracy")

print(f"\n{'='*60}")
print(f"KEY NUMBERS FOR YOUR MEETING")
print(f"{'='*60}")
print(f"  NG Recall: {ng_recall:.1%} — catches {tn} out of {int(ng_total)} defective covers")
if fp > 0:
    print(f"  ⚠️  {fp} defective cover(s) MISSED by AI")
else:
    print(f"  ✅ No defective covers missed!")
print(f"  OK Recall: {ok_recall:.1%} — {fn} false alarm(s) out of {int(ok_total)} good covers")
print(f"  Weighted F1: {w_f1:.1%}")
