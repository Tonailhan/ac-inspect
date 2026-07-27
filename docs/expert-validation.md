# Expert Validation Study

**Date:** 21 July 2026
**Verified by:** Two qualified potline personnel. Identities and employee
numbers are recorded on the signed validation form, retained internally.
**Project by:** Mohammed Tona Ilhan

## 1. Purpose

Held-out test accuracy measures how a model performs on images drawn from the
same pool it was trained on. It does **not** establish whether the model agrees
with how qualified technicians actually judge anode covers on the potline.

This study was run to answer that question directly: **when the model and a
qualified expert look at the same photograph, how often do they agree?**

## 2. Methodology

- **Sample:** 34 anode cover photographs (numbered 001–034), taken under normal
  plant conditions.
- **Model verdicts** were recorded first, without reference to any expert
  opinion, to prevent anchoring.
- **Expert verdicts** were provided independently by two qualified potline
  personnel, who signed the record sheet.
- **Ground truth** is taken to be the expert judgement.
- Agreement was scored per photograph as a binary match.

The signed record sheet is retained as the primary evidence for this study.

## 3. Results

Two models were evaluated against the same 34 photographs:

- **Model A** — the originally deployed model (classification threshold 0.25)
- **Model B** — the retrained model with a corrected train/validation split
  (classification threshold 0.525)

| Metric | Model A | Model B |
|---|---|---|
| Agreement with expert | 17/34 (50.0%) | 19/34 (55.9%) |
| **Defects detected (NG recall)** | **7/16 (43.8%)** | **6/16 (37.5%)** |
| Defects missed | 9 | 10 |
| Good covers passed (OK recall) | 10/18 (55.6%) | 13/18 (72.2%) |
| False alarms | 8 | 5 |

### Interpretation

Model B achieves higher overall agreement, but the improvement comes entirely
from a reduction in false alarms. On the metric that matters most for safety —
**detecting actual defects** — Model B performs slightly worse than Model A.

For reference:
- Random guessing would score 50.0%
- Always answering "OK" would score 52.9% (18 of 34 photos are OK)

Both models therefore perform close to, and in places below, trivial baselines
on real plant photographs.

## 4. Root Cause Analysis

### 4.1 The generalisation gap

| Evaluation set | Reported accuracy | NG recall |
|---|---|---|
| Held-out test set (Model B) | 81.7% | 78.3% |
| Expert-judged plant photos (Model B) | 55.9% | 37.5% |

The model performs substantially worse on real plant photographs than its own
test set predicts.

### 4.2 Loss of class separation

A well-functioning binary classifier assigns low P(OK) scores to defective
covers and high scores to good ones. Comparing the two evaluation sets:

| Evaluation set | Mean P(OK) for NG images | Mean P(OK) for OK images | Separation |
|---|---|---|---|
| Held-out test set | 0.406 | 0.849 | **0.443** |
| Expert-judged photos | 0.578 | 0.716 | **0.138** |

On real photographs the two distributions overlap almost completely. The model
is not merely mis-calibrated — it is largely failing to distinguish the classes.

### 4.3 The threshold is not the cause

A threshold sweep was performed across the full range on the expert-judged set:

| Threshold | NG recall | OK pass rate | Agreement |
|---|---|---|---|
| 0.10 | 31.2% | 94.4% | **64.7%** (best) |
| 0.25 | 31.2% | 83.3% | 58.8% |
| 0.525 (deployed) | 37.5% | 72.2% | 55.9% |
| 0.85 | 68.8% | 55.6% | 61.8% |

**No threshold value yields acceptable performance.** The best achievable
agreement is 64.7%, at which only 31.2% of defects are detected. Raising the
threshold to catch more defects causes false alarms to rise at a comparable
rate, because the underlying scores do not separate the classes.

Several expert-confirmed defects received near-certain "good" scores
(photographs 028, 020 and 018 scored P(OK) = 0.998, 0.996 and 0.985
respectively). No threshold can recover such cases without flagging virtually
every good cover as defective.

### 4.4 Probable explanation

The model scores its own test set well but does not transfer to expert-judged
photographs. This pattern is characteristic of one or both of:

1. **Labelling standard mismatch** — the criteria used to label the training
   images may differ from the criteria the experts apply.
2. **Distribution shift** — the training photographs may differ systematically
   from these plant photographs in camera, lighting, angle or context.

Distinguishing between these would require visual comparison of misclassified
cases against training examples. This was not carried out within the scope of
this study.

## 5. Conclusions

1. The system is **not suitable for unsupervised deployment** as a safety or
   quality gate in its current state.
2. The operationally meaningful figures are the field measurements
   (**55.9% agreement, 37.5% defect detection**), not the held-out test
   accuracy of 81.7%. Published or presented material should cite the field
   figures.
3. The system's value at present is as a **demonstrator** of the end-to-end
   pipeline — image capture, inference, and result reporting — rather than as a
   production inspection tool.
4. All model output must be physically verified by a qualified technician or
   potline supervisor, consistent with the disclaimer shown in the application.

## 6. Recommendations

1. **Reconcile labelling criteria.** Establish whether the training labels were
   assigned using the same standard the experts apply. This is the single
   highest-value diagnostic and requires no new photography.
2. **Expand the expert-validated set.** The 34 photographs used here are the
   only independently verified data available. A larger expert-labelled set
   would both improve training and support more reliable evaluation.
3. **Re-validate after any retraining.** Held-out test accuracy has been shown
   to overstate field performance for this problem; the expert-judged set should
   be the acceptance criterion.
4. **Retain the current threshold documentation.** Each retrained model produces
   its own probability scale; the classification threshold must be re-derived
   and updated in `backend/app.py` whenever weights are replaced.

## 7. Note on Statistical Confidence

The expert-judged set contains 16 NG and 18 OK photographs. With a sample this
small, a single reclassified photograph shifts NG recall by approximately 6
percentage points. The measured differences between Model A and Model B
(43.8% vs 37.5% NG recall) are within the range attributable to sampling
variation, and should not be treated as a reliable ranking of the two models.

The broader finding — that field performance is far below test-set performance,
and close to trivial baselines — rests on a much larger effect and is not
explained by sample size alone.
