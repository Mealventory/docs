# Product, receipt and expiry-tag scanning

## Changes

- Frontend scanning uses `POST /api/v1/scan/preview`. This authenticated, household-scoped endpoint returns candidates without writing inventory. The review screen saves confirmed items using the existing items API.
- Both scanner entry points offer Product, Receipt, Expiry tag and Barcode modes. Barcode lookup is unchanged.
- Expiry-only tags open an unnamed, editable review item. A food name is required before saving.
- Receipt/tag uploads retain 2400px width for text recognition. Unreadable local images fail explicitly instead of uploading their file path. Local responses are not read twice.
- Google Vision document text detection handles receipts/tags. Product recognition falls back to packaging OCR if classification/labels find nothing. Recognition outages return service errors instead of appearing as an empty scan.
- Recognition remains limited to the food vocabulary and OCR quality. No claim of universal product recognition or measured accuracy improvement is made.

## Run and verify

Restart backend and AI services with these changes, then reload Expo. An older backend will not have the preview endpoint. Keep the backend tunnel running; its URL only needs updating if the tunnel itself restarts.

1. Product: photograph a clearly visible apple, then a yogurt package with its name visible.
2. Receipt: photograph a flat, well-lit grocery receipt with legible food names.
3. Expiry tag: fill the frame with a best-before label. Confirm its date and enter the food name.
4. Cancel review: inventory must remain unchanged. Save once: items must appear once.
5. Repeat using the photo library and check returning to the camera.
6. If recognition fails, record the exact error and keep the source photo for diagnosis.

Offline automated checks cover preview responses/no writes, tag dates, upload failures, service errors and packaging fallback. Real-device and live Google Vision accuracy testing remains required.
