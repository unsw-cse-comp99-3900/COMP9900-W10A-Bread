-- Writingway AI Story Database Schema
-- Database: ai_syory
-- Created for AI-powered creative writing assistant

-- Create database (uncomment if needed)
-- CREATE DATABASE ai_syory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE ai_syory;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS ai_conversations;
DROP TABLE IF EXISTS user_settings;
DROP TABLE IF EXISTS compendium_entries;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

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
);

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
);

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
);

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
);

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
);

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
);

-- Insert default admin user
INSERT INTO users (username, email, hashed_password, full_name, is_active) VALUES
('admin', 'admin@writingway.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'Administrator', TRUE);

-- Insert demo user
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
('My First Novel', 'A thrilling adventure story about a young writer discovering the power of AI-assisted creativity.', 2);

-- Insert sample documents
INSERT INTO documents (title, content, document_type, project_id, order_index) VALUES
('Chapter 1: The Beginning', '<h1>Chapter 1: The Beginning</h1><p>It was a dark and stormy night when Sarah first discovered the mysterious writing assistant...</p>', 'chapter', 1, 1),
('Character: Sarah', '<h2>Sarah Johnson</h2><p><strong>Age:</strong> 25</p><p><strong>Occupation:</strong> Aspiring novelist</p><p><strong>Background:</strong> A creative writing graduate who dreams of becoming a published author.</p>', 'character', 1, 2),
('Setting: The Coffee Shop', '<h2>The Cozy Corner Café</h2><p>A small, intimate coffee shop where Sarah spends most of her writing time. The walls are lined with bookshelves, and the aroma of freshly brewed coffee fills the air.</p>', 'location', 1, 3);

-- Insert sample compendium entries
INSERT INTO compendium_entries (title, content, entry_type, project_id, tags) VALUES
('Magic System', 'In this world, creativity itself is a form of magic. Writers can bring their words to life through the power of imagination and AI assistance.', 'worldbuilding', 1, '["magic", "creativity", "writing"]'),
('The Writing Guild', 'An ancient organization of writers who have mastered the art of creative magic. They guide new writers in their journey.', 'organization', 1, '["guild", "writers", "organization"]');

-- Create views for common queries
CREATE VIEW active_projects AS
SELECT p.*, u.username as owner_name, 
       COUNT(d.id) as document_count
FROM projects p
JOIN users u ON p.owner_id = u.id
LEFT JOIN documents d ON p.id = d.project_id AND d.is_active = TRUE
WHERE p.is_active = TRUE
GROUP BY p.id;

CREATE VIEW project_statistics AS
SELECT p.id as project_id,
       p.name as project_name,
       COUNT(DISTINCT d.id) as total_documents,
       COUNT(DISTINCT CASE WHEN d.document_type = 'chapter' THEN d.id END) as chapters,
       COUNT(DISTINCT CASE WHEN d.document_type = 'character' THEN d.id END) as characters,
       COUNT(DISTINCT CASE WHEN d.document_type = 'location' THEN d.id END) as locations,
       COUNT(DISTINCT c.id) as compendium_entries,
       SUM(CHAR_LENGTH(d.content)) as total_word_count
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
    GROUP BY p.id
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

DELIMITER ;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ai_syory.* TO 'writingway_user'@'localhost' IDENTIFIED BY 'your_password';
-- FLUSH PRIVILEGES;

-- Display table information
SELECT 'Database schema created successfully!' as status;
SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'ai_syory' 
ORDER BY TABLE_NAME;
