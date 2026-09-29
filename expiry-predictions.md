# Expiry prediction integration (#93 / frontend #74)

Manual Add and Edit Item now offer **Predict expiry**. Scan Review offers it for items without an expiry date. Enter the purchase date, request a suggestion, and explicitly apply it before saving the item. Existing dates are never automatically replaced. Editing supports a separate explicit “Replace date with estimate” action.

## Run and test

Start AI-services on its configured port (normally 8001), then the backend with `AI_SERVICE_URL` pointing to it. Start Expo using the team's normal backend URL/tunnel configuration. No database migration is required for this integration.

For a controlled test, enter a food name, fridge storage, today's purchase date and a known shelf-life baseline of 7 days. Request an estimate, apply it, save, and verify the saved date from another household member's phone. Repeat without applying: the original expiry must remain unchanged. Changing item details during a request discards the old response.

## Current model limitation

The checked-in expiry model training script uses only eight synthetic examples, with shelf-life inputs of 5–30 days, temperatures 4–25 C and humidity 50–70%. It does not identify shelf life from a food name. This feature is experimental and does not establish food safety.

The backend looks for one unambiguous, supported shelf-life value associated with the same food name in the selected household's food records. New items currently do not populate that value. An optional known-shelf-life input supports the model without fabricating a default. Missing/ambiguous values return an unavailable state. Freezer and spice-rack predictions are not supported by the current model. Manual entry remains available. Fridge uses assumed 4 C / 50% humidity; pantry uses assumed 20 C / 50%, not sensor readings.

**Automatic food-name-only prediction remains blocked on a validated shelf-life catalogue and a better validated model** (related AI-services #6). Do not mark the full automatic expiry journey complete based on this integration alone.

## API

`POST /api/v1/items/predict-expiry` requires a bearer token and authorized `X-Household-ID`. JSON: `name`, `storage_zone`, `purchase_date`, optional `item_id`, optional `avg_shelf_life_days` (5–30). An existing item ID is checked against the selected household. The endpoint never modifies inventory.

Response includes `predicted_expiry_date` or null, `source` (`model` or `unavailable`), explanation, purchase date, assumed conditions, and baseline source. The backend calls AI-services `/scan/predict-expiry` using query parameters; inference stays in AI-services. Provider failures yield an unavailable response, not an invented date. Saving uses the existing item creation/update endpoints. The selected date persists; prediction provenance currently does not persist in the database.

## Checks

Automated tests cover permissions, preserving a date until explicit save, failure and invalid-output fallback, input validation, explicit apply, and stale-response rejection. Phone interaction and model accuracy require separate validation.

Local verification: 219 backend tests passed (69 skipped), 92 frontend tests passed, TypeScript check passed, and 22 AI-services tests passed. A direct model inference check returned results but warned that the artifact was saved with scikit-learn 1.8.0 while the installed environment uses 1.9.1. Align training/runtime versions and validate accuracy before treating predictions as reliable.
