-- Writingway AI Story Database Schema for MySQL
-- Database: ai_syory
-- Created for AI-powered creative writing assistant

-- Create database
CREATE DATABASE IF NOT EXISTS ai_syory 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE ai_syory;

-- Drop tables if they exist (for clean setup)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS ai_conversations;
DROP TABLE IF EXISTS user_settings;
DROP TABLE IF EXISTS compendium_entries;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- Users table - Store user accounts
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Projects table - Store writing projects
CREATE TABLE projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    cover_image VARCHAR(500),
    owner_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner (owner_id),
    INDEX idx_active (is_active),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Documents table - Store writing documents with hierarchical structure
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    content LONGTEXT,
    document_type VARCHAR(50) DEFAULT 'scene',
    order_index INT DEFAULT 0,
    project_id INT NOT NULL,
    parent_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES documents(id) ON DELETE SET NULL,
    INDEX idx_project (project_id),
    INDEX idx_parent (parent_id),
    INDEX idx_type (document_type),
    INDEX idx_order (order_index),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Compendium entries table - Store world-building elements
CREATE TABLE compendium_entries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    entry_type VARCHAR(50),
    tags JSON,
    project_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_type (entry_type),
    INDEX idx_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User settings table - Store user preferences
CREATE TABLE user_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    theme VARCHAR(50) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'en',
    font_size INT DEFAULT 14,
    auto_save BOOLEAN DEFAULT TRUE,
    ai_settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- AI conversations table - Store AI chat history
CREATE TABLE ai_conversations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    project_id INT NULL,
    document_id INT NULL,
    messages JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_project (project_id),
    INDEX idx_document (document_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default admin user (password: admin123)
INSERT INTO users (username, email, hashed_password, full_name, is_active) VALUES
('admin', 'admin@writingway.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'Administrator', TRUE);

-- Insert demo user (password: demo123)
INSERT INTO users (username, email, hashed_password, full_name, is_active) VALUES
('demo', 'demo@writingway.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'Demo User', TRUE);

-- Insert default settings for admin user
INSERT INTO user_settings (user_id, theme, language, font_size, auto_save, ai_settings) VALUES
(1, 'light', 'en', 14, TRUE, '{}');

-- Insert default settings for demo user
INSERT INTO user_settings (user_id, theme, language, font_size, auto_save, ai_settings) VALUES
(2, 'light', 'en', 14, TRUE, '{}');

-- Insert sample project for demo
INSERT INTO projects (name, description, owner_id) VALUES
('我的第一部小说', '一个关于年轻作家发现AI辅助创作力量的惊险冒险故事。', 2);

-- Insert sample documents
INSERT INTO documents (title, content, document_type, project_id, order_index) VALUES
('第一章：开始', '<h1>第一章：开始</h1><p>那是一个风雨交加的夜晚，莎拉第一次发现了神秘的写作助手...</p>', 'chapter', 1, 1),
('角色：莎拉', '<h2>莎拉·约翰逊</h2><p><strong>年龄：</strong> 25岁</p><p><strong>职业：</strong> 有抱负的小说家</p><p><strong>背景：</strong> 一个梦想成为出版作家的创意写作毕业生。</p>', 'character', 1, 2),
('场景：咖啡店', '<h2>温馨角落咖啡馆</h2><p>一个小而温馨的咖啡店，莎拉在这里度过大部分写作时光。墙上排满了书架，新鲜咖啡的香气弥漫在空气中。</p>', 'location', 1, 3);

-- Insert sample compendium entries
INSERT INTO compendium_entries (title, content, entry_type, project_id, tags) VALUES
('魔法系统', '在这个世界里，创造力本身就是一种魔法。作家可以通过想象力和AI辅助的力量让文字变成现实。', 'worldbuilding', 1, '["魔法", "创造力", "写作"]'),
('作家公会', '一个古老的作家组织，他们掌握了创意魔法的艺术。他们指导新作家踏上写作之旅。', 'organization', 1, '["公会", "作家", "组织"]');

-- Create views for common queries
CREATE VIEW active_projects AS
SELECT p.*, u.username as owner_name,
       COUNT(d.id) as document_count
FROM projects p
JOIN users u ON p.owner_id = u.id
LEFT JOIN documents d ON p.id = d.project_id AND d.is_active = TRUE
WHERE p.is_active = TRUE
GROUP BY p.id, p.name, p.description, p.cover_image, p.owner_id, p.is_active, p.created_at, p.updated_at, u.username;

CREATE VIEW project_statistics AS
SELECT p.id as project_id,
       p.name as project_name,
       COUNT(DISTINCT d.id) as total_documents,
       COUNT(DISTINCT CASE WHEN d.document_type = 'chapter' THEN d.id END) as chapters,
       COUNT(DISTINCT CASE WHEN d.document_type = 'character' THEN d.id END) as characters,
       COUNT(DISTINCT CASE WHEN d.document_type = 'location' THEN d.id END) as locations,
       COUNT(DISTINCT c.id) as compendium_entries,
       COALESCE(SUM(CHAR_LENGTH(d.content)), 0) as total_word_count
FROM projects p
LEFT JOIN documents d ON p.id = d.project_id AND d.is_active = TRUE
LEFT JOIN compendium_entries c ON p.id = c.project_id
WHERE p.is_active = TRUE
GROUP BY p.id, p.name;

-- Create stored procedures for common operations
DELIMITER //

CREATE PROCEDURE GetUserProjects(IN user_id INT)
BEGIN
    SELECT p.*,
           COUNT(d.id) as document_count,
           MAX(d.updated_at) as last_activity
    FROM projects p
    LEFT JOIN documents d ON p.id = d.project_id AND d.is_active = TRUE
    WHERE p.owner_id = user_id AND p.is_active = TRUE
    GROUP BY p.id, p.name, p.description, p.cover_image, p.owner_id, p.is_active, p.created_at, p.updated_at
    ORDER BY p.updated_at DESC;
END //

CREATE PROCEDURE GetProjectDocuments(IN project_id INT)
BEGIN
    SELECT d.*,
           parent.title as parent_title
    FROM documents d
    LEFT JOIN documents parent ON d.parent_id = parent.id
    WHERE d.project_id = project_id AND d.is_active = TRUE
    ORDER BY d.order_index, d.created_at;
END //

CREATE PROCEDURE GetProjectStats(IN project_id INT)
BEGIN
    SELECT
        COUNT(DISTINCT d.id) as total_documents,
        COUNT(DISTINCT CASE WHEN d.document_type = 'chapter' THEN d.id END) as chapters,
        COUNT(DISTINCT CASE WHEN d.document_type = 'character' THEN d.id END) as characters,
        COUNT(DISTINCT CASE WHEN d.document_type = 'location' THEN d.id END) as locations,
        COUNT(DISTINCT c.id) as compendium_entries,
        COALESCE(SUM(CHAR_LENGTH(d.content)), 0) as total_characters,
        COALESCE(SUM(CHAR_LENGTH(d.content) - CHAR_LENGTH(REPLACE(d.content, ' ', '')) + 1), 0) as estimated_words
    FROM projects p
    LEFT JOIN documents d ON p.id = d.project_id AND d.is_active = TRUE
    LEFT JOIN compendium_entries c ON p.id = c.project_id
    WHERE p.id = project_id AND p.is_active = TRUE
    GROUP BY p.id;
END //

DELIMITER ;

-- Create indexes for better performance
CREATE INDEX idx_documents_updated ON documents(updated_at);
CREATE INDEX idx_projects_updated ON projects(updated_at);
CREATE INDEX idx_users_created ON users(created_at);

-- Display success message and table information
SELECT 'ai_syory数据库结构创建成功！' as status;
SELECT 'Database: ai_syory' as database_name;
SELECT 'Tables created: 6' as table_count;
SELECT 'Sample data inserted: Yes' as sample_data;
SELECT 'Views created: 2' as views_count;
SELECT 'Stored procedures: 3' as procedures_count;

-- Show table sizes
SELECT
    TABLE_NAME as '表名',
    TABLE_ROWS as '行数',
    ROUND(DATA_LENGTH/1024,2) as '数据大小(KB)',
    ROUND(INDEX_LENGTH/1024,2) as '索引大小(KB)'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'ai_syory'
ORDER BY TABLE_NAME;
