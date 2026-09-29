-- Business Portal Schema (MySQL)

CREATE DATABASE IF NOT EXISTS business_portal;
USE business_portal;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('owner', 'accountant') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(100),
    monthly_salary DECIMAL(12,2) NOT NULL,
    join_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE salary_payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    status ENUM('paid', 'unpaid') DEFAULT 'unpaid',
    paid_date DATE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by INT,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    UNIQUE KEY unique_employee_month (employee_id, month, year)
);

CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(150) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    date_received DATE NOT NULL,
    status ENUM('pending', 'paid') DEFAULT 'pending',
    file_path VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE cash_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('in', 'out') NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    category VARCHAR(100),
    date DATE NOT NULL,
    description VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(50) NOT NULL,       -- e.g. 'create', 'update', 'delete'
    table_name VARCHAR(50) NOT NULL,
    record_id INT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Seed the owner account (change password after first login!)
-- Password hash below is a placeholder - generate a real one with werkzeug.security.generate_password_hash
-- INSERT INTO users (name, email, password_hash, role) VALUES ('Father', 'owner@example.com', '<hash>', 'owner');
