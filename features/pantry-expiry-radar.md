# Pantry expiry radar — frontend #7

The pantry dashboard now groups the current household inventory into Expired, Today and Next 48 hours. Tapping a group filters the list; tapping it again or choosing Show all expiry dates removes the urgency filter. Counts follow the current storage-zone, category and search filters, but remain independent of the selected urgency group.

Storage tabs: All zones, Fridge, Freezer, Pantry and Spices. Categories remain available separately. Search waits 250 ms after typing. Clear filters resets search, storage, category and urgency together. Account/household changes also reset filters. Items sort by earliest expiry first, with undated/invalid dates last and stable name/ID tie-breaking. Past dates are labelled Expired rather than Today; no-date items use neutral styling.

Dates are calendar dates without timestamps. Today uses the phone's local date. Next 48 hours means tomorrow and the following calendar day, not a precise rolling 48-hour deadline. Calendar arithmetic avoids daylight-saving rounding errors. The dashboard rechecks its local day every 30 seconds and immediately on app foreground. Freezer items keep their saved dates; freezing does not automatically extend them.

The recipe button opens the existing household recipe screen when the current view includes items due today or within two days. Recipe generation still uses the household pantry and its existing backend prioritization; it does not inherit dashboard filters. Past-due food is not promoted by this button.

## Implementation choice

The dashboard uses React Native FlatList for virtualization and pull-to-refresh rather than adding FlashList. Existing theme colors and household data provider are reused. No backend/schema/dependency changes are needed. Inventory errors show a retry state and suppress stale rows/counts. Phone frame-rate performance has not been measured; do not claim verified 60fps.

## Phone checks before closing #7

1. Reload Expo. In a test household, create items dated yesterday, today, tomorrow, two days out, three days out, and no date. Use multiple storage zones.
2. Confirm radar counts and nearest-expiry ordering. Yesterday must say Expired, and undated items must appear last.
3. Tap each radar group, then Show all expiry dates. Combine Fridge with Produce and a search term. Clear filters must restore all items.
4. Test 50 items and scroll to the bottom. Check touch targets, text wrapping, light/dark mode and smoothness on the phone.
5. Edit a date, consume/discard an item, and verify another household member's dashboard updates through the existing refresh/polling flow.
6. Switch households: no old household rows or filters should remain.
7. Tap Find recipes for expiring food, generate recipes, and check that eligible household ingredients are used. This shortcut does not pass the current zone/search filter.
8. Disconnect the backend and refresh. Verify retry state, then reconnect. Test foregrounding the app after a local date change.

Automated coverage includes date validation, DST/calendar boundaries, 50-item sorting without input mutation, zone/category/search intersections, urgency counts, household filter reset, item/recipe navigation and load-error handling. These tests do not replace device performance or multi-phone checks.
