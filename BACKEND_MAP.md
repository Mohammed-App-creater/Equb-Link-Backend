# BACKEND MAP

## Overview
This is the backend for **Equb App** — a digital platform for Ethiopian *equb* (rotating savings & credit groups). It serves three classes of users:

- **Customers** — community members who join equbs, pay round contributions, and receive payouts.
- **Equb Admins (Owners)** — users who create and operate equbs: configure rules, approve members and payments, run the lottery draw, and manage payout bank accounts.
- **System Admins** — platform staff who manage adverts, FAQs, equb types/categories, and have global oversight.

Domain coverage: equb lifecycle (create, join, contribute, draw, payout), member & payment approvals, lottery rounds, multi-account payout setup, Chapa online payments (Ethiopian payment gateway), notifications, support tickets, and adverts/FAQs/CMS content.

## Tech Stack
- **Framework:** Django 5.2 + Django REST Framework 3.16
- **Database:** SQLite (`db.sqlite3` at the project root). A commented-out MySQL config is in [equb/settings.py](equb/settings.py). PostgreSQL is **not** configured.
- **Auth:** DRF `TokenAuthentication` (via `rest_framework.authtoken`). No JWT, no session-based API auth. Custom user model `user.Account` keyed on phone number.
- **Dev environment:** No Docker / docker-compose present. Local Python venv (`myenv/`). Production deploy is a shell script: [.scripts/deploy.sh](.scripts/deploy.sh) (clones repo, creates venv, installs requirements, runs migrations, restarts gunicorn + nginx). CI/CD: [.github/workflows/deploy.yml](.github/workflows/deploy.yml).
- **Python version:** Not pinned in repo; Django 5.2 requires Python ≥ 3.10.
- **Key dependencies** ([requirements.txt](requirements.txt)):
  - `Django==5.2`, `djangorestframework==3.16.0`
  - `django-cors-headers==4.7.0`, `django-filter==25.1`
  - `drf-spectacular==0.28.0` (OpenAPI schema + Swagger/Redoc)
  - `django-cleanup==9.0.0` (auto-delete orphaned files)
  - `pillow==11.1.0` (ImageField support)
  - `wagtail`, `django-jazzmin`, `django-admin-interface`, `django-colorfield` (admin UI / CMS — installed but only Jazzmin/admin-interface/colorfield are wired into `INSTALLED_APPS`; Wagtail urls are commented out)
  - **Not in requirements.txt but imported:** `pandas` (used in [api/owner_panel/views.py](api/owner_panel/views.py) for Excel export — missing dependency), `requests` (Chapa API calls)

## Project Structure
```
/
├── api/                          # All Django apps live under here (added to sys.path in settings.py)
│   ├── advert/                   # Adverts, FAQs, Testimonials, Feedback
│   ├── equbApp/                  # Core equb domain: equbs, members, payments, lottery, notifications, Chapa
│   ├── owner_panel/              # Equb-owner-facing CRUD: dashboard, members/payments approval, rounds, exports
│   └── user/                     # Custom user model (phone-based) + signup/login + profile
├── equb/                         # Django project package
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates/
│   └── payment_success.html      # Chapa return_url landing page
├── media/                        # User-uploaded files (profile photos, receipts, advert/category images)
├── myenv/                        # Local virtualenv (gitignored expected)
├── .github/workflows/deploy.yml  # CI deploy
├── .scripts/deploy.sh            # Server-side deploy script
├── manage.py
├── requirements.txt
├── db.sqlite3
├── API_ENDPOINTS.md              # Existing endpoint notes
└── alementest.rest                # REST client request collection
```

Each Django app follows the standard layout: `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `apps.py`, `tests.py`, `migrations/`. `equbApp` additionally has `pagination.py` and `bank_constants.py`. `owner_panel` and `user` add `permissions.py`.

## Django Apps

### 1. `user` — Authentication & Profiles
Custom user model and role-based profiles. Phone is the username field; Ethiopian phone format is enforced via regex.

**Models** ([api/user/models.py](api/user/models.py)):
- `Account` (AUTH_USER_MODEL) — phone-based user with three role flags: `is_admin`, `is_customer`, `is_equb_admin`. `MyAccountManager` exposes `create_customer`, `create_admin`, `create_equb_admin`, `create_superuser`.
- `Admin` — system-admin profile (UUID id, OneToOne to Account, name, phone, photo).
- `Customer` — customer profile + referral system (`referral_code`, `referred_by`, `referral_point`).
- `EqubAdmin` — equb-owner profile; auto-flips `user.is_equb_admin=True` on save.

**Serializers** ([api/user/serializers.py](api/user/serializers.py)):
- `UserSerializer` — full Account; `AdminSerializer` / `AdminPostSerializer` — read-with-nested-user / write-with-PK.
- `CustomerSerializer` / `CustomerDataSerializer` — same pattern for Customer.
- `EqubAdminSerializer` / `EqubAdminDataSerializer` — same pattern for EqubAdmin.
- `ProfileUpdateSerializer` — updates `email` (Account) and `photo` (whichever profile exists).
- `ChangePasswordSerializer` — old/new/confirm password validation.

**Views** ([api/user/views.py](api/user/views.py)):
- `signup` (FBV, POST) — universal signup; routes by `role` to customer/admin/equb_admin creation.
- `customer_signup` (FBV, POST, AllowAny) — customer-only signup with auto-generated referral code.
- `create_admin` / `create_equb_admin` (FBV, POST, IsAuthenticated + IsAdminUser) — superadmin-only creation flows.
- `login` (FBV, POST) — phone+password → token; serializes by role.
- `loginWithToken` (FBV, POST) — same as `login` but returns key as `token` (vs. `access_token`); used by mobile/owner client.
- `me` (FBV, GET, IsAuthenticated) — current user profile by role.
- `UpdateProfileView` (CBV, APIView, PUT) — partial profile update.
- `ChangePasswordView` (CBV, APIView, POST) — change password.

**URLs** ([api/user/urls.py](api/user/urls.py)) — mounted at `""` (root):
- `POST /signup`
- `POST /login`
- `GET  /me/`
- `POST /api/owner/login`
- `POST /signup/customer/`
- `POST /admin/create/`
- `POST /equb-admin/create/`
- `PUT  /profile/update/`
- `POST /profile/change-password/`

---

### 2. `advert` — Adverts, FAQs, Testimonials, Feedback
Marketing/CMS-style content surfaced to customers and managed by admins.

**Models** ([api/advert/models.py](api/advert/models.py)):
- `Advert` — homepage banners (UUID id, title, three images).
- `Testimonial` — name, position, image, description.
- `Feedback` — visitor contact-form submission (first/last name, email, message).
- `FAQ` — question/answer with `is_active` toggle and timestamps.

**Serializers** ([api/advert/serializers.py](api/advert/serializers.py)):
- `AdevertSerializer`, `TestimonialSerializer`, `FeedbackSerializer`, `FAQSerializer` — all `ModelSerializer` with `fields = "__all__"`.

**Views** ([api/advert/views.py](api/advert/views.py)) — all FBVs:
- `AdvertGetPostAdmin` (GET/POST, IsAdmin) — list + create adverts.
- `AdvertGetDeleteUpdateAdmin` (GET/PUT/DELETE, IsAdmin) — by UUID.
- `AdvertGetPublic` (GET, IsAuthenticated) — flattens `images`/`images2`/`images3` into one absolute-URL array.
- `faq_list_create_admin` (GET/POST, IsAdmin), `faq_detail_admin` (GET/PUT/DELETE, IsAdmin).
- `faq_list` (GET, public) — only active FAQs.

**URLs** ([api/advert/urls.py](api/advert/urls.py)) — mounted at `""`:
- `GET/POST /advert/`
- `GET/PUT/DELETE /advert/<uuid:id>/`
- `GET /advert_public/`
- `GET/POST /admin_faqs/`
- `GET/PUT/DELETE /admin_faqs/<int:id>/`
- `GET /faqs/`

---

### 3. `equbApp` — Core Equb Domain
The largest app. Owns the equb lifecycle, members, payments, lottery winners, notifications, support tickets, and Chapa integration.

**Models** ([api/equbApp/models.py](api/equbApp/models.py)):
- `UUIDModel`, `TimeStampedModel` — abstract bases (defined but most concrete models redeclare fields manually).
- `EqubType` — categorical type of equb (e.g. weekly, monthly).
- `EqubCategory` — category with image, description, `is_favorite` flag.
- `OwnerBankAccount` — owner's saved payout account (bank_code from `ETHIOPIAN_BANKS`, account number/holder, optional label). Unique on `(owner, bank_code, account_number)`.
- `Equb` — the equb itself: owner FK, category FK, equb_type FK, dates, rules, payout system (`first_come_first_serve` | `random`), `total_members`, `contribution_amount`, computed `total_payout` & `total_equb_value`, status (`draft`/`active`/`completed`/`cancelled`), M2M to `OwnerBankAccount` for payouts.
- `EqubMember` — user's membership in an equb with `status` (pending/active/inactive/removed), `payment_status` (pending/paid), `has_received_payout`. Unique on `(user, equb)`.
- `Payment` — contribution record per member per round; status pending/completed/rejected, `approved_by`, `approved_at`, `rejected_reason`, `receipt_image`. Unique on `(equb_member, round_number)`.
- `LotteryWinner` — winner per equb per round. Unique on `(equb, round_number)`.
- `Notification` — per-user notifications (`notif_type`, `message`, `is_read`).
- `SupportTicket` — open/in_progress/resolved tickets.

**`bank_constants.py`** — `ETHIOPIAN_BANKS` list (code, name, logo_url) + helpers `get_bank_by_code`, `is_valid_bank_code`.

**Serializers** ([api/equbApp/serializers.py](api/equbApp/serializers.py)):
- `EqubTypeSerializer`, `EqubCategorySerializer`, `EqubCategoryWithCountSerializer` (adds `total_equbs`).
- `OwnerBankAccountPublicSerializer` — public read view (bank name + logo resolved from constants).
- `EqubSerializer` — full equb with nested public bank accounts.
- `UserPublicSerializer` — id/phone/name (resolves name from whichever profile exists).
- `EqubMemberSerializer` — nested user, joined_at, status; `EqubMemberCreateSerializer` — capacity & duplicate validation.
- `PaymentSerializer` — validates duplicate-round and amount-matches-contribution.
- `LotteryWinnerSerializer` — validates one-winner-per-round.
- `NotificationSerializer`, `SupportTicketSerializer`.
- `JoinEqubSerializer` — validates accept-terms join with full back-payment.

**Views** ([api/equbApp/views.py](api/equbApp/views.py)) — virtually all FBVs. Two route families: `admin/*` (system-admin CRUD) and customer/mobile flows. Includes a local `notify_admins` helper that bulk-creates notifications for all admin/equb-admin users.

System-admin CRUD pairs (each is `list_create` + `detail` GET/PUT/DELETE, `IsAdminUser`):
- `equb_type_list_create_admin` / `equb_type_detail_admin`
- `equb_category_list_create_admin` / `equb_category_detail_admin`
- `equb_list_create_admin` / `equb_detail_admin`
- `equb_member_list_create_admin` / `equb_member_detail_admin`
- `payment_list_create_admin` / `payment_detail_admin`
- `lottery_winner_list_create_admin` / `lottery_winner_detail_admin`
- `notification_list_create_admin` / `notification_detail_admin`
- `support_ticket_list_create_admin` / `support_ticket_detail_admin`

Customer / mobile views:
- `equb_categories_with_count` — categories ordered favorites-first with active-equb count.
- `get_active_equbs_by_category` — all categories with their active equbs (paginated).
- `get_active_equbs_by_category_id` — equbs for one category, with members count, total/current round.
- `get_active_equbs_by_type_id` — equbs filtered by EqubType.
- `equb_members_list` — list members of an equb.
- `equb_join_cost` — calculate back-payment required to join an in-progress equb.
- `join_equb_initial` — join before round 1; pay round 0; pending admin approval.
- `join_equb` — join after start; pay all completed rounds at once.
- `join_equb_chapa` — join with Chapa-initialized payment.
- `equb_detail` — single equb with members/winners/round progress.
- `customer_dashboard` — user's memberships, contributions, payment history, winnings, notifications.
- `pay_equb_contribution` — manual receipt upload OR Chapa init (branches on `payment_method`).
- `pay_equb_contribution_chapa` — dedicated Chapa contribution flow.
- `payment_success` — renders [templates/payment_success.html](templates/payment_success.html).
- `admin_approve_payment` — approve/reject pending payment.
- `approve_payment` (legacy, IsAuthenticated) — separate approve helper.
- `list_pending_payments` — admin queue.
- `customer_notifications` — current-user notifications, paginated.
- `mark_notification_as_read` — bulk-mark-read by ID list.
- `initialize_chapa_payment` / `verify_chapa_payment` / `chapa_callback` — Chapa lifecycle.

**URLs** ([api/equbApp/urls.py](api/equbApp/urls.py)) — mounted at `""`. See API Overview below for full list.

---

### 4. `owner_panel` — Equb Owner Dashboard
Owner-facing CRUD/operations layer, gated by the custom `IsEqubOwner` permission.

**Models** ([api/owner_panel/models.py](api/owner_panel/models.py)):
- `AuditLog` — owner action trail (user, action, target, timestamp, JSON `meta`).
- `LotteryRound` — round bookkeeping per equb (round number, winner FK to user, seed, drawn_at, is_paid). Unique on `(equb, round)`.

**Permissions** ([api/owner_panel/permissions.py](api/owner_panel/permissions.py)):
- `IsEqubOwner` — authenticated AND `request.user.is_equb_admin`. Object-level: `obj.owner == request.user` or `obj.equb.owner == request.user`.

**Serializers** ([api/owner_panel/serializers.py](api/owner_panel/serializers.py)):
- `OwnerBankAccountSerializer` — write/read with `linked_equbs`, bank name/logo, validation.
- `OwnerEqubSerializer` — write category/equb_type as PKs, read as nested detail; manages `payout_bank_account_ids` M2M sync (rejects accounts not owned by the owner).
- `OwnerMemberSerializer` — flattened member with resolved name, phone, has_paid.
- `OwnerPaymentSerializer` — full payment, status/approver fields read-only.
- `OwnerRoundSerializer` — frontend-shaped fields (`roundNumber`, `drawDate`, `winnerName`, derived `status`).

**Views** ([api/owner_panel/views.py](api/owner_panel/views.py)) — primarily class-based (generics + APIView):
- `EthiopianBankListView` (APIView, AllowAny) — picker list of banks/wallets.
- `OwnerBankAccountListCreateView` / `OwnerBankAccountDetailView` (generics) — owner's bank accounts CRUD.
- `OwnerEqubListCreateView` / `OwnerEqubDetailView` (generics) — owner's equbs CRUD; `destroy` blocks deletion if any payments exist.
- `OwnerEqubBankingView` (APIView) — combined banking summary for one equb.
- `OwnerMemberListView` (generic ListAPIView) — members for one equb.
- `OwnerMemberApproveView` / `OwnerMemberRejectView` (APIView, POST) — approve/reject + write AuditLog.
- `OwnerPaymentListView` — payments per equb with `?status=` filter.
- `OwnerPaymentApproveView` / `OwnerPaymentRejectView` — set status, stamp approver, log.
- `OwnerDashboardView` — totals: equbs, pending members, pending payments.
- `OwnerRoundListView` — auto-creates the next pending round if none exists, returns all rounds.
- `OwnerDrawView` (POST) — runs deterministic SHA-256-seeded draw across paid eligible members.
- `OwnerPayoutView` (POST) — marks round paid + AuditLog.
- `OwnerExportView` (GET, `?type=payments`) — Excel export via pandas.
- `EqubReportSummaryView` — expected/collected/pending amounts, members paid.
- `EqubActivityView` — AuditLog entries for the equb's user set, mapped to a frontend ActivityLog shape.
- `EqubTypesView`, `EqubCategoriesView` — dropdown sources for the owner UI.

**URLs** ([api/owner_panel/urls.py](api/owner_panel/urls.py)) — mounted at both `api/owner/` AND `owner/` (mobile / older clients). All routes appear under both prefixes.

## Authentication & Permissions

**Auth backend.** [equb/settings.py](equb/settings.py) sets DRF default to `TokenAuthentication`. `rest_framework.authtoken` is in `INSTALLED_APPS`. Tokens are issued on signup/login and on every login the previous token is deleted and replaced (see [api/user/views.py](api/user/views.py)). Custom user model: `AUTH_USER_MODEL = "user.Account"`, keyed on phone (Ethiopian regex enforced).

**Roles.** Three boolean flags on `Account`: `is_admin` (system admin), `is_customer`, `is_equb_admin` (equb owner). Plus standard `is_staff` / `is_superuser`.

**Permission classes.**
- DRF built-ins: `AllowAny`, `IsAuthenticated`, `IsAdminUser` (note: DRF's built-in `IsAdminUser` checks `is_staff`).
- Custom in [api/user/permissions.py](api/user/permissions.py): `IsAdminUser` (checks `request.user.is_admin`), `IsCustomerUser`, `IsEqubAdminUser`, `IsEqubAdminOrIsCustomerUser`, `IsEqubAdminOrIsAdminUser`, `IsCustomerOrIsAdminUser`. Note: the custom `IsEqubAdminUser` references `is_equbadmin` (typo) and will not match `is_equb_admin`.
- Custom in [api/owner_panel/permissions.py](api/owner_panel/permissions.py): `IsEqubOwner` — authenticated + `is_equb_admin` + object-level `owner` match.

**No auth middleware customization.** Token must be sent as `Authorization: Token <key>`.

## API Overview

| Method | URL | View | Description |
|---|---|---|---|
| POST | `/signup` | `signup` | Universal signup (role: customer\|admin\|equb_admin) |
| POST | `/login` | `login` | Login → `access_token` |
| POST | `/api/owner/login` | `loginWithToken` | Login → `token` (owner/mobile client) |
| GET  | `/me/` | `me` | Current user profile by role |
| POST | `/signup/customer/` | `customer_signup` | Customer-only signup w/ referral code |
| POST | `/admin/create/` | `create_admin` | Superadmin creates admin |
| POST | `/equb-admin/create/` | `create_equb_admin` | Superadmin creates equb admin |
| PUT  | `/profile/update/` | `UpdateProfileView` | Update email + photo |
| POST | `/profile/change-password/` | `ChangePasswordView` | Change password |
| GET/POST | `/advert/` | `AdvertGetPostAdmin` | List/create adverts (admin) |
| GET/PUT/DELETE | `/advert/<uuid:id>/` | `AdvertGetDeleteUpdateAdmin` | Advert detail (admin) |
| GET | `/advert_public/` | `AdvertGetPublic` | Public advert list (auth) |
| GET/POST | `/admin_faqs/` | `faq_list_create_admin` | FAQ admin list/create |
| GET/PUT/DELETE | `/admin_faqs/<int:id>/` | `faq_detail_admin` | FAQ admin detail |
| GET | `/faqs/` | `faq_list` | Public active FAQs |
| GET/POST | `/admin/equb-types/` | `equb_type_list_create_admin` | EqubType admin |
| GET/PUT/DELETE | `/admin/equb-types/<uuid:id>/` | `equb_type_detail_admin` | EqubType detail |
| GET/POST | `/admin/equb-categories/` | `equb_category_list_create_admin` | EqubCategory admin |
| GET/PUT/DELETE | `/admin/equb-categories/<uuid:id>/` | `equb_category_detail_admin` | EqubCategory detail |
| GET/POST | `/admin/equbs/` | `equb_list_create_admin` | Equb admin list/create |
| GET/PUT/DELETE | `/admin/equbs/<uuid:id>/` | `equb_detail_admin` | Equb admin detail |
| GET/POST | `/admin/equb-members/` | `equb_member_list_create_admin` | EqubMember admin (filters: equb, user) |
| GET/PUT/DELETE | `/admin/equb-members/<uuid:id>/` | `equb_member_detail_admin` | EqubMember detail |
| GET/POST | `/admin/payments/` | `payment_list_create_admin` | Payment admin |
| GET/PUT/DELETE | `/admin/payments/<uuid:id>/` | `payment_detail_admin` | Payment detail |
| POST | `/admin/payments/<uuid:payment_id>/approve/` | `admin_approve_payment` | Approve/reject payment |
| GET/POST | `/admin/lottery-winners/` | `lottery_winner_list_create_admin` | LotteryWinner admin |
| GET/PUT/DELETE | `/admin/lottery-winners/<uuid:id>/` | `lottery_winner_detail_admin` | LotteryWinner detail |
| GET/POST | `/admin/notifications/` | `notification_list_create_admin` | Notification admin |
| GET/PUT/DELETE | `/admin/notifications/<uuid:id>/` | `notification_detail_admin` | Notification detail |
| GET/POST | `/admin/support-tickets/` | `support_ticket_list_create_admin` | SupportTicket admin |
| GET/PUT/DELETE | `/admin/support-tickets/<uuid:id>/` | `support_ticket_detail_admin` | SupportTicket detail |
| GET | `/mobile_equb_categories/` | `equb_categories_with_count` | Categories + active count |
| GET | `/mobile_equbs_by_category/` | `get_active_equbs_by_category` | All categories + active equbs |
| GET | `/all_equb_by_category_id/<uuid:category_id>/` | `get_active_equbs_by_category_id` | Active equbs for category |
| GET | `/all_equb_by_equbs_type/<uuid:equb_type_id>/` | `get_active_equbs_by_type_id` | Active equbs for type |
| GET | `/equb_join_cost/<uuid:equb_id>/` | `equb_join_cost` | Cost to join in-progress equb |
| POST | `/equbs/<uuid:equb_id>/join/` | `join_equb` | Join in-progress (back-pay) |
| POST | `/equbs/<uuid:equb_id>/join-initial/` | `join_equb_initial` | Join before start (round 0) |
| POST | `/equbs/<uuid:equb_id>/join-chapa/` | `join_equb_chapa` | Join + pay via Chapa |
| GET | `/equbs/<uuid:id>/` | `equb_detail` | Equb full detail |
| GET | `/customer/dashboard/` | `customer_dashboard` | User dashboard |
| POST | `/equbs/<uuid:equb_id>/pay/` | `pay_equb_contribution` | Pay current round (manual or Chapa) |
| POST | `/equbs/<uuid:equb_id>/pay-contribution-chapa/` | `pay_equb_contribution_chapa` | Pay current round via Chapa |
| GET | `/payment-success/` | `payment_success` | Chapa return_url page |
| GET | `/payment/pending-list/` | `list_pending_payments` | Pending payments list |
| GET | `/notifications/` | `customer_notifications` | User notifications |
| GET | `/api/owner/notifications/` | `customer_notifications` | Same (owner alias) |
| POST | `/notifications/read/` | `mark_notification_as_read` | Mark notifications read |
| POST | `/api/owner/notifications/read/` | `mark_notification_as_read` | Same (owner alias) |
| POST | `/chapa/initialize/` | `initialize_chapa_payment` | Init Chapa payment (RN client) |
| GET | `/chapa/verify/<str:tx_ref>/` | `verify_chapa_payment` | Verify Chapa transaction |
| GET/POST | `/chapa/callback/` | `chapa_callback` | Chapa webhook |
| GET | `/api/owner/banks/` (and `/owner/banks/`) | `EthiopianBankListView` | Predefined banks (AllowAny) |
| GET/POST | `/api/owner/bank-accounts/` | `OwnerBankAccountListCreateView` | Owner bank accounts |
| GET/PUT/PATCH/DELETE | `/api/owner/bank-accounts/<uuid:pk>/` | `OwnerBankAccountDetailView` | Owner bank account detail |
| GET/POST | `/api/owner/equbs/` | `OwnerEqubListCreateView` | Owner's equbs |
| GET | `/api/owner/equbs/<uuid:equb_id>/banking/` | `OwnerEqubBankingView` | Equb banking summary |
| GET/PUT/PATCH/DELETE | `/api/owner/equbs/<uuid:pk>/` | `OwnerEqubDetailView` | Owner equb detail |
| GET | `/api/owner/equbs/<uuid:equb_id>/members/` | `OwnerMemberListView` | Members in equb |
| POST | `/api/owner/equbs/<uuid:equb_id>/members/<uuid:member_id>/approve/` | `OwnerMemberApproveView` | Approve member |
| POST | `/api/owner/equbs/<uuid:equb_id>/members/<uuid:member_id>/reject/` | `OwnerMemberRejectView` | Reject member |
| GET | `/api/owner/equbs/<uuid:equb_id>/payments/` | `OwnerPaymentListView` | Payments in equb |
| POST | `/api/owner/equbs/<uuid:equb_id>/payments/<uuid:payment_id>/approve/` | `OwnerPaymentApproveView` | Approve payment |
| POST | `/api/owner/equbs/<uuid:equb_id>/payments/<uuid:payment_id>/reject/` | `OwnerPaymentRejectView` | Reject payment |
| GET | `/api/owner/dashboard/` | `OwnerDashboardView` | Owner dashboard counts |
| GET | `/api/owner/equbs/<uuid:equb_id>/rounds/` | `OwnerRoundListView` | Rounds (auto-creates next) |
| POST | `/api/owner/equbs/<uuid:equb_id>/rounds/<int:round>/draw/` | `OwnerDrawView` | Run lottery draw |
| POST | `/api/owner/equbs/<uuid:equb_id>/rounds/<int:round>/payout/` | `OwnerPayoutView` | Mark round paid out |
| GET | `/api/owner/equbs/<uuid:equb_id>/export/` | `OwnerExportView` | Excel export (`?type=payments`) |
| GET | `/api/owner/equbs/<uuid:equb_id>/reports/` | `EqubReportSummaryView` | Report totals |
| GET | `/api/owner/equbs/<uuid:equb_id>/activity/` | `EqubActivityView` | Activity logs |
| GET | `/api/owner/equbs/types/` | `EqubTypesView` | Equb types (owner picker) |
| GET | `/api/owner/equbs/categories/` | `EqubCategoriesView` | Equb categories (owner picker) |
| GET | `/admin/` | Django admin | Jazzmin/admin-interface UI |
| GET | `/api/schema/` | `SpectacularAPIView` | OpenAPI schema |
| GET | `/api/schema/docs/` | `SpectacularSwaggerView` | Swagger UI |
| GET | `/api/schema/redoc/` | `SpectacularRedocView` | Redoc UI |

> All `/api/owner/*` routes are also reachable under the bare `/owner/*` prefix (declared twice in [equb/urls.py](equb/urls.py)).

## Environment Variables
**No `.env` or `os.environ.get(...)` reads are used in the project's own code.** The only `os.environ` references in repo source are the standard Django bootstraps:

- [manage.py](manage.py): `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equb.settings')`
- [equb/wsgi.py](equb/wsgi.py): same
- [equb/asgi.py](equb/asgi.py): same

All other configuration is **hard-coded in [equb/settings.py](equb/settings.py)** — including secrets that should be in env vars:

- `SECRET_KEY` — Django secret (literal in settings.py)
- `DEBUG` — `True`
- `ALLOWED_HOSTS` — `["*"]`
- `CORS_ALLOWED_ORIGINS` — explicit list (localhost variants, Vercel admin URL, a couple of LAN/server IPs)
- `DATABASES.default` — SQLite path
- `CHAPA_SECRET_KEY` — Chapa test secret
- `CHAPA_BASE_URL` — Chapa test public key

> No environment-variable layer exists yet. Hardcoded credentials in [equb/settings.py](equb/settings.py) lines 15, 220–221 should be moved to env vars before production.

## Docker Setup
**Not present.** There is no `Dockerfile`, no `docker-compose.yml`, and no Docker references anywhere in the repo. Deployment is bare-metal:

- [.scripts/deploy.sh](.scripts/deploy.sh) — runs on the target server: clones/pulls from GitHub, builds a venv, installs requirements, runs `collectstatic`, `makemigrations`, `migrate`, then restarts `gunicorn` and `nginx` via `systemctl`.
- [.github/workflows/deploy.yml](.github/workflows/deploy.yml) — GitHub Actions workflow that triggers the deploy script.

Local dev: activate `myenv/`, run `python manage.py runserver`.

## Key Conventions

**View style is mixed and inconsistent.**
- `user`, `advert`, `equbApp` rely overwhelmingly on **function-based views** with `@api_view` + `@permission_classes`. The two CBVs in `user` (`UpdateProfileView`, `ChangePasswordView`) are the exception.
- `owner_panel` is the opposite: **class-based** throughout, mostly DRF `generics.ListCreateAPIView`/`RetrieveUpdateDestroyAPIView` with a few `APIView` subclasses for custom actions.

**Admin CRUD pattern in `equbApp`.** Each domain model has the same handwritten pair: `<model>_list_create_admin` (GET/POST) + `<model>_detail_admin` (GET/PUT/DELETE), with manual `paginated_response(...)` helper instead of generics. Filters come from query string (`equb`, `user`, `round_number`, `status`).

**Response envelope.** Most endpoints wrap data as `{"data": ..., "message": ...}` (sometimes with extra fields). Not enforced by a renderer — each view does it manually, and the owner panel CBVs do not follow it (they return DRF defaults).

**Serializer style.** Almost every serializer is `ModelSerializer` with `fields = "__all__"`. A few (`EqubMemberSerializer`, `OwnerMemberSerializer`, `OwnerBankAccountPublicSerializer`) explicitly list fields. Validation is done in `validate(...)` on `PaymentSerializer`, `LotteryWinnerSerializer`, `OwnerBankAccountSerializer`, `JoinEqubSerializer`. Two patterns coexist for "write PK / read nested": e.g. `CustomerSerializer` (write) vs. `CustomerDataSerializer` (read).

**No shared base classes/mixins.** Each app's serializers/views live in isolation. No common mixin module, no common pagination class beyond two duplicate `StandardResultsSetPagination` definitions ([api/equbApp/pagination.py](api/equbApp/pagination.py) and an inner duplicate inside [api/equbApp/views.py](api/equbApp/views.py)). DRF default page size is 6 (settings) but ad-hoc pagination uses 10.

**ID strategy.** All domain models use `UUIDField(primary_key=True, default=uuid.uuid4)`. `LotteryRound` is the exception (default integer PK). FAQ also uses an integer PK.

**Migrations.** Standard Django: each app has its own `migrations/` folder. `equbApp` has six migrations reflecting the iterative addition of payment approval fields, owner bank accounts, and the M2M payout-account relationship. No data migrations or squashes.

**Notifications convention.** Domain mutations call `Notification.objects.create(user=...)` for the actor and `notify_admins(message, notif_type)` (a small helper in [api/equbApp/views.py](api/equbApp/views.py)) for staff. Owner-side mutations also write `AuditLog` rows.

**Stale / suspicious code worth flagging.**
- `pandas` is imported by [api/owner_panel/views.py](api/owner_panel/views.py) but is missing from [requirements.txt](requirements.txt) — `OwnerExportView` will crash unless installed manually.
- The custom `IsEqubAdminUser` in [api/user/permissions.py](api/user/permissions.py) checks `is_equbadmin` (no underscore), which doesn't exist on the model (`is_equb_admin` does).
- `OwnerDrawView` filters members with `status="approved"`, but `EqubMember.status` choices are `pending/active/inactive/removed` (no `approved`). The draw will never find members.
- `LotteryWinner.__str__` and `Equb.lotterywinner_set` references coexist with `LotteryRound` in `owner_panel` — two parallel "winner" data models.
- A second `OwnerRoundSerializer` is accidentally redefined inside [api/owner_panel/permissions.py](api/owner_panel/permissions.py).
- `initialize_chapa_payment` writes to `payment.chapa_checkout_url`, but no such field exists on the `Payment` model.
- Wagtail apps are in `INSTALLED_APPS` but Wagtail URLs are commented out in [equb/urls.py](equb/urls.py).
- `DEBUG=True`, `ALLOWED_HOSTS=["*"]`, hardcoded `SECRET_KEY` and `CHAPA_SECRET_KEY` in committed [equb/settings.py](equb/settings.py).
