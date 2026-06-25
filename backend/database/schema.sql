CREATE TABLE users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(255) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE meetings (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    title VARCHAR(255) NOT NULL,

    source_type ENUM(
        'upload',
        'youtube'
    ) NOT NULL,

    source_url TEXT,

    file_path TEXT,

    transcript LONGTEXT,

    summary LONGTEXT,

    key_points LONGTEXT,

    tasks LONGTEXT,

    decisions LONGTEXT,

    status ENUM(
        'processing',
        'completed',
        'failed'
    ) DEFAULT 'processing',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(id)

);

CREATE TABLE chat_messages (

    id INT AUTO_INCREMENT PRIMARY KEY,

    meeting_id INT NOT NULL,

    user_id INT NOT NULL,

    sender ENUM(
        'user',
        'assistant'
    ) NOT NULL,

    question LONGTEXT NOT NULL,

    answer LONGTEXT NOT NULL,

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (meeting_id)
    REFERENCES meetings(id),

    FOREIGN KEY (user_id)
    REFERENCES users(id)

);

CREATE TABLE live_meetings (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    title VARCHAR(255),

    transcript LONGTEXT,

    status ENUM(
        'active',
        'ended'
    ) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(id)

);