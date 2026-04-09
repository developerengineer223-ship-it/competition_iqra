-- Allama Iqbal Platform Database Schema (PostgreSQL)

CREATE TABLE verses (
  id SERIAL PRIMARY KEY,
  poem_id INT,
  text_urdu TEXT NOT NULL,
  text_persian TEXT,
  order_in_poem INT,
  metadata JSONB
);

CREATE TABLE translations (
  id SERIAL PRIMARY KEY,
  verse_id INT REFERENCES verses(id),
  language VARCHAR(10),
  text TEXT,
  translator VARCHAR(100),
  notes TEXT
);

CREATE TABLE historical_context (
  id SERIAL PRIMARY KEY,
  verse_id INT REFERENCES verses(id),
  context_text TEXT,
  sources TEXT
);

CREATE TABLE commentary (
  id SERIAL PRIMARY KEY,
  verse_id INT REFERENCES verses(id),
  user_id INT,
  text TEXT,
  scholarly_flag BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  role VARCHAR(20),
  premium_status BOOLEAN DEFAULT FALSE
);

CREATE TABLE bookmarks (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  verse_id INT REFERENCES verses(id),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_progress (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  verse_id INT REFERENCES verses(id),
  status VARCHAR(20),
  last_accessed TIMESTAMP
);

CREATE INDEX idx_verse_text_urdu ON verses USING GIN (to_tsvector('simple', text_urdu));
CREATE INDEX idx_translation_text ON translations USING GIN (to_tsvector('simple', text));
CREATE INDEX idx_verse_id_language ON translations(verse_id, language);
