# Recipes from expiring household food

Open **Recipes → Find recipes for my pantry**.

The backend reads the selected household's active inventory. Items dated today through three days from today are prioritized. Past-date items and zero-quantity or inactive items are excluded. Undated items and later-dated items can support recipes. Duplicate ingredient names use the earliest eligible expiry date. Dates follow the backend server's calendar date; these suggestions do not establish food safety.

Suggestions show priority ingredients, steps, preparation/cooking time, and extras to check. Extras are not assumed to be in stock. Generating or opening a recipe does not change inventory. Generated suggestions can be saved to the household collection; regenerate suggestions after inventory changes. Saved recipe persistence requires `backend/scripts/add_household_saved_recipes.sql` on databases that do not yet have that table. There is no automatic expiry prediction in this feature.

## Cooking and leftovers

After the cooking steps, review the servings prepared and the pantry ingredients used. Confirming ingredient amounts updates those pantry items. Choosing **Finish without changing pantry** records that the meal is finished without changing ingredient quantities.

After either completion path, **Save Leftovers** is optional. The form starts with the recipe name and servings prepared; edit the name or portion count as needed, then choose the fridge or freezer. A use-by or quality date is never guessed: confirm a date you know, or explicitly confirm that the date is unknown to leave it unset. **Skip saving leftovers** finishes without creating a pantry item.

Leftovers are added as a separate household inventory item. Saving or retrying a leftover does not reverse or repeat the recipe's ingredient deductions. The client persists the exact leftover request before sending it and derives a distinct idempotency key from the recipe completion ID, so retrying after an interrupted response does not create a second item. The existing household-scoped inventory batch endpoint enforces access and idempotency.

## Configuration

Backend `.env` requires `OPENROUTER_API_KEY` and a supported `OPENROUTER_MODEL`. Keep keys out of Git. The existing backend OpenRouter integration generates recipes; this flow does not require the AI-services process. Ingredient names and days until expiry are sent to the configured provider, without user identifiers or household IDs.

Frontend uses its existing `EXPO_PUBLIC_BACKEND_URL` (or `EXPO_PUBLIC_API_URL` fallback). Keep the backend and tunnel running. Restart the backend and reload Expo after applying the changes.

## API

`GET /api/v1/recipes/` requires a bearer token and `X-Household-ID` for a household the user belongs to. It returns `recipes` and `priority_items`. Empty eligible inventory returns empty arrays without calling the model. Invalid provider output or provider failures return 503; provider timeout returns 504. The existing route is retained; selection now uses household inventory rather than legacy per-user inventory.

## Manual verification

1. In a test household add an item dated today, one dated three days ahead, one four days ahead, one without a date, and one past-date item.
2. Generate recipes. Each suggestion should use at least one priority item when priority ingredients exist. Past-date ingredients must not be sent to the provider.
3. Open a suggestion. Check its steps, use-soon list, and extra ingredients.
4. Switch households during generation. Results from the previous household must not appear.
5. Test an empty household and an unavailable provider. Expect an empty state or retryable error, not demo recipes.
6. Finish cooking a recipe and confirm servings prepared. Save leftovers to the fridge and then the freezer in separate runs; verify the item name, portion quantity, and storage zone.
7. Save one leftover with a confirmed quality date and another with the date explicitly left unset. Verify that an unconfirmed or invalid date cannot be saved.
8. Finish a recipe without changing pantry quantities, then save leftovers. Simulate an interrupted leftover save and retry it; verify ingredient deductions are unchanged and only one leftover item is created.

Automated tests use an isolated database and mocked model responses. Live model quality and phone interaction require manual verification.
