# CloudDedup — Cloud-Based File Deduplication and Storage Optimization System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.x-orange.svg)](https://www.mysql.com/)
[![Firebase](https://img.shields.io/badge/Firebase-Admin%20%26%20Storage-yellow.svg)](https://firebase.google.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Tests](https://img.shields.io/badge/Tests-11%20Passed-brightgreen.svg)]()

> A functional, professional Cloud Computing microproject demonstrating **Content-Addressable Storage (CAS)** and cloud resource optimization using **SHA-256 fingerprinting**, **Firebase Cloud Storage**, and **MySQL**.

---

## 1. Project Overview

Cloud storage costs grow rapidly when users upload duplicate files under different names. **CloudDedup** solves this problem by identifying duplicate files using **cryptographic content hashing (SHA-256)** rather than unreliable file names.

### The Problem & Solution Example:
Suppose a student uploads three files:
- `assignment.pdf` — 10 MB
- `cloud_assignment.pdf` — 10 MB
- `final_assignment.pdf` — 10 MB

All three files contain the exact same byte content.
- **Without CloudDedup**: 3 physical cloud uploads = 30 MB consumed.
- **With CloudDedup**:
  - SHA-256 hash calculated: `a8f23c9d...`
  - Only **1 physical copy** (10 MB) is stored in Firebase Cloud Storage.
  - **3 separate file references** are created in MySQL for user convenience.
  - **Logical Storage**: 30 MB
  - **Physical Cloud Storage**: 10 MB
  - **Storage Saved**: 20 MB (66.67% reduction)

---

## 2. Technology Stack & Architecture

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons | Responsive cloud management dashboard UI. |
| **Data Visualization** | Chart.js 4.4 | Real-time storage comparison, distribution, and trend charts. |
| **Backend API** | Python 3, Flask, Flask Blueprints | RESTful API endpoints and deduplication pipeline. |
| **Authentication** | Firebase Authentication (Web SDK & Admin SDK) | Secure JWT ID token verification; zero passwords in MySQL. |
| **Metadata Database**| MySQL & SQLAlchemy ORM | Storing users, unique stored files, file references, and audit logs. |
| **Cloud Object Storage**| Firebase Cloud Storage (Google Cloud) | Storing unique physical file bytes at `objects/<sha256_hash>`. |
| **Fingerprinting** | Python `hashlib.sha256` | 64 KB chunked binary content hashing. |

---

## 3. Directory Structure

```
CloudDedup/
├── app.py                      # Application entry point
├── config.py                   # Configuration and environment settings
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment secrets
├── .gitignore                  # Git exclusions for secrets and keys
├── README.md                   # Complete documentation and viva guide
│
├── app/
│   ├── __init__.py             # Flask application factory
│   ├── extensions.py           # SQLAlchemy database instance
│   ├── models/                 # MySQL database models
│   │   ├── user.py             # User profile model
│   │   ├── stored_file.py      # Unique physical cloud file model
│   │   ├── file_reference.py   # User-facing logical file reference model
│   │   └── upload_event.py     # Upload history and deduplication audit log
│   ├── routes/                 # Flask Blueprints
│   │   ├── auth_routes.py      # Login, registration, token sync
│   │   ├── dashboard_routes.py # Summary metrics and dashboard view
│   │   ├── upload_routes.py    # Dedicated file upload and API
│   │   ├── file_routes.py      # My Files listing, download, safe deletion
│   │   ├── duplicate_routes.py # Duplicate groups overview and details
│   │   └── statistics_routes.py# Storage analytics and Chart.js endpoints
│   ├── services/               # Core business logic services
│   │   ├── hashing_service.py  # 64 KB chunked binary SHA-256 fingerprinting
│   │   ├── firebase_auth_service.py # Firebase JWT ID token verification
│   │   ├── firebase_storage_service.py # Cloud Storage bucket upload/download
│   │   ├── deduplication_service.py # Core CAS deduplication engine
│   │   ├── file_management_service.py # Reference queries and safe deletion
│   │   └── statistics_service.py # Metric formulas and group calculations
│   ├── middleware/
│   │   └── authentication.py   # @require_auth decorator and user sync
│   ├── utils/
│   │   ├── validators.py       # Extension, size, MIME validators
│   │   └── file_helpers.py     # Byte formatting and UI category icons
│   ├── templates/              # Jinja2 HTML Templates
│   │   ├── base.html           # Dark navy sidebar & topbar master layout
│   │   ├── login.html          # Authentication login page
│   │   ├── register.html       # User registration page
│   │   ├── forgot_password.html# Password reset request page
│   │   ├── dashboard.html      # 7 Metric cards & 4 Chart.js charts
│   │   ├── upload.html         # Drag-and-drop upload & status banner
│   │   ├── my_files.html       # Searchable, filterable file reference table
│   │   ├── duplicate_groups.html # Content clusters with >= 2 references
│   │   ├── duplicate_group_details.html # Detailed reference comparison
│   │   ├── statistics.html     # Deep analytics & formula breakdowns
│   │   ├── settings.html       # Profile and CAS engine specifications
│   │   └── errors/             # 404 and 500 error pages
│   └── static/
│       ├── css/style.css       # Custom modern dashboard styles
│       └── js/                 # Client controllers (auth, dashboard, upload, etc.)
│
├── tests/                      # Automated Test Suite (Pytest)
│   ├── test_hashing.py         # SHA-256 chunked calculation tests
│   ├── test_deduplication.py   # New upload vs duplicate upload workflows
│   ├── test_statistics.py      # Formula validations & duplicate groups
│   └── test_file_access.py     # Multi-user isolation & reference deletion
│
└── docs/
    ├── architecture.md         # Full architecture and algorithms
    └── database_schema.md      # ERD, table definitions, and SQL DDL
```

---

## 4. Installation & Setup Guide

### Step 1: Install Python Dependencies
Open PowerShell or Command Prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 2: Configure MySQL Database
1. Start your local MySQL server (or XAMPP / MariaDB).
2. Create the database:
   ```sql
   CREATE DATABASE clouddedup_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update your MySQL credentials in `.env`:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=clouddedup_db
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
```
*(Note: If MySQL is not running on your machine, CloudDedup automatically initializes a local database in `instance/clouddedup.db` so you can test immediately without setup blockers!)*

### Step 4: Configure Firebase (Authentication & Cloud Storage)
1. Go to the [Firebase Console](https://console.firebase.google.com/) and create a project.
2. **Enable Authentication**: Under **Build > Authentication > Sign-in method**, enable **Email/Password**.
3. **Enable Cloud Storage**: Under **Build > Storage**, click **Get Started** to create a storage bucket.
4. **Download Service Account Key**:
   - Go to **Project Settings > Service Accounts**.
   - Click **Generate new private key**.
   - Save the downloaded JSON file as `serviceAccountKey.json` in the project root directory.
5. In `.env`, set:
   ```env
   FIREBASE_PROJECT_ID=your-firebase-project-id
   FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
   FIREBASE_SERVICE_ACCOUNT_PATH=serviceAccountKey.json
   ```
6. Copy your web app config from Firebase Project Settings into `app/static/js/firebase-config.js`.

*(Offline / Demo Viva Note: If you do not have Firebase credentials ready, CloudDedup includes a built-in offline demonstration mode with pre-configured demo student accounts so the complete deduplication engine can be demonstrated immediately!)*

---

## 5. Running the Application

Start the Flask server:
```bash
python app.py
```
Open your web browser and navigate to:
**http://127.0.0.1:5000**

---

## 6. Running Automated Tests

Run the full pytest automated test suite:
```bash
python -m pytest -v
```
All 11 tests will execute and pass:
- SHA-256 chunked calculation verification
- Identical content producing identical hashes across different filenames
- New file upload workflow (1 stored file, 1 reference)
- Duplicate file upload workflow (1 stored file, 2 references, physical upload skipped)
- Modified content detection
- Multi-user isolation and unauthorized access rejection
- Reference deletion lifecycle (retaining physical object until last reference is removed)
- Storage statistics calculations and duplicate group discovery

---

## 7. How to Test & Demonstrate for Viva

Follow these steps to demonstrate the deduplication engine in action:

### Scenario 1: First Upload (Original File)
1. Log in (or click **User A (Alex)** on the login screen for quick demo mode).
2. Go to **Upload File**.
3. Select any file from your computer (e.g. `report.pdf`).
4. Click **Upload to Cloud**.
5. **Observed Result**:
   - Status banner: `New File Uploaded to Cloud!`
   - 1 physical object stored at `objects/<sha256_hash>`.
   - In Dashboard: Total Files = 1, Unique Files = 1, Storage Saved = 0 B.

### Scenario 2: Duplicate Upload with a Different Filename
1. Take the exact same file on your computer and make a copy with a different name, e.g., `final_report_v2.pdf`.
2. Go to **Upload File** and upload `final_report_v2.pdf`.
3. **Observed Result**:
   - Status banner: `Duplicate Content Detected!` (Amber alert).
   - "Physical upload skipped! SHA-256 fingerprint matched existing cloud object."
   - Storage saved is highlighted.
4. Go to **My Files**:
   - Both `report.pdf` and `final_report_v2.pdf` are listed!
   - `report.pdf` is labeled **Original**.
   - `final_report_v2.pdf` is labeled **Duplicate**.
   - Both display the identical SHA-256 hash.

### Scenario 3: Verify Duplicate Groups
1. Navigate to **Duplicate Groups**.
2. A duplicate group card appears showing:
   - 2 references linked to this content hash.
   - Potential savings = Size of file $\times (2 - 1)$.
3. Click **View Group References** to inspect both filenames, download them, or delete duplicates.

### Scenario 4: Download Verification
1. On **My Files**, click download on `report.pdf` &rarr; downloaded with name `report.pdf`.
2. Click download on `final_report_v2.pdf` &rarr; downloaded with name `final_report_v2.pdf`.
3. Both files contain the exact same original content retrieved from the single cloud object!

### Scenario 5: Reference-Based Deletion
1. In **My Files**, delete `final_report_v2.pdf`.
2. The reference count decreases from 2 to 1.
3. The physical object is safely retained because `report.pdf` still references it.
4. Now delete `report.pdf` &rarr; Reference count hits 0; the physical object is permanently purged from cloud storage!

---

## 8. College Viva & Technical Defense Q&A

### Q1: What is file deduplication, and how does Content-Addressable Storage (CAS) work?
**Answer**: Deduplication is a data compression technique that eliminates duplicate copies of repeating data. In CloudDedup, we use Content-Addressable Storage (CAS), where data is retrieved and addressed based on its cryptographic content fingerprint (SHA-256) rather than its user-assigned filename or directory path.

### Q2: Why calculate SHA-256 on the backend instead of trusting the frontend?
**Answer**: Frontend calculations can be maliciously spoofed or modified. If an attacker sent an arbitrary hash of an existing file without sending the actual content, they could gain unauthorized access to that file. The backend must independently stream the binary bytes and compute the SHA-256 hash.

### Q3: Why process file hashing in 64 KB chunks rather than reading the entire file?
**Answer**: If a user uploads a 50 MB or 500 MB file, loading the entire file into memory at once creates high RAM pressure on the Flask server ($O(N)$ memory). Streaming in 64 KB chunks maintains an $O(1)$ constant memory footprint.

### Q4: How is user privacy maintained if multiple users upload the same file?
**Answer**: In CloudDedup, while physical cloud objects are shared at the storage layer, the metadata layer (`file_references`) is strictly partitioned by `user_id`. Each query filters by `FileReference.user_id == current_user.id`. User A can never see User B's filenames, upload history, or duplicate groups.

### Q5: What happens if a database error occurs after a file is uploaded to Firebase Storage?
**Answer**: CloudDedup implements transactional compensation logic. If the physical upload to Firebase Storage succeeds but the subsequent MySQL commit fails, an exception handler immediately catches the error and executes `FirebaseStorageService.delete_file()` to remove the orphan cloud object.
