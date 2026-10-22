# TDR-005: Expo Push Notification Gateway vs Direct APNs/FCM (DOCS-02)

- **Status**: Accepted
- **Deciders**: Mealventory Architecture Team
- **Date**: 2026-10-15
- **Technical Domain**: Mobile Notifications & Background Relays

---

## 1. Context & Problem Statement

Mealventory's core value proposition is proactive waste prevention. When perishable items (milk, produce, meat) approach their expiration date, the platform must alert household members via lock-screen push notifications.

We needed a backend push notification architecture capable of delivering alerts across both iOS (APNs) and Android (FCM) devices reliably without unnecessary operational overhead.

---

## 2. Decision Drivers

- **Cross-Platform Uniformity**: Deliver notifications to mixed households (e.g., iPhone owner sharing pantry with Android user) using a single backend dispatch payload.
- **Credential Simplicity**: Avoid maintaining separate APNs HTTP/2 certificate rotations and Google FCM service account credentials in the FastAPI backend.
- **Expo Ecosystem Synergy**: Seamless integration with the mobile client's `expo-notifications` library.

---

## 3. Decision

We chose the **Expo Push Notification Gateway** as the unified notification relay.

The mobile client obtains an `ExponentPushToken[xxxxxxxxxxxxxx]` upon user permission grant and registers it with the backend via `POST /api/v1/notifications/register-token`.

When the daily expiration cron runs, the FastAPI backend dispatches batched JSON payloads directly to Expo's REST endpoint:
```http
POST https://exp.host/--/api/v2/push/send
Content-Type: application/json

[
  {
    "to": "ExponentPushToken[xxxxxxxxxxxxxx]",
    "title": "⚠️ Expiry Warning",
    "body": "Apples and Whole Milk expire in 48 hours!",
    "sound": "default",
    "data": { "screen": "radar", "household_id": "abc-123" }
  }
]
```

Expo automatically negotiates with Apple APNs and Google FCM to deliver the push notification.

---

## 4. Alternatives Considered

### Alternative A: Direct APNs & FCM Dual Integration
- **Evaluation**: Backend directly connects to Apple's HTTP/2 APNs endpoints using `.p8` keys and Google's FCM v1 REST API using Google OAuth tokens.
- **Rejection Rationale**: Substantial operational complexity. Maintaining two separate protocol clients, credential rotation schedules, error code mappings, and device token formats in a Python backend adds significant ongoing maintenance overhead with zero user-facing benefit.

### Alternative B: Third-Party Customer Engagement Platforms (OneSignal / Braze)
- **Evaluation**: Incorporating heavy marketing push platforms.
- **Rejection Rationale**: Adds proprietary native SDK bloat to the mobile app, introduces third-party user data privacy tracking concerns, and incurs monthly subscription costs.

---

## 5. Consequences & Tradeoffs

### Positive Consequences
- **Single Backend Endpoint**: One unified HTTP request delivers notifications to all iOS and Android devices in a household.
- **Automatic Token Receipt Checking**: Expo provides a ticket and receipt verification API to identify uninstalled apps or invalid tokens.
- **Zero APNs/FCM Backend Secrets**: Certificate and key management is handled securely within EAS configuration.

### Negative Consequences & Mitigation
- **Third-Party Relay Dependency**: Notification delivery depends on Expo's push relay availability.
  - *Mitigation*: Push notifications are a secondary convenience channel. The in-app Expiry Radar dashboard is the primary source of truth, ensuring users never miss expiring items when actively using the app.
