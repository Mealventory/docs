# Expiry estimates and shelf-life catalogue (#93 / frontend #74)

Manual Add, Edit Item and Scan Review use the shared expiry estimation control. An estimate must be explicitly applied and then saved. Existing dates are never overwritten automatically. No database migration or AI-services change is required.

## Try it on a phone

1. Restart the backend and reload Expo with the updated frontend. Both repositories need this branch.
2. Add `Carrots`, choose Fridge, and leave advanced shelf life blank. Tap Predict expiry, choose Whole / uncut, check the purchase date, and tap Predict expiry again. Expect a storage-guide estimate 14 days after that date.
3. Apply and save. Check that another household member sees the saved date. Repeat without applying: an existing date must stay unchanged.
4. Try `Yogurt` in Fridge. Choose Opened and enter the actual opening date. Request the estimate again: expect opening date plus three days. Unopened yogurt directs you to the package date instead of inventing a duration.
5. Try `Ginger` as Whole / uncut: fridge gives 14 days; pantry gives seven days, with the corresponding source shown.
6. Try unknown or composite names such as `strawberry jam`, or yogurt in Pantry. Expect no catalogue date. Verify that changing the food or storage location discards an old suggestion.

These are guide-based estimates, not measured spoilage dates. An earlier package date takes precedence. Storage assumptions and the source link are shown with each estimate. Past estimates remain in the past; they are not extended from today.

## Catalogue and matching

Backend `app/data/shelf_life_catalogue.json` is a versioned, source-linked snapshot with a review date. It currently covers 33 food groups and 46 condition/location entries, including milk, yogurt, cottage cheese, selected meat and eggs, common vegetables, berries, citrus, avocado, bread and ginger. It is deliberately not a complete food database.

The reviewed catalogue uses exact aliases and requires the user to choose the matching food condition. If it has no match, the backend also asks the offline USDA FoodKeeper matcher. It uses RapidFuzz `token_sort_ratio` and accepts scores above 75; preparation words such as “fresh” and “fillet” are removed before matching. Equal top scores are left unmatched. This broadens coverage without replacing exact curated matches, though a fuzzy match can still select the wrong food group; check the matched food and source before applying the suggestion.

Health Canada's general storage chart supplies the reviewed catalogue's dairy, meat, eggs and selected vegetable entries. NDSU Extension's 2013 guide supplies the remaining produce and plain bread. Ginger uses University of Minnesota and Iowa State extension guidance. The FoodKeeper snapshot contains 613 groups from data version 128, dated September 7, 2018; the USDA currently lists this English JSON dataset as public-domain CC0. FoodKeeper ranges use their upper endpoint, and months, weeks and years convert to 30, 7 and 365 days. For example, “Fresh Salmon Fillet” matches “Fish - Fresh” and uses the 1–2 day refrigerated range's upper endpoint: two days from the entered purchase date. USDA freezer durations estimate quality, not a food safety deadline.

- [Health Canada: Safe food storage](https://www.canada.ca/en/health-canada/services/general-food-safety-tips/safe-food-storage.html)
- [NDSU Extension: Food Storage Guide, hosted by Purdue](https://extension.purdue.edu/county/floyd/hhs/hhs-education-papers/food-storage-guide.pdf)
- [University of Minnesota: Ginger](https://reallifegoodfood.umn.edu/vegetables/ginger)
- [Iowa State: Storing fresh ginger](https://blogs.extension.iastate.edu/answerline/2019/03/25/how-to-store-fresh-ginger/comment-page-1/)
- [USDA FSIS: FoodKeeper data and CC0 download listing](https://catalog.data.gov/dataset/fsis-foodkeeper-data)

For published ranges, reviewed catalogue entries use the lower endpoint while the USDA fallback uses the upper endpoint to reflect the full FoodKeeper window. No interpolation, temperature adjustment or prototype-model inference is applied to catalogue entries. Refrigerated entries assume continuous storage at 4°C or below. Whole produce means fresh and uncut; avocado and pear guidance assumes ripe fruit. Opened foods count from opening and cooked foods from cooking. Unopened dairy has no numeric estimate because the source specifies the package date. Spice-rack storage remains unsupported.

To extend coverage, add reviewed aliases, food state, actual storage zone, start-date meaning, duration and primary source URL. Do not broaden aliases to foods with different preparation/storage requirements. Add tests for the new match and nearby names that must not match.

## API and compatibility

`POST /api/v1/items/predict-expiry` requires a bearer token and authorized `X-Household-ID`. Inputs: `name`, `storage_zone`, `purchase_date`, optional `item_id`, `food_state`, and `avg_shelf_life_days` (5–30). For compatibility the API field remains `purchase_date`, but it represents the opening/cooking date when that condition is selected. Future dates are rejected. Existing item IDs are checked for household ownership and active status before any estimate.

`food_state`: `whole`, `raw`, `cooked`, `opened`, `unopened`, `ready_to_eat`. Missing or mismatched conditions return `source: unavailable`, no date, and `food_state_options` for the frontend to display. Known foods in unsupported zones also return no date, even when a manual baseline is supplied.

Responses add `source: catalogue`, `source_name`, `source_url`, `matched_food`, `shelf_life_days`, and `food_state_options`. Existing `model` and `unavailable` responses remain. Deploy frontend and backend together: older frontends cannot display the condition choices. The endpoint never saves inventory; existing create/PATCH operations persist the chosen date. Estimate provenance and condition are not persisted with inventory yet.

## Experimental model fallback

Names not found in either storage guide retain the previous opt-in flow: enter a known baseline under Advanced options, or use one unambiguous household food metadata value. AI-services must be running for USDA matching and the model fallback. The model's eight synthetic training examples do not provide validated food safety predictions. Fridge uses assumed 4°C / 50% humidity and pantry 20°C / 50%; the model does not estimate freezer or spice-rack dates. Provider failures leave the date unchanged.

Exact reviewed-catalogue matches take precedence over the USDA lookup; both take precedence over manual/model baselines. The USDA snapshot requires the AI service but no live external catalogue download.

## Validation

Automated tests cover aliases, per-condition and per-location durations, missing conditions, unknown/composite foods, label-only guidance, preserving past dates, tenant authorization, explicit application, source labels and stale-response cancellation. Tests use isolated databases and mocked AI calls. Phone layout and a live save across two phones still require the manual checks above.

## Whole citrus at room temperature

Mandarins, clementines, tangerines and the other curated citrus aliases now support Pantry as well as Fridge. Choose Whole / uncut and use the actual purchase date: Pantry suggests seven days, while the existing Fridge guidance remains fourteen days. The pantry value is a quality estimate for fresh, unpeeled fruit, not a universal fruit expiry rule. Peeled or prepared fruit is not covered by this entry. Check daily and discard moldy fruit. Source: [University of Illinois Extension, winter citrus](https://extension.illinois.edu/blogs/live-well-eat-well/2024-01-24-eat-all-varieties-winter-citrus). Restart the backend after catalogue changes because the data is cached in each process.
