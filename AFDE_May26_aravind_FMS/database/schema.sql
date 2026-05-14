-- Feedback Management System – Database Schema
-- Compatible with SQLite and PostgreSQL

CREATE TABLE IF NOT EXISTS feedback (
    feedback_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_name VARCHAR(100)  NOT NULL,
    program_name     VARCHAR(200)  NOT NULL,
    rating           INTEGER       NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comments         TEXT,
    submitted_at     DATETIME      DEFAULT CURRENT_TIMESTAMP
);

-- Sample seed data
INSERT INTO feedback (participant_name, program_name, rating, comments) VALUES
  ('Alice Johnson',  'React Workshop 2025',        5, 'Excellent workshop! Hands-on sessions were very helpful.'),
  ('Bob Smith',      'Python for Data Engineers',  4, 'Great content. Could use more real-world examples.'),
  ('Carol Williams', 'FastAPI Masterclass',         5, 'Loved the live coding sessions and clear explanations.'),
  ('David Brown',    'React Workshop 2025',         3, 'Good but felt rushed towards the end.'),
  ('Eva Martinez',   'Docker & Kubernetes',         4, 'Very informative. Labs were well structured.');
