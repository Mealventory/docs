# Pantry quick quantity controls

Implements Mealventory/frontend#71. Use the minus and plus buttons below a pantry card to change its quantity by one existing unit. Tap the card to open full editing, including fractional changes.

## Behaviour

- The card immediately previews the new quantity and shows Saving while the existing household inventory API persists it.
- Repeated taps and detail navigation are blocked during a save. Only quantity is sent, preserving other item fields.
- A decrement reaching zero asks whether the remaining food was consumed or discarded. Cancel leaves it unchanged. Zero or negative quantities are never submitted.
- Failed saves remove the preview, show an error, and refresh inventory to reconcile the server state.
- Controls are isolated by account, household and item. Existing inventory refresh synchronizes other devices.
- Values that cannot be parsed require full detail editing. Each tap changes one unit, including items measured in kilograms or litres.

## Validation

TypeScript checking and all 110 frontend tests pass. Eight new tests cover quantity parsing, fractional values, optimistic updates, duplicate taps, failed saves, zero prompts, consumed/discarded transitions and remote changes.

Phone verification remains:

1. Add an item with quantity 3. Tap plus and minus; verify the saved value after refreshing and on another phone.
2. Reduce a quantity of 1 (and separately 0.5) and check Cancel, Consumed and Discarded. Each lifecycle action should remove the active item.
3. Disconnect the backend, attempt an update, and confirm an error and no permanently unsaved quantity.
4. Switch households and verify quantities belong to the selected household.
5. Tap the card to confirm full editing still opens. Check controls and prompts on a small screen.

## Concurrency limitation

The existing API saves an absolute quantity; it does not provide atomic increments or version checks. Two phones editing the same item simultaneously can overwrite one another, with the last successful write winning. Refresh reconciles the displayed value; conflict-free simultaneous increments require a separate backend change.

No backend or database changes are required for this feature. Reload the frontend after updating.
