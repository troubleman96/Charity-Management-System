# Software Requirements Specification (SRS)
## Charity Management System for Orphan Support Groups
**Version:** 1.0 | **Date:** 2025-2026 | **Author:** DIT — Ordinary Diploma IT

---

## 1. Introduction

### 1.1 Purpose
This SRS defines the complete functional and non-functional requirements for a web-based Charity Management System (CMS) built with Django. The system automates donor registration, donation tracking, beneficiary management, internal communication, and administrative reporting for orphan support organizations in Tanzania.

### 1.2 Scope
The system replaces paper-based and spreadsheet-based processes with a centralized, role-based web platform accessible via any modern browser. The initial deployment targets a single orphan support organization with architecture designed for future multi-organization SaaS scaling.

### 1.3 Definitions
| Term | Definition |
|------|-----------|
| Beneficiary | An orphaned child registered and supported by the organization |
| Donor | An individual or entity making cash or in-kind contributions |
| Staff/Volunteer | Internal organization member managing operations |
| Admin | Super-user managing the entire system |
| In-kind Donation | Non-cash contributions (food, clothes, books, etc.) |
| RBAC | Role-Based Access Control |

---

## 2. Overall Description

### 2.1 Product Perspective
A standalone Django full-stack SaaS web application with:
- Multi-role authentication (Admin, Staff, Donor, Public)
- RESTful internal APIs (Django REST Framework) for dashboard widgets
- PostgreSQL relational database
- Celery + Redis for async notifications
- WhatsApp/SMS notifications via Africa's Talking (Tanzania-local)
- PDF report generation via WeasyPrint
- Hosted on a VPS (e.g., DigitalOcean, Hetzner)

### 2.2 User Classes

| Role | Permissions Summary |
|------|-------------------|
| **Super Admin** | Full CRUD on all modules, system settings, user management |
| **Staff/Volunteer** | Manage beneficiaries, record donations, send notifications |
| **Donor** | View own profile, donation history, receipts, beneficiary updates |
| **Public** | View landing page, register as donor |

### 2.3 Operating Environment
- Backend: Python 3.11+, Django 5.x, PostgreSQL 16
- Frontend: Django Templates + Tailwind CSS + Alpine.js (HTMX for dynamic updates)
- Task Queue: Celery + Redis
- Storage: Local / AWS S3 for production file uploads
- Deployment: Docker + Nginx + Gunicorn

---

## 3. Functional Requirements

### 3.1 Module 1: Authentication & User Management

| ID | Requirement |
|----|------------|
| FR-1.1 | System shall provide secure registration for Donors via public signup form |
| FR-1.2 | Admin/Staff accounts shall be created only by Super Admin |
| FR-1.3 | All passwords shall be hashed (Django PBKDF2 / Argon2) |
| FR-1.4 | System shall enforce role-based access control on every view |
| FR-1.5 | Users shall be able to reset passwords via email token |
| FR-1.6 | System shall log all login attempts (success and failure) |
| FR-1.7 | Sessions shall expire after 30 minutes of inactivity (configurable) |

### 3.2 Module 2: Beneficiary Management

| ID | Requirement |
|----|------------|
| FR-2.1 | Staff/Admin shall register orphan beneficiaries with full profile |
| FR-2.2 | Profile fields: full name, DOB, gender, school, grade, health status, guardian name, guardian contact, location, photo, date enrolled |
| FR-2.3 | System shall track assistance history per beneficiary (food, education, medical, clothing) |
| FR-2.4 | Staff shall submit and manage assistance requests per beneficiary |
| FR-2.5 | Admin shall approve or reject assistance requests from the dashboard |
| FR-2.6 | System shall display beneficiary status: Active, Inactive, Graduated |
| FR-2.7 | System shall support search and filter beneficiaries by status, school, location |

### 3.3 Module 3: Donor Management

| ID | Requirement |
|----|------------|
| FR-3.1 | Donors shall register with: name, email, phone, address, organization (optional) |
| FR-3.2 | Donors shall have a personal dashboard showing their donation history |
| FR-3.3 | Donors shall be linked to specific beneficiaries they sponsor |
| FR-3.4 | System shall display beneficiary progress updates to the linked donor |
| FR-3.5 | Donor profiles shall be searchable by Admin/Staff |

### 3.4 Module 4: Donation Management

| ID | Requirement |
|----|------------|
| FR-4.1 | Staff/Admin shall record cash donations with: date, amount (TZS), donor, purpose, allocation |
| FR-4.2 | Staff/Admin shall record in-kind donations with: date, item description, estimated value, donor |
| FR-4.3 | System shall automatically generate a unique digital receipt (PDF) per donation |
| FR-4.4 | System shall email receipt to donor upon donation recording |
| FR-4.5 | Donations shall have status: Received, Allocated, Partially Allocated |
| FR-4.6 | System shall maintain a complete immutable donation ledger |
| FR-4.7 | Admin shall be able to allocate donation funds to specific beneficiaries or programs |
| FR-4.8 | System shall calculate and display total received, allocated, and remaining funds in real-time |

### 3.5 Module 5: Communication & Notifications

| ID | Requirement |
|----|------------|
| FR-5.1 | System shall send automated email notification to donor on donation receipt |
| FR-5.2 | System shall send low-funds alert to Admin when available balance < threshold |
| FR-5.3 | Admin shall broadcast announcements to all donors via email |
| FR-5.4 | Staff shall send beneficiary progress update to linked donors |
| FR-5.5 | System shall support internal staff messaging (simple inbox) |
| FR-5.6 | All notifications shall be logged with timestamp and delivery status |
| FR-5.7 | System shall support SMS notifications via Africa's Talking API (optional/configurable) |

### 3.6 Module 6: Administrative Dashboard

| ID | Requirement |
|----|------------|
| FR-6.1 | Dashboard shall display: total donations (all-time, monthly), number of active beneficiaries, number of active donors, pending requests count, available funds |
| FR-6.2 | Dashboard shall include line chart: donations over time (monthly) |
| FR-6.3 | Dashboard shall include pie/bar chart: donation types (cash vs in-kind) |
| FR-6.4 | Dashboard shall include recent activity feed |
| FR-6.5 | Dashboard shall show pending assistance requests requiring approval |
| FR-6.6 | Admin shall generate downloadable PDF reports: monthly summary, annual summary, beneficiary report, donor report |
| FR-6.7 | Reports shall include organization logo and auto-generated date |

---

## 4. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|------------|
| NFR-1 | Security | All pages require authentication except landing, login, and donor signup |
| NFR-2 | Security | CSRF protection on all POST forms (Django default) |
| NFR-3 | Security | SQL injection protected via Django ORM (no raw queries) |
| NFR-4 | Security | Sensitive data (phone numbers) encrypted at rest |
| NFR-5 | Performance | Dashboard page load < 2 seconds for up to 10,000 records |
| NFR-6 | Performance | PDF receipt generation < 5 seconds |
| NFR-7 | Reliability | System uptime target: 99.5% |
| NFR-8 | Usability | Mobile-responsive UI (Tailwind CSS breakpoints) |
| NFR-9 | Scalability | Architecture supports multi-tenant SaaS expansion |
| NFR-10 | Backup | Daily automated database backups |
| NFR-11 | Compliance | User data handling compliant with organizational data policy |

---

## 5. System Constraints
- Must run on low-cost VPS (2 vCPU, 2GB RAM minimum)
- Supports Swahili/English bilingual interface (i18n ready)
- Internet connectivity required for all operations
- Initial deployment: single organization (not multi-tenant yet)
