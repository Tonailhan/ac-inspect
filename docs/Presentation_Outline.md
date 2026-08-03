# Presentation Outline: Anode Cover Inspector

---

## Slide 1: Title Slide
- **Title:** Automating Quality Control: The AI Anode Cover Inspector
- **Subtitle:** A Technical Overview of our New Machine Learning System
- **Presenter:** [Your Name / Title]

## Slide 2: The Core Problem
- **Visual:** A photo comparing an ideal anode cover to one with a clear defect (like a fire leak or middle drop).
- **Bullet Points:**
  - Currently, cover quality (shaping, compactness, thickness) is judged entirely by human eyesight.
  - This is subjective: What is "OK" to one person might have a minor defect another missed.
  - We suffer from specific, recurring defects: Fire leaks, poor shaping, thick/less powder, and structural drops.
  - These defects leak heat, wasting expensive electricity and degrading the anode via air burn.
- **Speaker Notes:** Start by reminding everyone that a good cover is more than just powder thickness—it's about shaping, compactness, and sealing the pot. Point out that humans naturally have different standards, so we need a completely objective, digital way to catch things like fire leaks and middle drops.

## Slide 3: The Tech Stack (How it's built)
- **Visual:** A diagram showing three boxes: 1. Phone App (Next.js), 2. Server (Python FastAPI), 3. AI Brain (MobileNetV2).
- **Bullet Points:**
  - **The App (Frontend):** Built with Next.js. Operators use it on their phones via a simple web link—no app installation required.
  - **The Server (Backend):** Built with Python FastAPI. It safely catches the photos sent from the phones and manages the heavy traffic.
  - **The Brain (AI):** A Deep Learning model that analyzes the pixels and makes the final decision.
- **Speaker Notes:** Explain that we didn't just build one massive, slow program. We separated the user interface from the "brain" so the system is lightning-fast and won't crash even if 50 operators use it at once.

## Slide 4: Deep Dive into the AI (MobileNetV2)
- **Visual:** A graphic showing a picture going into a neural network and coming out as an "OK / 95%" score.
- **Bullet Points:**
  - We use **MobileNetV2**, an AI originally designed by Google for mobile devices.
  - **Why?** It is incredibly fast and efficient. It doesn't require a million-dollar supercomputer to run.
  - The AI was trained on our historical photos to recognize the exact visual patterns of our 9 major NG defects (e.g., poor shaping, powder imbalances, drops, and fire leaks).
- **Speaker Notes:** Break down the AI simply. Explain that we fed the AI hundreds of examples of our specific floor defects—like thick powder between high and low anodes, or poor compactness. It calculates a score from 0 to 100%, and if it detects those defect patterns, it flags it as NG. **Describe here what the AI was *designed* to do — save how well it actually does it for Slide 6.** Avoid saying "accurate" or "reliable" on this slide; you will present the measured performance shortly, and the two must not contradict each other.

## Slide 5: The Workflow (Live Demo)
- **Visual:** Screen recording of the app in action on a phone.
- **Bullet Points:** 
  - Operator takes a photo on their phone.
  - Photo upload and result display all happen in the browser — nothing to install.
  - The Python server processes the image in less than 1 second.
  - Result (OK/NG) is displayed instantly.
- **Speaker Notes:** Emphasise that operators need nothing installed — any phone on the plant Wi-Fi can open the tool from a bookmark, which is what makes floor adoption realistic.

## Slide 6: Does It Actually Work? (Expert Validation)
- **Visual:** A photo of the signed expert judgement form, next to a simple bar chart comparing "Lab Test: 82%" against "Real Plant Photos: 56%".
- **Bullet Points:**
  - We tested the AI against **two qualified potline experts** on 34 real plant photos.
  - Photo set prepared by an R&D engineer — we didn't know the mix in advance.
  - Every photo run through the system, 001–034, results recorded, then reviewed and marked by the expert.
  - **Agreement: 19 of 34 (56%).** Defects detected: **6 of 16 (38%).**
  - Internal testing suggested 82% — real photos told a different story.
  - Conclusion: a working **demonstrator**, not yet an inspection tool.
- **Speaker Notes:** This is the most important slide in the deck — do not skip it or rush it. Presenting a limitation you discovered yourself is far stronger than having someone in the audience discover it for you. Explain the analogy plainly: testing the AI on photos from its own training collection is like examining a student using the exact questions they revised from — a high score doesn't prove understanding. The expert test was the real exam. Be ready to say clearly: "I would not recommend relying on this for inspection decisions today." That sentence builds more credibility than any accuracy figure. If asked why it underperforms, the honest answer is that the training photos may not have been labelled to the same standard the experts apply — and confirming that is the next step, not more data collection.
- **If asked whether the test was blind:** answer honestly — it was not. The expert could see the AI's answer when marking the sheet. Say what that means: it would make agreement look *better*, not worse, so the real figure could be lower than 56%. Volunteering this before you are asked is a strength; being caught out on it is not. Next time, have the expert judge each photo before the AI's answer is shown.

## Slide 7: Security & Deployment
- **Visual:** A padlock icon and a Wi-Fi symbol.
- **Bullet Points:**
  - **100% Local:** Runs entirely on the plant's internal Wi-Fi.
  - **Private:** Photos are never uploaded to the public internet or external cloud servers.
  - **Zero-Config Startup:** Designed with automated scripts so anyone can turn the server on with one click.
- **Speaker Notes:** Managers love hearing about security. Reassure them that our data is safe because this system operates internally. It's an "in-house" solution.

## Slide 8: Next Steps & Future Expansion
- **Visual:** A simple roadmap: "Fix accuracy" → "Pilot" → "Expand".
- **Bullet Points:**
  - **First:** confirm the training photos were labelled to the same standard the experts use — the most likely cause of the gap, and it costs nothing but time.
  - **Then:** grow the expert-verified photo set and re-validate against expert judgement.
  - **Later:** connect to the central database to track defect trends by shift.
  - **Long term:** run the same model on crane-mounted cameras for continuous scanning.
- **Speaker Notes:** Keep the ordering honest — the database and crane ideas are genuinely exciting, but they come after accuracy is solved. Framing it this way shows engineering judgement rather than over-promising. The infrastructure (capture, inference, display, deployment) is built and proven; what remains is teaching the model the right standard.

## Slide 9: Q&A
- **Title:** Questions & Discussion
- **Visual:** Press Metal Bintulu Logo or Project Logo.
