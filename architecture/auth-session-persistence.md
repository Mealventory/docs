# Authentication Session Persistence & Splash Screen Hydration (#56)

## 1. Overview & Architectural Requirements

To deliver a smooth and secure user experience across application cold starts and device restarts, the client implements persistent authentication session management:

1. **Persistent Secure Storage**:
   - On native iOS and Android, authentication sessions are stored in the device's hardware-backed secure storage (`expo-secure-store`), utilizing the iOS Keychain and Android Keystore.
   - On web, sessions use standard `localStorage` with memory fallback in private browsing or server environments.
   - Values are strictly isolated to authentication tokens; no service-role keys, JWT signing secrets, or database credentials are ever stored or exposed in client code.

2. **Supabase Client Session Configuration**:
   - In `frontend/src/lib/supabase.ts`, `persistSession: true` is configured alongside the custom `authStorageAdapter` and `autoRefreshToken: true`.
   - Web URL detection (`detectSessionInUrl: Platform.OS === 'web'`) and password recovery flow (`initialRecovery`, `acceptRecoveryLink`) remain active and functional.

3. **Flicker-Free Splash Screen & Hydration Flow**:
   - The native splash screen (`expo-splash-screen`) is prevented from auto-hiding during initial app load (`SplashScreen.preventAutoHideAsync()`).
   - Root layout (`app/_layout.tsx`) mounts font loaders, theme, auth, and inventory providers.
   - `RootLayoutContent` guards rendering until the authentication session has finished hydrating from storage (`ready === true`).
   - `SplashScreen.hideAsync()` is invoked only after `ready` is true. If the user has an existing session, the authenticated household screen renders directly without flickering or flashing the unauthenticated welcome screen.

4. **Session Lifecycle, Logout, & Account Switching Isolation**:
   - On logout (`signOutAccount`), the session is terminated on the Supabase server and cleared from the persistent storage adapter (`removeItem`). Restarting the app after logout opens the sign-in screen.
   - Switching accounts clears household selection (`selectHousehold(null)` in `AuthContext`) and immediately resets the inventory scope (`InventoryContext` stores are scoped by `userId:householdId`). No cached data from a previous account can leak to another user.
   - Automatic token refresh resumes when the app becomes `active` (`AppState.addEventListener('change', ...)`).

---

## 2. Storage Adapter Architecture (`src/lib/authStorage.ts`)

### Storage Implementation Matrix

| Platform | Storage Mechanism | Security Level | Key Characteristics |
|---|---|---|---|
| **iOS** | `expo-secure-store` | Hardware Keychain | Encrypted at rest, persists across app restarts |
| **Android** | `expo-secure-store` | Hardware Keystore / Encrypted SharedPreferences | Encrypted at rest, 1800-byte transparent chunking |
| **Web** | `window.localStorage` | Browser storage | Preserves session and redirect handling |
| **Node / SSR / Tests** | In-Memory `Map` fallback | Ephemeral | Safe execution without missing-module failures |

### Key Sanitization & Chunking Strategy
- **Key Sanitization**: `expo-secure-store` restricts keys to `[a-zA-Z0-9._-]`. `toSafeSecureStoreKey` deterministically encodes illegal characters (e.g. `:`, `/`, `@`) to hexadecimal representations `_xx_`, preventing native exceptions.
- **Payload Chunking**: To accommodate Android Keystore 2048-byte limits, payloads exceeding 1800 characters are automatically split into chunks (`_chunk_0`, `_chunk_1`, ...) with a metadata key tracking the chunk count (`_chunks`). Reading reassembles the chunks into the original payload transparently, and deleting removes all chunks.

---

## 3. Verification & Automated Tests

Automated tests cover all criteria under `tests/authStorage.test.cjs` and `tests/authPersistence.test.cjs`:
- `tests/authStorage.test.cjs`: Validates key sanitization, payload storage, chunking of large sessions (>1800 bytes), chunk reassembly, cleanup on delete/overwrite, and web storage fallback.
- `tests/authPersistence.test.cjs`: Validates `createClient` configuration (`persistSession: true`), absence of hardcoded server secrets, splash screen flicker elimination, logout storage clearance, account switching data isolation, and background/active app state token auto-refresh.

Run automated tests:
```powershell
npm test
npm run typecheck
```
