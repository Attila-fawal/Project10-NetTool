CREATE DATABASE IF NOT EXISTS nettool_db;
USE nettool_db;

CREATE TABLE IF NOT EXISTS roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE IF NOT EXISTS device_types (
    device_type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    device_type_id INT NOT NULL,
    device_address VARCHAR(45) NOT NULL,
    network_mask VARCHAR(45) NOT NULL,
    default_gateway VARCHAR(45) NOT NULL,
    location VARCHAR(100),
    notes TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_type_id) REFERENCES device_types(device_type_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

INSERT IGNORE INTO roles (role_name) VALUES
    ('Admin'),
    ('Viewer');

INSERT IGNORE INTO users (username, password_hash, role_id)
    SELECT 'admin', 'scrypt:32768:8:1$TQ92idIXWbqcxgnN$3f4e6ae1d2442a7e9951d1b4995cf3e339859df77e365bfdd83bf0484f797bdb3cee0ec366d4dafaa75ba1b6f7b8a7b5cb9081490895d93405802148efe648e8', role_id
    FROM roles WHERE role_name = 'Admin'
    LIMIT 1;

INSERT IGNORE INTO users (username, password_hash, role_id)
    SELECT 'viewer', 'scrypt:32768:8:1$1Tec1ZVq2Hwb9E6i$971f385dae3d6a14d60e36b75357c7c246d64fe1620a94f47a05e720ce02b7caa93e12ed84a8053a22cf1a191464dfc2f254000be5155e95e8243e1ade24d92d', role_id
    FROM roles WHERE role_name = 'Viewer'
    LIMIT 1;

INSERT IGNORE INTO device_types (type_name, description) VALUES
    ('Router', 'Routing device for network traffic'),
    ('Switch', 'Layer 2 switch with multiple ports'),
    ('Server', 'On-premises compute server'),
    ('Firewall', 'Network security appliance'),
    ('Access Point', 'Wireless access point');

INSERT IGNORE INTO devices (device_name, device_type_id, device_address, network_mask, default_gateway, location, notes, created_by) VALUES
    ('Core Router', 1, '192.168.1.1', '255.255.255.0', '192.168.1.254', 'Data Center', 'Main routing device for the campus network.', 1),
    ('Distribution Switch', 2, '192.168.2.10', '255.255.255.0', '192.168.2.1', 'Server Room', 'Aggregates floor switches and connects to core router.', 1),
    ('Application Server', 3, '10.0.10.20', '255.255.255.0', '10.0.10.1', 'Server Rack 3', 'Hosts business applications and monitoring services.', 1),
    ('Firewall A', 4, '10.0.0.1', '255.255.255.0', '10.0.0.254', 'Main Security Closet', 'Protects the internal network from external threats.', 1),
    ('Lobby WiFi', 5, '172.16.0.5', '255.255.255.0', '172.16.0.1', 'Front Lobby', 'Wireless access point for visitors and staff.', 1);
