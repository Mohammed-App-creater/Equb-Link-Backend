# API Endpoints for Equb Mobile App

This document outlines the API endpoints required for the Equb Mobile application, based on the existing pages and components.

## Base URL
`https://api.mesobequb.com/v1` (Example)

## 1. Authentication & Onboarding

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| **POST** | `/auth/register` | Register a new user | `{ fullName, email, phone, password }` |
| **POST** | `/auth/login` | Login user | `{ phone, password }` |
| **POST** | `/auth/verify-otp` | Verify OTP (if enabled) | `{ phone, otp }` |
| **POST** | `/auth/forgot-password` | Request password reset | `{ phone }` |
| **POST** | `/auth/reset-password` | Reset password | `{ phone, otp, newPassword }` |
| **POST** | `/auth/upload-kyc` | Upload ID/Profile Image | `FormData { file }` |

## 2. User Profile

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| **GET** | `/user/profile` | Get current user profile | - |
| **PUT** | `/user/profile` | Update profile info | `{ fullName, email, avatar }` |
| **PUT** | `/user/password` | Change password | `{ oldPassword, newPassword }` |
| **GET** | `/user/settings` | Get user settings (notifications, etc) | - |
| **PUT** | `/user/settings` | Update settings | `{ pushEnabled, emailEnabled }` |

## 3. Home & Dashboard

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| **GET** | `/home/summary` | Get balance & stats | - |
| **GET** | `/home/modules` | Get quick action modules | - |
| **GET** | `/home/top-categories`| Get featured categories | - |
| **GET** | `/home/notifications` | Get recent notifications | - |

## 4. Browse & Categories

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| **GET** | `/categories` | List all categories | - |
| **GET** | `/categories/{id}/subcategories` | Get subcategories | - |
| **GET** | `/categories/{id}/equbs` | List equbs in category | - |

## 5. Equb Management (Joining & Details)

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| **GET** | `/equbs/{id}` | Get equb details | - |
| **POST** | `/equbs/{id}/join` | Join an equb | `{ agreeTerms: true }` |
| **GET** | `/equbs/{id}/members` | List public members (optional) | - |

## 6. My Equbs (Active & History)

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| **GET** | `/my-equbs` | List user's equbs | `?status=active|completed` |
| **GET** | `/my-equbs/{id}` | Get specific equb details | - |
| **GET** | `/my-equbs/{id}/rounds` | Get round schedule/winners | - |
| **GET** | `/my-equbs/{id}/group` | Get group chat/info | - |

## 7. Payments

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| **GET** | `/payments/history` | Get transaction history | `?limit=20` |
| **POST** | `/payments/initiate` | Initiate payment | `{ equbId, amount, method }` |
| **POST** | `/payments/verify/{id}`| Verify payment status | - |

## 8. Winners & Lottery

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| **GET** | `/winners` | Get recent winners | `?limit=10` |
| **GET** | `/lottery/status` | Get current lottery status | - |

## 9. Support & Notifications

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| **GET** | `/notifications` | List all notifications | - |
| **POST** | `/notifications/read` | Mark as read | `{ ids: [] }` |
| **GET** | `/support/faq` | Get FAQs | - |
| **POST** | `/support/contact` | Send support message | `{ subject, message }` |
