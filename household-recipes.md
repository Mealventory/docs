# Recipes from expiring household food

Open **Recipes → Find recipes for my pantry**, or use **Use expiring food** on the pantry screen.

The backend reads the selected household's active inventory. Items dated today through three days from today are prioritized. Past-date items and zero-quantity or inactive items are excluded. Undated items and later-dated items can support recipes. Duplicate ingredient names use the earliest eligible expiry date. Dates follow the backend server's calendar date; these suggestions do not establish food safety.

Suggestions show priority ingredients, steps, preparation/cooking time, and extras to check. Extras are not assumed to be in stock. Generating or opening a recipe does not change inventory. Recipes are session-only; regenerate after inventory changes. There is no automatic expiry prediction in this feature.

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

Automated tests use an isolated database and mocked model responses. Live model quality and phone interaction require manual verification.
