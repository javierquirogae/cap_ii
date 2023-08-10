CREATE TABLE saves (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL UNIQUE,
    used BOOLEAN NOT NULL,
    rating INTEGER DEFAULT 0,
    notes TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    image_url TEXT DEFAULT '/static/images/default-pic.png',
    password TEXT NOT NULL
);