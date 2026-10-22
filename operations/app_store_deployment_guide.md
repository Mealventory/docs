# App Store & Google Play Production Deployment Guide (DOCS-01)

This guide documents the automated build, signing, and submission pipeline for distributing the Mealventory cross-platform mobile client via **Expo Application Services (EAS)** and **Fastlane**.

---

## 📱 Build Profiles Architecture (`eas.json`)

Mealventory configures three strict build profiles in `frontend/eas.json`:

```json
{
  "cli": {
    "version": ">= 12.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "channel": "development"
    },
    "preview": {
      "distribution": "internal",
      "channel": "staging",
      "ios": {
        "simulator": false
      },
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "distribution": "store",
      "channel": "production",
      "autoIncrement": true,
      "ios": {
        "simulator": false
      },
      "android": {
        "buildType": "app-bundle"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "apple-dev@mealventory.app",
        "ascAppId": "6470000000",
        "appleTeamId": "TEAM_ID"
      },
      "android": {
        "serviceAccountKeyPath": "./credentials/play-service-account.json",
        "track": "internal"
      }
    }
  }
}
```

---

## 🔐 Credentials & App Signing

### 1. iOS App Store & TestFlight
- **Bundle Identifier**: `com.mealventory.app`
- **Apple Developer Account**: Organization membership required with App Manager or Admin role.
- **Signing Credentials**:
  - EAS automatically manages certificates, distribution provisioning profiles, and push notification entitlements:
    ```bash
    eas credentials --platform ios
    ```
  - An **Apple App-Store Connect API Key** (`AuthKey_KEYID.p8`) is stored in EAS Secrets for zero-friction CI/CD authentication without 2FA disruption.

### 2. Google Play Store
- **Application ID**: `com.mealventory.app`
- **Upload Keystore**:
  - Managed by EAS or manually backed up:
    ```bash
    eas credentials --platform android
    ```
- **Google Play Developer API**:
  - A dedicated GCP Service Account (`play-deployer@mealventory.iam.gserviceaccount.com`) with *Release Manager* role in Google Play Console.
  - JSON private key configured in EAS Submit.

---

## 🌐 Production Environment Variables

Never commit production API keys to git. Inject them securely via EAS Secrets:

```bash
cd Mealventory/frontend

# Supabase Production Tenant
eas secret:create --scope project --name EXPO_PUBLIC_SUPABASE_URL --value "https://prod-db.supabase.co" --type string
eas secret:create --scope project --name EXPO_PUBLIC_SUPABASE_ANON_KEY --value "eyJhbGciOiJIUzI1Ni..." --type string

# Production Backend Ingress URL
eas secret:create --scope project --name EXPO_PUBLIC_BACKEND_URL --value "https://api.mealventory.app" --type string
```

---

## 🚀 Build & Submission Workflow

### Step 1: Pre-Build Audit & Asset Verification
Run automated linting, type-checking, and unit tests:
```bash
npm run lint
npm run typecheck
npm test
```
Verify branding icons: `assets/branding/icon.png` (1024x1024) and `assets/branding/adaptive-icon.png`.

### Step 2: Trigger Cloud Production Builds

```bash
# Build both iOS (.ipa) and Android (.aab) simultaneously
eas build --platform all --profile production
```

Monitor live build progress in the Expo dashboard or terminal stream.

### Step 3: Automated Store Submission

#### Deploy to Apple TestFlight:
```bash
eas submit --platform ios --profile production
```
- Transfers the signed `.ipa` to App Store Connect.
- Automatically processes through Apple Transporter.
- Becomes available to internal testers on TestFlight in ~15 minutes.

#### Deploy to Google Play Internal Track:
```bash
eas submit --platform android --profile production
```
- Uploads the signed Android App Bundle (`.aab`) to the Google Play Developer Console.
- Targets the `internal` testing track for immediate QA verification.

---

## 📋 Pre-Submission Compliance Checklist

Before promoting builds from internal testing tracks to public production review:

| Requirement | Scope | Status | Notes |
|---|---|---|---|
| **Privacy Manifest (`NSPrivacy`)** | iOS | Verified | Declares camera usage reason and local storage (`NSCameraUsageDescription`, `NSPhotoLibraryUsageDescription`) |
| **Export Compliance** | iOS | Exempt | Uses standard HTTPS encryption (`ITSAppUsesNonExemptEncryption = false`) |
| **Camera & Media Permissions** | Android | Verified | `android.permission.CAMERA` declared for receipt and barcode scanner |
| **App Tracking Transparency** | iOS | N/A | Mealventory does not track users or use 3rd-party ad trackers |
| **Account Deletion Flow** | Store Guidelines | Required | User profile allows initiating full household leaving or account deletion |
| **Privacy Policy URL** | App Stores | Active | Hosted at `https://mealventory.app/privacy` |
