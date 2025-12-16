-- Script khởi tạo database cho Workout AI
-- Chạy script này trong phpMyAdmin hoặc MySQL command line

-- Tạo database (nếu chưa tồn tại)
CREATE DATABASE IF NOT EXISTS workout_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Sử dụng database
USE workout_ai;

-- Tạo bảng users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sau khi tạo bảng, chạy file seed_users.py để thêm dữ liệu mẫu
-- Hoặc import file seed_data.sql (nếu đã có password hash)

