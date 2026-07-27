"""
Anode Cover Inspector — MobileNetV2 Training (100 Epoch Edition)
================================================================
Google Colab script for training with extended epochs.

Changes from original:
  - Phase 1: 30 epochs (was 10) — head-only training
  - Phase 2: 100 epochs (was 15) — fine-tuning
  - Added ReduceLROnPlateau to auto-lower learning rate on plateaus
  - Added TensorBoard logging
  - EarlyStopping patience increased to 10 for Phase 2

Fixes in this revision:
  - LEAKAGE FIX: train/val/test are now split at the FILE level (stratified
    70/15/15) instead of take()/skip() on a shuffled dataset. The old split
    re-randomized every epoch, so val overlapped with train — val_loss,
    EarlyStopping, checkpointing, and the threshold search were all
    contaminated. Expect metrics to drop vs. previous runs; the new numbers
    are the honest ones.
  - Threshold is now chosen with a safety constraint (NG recall floor),
    not plain macro-F1 — missing a defect costs more than a false alarm.
  - Outputs (model, plots) are saved to CV_ACQI_outputs/, NOT the dataset
    folder. A stray subfolder in the dataset dir would be treated as a
    third class and crash binary labeling; the script now asserts only
    NG/ and OK/ exist.

The model will NOT actually train for all 100 epochs. EarlyStopping will
automatically stop training when validation loss stops improving. Setting
100 epochs just gives the model maximum room to converge.
"""

import tensorflow as tf
from tensorflow.keras import layers, models
from google.colab import drive
import os
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# STEP 1: MOUNT GOOGLE DRIVE & LOAD DATA
# ==============================================================================
print("Connecting to Google Drive...")
drive.mount('/content/drive')

data_dir = '/content/drive/MyDrive/CV_ACQI'
output_dir = '/content/drive/MyDrive/CV_ACQI_outputs'
os.makedirs(output_dir, exist_ok=True)

IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.bmp')

# Verify the folder structure. The dataset dir must contain ONLY the two
# class folders — any other subfolder (e.g. "Results") would be treated as
# a third class and crash binary labeling.
print("\nChecking dataset structure...")
class_dirs = sorted(d for d in os.listdir(data_dir)
                    if os.path.isdir(os.path.join(data_dir, d)))
assert class_dirs == ['NG', 'OK'], (
    f"Expected exactly ['NG', 'OK'] in {data_dir}, found {class_dirs}. "
    f"Move any other folders out of the dataset directory."
)
for class_name in class_dirs:
    class_path = os.path.join(data_dir, class_name)
    count = len([f for f in os.listdir(class_path)
                 if f.lower().endswith(IMAGE_EXTS)])
    print(f"  {class_name}: {count} images")


# ==============================================================================
# STEP 2: LOAD & SPLIT DATASET (70% Train / 15% Val / 15% Test)
# ==============================================================================
print("\nLoading dataset (using ALL images)...")

# Class mapping (alphabetical, same as image_dataset_from_directory):
#   NG = class 0, OK = class 1
# With sigmoid output: > threshold = OK, otherwise NG
#
# LEAKAGE-SAFE SPLIT: the previous version did take()/skip() on a dataset
# built with shuffle=True — tf.data reshuffles on EVERY epoch, so the
# train/val boundary moved each epoch and val images leaked into training.
# We now split the FILE LIST once, stratified per class so train/val/test
# all keep the same OK:NG ratio, and build each tf.data pipeline from its
# own fixed set of files.

BATCH_SIZE = 16
IMG_SIZE = (224, 224)
CLASS_NAMES = ['NG', 'OK']  # alphabetical: NG=0, OK=1

rng = np.random.RandomState(42)
file_paths, file_labels = [], []
for label, cname in enumerate(CLASS_NAMES):
    class_path = os.path.join(data_dir, cname)
    fs = sorted(f for f in os.listdir(class_path)
                if f.lower().endswith(IMAGE_EXTS))
    file_paths.extend(os.path.join(class_path, f) for f in fs)
    file_labels.extend([label] * len(fs))

file_paths = np.array(file_paths)
file_labels = np.array(file_labels, dtype='float32')

# Stratified 70/15/15: shuffle and split each class independently
train_idx, val_idx, test_idx = [], [], []
for label in (0, 1):
    idx = np.where(file_labels == label)[0]
    rng.shuffle(idx)
    n = len(idx)
    n_train = int(0.70 * n)
    n_val = int(0.15 * n)
    train_idx.extend(idx[:n_train])
    val_idx.extend(idx[n_train:n_train + n_val])
    test_idx.extend(idx[n_train + n_val:])

def load_image(path, label):
    img = tf.io.read_file(path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img.set_shape([None, None, 3])
    img = tf.image.resize(img, IMG_SIZE)
    return img, tf.reshape(label, (1,))

def make_ds(indices, shuffle=False):
    paths = file_paths[indices]
    labels = file_labels[indices]
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if shuffle:
        # Reshuffling here is safe: this pipeline only ever contains its
        # own split's files
        ds = ds.shuffle(len(indices), seed=42, reshuffle_each_iteration=True)
    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    return ds.batch(BATCH_SIZE)

train_ds = make_ds(train_idx, shuffle=True)
val_ds = make_ds(val_idx)
test_ds = make_ds(test_idx)

print(f"\nDataset split (stratified 70/15/15):")
print(f"  Train: {len(train_idx)} images ({len(train_ds)} batches)")
print(f"  Val:   {len(val_idx)} images ({len(val_ds)} batches)")
print(f"  Test:  {len(test_idx)} images ({len(test_ds)} batches)")
print(f"\nClass mapping (alphabetical): NG=0, OK=1")
print(f"Sigmoid output > threshold = OK, otherwise NG")


# ==============================================================================
# STEP 3: CALCULATE CLASS WEIGHTS (handles OK:NG imbalance)
# ==============================================================================
print("\nCalculating class weights for imbalanced data...")

# Extra emphasis on catching defects. 1.0 = plain balanced weighting.
# Raise it (e.g. 1.5–2.0) to make each MISSED NG cost more during training,
# pushing the model to output lower P(OK) on defects — a training-side lever
# that improves NG detection WITHOUT changing the inference threshold.
NG_WEIGHT_MULTIPLIER = 1.5

# Count labels in the TRAINING split only (val/test must not influence training)
train_labels = file_labels[train_idx]
n_ng = np.sum(train_labels == 0)
n_ok = np.sum(train_labels == 1)
total = len(train_labels)

# Calculate balanced weights — gives higher weight to the minority class
weight_ng = total / (2.0 * n_ng) if n_ng > 0 else 1.0
weight_ok = total / (2.0 * n_ok) if n_ok > 0 else 1.0

# Apply the defect-emphasis multiplier on top of the balanced NG weight
weight_ng_balanced = weight_ng
weight_ng = weight_ng * NG_WEIGHT_MULTIPLIER

class_weight = {0: weight_ng, 1: weight_ok}

print(f"  NG (class 0): {int(n_ng)} images, balanced weight = {weight_ng_balanced:.3f}")
print(f"  OK (class 1): {int(n_ok)} images, weight = {weight_ok:.3f}")
if NG_WEIGHT_MULTIPLIER != 1.0:
    print(f"  NG weight boosted x{NG_WEIGHT_MULTIPLIER} -> {weight_ng:.3f} (defect emphasis)")


# ==============================================================================
# STEP 4: DATA AUGMENTATION (critical for small datasets)
# ==============================================================================
# Augmentation applied to DATASET (not inside model) to avoid save/pickle errors.
# Tailored for potline photo conditions:
#   - Brightness varies (phone flash vs ambient)
#   - Camera angles are inconsistent
#   - Left/right doesn't matter, but up/down does (gravity)
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),            # Left/right doesn't matter
    layers.RandomRotation(0.08),                # ±29 degrees (0.08 of 360°) for handheld angle variation
    layers.RandomBrightness(0.3),               # ±30% for flash variability
    layers.RandomContrast(0.2),                 # ±20% for dust/lighting
    layers.RandomZoom((-0.1, 0.1)),             # Slight zoom variation
], name="data_augmentation")

# Apply augmentation to training data ONLY (not val/test)
def augment(image, label):
    return data_augmentation(image, training=True), label

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.map(augment, num_parallel_calls=AUTOTUNE).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)
test_ds = test_ds.prefetch(buffer_size=AUTOTUNE)


# ==============================================================================
# STEP 5: BUILD MOBILENETV2 MODEL
# ==============================================================================
print("\nBuilding MobileNetV2 model...")

# Load base model with ImageNet weights
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)

# Freeze all base layers for Phase 1
base_model.trainable = False

# Build the full model (augmentation is applied via dataset, NOT inside model)
model = models.Sequential([
    # Rescaling: converts [0, 255] → [-1, 1] as MobileNetV2 expects
    layers.Rescaling(1./127.5, offset=-1, name="rescaling"),
    
    # MobileNetV2 backbone (frozen)
    base_model,
    
    # Classification head
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(1, activation='sigmoid')
])

# Build the model to see summary
model.build(input_shape=(None, 224, 224, 3))
model.summary()


# ==============================================================================
# STEP 6: PHASE 1 — TRAIN HEAD ONLY (base frozen) — 30 EPOCHS
# ==============================================================================
PHASE1_EPOCHS = 30  # Increased from 10 to give the head more time to converge

print(f"\n{'='*60}")
print(f"PHASE 1: Training classification head ({PHASE1_EPOCHS} epochs max)")
print(f"Base model: FROZEN")
print(f"EarlyStopping: patience=10")
print(f"{'='*60}")

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Callbacks for Phase 1 (same small-val-set noise applies here)
early_stop_p1 = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=10,       # Raised from 7 — don't quit on a noisy val_loss blip
    restore_best_weights=True,
    verbose=1
)

reduce_lr_p1 = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,       # Halve the learning rate
    patience=4,        # Raised from 3 — keep below EarlyStopping's patience
    min_lr=1e-6,
    verbose=1
)

history_phase1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=PHASE1_EPOCHS,
    class_weight=class_weight,
    callbacks=[early_stop_p1, reduce_lr_p1]
)

phase1_actual_epochs = len(history_phase1.history['loss'])
print(f"\n✅ Phase 1 completed in {phase1_actual_epochs}/{PHASE1_EPOCHS} epochs")


# ==============================================================================
# STEP 7: PHASE 2 — FINE-TUNE LAST 30 LAYERS — 100 EPOCHS
# ==============================================================================
PHASE2_EPOCHS = 100  # Increased from 15 — EarlyStopping will handle the rest

print(f"\n{'='*60}")
print(f"PHASE 2: Fine-tuning last 30 layers ({PHASE2_EPOCHS} epochs max)")
print(f"Base model: PARTIALLY UNFROZEN")
print(f"EarlyStopping: patience=20")
print(f"ReduceLROnPlateau: patience=6, factor=0.5")
print(f"{'='*60}")

# Unfreeze the last 30 layers of MobileNetV2
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

trainable_count = sum(1 for layer in base_model.layers if layer.trainable)
print(f"Trainable MobileNetV2 layers: {trainable_count} of {len(base_model.layers)}")

# Recompile with lower learning rate (critical for fine-tuning)
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Save best model during fine-tuning (use .keras format, not .h5).
# Saved OUTSIDE the dataset folder so reruns don't see stray files/folders.
model_save_path = os.path.join(output_dir, 'anode_mobilenet_v2.keras')
checkpoint = tf.keras.callbacks.ModelCheckpoint(
    model_save_path,
    monitor='val_loss',
    save_best_only=True,
    verbose=1
)

# EarlyStopping for fine-tuning.
# The honest validation split is small (~56 images), so val_loss is NOISY —
# a couple of unlucky images can cause several "no improvement" epochs in a
# row and stop training long before the model has converged. High patience
# lets it ride out that noise; checkpointing means over-running costs only
# Colab time, never model quality.
early_stop_p2 = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=20,       # Raised from 10 — small val set makes val_loss jumpy
    restore_best_weights=True,
    verbose=1
)

# Auto-reduce learning rate when loss plateaus.
# Patience must stay well below EarlyStopping's, so the LR gets a chance to
# drop and escape a plateau before training is cut off.
reduce_lr_p2 = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,        # Halve the learning rate
    patience=6,        # Raised from 4 — avoid collapsing the LR on noise
    min_lr=1e-7,       # Don't go below this
    verbose=1
)

# TensorBoard logging (optional, viewable in Colab)
tensorboard_cb = tf.keras.callbacks.TensorBoard(
    log_dir='/content/logs/phase2',
    histogram_freq=1
)

history_phase2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=PHASE2_EPOCHS,
    class_weight=class_weight,
    callbacks=[early_stop_p2, checkpoint, reduce_lr_p2, tensorboard_cb]
)

phase2_actual_epochs = len(history_phase2.history['loss'])
print(f"\n✅ Phase 2 completed in {phase2_actual_epochs}/{PHASE2_EPOCHS} epochs")
print(f"📊 Total epochs trained: {phase1_actual_epochs + phase2_actual_epochs}")


# ==============================================================================
# STEP 8: FIND OPTIMAL THRESHOLD ON VALIDATION SET (safety-constrained)
# ==============================================================================
from sklearn.metrics import confusion_matrix, classification_report, precision_score, recall_score, f1_score

# Missing a defect (NG passed as OK) is dangerous; flagging a good cover is
# merely wasteful. So instead of maximizing plain macro-F1, we require a
# minimum NG catch rate and only optimize F1 among thresholds that meet it.
MIN_NG_RECALL = 0.95

print(f"\n{'='*60}")
print("FINDING OPTIMAL CLASSIFICATION THRESHOLD")
print(f"Constraint: NG recall >= {MIN_NG_RECALL*100:.0f}%")
print(f"{'='*60}")

# Load best model from checkpoint
best_model = tf.keras.models.load_model(model_save_path)

# Get raw sigmoid probabilities on VALIDATION set
val_probs = []
val_true = []
for images, labels in val_ds:
    preds = best_model.predict(images, verbose=0)
    val_probs.extend(preds.flatten())
    val_true.extend(labels.numpy().flatten().astype(int))
val_probs = np.array(val_probs)
val_true = np.array(val_true)

# Try thresholds and pick the best F1 AMONG those meeting the NG-recall floor
print("\nThreshold search (on validation set):")
print(f"  {'Threshold':>10}  {'NG Recall':>10}  {'OK Recall':>10}  {'F1 (avg)':>10}  {'Safe?':>6}")
print(f"  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*6}")

best_threshold = None
best_f1 = 0.0
threshold_results = []

for t in np.arange(0.05, 0.96, 0.025):
    t_preds = (val_probs > t).astype(int)

    ng_rec = recall_score(val_true, t_preds, pos_label=0, zero_division=0)
    ok_rec = recall_score(val_true, t_preds, pos_label=1, zero_division=0)
    f1_avg = f1_score(val_true, t_preds, average='macro', zero_division=0)
    meets_floor = ng_rec >= MIN_NG_RECALL

    threshold_results.append((t, ng_rec, ok_rec, f1_avg, meets_floor))
    print(f"  {t:>10.3f}  {ng_rec*100:>9.1f}%  {ok_rec*100:>9.1f}%  {f1_avg:>10.3f}  {'✓' if meets_floor else '✗':>6}")

    if meets_floor and f1_avg > best_f1:
        best_f1 = f1_avg
        best_threshold = t

if best_threshold is None:
    # No threshold reaches the NG-recall floor — fall back to the highest NG
    # recall, breaking ties by F1. Flag this loudly: the model itself may be
    # too weak for safe deployment.
    t, ng_rec, ok_rec, f1_avg, _ = max(threshold_results, key=lambda r: (r[1], r[3]))
    best_threshold, best_f1 = t, f1_avg
    print(f"\n⚠️  WARNING: no threshold reaches NG recall >= {MIN_NG_RECALL*100:.0f}%.")
    print(f"   Falling back to threshold {best_threshold:.3f} (NG recall {ng_rec*100:.1f}%).")
    print(f"   Consider more NG training data before deploying this model.")
else:
    print(f"\n✅ Optimal threshold: {best_threshold:.3f} (F1={best_f1:.3f}, NG recall floor met)")
print(f"   Default was 0.50 — {'no change needed' if abs(best_threshold - 0.5) < 0.05 else f'shifted to {best_threshold:.3f}'}")


# ==============================================================================
# STEP 9: EVALUATE ON TEST SET (with optimal threshold)
# ==============================================================================
print(f"\n{'='*60}")
print(f"EVALUATION ON TEST SET (threshold = {best_threshold:.2f})")
print(f"{'='*60}")

# Evaluate with default 0.5 for Keras accuracy metric
test_loss, test_accuracy_default = best_model.evaluate(test_ds)

# Get raw probabilities on test set
test_probs = []
all_labels = []

for images, labels in test_ds:
    preds = best_model.predict(images, verbose=0)
    test_probs.extend(preds.flatten())
    all_labels.extend(labels.numpy().flatten().astype(int))

test_probs = np.array(test_probs)
all_labels = np.array(all_labels)

# Apply OPTIMAL threshold (not hardcoded 0.5)
all_preds = (test_probs > best_threshold).astype(int)
test_accuracy = np.mean(all_preds == all_labels)

print(f"\nTest Loss:     {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.1f}%)  [threshold={best_threshold:.2f}]")
if abs(best_threshold - 0.5) >= 0.05:
    print(f"  (vs {test_accuracy_default*100:.1f}% with default 0.5 threshold)")

# Confusion matrix
cm = confusion_matrix(all_labels, all_preds)
print(f"\nConfusion Matrix (threshold = {best_threshold:.2f}):")
print(f"              Predicted NG  Predicted OK")
print(f"  Actual NG:  {cm[0][0]:>11}  {cm[0][1]:>12}")
print(f"  Actual OK:  {cm[1][0]:>11}  {cm[1][1]:>12}")

print(f"\nClassification Report:")
print(classification_report(all_labels, all_preds, target_names=['NG', 'OK']))

# Show raw probability distribution
print(f"\nRaw sigmoid output distribution:")
ng_probs = test_probs[all_labels == 0]
ok_probs = test_probs[all_labels == 1]
print(f"  NG images: min={ng_probs.min():.3f}, mean={ng_probs.mean():.3f}, max={ng_probs.max():.3f}")
print(f"  OK images: min={ok_probs.min():.3f}, mean={ok_probs.mean():.3f}, max={ok_probs.max():.3f}")
print(f"  Threshold: {best_threshold:.2f}")


# ==============================================================================
# STEP 10: VISUAL CONFUSION MATRIX (boss-friendly heatmap)
# ==============================================================================
fig_cm, ax_cm = plt.subplots(figsize=(6, 5))
im = ax_cm.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
ax_cm.figure.colorbar(im, ax=ax_cm)

classes = ['NG (Defective)', 'OK (Good)']
ax_cm.set(xticks=[0, 1], yticks=[0, 1],
          xticklabels=classes, yticklabels=classes,
          ylabel='Actual', xlabel='Predicted',
          title=f'Confusion Matrix — Threshold={best_threshold:.2f}')

# Add text annotations to each cell
thresh = cm.max() / 2.
for i in range(2):
    for j in range(2):
        ax_cm.text(j, i, format(cm[i, j], 'd'),
                   ha="center", va="center", fontsize=20, fontweight='bold',
                   color="white" if cm[i, j] > thresh else "black")

plt.tight_layout()
cm_path = os.path.join(output_dir, 'confusion_matrix.png')
plt.savefig(cm_path, dpi=150, bbox_inches='tight')
plt.show()
print(f"📊 Confusion matrix saved to: {cm_path}")


# ==============================================================================
# STEP 11: PLOT TRAINING HISTORY (BOTH PHASES)
# ==============================================================================
# Combine both phases
acc = history_phase1.history['accuracy'] + history_phase2.history['accuracy']
val_acc = history_phase1.history['val_accuracy'] + history_phase2.history['val_accuracy']
loss = history_phase1.history['loss'] + history_phase2.history['loss']
val_loss = history_phase1.history['val_loss'] + history_phase2.history['val_loss']

fig, axes = plt.subplots(1, 3, figsize=(20, 5))

# --- Accuracy plot ---
axes[0].plot(acc, label='Train Accuracy', linewidth=2)
axes[0].plot(val_acc, label='Val Accuracy', linewidth=2)
axes[0].axvline(x=phase1_actual_epochs - 1, color='gray', 
            linestyle='--', label='Fine-tuning start')
axes[0].set_title('Model Accuracy', fontsize=14)
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Accuracy')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# --- Loss plot ---
axes[1].plot(loss, label='Train Loss', linewidth=2)
axes[1].plot(val_loss, label='Val Loss', linewidth=2)
axes[1].axvline(x=phase1_actual_epochs - 1, color='gray',
            linestyle='--', label='Fine-tuning start')
axes[1].set_title('Model Loss', fontsize=14)
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Loss')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# --- Learning rate plot (if available) ---
# Older Keras logs the LR under 'lr'; newer versions use 'learning_rate'
lr_key = 'learning_rate' if 'learning_rate' in history_phase2.history else 'lr'
if lr_key in history_phase2.history:
    lr_p1 = history_phase1.history.get(lr_key, [0.001] * phase1_actual_epochs)
    lr_p2 = history_phase2.history[lr_key]
    all_lr = list(lr_p1) + list(lr_p2)
    axes[2].plot(all_lr, label='Learning Rate', linewidth=2, color='green')
    axes[2].axvline(x=phase1_actual_epochs - 1, color='gray',
                linestyle='--', label='Fine-tuning start')
    axes[2].set_title('Learning Rate Schedule', fontsize=14)
    axes[2].set_xlabel('Epoch')
    axes[2].set_ylabel('Learning Rate')
    axes[2].set_yscale('log')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
else:
    axes[2].text(0.5, 0.5, 'LR data not available', 
                 ha='center', va='center', fontsize=12)
    axes[2].set_title('Learning Rate Schedule', fontsize=14)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'training_results_100ep.png'), dpi=150)
plt.show()


# ==============================================================================
# STEP 12: EXECUTIVE SUMMARY (present this to your boss)
# ==============================================================================
# Calculate key business metrics
ng_recall = recall_score(all_labels, all_preds, pos_label=0)     # NG catch rate
ng_precision = precision_score(all_labels, all_preds, pos_label=0)
ok_recall = recall_score(all_labels, all_preds, pos_label=1)     # OK pass rate
ok_precision = precision_score(all_labels, all_preds, pos_label=1)
f1_ng = f1_score(all_labels, all_preds, pos_label=0)
f1_ok = f1_score(all_labels, all_preds, pos_label=1)

# Counts from confusion matrix
true_ng = cm[0][0]     # Correctly caught NG
missed_ng = cm[0][1]   # NG that slipped through as OK (DANGEROUS)
false_ng = cm[1][0]    # OK wrongly flagged as NG (wasteful but safe)
true_ok = cm[1][1]     # Correctly passed OK

total_test = len(all_labels)

print(f"\n{'='*60}")
print("📋 EXECUTIVE SUMMARY — ANODE COVER INSPECTION MODEL")
print(f"{'='*60}")
print(f"""
┌─────────────────────────────────────────────────────────┐
│  OVERALL ACCURACY:  {test_accuracy*100:.1f}%                              │
│  Test samples:      {total_test} images                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔍 DEFECT DETECTION (NG)                               │
│  ─────────────────────────                              │
│  Catch Rate (Recall):     {ng_recall*100:.1f}%                        │
│  → {true_ng} out of {true_ng + missed_ng} defective anodes were caught          │
│  → {missed_ng} defective anode(s) slipped through as OK            │
│                                                         │
│  Precision:               {ng_precision*100:.1f}%                        │
│  → When flagged as NG, {ng_precision*100:.0f}% were actually defective    │
│                                                         │
│  ✅ GOOD PRODUCT (OK)                                    │
│  ─────────────────────────                              │
│  Pass Rate (Recall):      {ok_recall*100:.1f}%                        │
│  → {true_ok} out of {true_ok + false_ng} good anodes were correctly passed      │
│  → {false_ng} good anode(s) were wrongly flagged as NG             │
│                                                         │
│  Precision:               {ok_precision*100:.1f}%                        │
│  → When passed as OK, {ok_precision*100:.0f}% were actually good          │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  F1-Score (NG): {f1_ng:.3f}    F1-Score (OK): {f1_ok:.3f}            │
└─────────────────────────────────────────────────────────┘

⚠️  KEY RISK METRIC: {missed_ng} of {true_ng + missed_ng} defective products passed as OK
    Miss Rate: {(1-ng_recall)*100:.1f}%
""")

print(f"{'='*60}")
print("✅ TRAINING COMPLETE!")
print(f"{'='*60}")
print(f"Phase 1: {phase1_actual_epochs} epochs (head only)")
print(f"Phase 2: {phase2_actual_epochs} epochs (fine-tuning)")
print(f"Total:   {phase1_actual_epochs + phase2_actual_epochs} epochs")
print(f"\n📁 Files saved to Google Drive (MyDrive/CV_ACQI_outputs/):")
print(f"   • anode_mobilenet_v2.keras    — trained model")
print(f"   • confusion_matrix.png        — visual confusion matrix")
print(f"   • training_results_100ep.png  — training curves")
print(f"\n🎯 Optimal threshold: {best_threshold:.3f}")
print(f"   Use this threshold in your backend instead of the default 0.50")
print(f"\nNext steps:")
print(f"1. Download 'anode_mobilenet_v2.keras' from Google Drive")
print(f"2. Place it in your project: weights/anode_mobilenet_v2.keras")
print(f"3. Update CLASSIFICATION_THRESHOLD in backend/app.py to {best_threshold:.3f}")
print(f"4. Restart the backend server")

