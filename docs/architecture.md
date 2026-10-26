# CloudDedup System Architecture & Design Specification

## 1. System Overview

**CloudDedup** is a cloud-based storage optimization and file deduplication platform designed to eliminate redundant physical data storage in cloud environments. It implements **Content-Addressable Storage (CAS)** principles using SHA-256 cryptographic hashing to identify duplicate content regardless of filenames.

---

## 2. Architectural Diagram

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT TIER                                       |
|  - HTML5 / CSS3 (Inter Typography, Dark Navy Sidebar, Light Dashboard)             |
|  - Bootstrap 5.3 + Bootstrap Icons                                                |
|  - Chart.js 4.4 Data Visualizations                                              |
|  - Firebase JavaScript SDK (User Registration, Login, Token Issuance)             |
+-----------------------------------------+-----------------------------------------+
                                          |
                        Authorization: Bearer <Firebase_ID_Token>
                        Multipart File Payload
                                          v
+-----------------------------------------------------------------------------------+
|                             BACKEND API TIER (FLASK)                              |
|                                                                                   |
|  +------------------------+  +--------------------------+  +--------------------+ |
|  | Authentication Filter  |  | File Validation Engine   |  | Chunk Hashing Svc  | |
|  | - Verify Firebase JWT  |  | - Allowed Extensions     |  | - Stream 64KB buf  | |
|  | - Resolve MySQL User   |  | - MIME verification      |  | - SHA-256 Digest   | |
|  +------------------------+  +--------------------------+  +--------------------+ |
|                                         |                                         |
|                                         v                                         |
|  +------------------------------------------------------------------------------+ |
|  |                        DEDUPLICATION ENGINE SERVICE                          | |
|  |  Checks SHA-256 hash in MySQL `stored_files`:                                | |
|  |   - Case A (New): Upload to Cloud -> Insert stored_file -> Insert reference  | |
|  |   - Case B (Duplicate): Skip upload -> Increment ref count -> Insert reference| |
|  |   - Compensation: If DB fails after cloud upload, delete orphan cloud blob    | |
|  +--------------------------------------+---------------------------------------+ |
+-----------------------------------------|-----------------------------------------+
                     |                    |
        Case A (New) |                    | Metadata & References
                     v                    v
+------------------------------------+  +-------------------------------------------+
|    OBJECT STORAGE TIER (FIREBASE)  |  |           METADATA TIER (MYSQL)           |
|                                    |  |                                           |
|  Deterministic Object Key:         |  |  - `users`: ID, Firebase UID, Email       |
|    `objects/<sha256_hash>`         |  |  - `stored_files`: Hash, Size, Path, Refs |
|                                    |  |  - `file_references`: User, StoredFileId  |
|  - Private Bucket                  |  |  - `upload_events`: Audit log history     |
+------------------------------------+  +-------------------------------------------+
```

---

## 3. Core Technical Modules

### 3.1 Content-Based Deduplication Algorithm

Traditional file systems organize files by directory paths and filenames. CloudDedup organizes physical objects by their **cryptographic fingerprint**.

1. **Stream Hashing**:
   - The backend streams incoming file bytes through a 64 KB binary buffer into `hashlib.sha256()`.
   - Streaming prevents loading entire multi-megabyte files into server RAM ($O(1)$ memory complexity).
2. **Deterministic Object Key**:
   - Every physical object in Firebase Cloud Storage is addressed strictly as `objects/<sha256_hash>`.
   - Filenames are never used as storage keys because multiple filenames can point to identical content.
3. **Reference Count Tracking**:
   - Each `stored_files` record maintains an active `reference_count`.
   - Multiple users or repeated uploads by the same user simply create new rows in `file_references` pointing to the single `stored_file_id`.

### 3.2 Storage Mathematics

For any user with a set of active file references $R = \{r_1, r_2, \dots, r_n\}$ mapping to unique physical stored objects $S = \{s_1, s_2, \dots, s_k\}$:

$$\text{Logical Storage} = \sum_{r \in R} \text{size}(r)$$

$$\text{Physical Storage} = \sum_{s \in S} \text{size}(s)$$

$$\text{Storage Saved} = \text{Logical Storage} - \text{Physical Storage}$$

$$\text{Saving Percentage} = \begin{cases} \left( \frac{\text{Storage Saved}}{\text{Logical Storage}} \right) \times 100 & \text{if } \text{Logical Storage} > 0 \\ 0.0\% & \text{if } \text{Logical Storage} = 0 \end{cases}$$

For a duplicate content cluster with $N$ user references and object size $S_{\text{obj}}$:
$$\text{Cluster Savings} = S_{\text{obj}} \times (N - 1)$$

---

## 4. Concurrency & Reliability Controls

- **Database Uniqueness Constraint**: `stored_files.sha256_hash` is indexed and enforced unique at the database engine level.
- **Race Condition Handling**: If two identical files are uploaded concurrently, the database catches the `IntegrityError`, rolls back the transaction, retrieves the existing `StoredFile`, and safely links the reference.
- **Transaction Compensation**: If physical cloud upload succeeds but MySQL database commit fails, an automatic compensation routine invokes `FirebaseStorageService.delete_file()` to prevent orphan cloud storage leaks.
- **Reference-Based Deletion**: Deleting a reference deletes only the user's `file_references` entry. The physical object and `stored_files` entry are purged only when the global system reference count reaches zero.
