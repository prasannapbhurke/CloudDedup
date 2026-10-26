-- =====================================================================
-- CloudDedup Database & Table Creation Script
-- Run this script in phpMyAdmin (SQL tab) or via MySQL Command Line.
-- =====================================================================

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS `clouddedup_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `clouddedup_db`;

-- Step 2: Create users Table
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `firebase_uid` VARCHAR(128) NOT NULL UNIQUE,
    `name` VARCHAR(150) NOT NULL,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_users_firebase_uid` (`firebase_uid`),
    INDEX `idx_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Step 3: Create stored_files Table (Unique Physical Cloud Objects)
CREATE TABLE IF NOT EXISTS `stored_files` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `sha256_hash` VARCHAR(64) NOT NULL UNIQUE,
    `file_size` BIGINT NOT NULL COMMENT 'File size in bytes',
    `storage_path` VARCHAR(512) NOT NULL COMMENT 'Cloud object path: objects/<sha256_hash>',
    `mime_type` VARCHAR(128) NOT NULL DEFAULT 'application/octet-stream',
    `reference_count` INT NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_stored_files_hash` (`sha256_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Step 4: Create file_references Table (User-Facing File Links)
CREATE TABLE IF NOT EXISTS `file_references` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `stored_file_id` INT NOT NULL,
    `display_name` VARCHAR(255) NOT NULL,
    `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `is_duplicate` BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX `idx_file_references_user` (`user_id`),
    INDEX `idx_file_references_stored` (`stored_file_id`),
    INDEX `idx_file_references_date` (`uploaded_at`),
    CONSTRAINT `fk_file_ref_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_file_ref_stored` FOREIGN KEY (`stored_file_id`) REFERENCES `stored_files`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Step 5: Create upload_events Table (Deduplication Audit History)
CREATE TABLE IF NOT EXISTS `upload_events` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `stored_file_id` INT NULL,
    `original_filename` VARCHAR(255) NOT NULL,
    `file_size` BIGINT NOT NULL,
    `sha256_hash` VARCHAR(64) NOT NULL,
    `event_type` VARCHAR(32) NOT NULL COMMENT 'new_upload or duplicate_detected',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_upload_events_user` (`user_id`),
    INDEX `idx_upload_events_hash` (`sha256_hash`),
    INDEX `idx_upload_events_date` (`created_at`),
    CONSTRAINT `fk_upload_event_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_upload_event_stored` FOREIGN KEY (`stored_file_id`) REFERENCES `stored_files`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
