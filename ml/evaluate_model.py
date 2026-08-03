"""
Anode Cover Inspector — Local Model Evaluation
================================================
Run this script to get honest metrics (F1, Precision, Recall)
instead of just accuracy, which is misleading for imbalanced data.

Usage:
    python evaluate_model.py <dataset_folder>

    dataset_folder should have this structure:
        dataset_folder/
        ├── NG/
        │   ├── img1.jpg
        │   └── ...
        └── OK/
            ├── img1.jpg
            └── ...

Example:
    python evaluate_model.py "C:/path/to/CV_ACQI"
    python evaluate_model.py "../test_images"
"""

import os
import sys
import numpy as np

# Must match CLASSIFICATION_THRESHOLD in backend/app.py
CLASSIFICATION_THRESHOLD = 0.525
from pathlib import Path

# Suppress TF warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array


def load_trained_model():
    """Load the trained model from weights directory."""
    weights_dir = os.path.join(os.path.dirname(__file__), '..', 'weights')
    model_candidates = [
        os.path.join(weights_dir, 'anode_mobilenet_v2.keras'),
        os.path.join(weights_dir, 'anode_mobilenet_v2.h5'),
        os.path.join(weights_dir, 'anode_classifier_v1.h5'),
    ]
    
    for candidate in model_candidates:
        if os.path.exists(candidate):
            print(f"Loading model: {os.path.basename(candidate)}")
            return load_model(candidate)
    
    print(f"ERROR: No model file found in {os.path.abspath(weights_dir)}")
    sys.exit(1)


def predict_single(model, image_path):
    """Predict a single image. Returns (predicted_class, confidence, raw_value)."""
    img = load_img(image_path, target_size=(224, 224))
    img_array = img_to_array(img)  # Raw [0, 255] — model has built-in Rescaling
    img_array = np.expand_dims(img_array, axis=0)
    
    raw_value = float(model.predict(img_array, verbose=0)[0][0])
    
    # NG=0, OK=1 (alphabetical). Sigmoid above the threshold = OK.
    # Must match CLASSIFICATION_THRESHOLD in backend/app.py (re-derived per model).
    if raw_value > CLASSIFICATION_THRESHOLD:
        return 1, raw_value, raw_value       # OK
    else:
        return 0, 1 - raw_value, raw_value   # NG


def evaluate(dataset_dir):
    """Run full evaluation on a folder with NG/ and OK/ subfolders."""
    dataset_dir = Path(dataset_dir)
    
    # Verify folder structure
    ng_dir = dataset_dir / "NG"
    ok_dir = dataset_dir / "OK"
    
    if not ng_dir.exists() or not ok_dir.exists():
        print(f"ERROR: Expected subfolders 'NG/' and 'OK/' in {dataset_dir}")
        print(f"  NG/ exists: {ng_dir.exists()}")
        print(f"  OK/ exists: {ok_dir.exists()}")
        sys.exit(1)
    
    # Collect images
    valid_ext = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    ng_images = [f for f in ng_dir.iterdir() if f.suffix.lower() in valid_ext]
    ok_images = [f for f in ok_dir.iterdir() if f.suffix.lower() in valid_ext]
    
    print(f"\n{'='*60}")
    print(f"DATASET SUMMARY")
    print(f"{'='*60}")
    print(f"  NG images: {len(ng_images)}")
    print(f"  OK images: {len(ok_images)}")
    print(f"  Total:     {len(ng_images) + len(ok_images)}")
    print(f"  Ratio:     1:{len(ok_images)/max(len(ng_images),1):.1f} (NG:OK)")
    
    # Load model
    model = load_trained_model()
    
    # Run predictions
    print(f"\nRunning predictions...")
    
    true_labels = []
    pred_labels = []
    confidences = []
    raw_values = []
    misclassified = []
    
    all_images = [(f, 0) for f in ng_images] + [(f, 1) for f in ok_images]
    
    for i, (img_path, true_label) in enumerate(all_images):
        pred_class, conf, raw = predict_single(model, str(img_path))
        true_labels.append(true_label)
        pred_labels.append(pred_class)
        confidences.append(conf)
        raw_values.append(raw)
        
        if pred_class != true_label:
            actual = "NG" if true_label == 0 else "OK"
            predicted = "NG" if pred_class == 0 else "OK"
            misclassified.append((img_path.name, actual, predicted, conf, raw))
        
        # Progress
        total = len(all_images)
        if (i + 1) % 10 == 0 or (i + 1) == total:
            print(f"  [{i+1}/{total}] processed", end='\r')
    
    print()
    
    true_labels = np.array(true_labels)
    pred_labels = np.array(pred_labels)
    
    # === CONFUSION MATRIX ===
    tp = np.sum((true_labels == 1) & (pred_labels == 1))  # OK correct
    tn = np.sum((true_labels == 0) & (pred_labels == 0))  # NG correct
    fp = np.sum((true_labels == 0) & (pred_labels == 1))  # NG predicted as OK (DANGEROUS)
    fn = np.sum((true_labels == 1) & (pred_labels == 0))  # OK predicted as NG (false alarm)
    
    print(f"\n{'='*60}")
    print(f"CONFUSION MATRIX")
    print(f"{'='*60}")
    print(f"                    Predicted NG    Predicted OK")
    print(f"  Actual NG:        {tn:>8}        {fp:>8}    {'⚠️ MISSED DEFECTS' if fp > 0 else ''}")
    print(f"  Actual OK:        {fn:>8}        {tp:>8}")
    
    # === PER-CLASS METRICS ===
    total = len(true_labels)
    accuracy = (tp + tn) / total if total > 0 else 0
    
    # NG metrics (class 0)
    ng_precision = tn / (tn + fn) if (tn + fn) > 0 else 0
    ng_recall = tn / (tn + fp) if (tn + fp) > 0 else 0
    ng_f1 = 2 * ng_precision * ng_recall / (ng_precision + ng_recall) if (ng_precision + ng_recall) > 0 else 0
    
    # OK metrics (class 1)
    ok_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    ok_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    ok_f1 = 2 * ok_precision * ok_recall / (ok_precision + ok_recall) if (ok_precision + ok_recall) > 0 else 0
    
    # Weighted averages
    ng_support = len(ng_images)
    ok_support = len(ok_images)
    w_precision = (ng_precision * ng_support + ok_precision * ok_support) / total
    w_recall = (ng_recall * ng_support + ok_recall * ok_support) / total
    w_f1 = (ng_f1 * ng_support + ok_f1 * ok_support) / total
    
    print(f"\n{'='*60}")
    print(f"CLASSIFICATION REPORT")
    print(f"{'='*60}")
    print(f"              Precision    Recall    F1-Score    Support")
    print(f"  NG           {ng_precision:>7.2%}   {ng_recall:>7.2%}     {ng_f1:>7.2%}       {ng_support}")
    print(f"  OK           {ok_precision:>7.2%}   {ok_recall:>7.2%}     {ok_f1:>7.2%}       {ok_support}")
    print(f"")
    print(f"  Accuracy                                {accuracy:>7.2%}       {total}")
    print(f"  Weighted Avg {w_precision:>7.2%}   {w_recall:>7.2%}     {w_f1:>7.2%}       {total}")
    
    # === KEY SAFETY METRIC ===
    print(f"\n{'='*60}")
    print(f"KEY METRIC FOR MEETING")
    print(f"{'='*60}")
    print(f"  NG Recall (defect detection rate): {ng_recall:.1%}")
    print(f"  → Out of {ng_support} defective covers, the model catches {tn} and misses {fp}")
    if fp > 0:
        print(f"  ⚠️  {fp} defective cover(s) would be MISSED by the AI")
    else:
        print(f"  ✅  No defective covers were missed!")
    
    # === MISCLASSIFIED IMAGES ===
    if misclassified:
        print(f"\n{'='*60}")
        print(f"MISCLASSIFIED IMAGES ({len(misclassified)} total)")
        print(f"{'='*60}")
        for name, actual, predicted, conf, raw in misclassified:
            print(f"  {name}: Actual={actual}, Predicted={predicted} (conf={conf:.1%}, raw={raw:.4f})")
    
    # === SUMMARY ===
    print(f"\n{'='*60}")
    print(f"SUMMARY FOR PRESENTATION")
    print(f"{'='*60}")
    print(f"  Overall Accuracy:  {accuracy:.1%}  {'(⚠️ inflated by imbalance)' if abs(ng_support - ok_support) > 0.3 * total else ''}")
    print(f"  Weighted F1 Score: {w_f1:.1%}  ← USE THIS instead of accuracy")
    print(f"  NG Detection Rate: {ng_recall:.1%}  ← Critical for safety")
    print(f"  False Alarm Rate:  {1-ok_recall:.1%}  (OK flagged as NG)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python evaluate_model.py <dataset_folder>")
        print("")
        print("  dataset_folder should contain NG/ and OK/ subfolders")
        print("")
        print("Examples:")
        print('  python evaluate_model.py "C:/path/to/CV_ACQI"')
        print('  python evaluate_model.py "G:/My Drive/CV_ACQI"')
        sys.exit(1)
    
    evaluate(sys.argv[1])
