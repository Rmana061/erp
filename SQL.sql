-- 建立資料庫
CREATE DATABASE my_database;
\c my_database;

-- 建立 customers 資料表
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    line_account VARCHAR(255),
    contact_name VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(255),
    address VARCHAR(255),
    viewable_products TEXT,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    remark TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 建立 products 資料表
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    dm_url VARCHAR(255),
    min_order_qty INT DEFAULT 1,
    max_order_qty INT,
    product_unit VARCHAR(50) NOT NULL,
    stock_quantity INT DEFAULT 0,
    status ENUM('available', 'unavailable') NOT NULL DEFAULT 'available',
    shipping_time TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 建立 orders 資料表
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    order_confirmed BOOLEAN DEFAULT FALSE,
    order_shipped BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 建立 order_details 資料表
CREATE TABLE order_details (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    product_id BIGINT NOT NULL REFERENCES products(id),
    product_quantity INT NOT NULL,
    product_unit VARCHAR(50) NOT NULL,
    order_status ENUM('待確認', '已確認', '已出貨', '完成', '取消') NOT NULL DEFAULT '待確認',
    shipping_date DATE,
    remark TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    supplier_note TEXT
);

-- 建立 logs 資料表
CREATE TABLE logs (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    operation_type ENUM('新增', '刪除', '修改', '查詢') NOT NULL,
    record_id BIGINT,
    operation_detail TEXT,
    performed_by BIGINT NOT NULL,
    user_type ENUM('客戶', '管理員') NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 建立 permission_levels 資料表
CREATE TABLE permission_levels (
    id BIGSERIAL PRIMARY KEY,
    level_name VARCHAR(50) NOT NULL,
    can_approve_orders BOOLEAN NOT NULL DEFAULT FALSE,
    can_edit_orders BOOLEAN NOT NULL DEFAULT FALSE,
    can_close_order_dates BOOLEAN NOT NULL DEFAULT FALSE,
    can_add_customer BOOLEAN NOT NULL DEFAULT FALSE,
    can_add_product BOOLEAN NOT NULL DEFAULT FALSE,
    can_add_personnel BOOLEAN NOT NULL DEFAULT FALSE,
    can_view_system_logs BOOLEAN NOT NULL DEFAULT FALSE,
    can_decide_product_view BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 插入權限等級
INSERT INTO permission_levels (level_name, can_approve_orders, can_edit_orders, can_close_order_dates, can_add_customer, can_add_product, can_add_personnel, can_view_system_logs, can_decide_product_view, created_at, updated_at)
VALUES
('最高權限', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, NOW(), NOW()),
('審核權限', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, NOW(), NOW()),
('基本權限', FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, NOW(), NOW()),
('檢視權限', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, NOW(), NOW());

-- 建立 administrators 資料表
CREATE TABLE administrators (
    id BIGSERIAL PRIMARY KEY,
    admin_account VARCHAR(100) UNIQUE NOT NULL,
    admin_password VARCHAR(255) NOT NULL,
    admin_name VARCHAR(100) NOT NULL,
    staff_no VARCHAR(50),
    permission_level_id BIGINT NOT NULL REFERENCES permission_levels(id),
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 插入管理員帳號
INSERT INTO administrators (admin_account, admin_password, admin_name, staff_no, permission_level_id, status, created_at, updated_at)
VALUES
('1', '1', 'Super Admin', 'A000', (SELECT id FROM permission_levels WHERE level_name = '最高權限'), 'active', NOW(), NOW());

-- 建立 locked_dates 資料表
CREATE TABLE locked_dates (
    id BIGSERIAL PRIMARY KEY,
    locked_date DATE UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 建立 line_users 資料表 (LINE個人用戶)
CREATE TABLE line_users (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    line_user_id VARCHAR(100) NOT NULL,
    user_name VARCHAR(100),
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 建立 line_groups 資料表 (LINE群組)
CREATE TABLE line_groups (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    line_group_id VARCHAR(100) NOT NULL,
    group_name VARCHAR(100),
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
