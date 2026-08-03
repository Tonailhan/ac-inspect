# Anode Cover Quality Inspection System
## Technical Project Report
**Prepared for:** Press Metal Bintulu
**Date:** July 2026

---

## 1. Executive Summary
This document explains the technical development of the "Anode Cover Inspector."
This system uses Artificial Intelligence (AI) to check the structural integrity,
shaping, and material distribution of our anode covers from a photograph, giving
operators a fast, consistent second opinion and creating a digital record of
defects by shift.

A complete working system was delivered: operators photograph a cover with any
phone on the plant Wi-Fi and receive a result in under a second, with no app
installation and no photograph ever leaving the building.

**Current status.** The system was validated against the judgement of two
qualified potline personnel on 34 real plant photographs (Section 4). In that
test the AI agreed with the experts on 56% of covers and detected 38% of
confirmed defects — substantially below the 82% suggested by internal testing.
The system is therefore presented as a **working demonstration of the technology
and the inspection workflow**, and is not yet suitable for supporting inspection
decisions. Section 7 sets out what would be required to close that gap.

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

## 4. Validation: Testing the AI Against Human Experts

Building the system is only half the work. The more important question is
whether the AI actually agrees with the people who do this job every day.

### How we tested it
A set of **34 photographs** of anode covers — a deliberate mix of good and
defective ones — was prepared by an R&D engineer, so we did not know in advance
how many of each there were.

We ran every photograph through the system one by one, from 001 to 034, writing
down what the AI said for each. A qualified potline technician then went through
our record sheet and marked, for each photograph, what the correct answer should
be and whether the AI had got it right. Finally we went through all 34 together
and discussed why each cover was good or defective. Both assessors signed the
completed record sheet, which is retained internally.

The experts' judgement was treated as the correct answer.

**One honest caveat about the method.** The technician could see the AI's answer
on the record sheet when giving their own. Ideally they would have judged each
photograph first, without knowing what the AI said. Seeing the answer can make a
person slightly more likely to agree with it — which means the real agreement
could be a little *lower* than the numbers below, not higher. That does not
change the conclusion; if anything it strengthens it.

### What we found

| Measure | Result |
|---|---|
| Times the AI agreed with the experts | 19 out of 34 (56%) |
| **Defective covers the AI detected** | **6 out of 16 (38%)** |
| Defective covers the AI missed | 10 |
| Good covers correctly passed | 13 out of 18 (72%) |
| Good covers wrongly flagged | 5 |

During internal testing, the AI scored 82% on photographs set aside from its own
training collection. On these real plant photographs, judged by experts, it
scored 56%.

**This difference is the single most important finding of the project.**

### Why the difference matters
Testing an AI on photographs from its own training collection is like giving a
student an exam using the same questions they revised from. A high score does not
prove they understand the subject.

The expert validation was the real exam — and it showed the AI has not yet
learned to judge anode covers the way an experienced technician does. In several
cases the AI was not merely wrong, but confidently wrong: it rated covers the
experts marked defective as over 99% likely to be acceptable.

We also confirmed that this cannot be fixed by simply adjusting the AI's
sensitivity setting. We tested every possible setting, and none produced
acceptable results — making the AI more suspicious caused it to flag good covers
at roughly the same rate as it caught bad ones.

### What this means for use on the floor
The system should be treated as a **demonstration of the technology**, not as a
replacement for inspection. Every result must be physically verified by a
qualified technician or potline supervisor, as stated in the disclaimer shown in
the application itself.

### A note on sample size
16 of the 34 photographs showed defects. With a sample this small, a single
photograph changes the detection rate by about 6 percentage points, so the
precise figures should be read as approximate. The overall conclusion — that
real-world performance falls well short of internal test results — rests on a
much larger gap and is not explained by sample size.

The full technical study is documented separately in `docs/expert-validation.md`.

## 5. Network and Deployment
To make this easy for the plant, operators do not need to download an app from the App Store. 
The system runs locally on a computer on the plant floor. As long as the operator connects their phone to the same Wi-Fi network, they simply open their web browser and type in the computer's IP address (e.g., `http://192.168.1.50:3000`).

We also created automated startup scripts (`start.bat`). If the computer restarts, a supervisor just double-clicks one file, and the entire system (Frontend, Backend, and AI) turns itself back on automatically.

## 6. Security and Privacy
Because the system runs entirely on the plant's local Wi-Fi, the photos of our potline never leave the building. They are not uploaded to the public internet, ensuring complete data privacy for Press Metal operations.

## 7. Next Steps for Production

The validation study in Section 4 shows the system is not yet ready to support
inspection decisions. The following steps are ordered by what would most improve
that.

1. **Confirm the labelling standard.** The AI learned from photographs that were
   sorted into "good" and "defective" folders. If those folders were sorted using
   different criteria than the experts apply, the AI has been learning the wrong
   standard — which would explain the results in Section 4. Reviewing a sample of
   the training photographs with the same assessors would confirm or rule this out.
   This costs nothing but time and is the most valuable next step.
2. **Expand the expert-verified collection.** The 34 photographs in this study are
   the only images checked by qualified personnel. A larger
   expert-verified set would improve both training and future testing.
3. **Re-validate after any retraining.** Internal test scores have been shown to
   overstate real performance for this task. Any future version should be measured
   against expert judgement before being considered for use.
4. **Pilot testing (only once detection improves).** Running the app alongside
   normal visual checks builds trust — but piloting at the current detection rate
   risks eroding that trust instead.
