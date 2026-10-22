# Technical Decision Records (TDR) Architecture Catalog (DOCS-02)

[Documentation home](../README.md)

This directory documents the foundational architectural and design decisions for the Mealventory platform. Each Technical Decision Record (TDR/ADR) outlines the technical context, decision drivers, chosen approach, alternatives evaluated, and operational consequences.

---

## 📚 TDR Catalog

| TDR | Title | Status | Scope |
|---|---|---|---|
| [**TDR-001**](TDR-001-multi-repo-architecture.md) | Multi-Repository Architecture | `Accepted` | Repository structure, CI/CD pipelines, and cross-repo dependency isolation |
| [**TDR-002**](TDR-002-supabase-rls-tenant-isolation.md) | Supabase PostgreSQL Row-Level Security (RLS) Tenant Isolation | `Accepted` | Multi-tenant security, zero-trust data boundaries, and authorization |
| [**TDR-003**](TDR-003-tanstack-query-mmkv-offline.md) | TanStack Query & MMKV for Offline-Resilient State | `Accepted` | Mobile state management, hydration speed, and offline query caching |
| [**TDR-004**](TDR-004-gemini-structured-vision-vs-yolo.md) | Multimodal Cloud Vision & OCR vs Edge YOLO Models | `Accepted` | Computer vision, receipt OCR parsing, and calibrated confidence scoring |
| [**TDR-005**](TDR-005-expo-push-notification-relay.md) | Expo Push Notification Gateway vs Direct APNs/FCM | `Accepted` | Background notifications, cross-platform token relays, and expiry alerts |
