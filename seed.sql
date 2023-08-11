-- Create tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    image_url TEXT DEFAULT '/static/images/default-pic.png',
    password TEXT NOT NULL
);

CREATE TABLE saves (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL UNIQUE,
    title TEXT,
    used BOOLEAN NOT NULL,
    rating INTEGER DEFAULT 0,
    notes TEXT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE plan (
    id SERIAL PRIMARY KEY,
    meal_id INTEGER NOT NULL UNIQUE,
    title TEXT,
    day_of_week TEXT DEFAULT '<day of week>',
    meal_of_day TEXT DEFAULT '<meal of day>',
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER NOT NULL,
    name TEXT,
    aisle TEXT,
    amount_metric NUMERIC,
    amount_us NUMERIC,
    unit_metric TEXT,
    unit_us TEXT,
    meal_id INTEGER REFERENCES plan(meal_id) ON DELETE CASCADE
);

-- Insert default values for day_of_week and meal_of_day
UPDATE plan SET day_of_week = '<day of week>';
UPDATE plan SET meal_of_day = '<meal of day>';
