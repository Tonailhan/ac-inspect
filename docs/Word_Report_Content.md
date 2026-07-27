# Anode Cover Quality Inspection System
## Technical Project Report
**Prepared for:** Press Metal Bintulu
**Date:** June 2026

---

## 1. Executive Summary
This document explains the technical development of the "Anode Cover Inspector." This system uses Artificial Intelligence (AI) to automatically check the structural integrity, shaping, and material distribution of our anode covers. By doing this, we give our operators a tool to instantly confirm quality against a strict set of defect criteria, reducing human error and preventing energy loss on the potline.

## 2. The Problem We Are Solving
Right now, checking the anode cover quality is done by human eyesight. An optimal cover requires proper shaping and compactness to seal the pot effectively. This manual inspection causes two problems:
1. **Inconsistency**: What looks "OK" to one technician might actually have hidden defects that another might miss.
2. **Data Loss**: We don't have a digital record of specific defects on a given shift.

A bad cover can have multiple failure points. Our system specifically targets these common "NG" (No Good) conditions:
- Poor shaping or poor compactness
- Thick powder (especially between high and low anodes)
- Less powder (insufficient coverage)
- Fire leaks (exposed areas allowing air burn)
- Middle drops, minor middle drops, or full anode cover drops

If these defects are missed, heat escapes from the pot, wasting electricity, and the carbon anode can oxidize too quickly. We needed a standard, digital way to verify coverage.

## 3. How The System Works (Architecture)
We built a modern web application separated into three distinct parts. This separation makes the app very fast and easy to update in the future.

### Part A: The User Interface (Frontend)
- **Technology used:** Next.js and React.
- **What it does:** This is the website the operator sees on their phone or tablet. It is designed to be lightweight. When an operator takes a photo, the app automatically shrinks the image size before sending it. This ensures the app works perfectly even if the plant Wi-Fi is slow.

### Part B: The Traffic Controller (Backend)
- **Technology used:** Python and FastAPI.
- **What it does:** This is the server that runs on the main computer. It safely receives the image from the operator's phone, checks that the data is valid, and hands it over to the AI model. FastAPI was chosen because it can handle many operators taking photos at the exact same time without slowing down.

### Part C: The Artificial Intelligence (Machine Learning)
- **Technology used:** MobileNetV2 (TensorFlow/Keras).
- **What it does:** This is the "brain" of the system. MobileNetV2 is a specific type of AI designed by Google to be incredibly fast. Instead of needing a massive supercomputer, it can analyze an image in milliseconds. 
- **How it decides:** The AI was trained on historical photos of good covers and covers exhibiting the specific NG defects (fire leaks, drops, poor shaping, etc.). When it looks at a new photo, it analyzes the visual patterns and calculates a confidence score from 0% to 100%. If it detects signs of these defects, it flags the image as "NG".

## 4. Network and Deployment
To make this easy for the plant, operators do not need to download an app from the App Store. 
The system runs locally on a computer on the plant floor. As long as the operator connects their phone to the same Wi-Fi network, they simply open their web browser and type in the computer's IP address (e.g., `http://192.168.1.50:3000`).

We also created automated startup scripts (`start.bat`). If the computer restarts, a supervisor just double-clicks one file, and the entire system (Frontend, Backend, and AI) turns itself back on automatically.

## 5. Security and Privacy
Because the system runs entirely on the plant's local Wi-Fi, the photos of our potline never leave the building. They are not uploaded to the public internet, ensuring complete data privacy for Press Metal operations.

## 6. Next Steps for Production
1. **Pilot Testing:** Have operators use the app alongside their normal visual checks for two weeks to build trust in the AI.
2. **Continuous Learning:** Save the "NG" photos to retrain the AI model next month, making it even smarter.
