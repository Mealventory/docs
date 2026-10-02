# Scan review data integrity

## GitHub issue title

Fix scan review defaults and partial-save error handling

## Description

The multi-item scan review can replace unknown expiry dates with today's date, display sample blueberries for missing or empty scan results, silently navigate away after partial save failures, and miss category-based storage defaults.

Preserve actual scan information and keep failed items available for correction and retry.

## Acceptance criteria

- Missing expiry dates remain blank in review and are submitted as null.
- Missing, empty or malformed scan input shows the empty state without sample food.
- Valid scan-provided storage zones are preserved; otherwise apply category defaults: dairy/meat/seafood to fridge, frozen foods to freezer, spices to spicerack, and others to pantry.
- Selected storage zones are included in inventory save requests.
- Partial failures display per-item errors and keep the review open.
- Acknowledged successful saves are removed from review so retries only submit remaining confirmed items.
- Repeated taps while saving do not start another submission.
- All-success submissions refresh inventory and navigate back.
- Frontend tests and TypeScript checks pass.

## Implementation and validation

Frontend branch: fix/scan-review-integrity.
35 frontend tests pass; TypeScript and whitespace checks pass.
No backend schema changes.

Manual phone checks remain: open review without scan results; review an item without expiry; override a zone; force one item to fail (for example an invalid date) and verify successful items disappear from review while the failed item stays editable.

Retries exclude acknowledged successes. A connection failure after a server commit but before receiving its response remains ambiguous; exactly-once saves would require backend idempotency support and are outside this change.
