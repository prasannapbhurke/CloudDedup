# CloudDedup Database Schema Specification

## 1. Overview

The CloudDedup database is implemented in **MySQL** using **SQLAlchemy ORM**. It adheres to third normal form (3NF) for relational integrity while supporting Content-Addressable Storage deduplication.

---

## 2. Entity-Relationship Diagram (ERD)

```
        +-----------------------------------------------+
        |                     users                     |
        +-----------------------------------------------+
        | PK  id             INT AUTO_INCREMENT         |
        | UK  firebase_uid   VARCHAR(128) INDEX         |
        |     name           VARCHAR(150)               |
        | UK  email          VARCHAR(255) INDEX         |
        |     created_at     DATETIME                   |
        |     updated_at     DATETIME                   |
        +-----------------------+-----------------------+
                                | 1
                                |
             +------------------+------------------+
             | M                                   | M
+------------v-------------------+   +-------------v-----------------+
|        file_references         |   |         upload_events         |
+--------------------------------+   +-------------------------------+
| PK  id          INT AUTO_INCR  |   | PK  id          INT AUTO_INCR |
| FK  user_id     INT (CASCADE)  |   | FK  user_id     INT (CASCADE) |
| FK  stored_file_id INT(RESTRICT|   | FK  stored_file_id INT (SET NULL)
|     display_name VARCHAR(255)  |   |     original_filename VARCHAR |
|     uploaded_at DATETIME INDEX |   |     file_size   BIGINT        |
|     is_duplicate BOOLEAN       |   |     sha256_hash VARCHAR(64)   |
+-----------------+--------------+   |     event_type  VARCHAR(32)   |
                  | M                |     created_at  DATETIME INDEX|
                  |                  +---------------+---------------+
                  | 1                                | M
        +---------v---------------------+            | 1 (nullable)
        |          stored_files         |<-----------+
        +-------------------------------+
        | PK  id          INT AUTO_INCR |
        | UK  sha256_hash VARCHAR(64)   |
        |     file_size   BIGINT (BYTES)|
        |     storage_path VARCHAR(512) |
        |     mime_type   VARCHAR(128)  |
        |     reference_count INT       |
        |     created_at  DATETIME      |
        +-------------------------------+
```

---

## 3. Table Definitions & SQL DDL

### Table 1: `users`
Stores user profile information synchronized from Firebase Authentication.
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firebase_uid VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_firebase_uid (firebase_uid),
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Table 2: `stored_files`
Represents unique physical file content stored in Firebase Cloud Storage.
```sql
CREATE TABLE stored_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sha256_hash VARCHAR(64) NOT NULL UNIQUE,
    file_size BIGINT NOT NULL COMMENT 'Size in bytes',
    storage_path VARCHAR(512) NOT NULL COMMENT 'Cloud object path: objects/<sha256_hash>',
    mime_type VARCHAR(128) NOT NULL DEFAULT 'application/octet-stream',
    reference_count INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stored_files_hash (sha256_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Table 3: `file_references`
Represents the user's view of files. Multiple references can point to the same stored physical file.
```sql
CREATE TABLE file_references (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stored_file_id INT NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_duplicate BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_file_references_user (user_id),
    INDEX idx_file_references_stored (stored_file_id),
    INDEX idx_file_references_date (uploaded_at),
    CONSTRAINT fk_file_ref_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_file_ref_stored FOREIGN KEY (stored_file_id) REFERENCES stored_files(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Table 4: `upload_events`
Historical audit log of all upload attempts and deduplication decisions over time.
```sql
CREATE TABLE upload_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stored_file_id INT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    sha256_hash VARCHAR(64) NOT NULL,
    event_type VARCHAR(32) NOT NULL COMMENT 'new_upload or duplicate_detected',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_upload_events_user (user_id),
    INDEX idx_upload_events_hash (sha256_hash),
    INDEX idx_upload_events_date (created_at),
    CONSTRAINT fk_upload_event_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_upload_event_stored FOREIGN KEY (stored_file_id) REFERENCES stored_files(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 4. Key Design Decisions

1. **No Passwords in MySQL**: Firebase Authentication handles password salting, hashing (scrypt/bcrypt), and session security. MySQL stores only verified identity metadata.
2. **Decoupled References**: `file_references` allows a user to maintain multiple files with identical content under different display names without duplicating cloud storage bytes.
3. **Independent Audit Log**: Deleting a reference from `file_references` leaves `upload_events` intact so historical timeline analytics and savings graphs remain valid.
