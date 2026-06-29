-- =====================================================
-- DATABASE
-- =====================================================

CREATE DATABASE IF NOT EXISTS whisp
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE whisp;

-- =====================================================
-- USERS
-- =====================================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MEETINGS (UPLOAD + YOUTUBE)
-- =====================================================

CREATE TABLE meetings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,

    title VARCHAR(255) NOT NULL,

    source_type ENUM('upload', 'youtube') NOT NULL,
    source_url TEXT NULL,
    file_path TEXT NULL,

    transcript LONGTEXT NULL,
    summary LONGTEXT NULL,
    key_points LONGTEXT NULL,
    tasks LONGTEXT NULL,
    decisions LONGTEXT NULL,

    status ENUM('processing', 'completed', 'failed', 'deleted')
        DEFAULT 'processing',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =====================================================
-- LIVE MEETINGS (REAL-TIME AUDIO / STREAM)
-- =====================================================

CREATE TABLE live_meetings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,

    title VARCHAR(255) NOT NULL,

    transcript LONGTEXT NULL,
    summary LONGTEXT NULL,

    status ENUM('active', 'ended') DEFAULT 'active',

    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =====================================================
-- CHAT (RAG / QA HISTORY)
-- =====================================================

CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,

    meeting_id INT NOT NULL,
    user_id INT NOT NULL,

    sender ENUM('user', 'assistant') NOT NULL,

    question LONGTEXT NOT NULL,
    answer LONGTEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =====================================================
-- INDEXES (PERFORMANCE)
-- =====================================================

CREATE INDEX idx_users_email ON users(email);

CREATE INDEX idx_meetings_user ON meetings(user_id);
CREATE INDEX idx_meetings_status ON meetings(status);
CREATE INDEX idx_meetings_source ON meetings(source_type);

CREATE INDEX idx_live_user ON live_meetings(user_id);
CREATE INDEX idx_live_status ON live_meetings(status);

CREATE INDEX idx_chat_user ON chat_messages(user_id);
CREATE INDEX idx_chat_meeting ON chat_messages(meeting_id);