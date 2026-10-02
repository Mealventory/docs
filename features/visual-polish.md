# Frontend visual polish

## Issue title
Polish app layouts, alignment and empty states

## Description
Improve visual consistency across pantry, recipes, shopping, scan review, forms, settings and household screens while preserving Mealventory's existing green palette, typography and rounded-card style.

## Acceptance criteria
- Pantry, filtered search, recipes and scan review have friendly empty states with relevant actions.
- Headers, icons, buttons and form fields align consistently without crowding narrow screens.
- Bottom navigation remains icons-only with Scan in the middle and respects device safe areas.
- Button labels and shopping rows wrap rather than overflow.
- Shared controls retain accessible labels and comfortable touch targets.
- Light and dark themes retain the existing colour scheme.
- Temporary visual-preview routes are removed from the shipped app.
- TypeScript and existing frontend tests pass.

## Work completed
The main visual pass is already merged into main. Follow-up branch ui/visual-polish-followup removes the temporary preview route, centres filter chips with 44-point minimum targets and preserves input focus highlighting with caller-provided handlers.

The first pass was inspected in a 375-pixel web preview in light/dark modes and on the household welcome screen. Physical-device layout checks, keyboard behavior, larger accessibility text and camera controls still need a manual pass. The preview did not sign into a real account.

Local dependencies were refreshed from the lockfile. The system Node 20.19.1 is below the installed Metro engine requirement; verification uses the available Node 24 runtime. Use a supported Node runtime for development.
