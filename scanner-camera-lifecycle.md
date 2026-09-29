# Scanner camera return fix

The scan tab and full-screen scanner now mount their camera only while the route is focused and the app is active. Returning from review resets the barcode lock, loading state, torch, and errors. Barcode lookups finishing after the scanner loses focus cannot open another review screen. The delayed barcode unlock timer has been removed.

## Verification

Frontend TypeScript checking and all 54 Node tests passed. Hook tests cover repeated focus transitions, background/resume, and initial inactive state. Native camera behavior still needs verification on a phone.

1. Reload Expo Go with the updated frontend.
2. Open Scan, choose Barcode, and scan a product.
3. From review, go back. Confirm the live camera returns and scan again. Repeat three times.
4. Leave the Scan tab and return; confirm the camera works.
5. Repeat using the full-screen scanner entry point.
6. Background the app and return; confirm the preview resumes.
7. Leave while a barcode lookup is pending; confirm it does not unexpectedly reopen review.

No backend or tunnel restart is required for this frontend change.
