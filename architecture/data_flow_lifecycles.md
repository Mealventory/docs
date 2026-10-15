# End-to-End Data Flow Lifecycles & Sequence Diagrams (DOCS-05)

This document provides detailed sequence diagrams and technical lifecycles for Mealventory's core cross-service workflows:
1. **Multimodal Receipt Ingestion & Inventory Stacking**
2. **Daily Expiry Risk Evaluation & Push Notification Cron**
3. **Expiry-Weighted Recipe Recommendation & Cook Deduction**

---

## 🧾 1. Receipt Ingestion & Duplicate Item Stacking Flow

The receipt ingestion flow processes camera captures of paper grocery receipts, parses line items via OCR, presents an interactive human-in-the-loop review sheet, and stacks identical items in the pantry database without creating duplicates.

```mermaid
sequenceDiagram
    autonumber
    actor User as Household Shopper
    participant App as Mobile Client (Expo)
    participant Backend as Backend API (FastAPI)
    participant AI as AI Vision Service
    participant GVision as Google Cloud Vision
    participant DB as PostgreSQL Database

    User->>App: Photograph grocery receipt
    App->>App: Validate MIME type & file size (< 8MB)
    App->>Backend: POST /api/v1/scan/upload (image bytes, mode='receipt')
    Note over Backend,AI: Internal Microservice Relay
    Backend->>AI: POST /scan/ (mode='receipt', multipart form)
    AI->>AI: EXIF transpose & contrast normalization
    AI->>GVision: ImageAnnotatorClient.text_detection(image_bytes)
    GVision-->>AI: Raw Text Annotations & Word Coordinates
    AI->>AI: Parse line items, extract prices, normalize food names
    AI->>AI: Calibrate confidence & evaluate needs_review
    AI-->>Backend: 200 OK (Typed ScanResponse JSON)
    Backend-->>App: 200 OK (ScanReview Payload)

    Note over App,User: Human-in-the-Loop Review
    App->>User: Display AI Review BottomSheet (Items, Prices, Expiry)
    User->>App: Verify/Adjust quantities, tap "Save to Inventory"
    
    App->>Backend: POST /api/v1/households/{id}/inventory/batch (items array)
    Backend->>DB: BEGIN TRANSACTION
    Backend->>DB: Query active candidate items matching (name, location, unit, expiry)
    Note over Backend,DB: Stacking Logic: Match candidate in same household
    alt Candidate Match Exists
        Backend->>DB: UPDATE inventory_items SET quantity = quantity + delta WHERE id = candidate.id
    else No Match
        Backend->>DB: INSERT INTO inventory_items (household_id, name, quantity, unit, ...)
    end
    Backend->>DB: COMMIT TRANSACTION
    DB-->>Backend: Batch Saved Successfully
    Backend-->>App: 201 Created (Consolidated Inventory Records)
    App->>App: Optimistic React Query cache update (No layout shift)
    App->>User: Display updated Pantry list with stacked quantities
```

---

## 🔔 2. Daily Expiry Risk Evaluation & Push Notification Cron Flow

Mealventory scans household inventory daily to alert families before perishable groceries expire, reducing domestic waste.

```mermaid
sequenceDiagram
    autonumber
    participant Cron as Cloud Scheduler / Daily Cron
    participant Backend as Backend Core Service
    participant DB as PostgreSQL Database
    participant ExpoPush as Expo Push Gateway
    participant APNS as Apple APNs / Google FCM
    actor Device as User Smartphone

    Cron->>Backend: POST /api/v1/notifications/trigger-expiry-checks (Cron Secret Header)
    Backend->>Backend: Verify authorization header
    Backend->>DB: Query active items WHERE expiry_date <= CURRENT_DATE + INTERVAL '2 days'
    DB-->>Backend: Return expiring items grouped by household_id
    
    loop For Each Household with Expiring Groceries
        Backend->>DB: SELECT push_token FROM user_devices WHERE household_id = household.id
        DB-->>Backend: Active device push tokens
        
        Backend->>Backend: Format payload: "⚠️ Strawberries & Milk expire in 48 hours!"
        Backend->>ExpoPush: POST https://exp.host/--/api/v2/push/send (messages batch)
        ExpoPush-->>Backend: 200 OK (ticket IDs returned)
        
        ExpoPush->>APNS: Forward to native notification relay
        APNS->>Device: Deliver push notification banner
    end

    Device->>Device: Display lock screen banner
    Device-->>Device: User taps notification -> Deep links into Expiry Radar screen
```

---

## 🍳 3. Expiry-Weighted Recipe Recommendation & Cook Deduction Flow

Mealventory analyzes ingredients nearing expiration and prompts an LLM to design recipes that consume those items first. When cooked, the exact ingredient quantities are atomically deducted from the pantry.

```mermaid
sequenceDiagram
    autonumber
    actor User as Household Cook
    participant App as Mobile Client
    participant Backend as Backend API
    participant DB as PostgreSQL Database
    participant LLM as OpenRouter / AI LLM Provider

    User->>App: Tap "Generate Recipes for My Pantry"
    App->>Backend: GET /api/v1/households/{id}/recipes/recommendations
    Backend->>DB: SELECT * FROM inventory_items WHERE household_id = id ORDER BY expiry_date ASC
    DB-->>Backend: Ranked pantry list (e.g., [Apples (expires tomorrow), Milk, Bread])
    
    Backend->>LLM: POST /chat/completions (Prompt: "Generate recipe using [Apples, Milk, Bread]")
    LLM-->>Backend: Structured Recipe JSON (Title, Ingredients, Instructions, Missing items)
    Backend-->>App: 200 OK (Recipe Recommendations)
    
    App->>User: Display "Apple Cinnamon French Toast" (3 of 4 in stock)
    User->>App: Tap "Add Missing Ingredients to Shopping List"
    App->>Backend: POST /api/v1/households/{id}/shopping (item: "Cinnamon")
    Backend->>DB: INSERT INTO shopping_list_items ...
    DB-->>Backend: Inserted
    Backend-->>App: 201 Created (Shopping list updated)
    
    User->>App: Tap "Cook This Meal"
    App->>Backend: POST /api/v1/households/{id}/recipes/{recipe_id}/cook
    Backend->>DB: BEGIN TRANSACTION
    loop For Each Recipe Ingredient
        Backend->>DB: UPDATE inventory_items SET quantity = quantity - required_qty WHERE id = item.id
        Note over Backend,DB: If remaining quantity <= 0, update status = 'consumed'
    end
    Backend->>DB: COMMIT TRANSACTION
    DB-->>Backend: Transaction Committed
    Backend-->>App: 200 OK (Inventory deducted)
    App->>User: Congratulate user & refresh pantry quantities
```
