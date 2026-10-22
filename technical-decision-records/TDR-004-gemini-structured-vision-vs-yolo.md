# TDR-004: Multimodal Cloud Vision & OCR vs Edge YOLO Models (DOCS-02)

- **Status**: Accepted
- **Deciders**: Mealventory AI & Architecture Team
- **Date**: 2026-10-15
- **Technical Domain**: Computer Vision, OCR & Machine Learning Architecture

---

## 1. Context & Problem Statement

Mealventory requires automated recognition across diverse visual inputs:
1. **Paper Grocery Receipts**: Long, crumpled, low-contrast thermal receipts from hundreds of distinct supermarket chains (Walmart, Costco, Loblaws, local markets).
2. **Fresh Produce**: Countertop photos of loose fruits and vegetables in varying quantities, lighting, and angles.
3. **Packaging Date Tags**: Diverse date stamps (ISO, Canadian bilingual month abbreviations, dot-matrix expiration prints).

We needed an AI architecture capable of extracting clean, structured inventory data while balancing inference latency, recognition accuracy, and operational complexity.

---

## 2. Decision Drivers

- **Zero-Shot Generalization**: The ability to parse arbitrary receipt formats without training custom templates for every grocery chain.
- **Strict Structured JSON Guarantee**: Extracted items must conform 100% to typed Pydantic models with quantities, units, and categories.
- **Maintainability**: Avoid ongoing model retraining, dataset labeling, and mobile weight deployment hurdles.
- **Offline & Low-Cost Capability**: Development environments and offline benchmarks must execute without incurring cloud API costs.

---

## 3. Decision

We selected a **Hybrid Cloud Multimodal Architecture**:
1. **Primary Production Engine**: Google Cloud Vision OCR for layout and text extraction, complemented by structured multimodal reasoning (Gemini 1.5 Flash structured outputs) and USDA FoodKeeper heuristics.
2. **Local Classification Fallback**: Lightweight Keras MobileNetV2 produce classifier for offline produce identification.
3. **Deterministic Mock Vision Pipeline**: Zero-cost mock engine (`services/mock_engine.py`) activated via `MOCK_VISION=true` or `GEMINI_API_KEY=mock`, returning deterministic high-confidence fixtures in < 50ms for local testing and CI.
4. **Calibrated Confidence Scoring**: Formulated thresholds (`>= 0.80` clean, `0.65–0.79` review needed, `< 0.50` rejected) surfacing uncertain items to the user via the `needs_review` flag.

---

## 4. Alternatives Considered

### Alternative A: Custom Fine-Tuned YOLOv8 Edge Model
- **Evaluation**: Training a custom YOLO object detection model deployed natively to iOS (CoreML) and Android (TFLite).
- **Rejection Rationale**: 
  - *Receipt Failure*: YOLO detects bounding boxes, but cannot perform the complex textual reasoning required to associate item names with prices, discount lines, and dates on complex paper receipts.
  - *Annotation Burden*: Collecting, annotating, and labeling tens of thousands of grocery items across changing seasonal produce varieties requires prohibitive manual effort.
  - *App Size Bloat*: Native model weights increase the mobile app bundle size by 30–80 MB.

### Alternative B: Open-Source Tesseract OCR on Mobile Client
- **Evaluation**: Compiling Tesseract into React Native via C++ bindings.
- **Rejection Rationale**: Extremely poor accuracy on skewed, crumpled receipts, low mobile framerates, and severe battery drain during mobile OCR processing.

---

## 5. Consequences & Tradeoffs

### Positive Consequences
- **High Document OCR Accuracy**: Google Vision accurately extracts skewed, crumpled, and faded thermal receipt text.
- **Structured Pydantic Contract**: Output conforms strictly to `ScanResponse`, preventing malformed JSON crashes.
- **Fast Local Benchmarks**: Developers and automated CI runners evaluate scan logic instantly via the mock engine without cloud credentials.

### Negative Consequences & Mitigation
- **Cloud Latency**: Network round-trip takes 800ms–1500ms per image.
  - *Mitigation*: Client displays an engaging scan HUD animation and optimistic review sheet transitions.
- **API Operating Costs**: Cloud Vision requests incur per-call costs at scale.
  - *Mitigation*: Rate limiting on scan endpoints ([operations/rate-limiting-88.md](../operations/rate-limiting-88.md)) and image preprocessing that scales down resolution before upload.
