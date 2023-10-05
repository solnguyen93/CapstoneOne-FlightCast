-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS feedback;

-- Connect to the database
\c feedback;

-- Create tables
CREATE TABLE users (
    username VARCHAR(20) PRIMARY KEY,
    password TEXT NOT NULL,
    email VARCHAR(50) NOT NULL,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL
);

CREATE TABLE feedbacks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    user_username VARCHAR(20) REFERENCES users(username)
);

-- Insert sample data
INSERT INTO users (username, password, email, first_name, last_name) VALUES
    ('user1', 'user1', 'user1@example.com', 'user1', 'user1'),
    ('user2', 'user2', 'user2@example.com', 'user2', 'user2');

INSERT INTO feedbacks (title, content, user_username) VALUES
    ('Feedback 1 Title', 'Feedback 1 Content', 'user1'),
    ('Feedback 2 Title', 'Feedback 2 Content', 'user1'),
    ('Feedback 3 Title', 'Feedback 3 Content', 'user2');
