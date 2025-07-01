
CREATE TABLE IF NOT EXISTS platform_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    page_id VARCHAR(100) NOT NULL,
    access_token TEXT NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    media_path VARCHAR(255),
    scheduled_time DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    account_id INT,
    FOREIGN KEY (account_id) REFERENCES platform_accounts(id)
);
