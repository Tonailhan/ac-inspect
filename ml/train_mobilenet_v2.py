"""DEPRECATED — DO NOT USE FOR TRAINING.

This script partitions the data with take()/skip() on a shuffled tf.data
dataset. Because such datasets re-shuffle on every epoch, validation images
leak into training, which invalidates early stopping, checkpoint selection
and every reported metric. The defect and its correction are documented in
the project report (Methodology, "Data Partitioning").

Use ml/train_mobilenet_v2_100epochs.py instead — it partitions the file list
once, stratified by class, before any pipeline is built.

Kept only as a historical record of the original procedure.
"""
import os
import sys

if os.environ.get('I_UNDERSTAND_THIS_SCRIPT_IS_BROKEN') != '1':
    sys.exit(
        "\nREFUSING TO RUN: this script has a train/validation leakage defect "
        "and produces invalid metrics.\nUse ml/train_mobilenet_v2_100epochs.py "
        "instead.\n(Set I_UNDERSTAND_THIS_SCRIPT_IS_BROKEN=1 to run it anyway.)"
    )

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

# Verify the folder structure
print("\nChecking dataset structure...")
for class_name in sorted(os.listdir(data_dir)):
    class_path = os.path.join(data_dir, class_name)
    if os.path.isdir(class_path):
        count = len([f for f in os.listdir(class_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
        print(f"  {class_name}: {count} images")


# ==============================================================================
# STEP 2: LOAD & SPLIT DATASET (70% Train / 15% Val / 15% Test)
# ==============================================================================
# First split: 80% train+val, 20% test
print("\nLoading dataset...")

# We use image_dataset_from_directory which sorts class names alphabetically
# This means: NG = class 0, OK = class 1
# With sigmoid output: > 0.5 = OK, < 0.5 = NG

full_train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.15,
    subset="training",
    seed=42,
    image_size=(224, 224),
    batch_size=16,
    label_mode='binary'  # Explicitly binary for sigmoid output
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

# Split the training set further into train (82%) and val (18%)
# This gives roughly 70/15/15 overall split
train_size = int(0.82 * len(full_train_ds))
train_ds = full_train_ds.take(train_size)
val_ds = full_train_ds.skip(train_size)

print(f"\nDataset split:")
print(f"  Train batches: {len(train_ds)}")
print(f"  Val batches:   {len(val_ds)}")
print(f"  Test batches:  {len(test_ds)}")
print(f"\nClass mapping (alphabetical): NG=0, OK=1")
print(f"Sigmoid output > 0.5 = OK, < 0.5 = NG")


# ==============================================================================
# STEP 3: CALCULATE CLASS WEIGHTS (handles 2:1 OK:NG imbalance)
# ==============================================================================
print("\nCalculating class weights for imbalanced data...")

# Count actual labels in training set
all_labels = []
for _, labels in full_train_ds:
    all_labels.extend(labels.numpy().flatten())
all_labels = np.array(all_labels)

n_ng = np.sum(all_labels == 0)
n_ok = np.sum(all_labels == 1)
total = len(all_labels)

# Calculate balanced weights
weight_ng = total / (2.0 * n_ng) if n_ng > 0 else 1.0
weight_ok = total / (2.0 * n_ok) if n_ok > 0 else 1.0

class_weight = {0: weight_ng, 1: weight_ok}

print(f"  NG (class 0): {int(n_ng)} images, weight = {weight_ng:.3f}")
print(f"  OK (class 1): {int(n_ok)} images, weight = {weight_ok:.3f}")


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
    layers.RandomRotation(0.08),                # ±15 degrees for angle variation
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
# STEP 6: PHASE 1 — TRAIN HEAD ONLY (base frozen)
# ==============================================================================
PHASE1_EPOCHS = 10

print(f"\n{'='*60}")
print(f"PHASE 1: Training classification head ({PHASE1_EPOCHS} epochs)")
print(f"Base model: FROZEN")
print(f"{'='*60}")

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Callbacks
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True,
    verbose=1
)

history_phase1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=PHASE1_EPOCHS,
    class_weight=class_weight,
    callbacks=[early_stop]
)


# ==============================================================================
# STEP 7: PHASE 2 — FINE-TUNE LAST 30 LAYERS OF BASE
# ==============================================================================
PHASE2_EPOCHS = 15

print(f"\n{'='*60}")
print(f"PHASE 2: Fine-tuning last 30 layers ({PHASE2_EPOCHS} epochs)")
print(f"Base model: PARTIALLY UNFROZEN")
print(f"{'='*60}")

# Unfreeze the last 30 layers of MobileNetV2
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

# Recompile with lower learning rate (critical for fine-tuning)
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Save best model during fine-tuning (use .keras format, not .h5)
model_save_path = '/content/drive/MyDrive/CV_ACQI/anode_mobilenet_v2.keras'
checkpoint = tf.keras.callbacks.ModelCheckpoint(
    model_save_path,
    monitor='val_loss',
    save_best_only=True,
    verbose=1
)

# Fresh early stopping for Phase 2 (don't carry over state from Phase 1)
early_stop_phase2 = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True,
    verbose=1
)

history_phase2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=PHASE2_EPOCHS,
    class_weight=class_weight,
    callbacks=[early_stop_phase2, checkpoint]
)


# ==============================================================================
# STEP 8: EVALUATE ON TEST SET
# ==============================================================================
print(f"\n{'='*60}")
print("EVALUATION ON TEST SET")
print(f"{'='*60}")

# Load best model from checkpoint
best_model = tf.keras.models.load_model(model_save_path)

# Evaluate
test_loss, test_accuracy = best_model.evaluate(test_ds)
print(f"\nTest Loss:     {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.1f}%)")

# Detailed predictions for confusion matrix
all_preds = []
all_labels = []

for images, labels in test_ds:
    preds = best_model.predict(images, verbose=0)
    all_preds.extend((preds.flatten() > 0.5).astype(int))
    all_labels.extend(labels.numpy().flatten().astype(int))

all_preds = np.array(all_preds)
all_labels = np.array(all_labels)

# Confusion matrix
from sklearn.metrics import confusion_matrix, classification_report

cm = confusion_matrix(all_labels, all_preds)
print(f"\nConfusion Matrix:")
print(f"              Predicted NG  Predicted OK")
print(f"  Actual NG:  {cm[0][0]:>11}  {cm[0][1]:>12}")
print(f"  Actual OK:  {cm[1][0]:>11}  {cm[1][1]:>12}")

print(f"\nClassification Report:")
print(classification_report(all_labels, all_preds, target_names=['NG', 'OK']))


# ==============================================================================
# STEP 9: PLOT TRAINING HISTORY
# ==============================================================================
# Combine both phases
acc = history_phase1.history['accuracy'] + history_phase2.history['accuracy']
val_acc = history_phase1.history['val_accuracy'] + history_phase2.history['val_accuracy']
loss = history_phase1.history['loss'] + history_phase2.history['loss']
val_loss = history_phase1.history['val_loss'] + history_phase2.history['val_loss']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Accuracy plot
ax1.plot(acc, label='Train Accuracy', linewidth=2)
ax1.plot(val_acc, label='Val Accuracy', linewidth=2)
ax1.axvline(x=len(history_phase1.history['accuracy'])-1, color='gray', 
            linestyle='--', label='Fine-tuning start')
ax1.set_title('Model Accuracy', fontsize=14)
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Loss plot
ax2.plot(loss, label='Train Loss', linewidth=2)
ax2.plot(val_loss, label='Val Loss', linewidth=2)
ax2.axvline(x=len(history_phase1.history['loss'])-1, color='gray',
            linestyle='--', label='Fine-tuning start')
ax2.set_title('Model Loss', fontsize=14)
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Loss')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/content/drive/MyDrive/CV_ACQI/training_results.png', dpi=150)
plt.show()

print(f"\n{'='*60}")
print("[SUCCESS] Training complete!")
print(f"{'='*60}")
print(f"Model saved to: {model_save_path}")
print(f"Training plot saved to: /content/drive/MyDrive/CV_ACQI/training_results.png")
print(f"\nNext steps:")
print(f"1. Download 'anode_mobilenet_v2.keras' from Google Drive")
print(f"2. Place it in your project: weights/anode_mobilenet_v2.keras")
print(f"3. Restart the backend server")
