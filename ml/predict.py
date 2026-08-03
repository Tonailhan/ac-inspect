"""
Standalone prediction script for anode cover inspection.
Uses MobileNetV2 model with built-in Rescaling layer.

Usage:
    python predict.py <image_path>
    python predict.py ../tests/anode_samples/test1.jpg
"""

import os
import sys
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Must match CLASSIFICATION_THRESHOLD in backend/app.py. Each trained model has
# its own probability scale, so this value is re-derived whenever the weights
# are replaced — see ml/train_mobilenet_v2_100epochs.py. A mismatch between this
# script and the API produces different verdicts for the same image, silently.
CLASSIFICATION_THRESHOLD = 0.525

# Load model — try .keras (new) first, then .h5 (legacy)
weights_dir = os.path.join(os.path.dirname(__file__), '..', 'weights')
model_candidates = [
    os.path.join(weights_dir, 'anode_mobilenet_v2.keras'),
    os.path.join(weights_dir, 'anode_mobilenet_v2.h5'),
    os.path.join(weights_dir, 'anode_classifier_v1.h5'),
]

model_path = None
for candidate in model_candidates:
    if os.path.exists(candidate):
        model_path = candidate
        break

if model_path is None:
    print(f"ERROR: No model file found in {os.path.abspath(weights_dir)}")
    print("Expected: anode_mobilenet_v2.keras, anode_mobilenet_v2.h5, or anode_classifier_v1.h5")
    sys.exit(1)

print(f"Loading model: {os.path.basename(model_path)}")
model = load_model(model_path)


def predict_image(image_path):
    """Predict OK/NG for an anode cover image.
    
    IMPORTANT: The model has a built-in Rescaling layer that converts
    [0, 255] -> [-1, 1]. Do NOT pre-normalize the image.
    """
    # Load and resize to 224x224
    img = load_img(image_path, target_size=(224, 224))
    
    # Convert to array — raw pixels [0, 255], NO normalization
    img_array = img_to_array(img)
    
    # Add batch dimension: (1, 224, 224, 3)
    img_array = np.expand_dims(img_array, axis=0)

    # Predict
    prediction = model.predict(img_array, verbose=0)
    raw_value = float(prediction[0][0])
    
    # Keras sorts class names alphabetically: NG=0, OK=1
    # Sigmoid output above the threshold = OK (class 1), otherwise NG (class 0)
    if raw_value > CLASSIFICATION_THRESHOLD:
        class_label = 'OK'
        confidence = raw_value
    else:
        class_label = 'NG'
        confidence = 1 - raw_value
    
    return class_label, confidence, raw_value


if __name__ == '__main__':
    # Get image path from command line or use default
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Usage: python predict.py <image_path>")
        print("Example: python predict.py ../tests/anode_samples/test1.jpg")
        sys.exit(1)
    
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)
    
    label, confidence, raw = predict_image(image_path)
    print(f"\nResult:     {label}")
    print(f"Confidence: {confidence:.1%}")
    print(f"Raw output: {raw:.4f}")
    print(f"  (NG=0.0 ←── {CLASSIFICATION_THRESHOLD} ──→ 1.0=OK)")
