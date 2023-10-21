-- this file is out-of-scope for vulnerabilities. It is used to initialize the database.
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS memes;
DROP TABLE IF EXISTS meme_shares;
DROP TABLE IF EXISTS comments;

CREATE TABLE IF NOT EXISTS users (
    username varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    password_hash varchar(255) NOT NULL,
    is_admin int DEFAULT 0
);

CREATE TABLE IF NOT EXISTS memes (
    name varchar(255) NOT NULL,
    owner int NOT NULL,
    FOREIGN KEY (owner) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS meme_shares (
    user int NOT NULL,
    meme int NOT NULL,
    FOREIGN KEY (user) REFERENCES user(rowid),
    FOREIGN KEY (meme) REFERENCES meme(rowid)
);

CREATE TABLE IF NOT EXISTS comments (
    author int NOT NULL,
    meme int NOT NULL,
    title varchar(500) NOT NULL,
    body varchar(5000) NOT NULL,
    FOREIGN KEY (author) REFERENCES user(rowid),
    FOREIGN KEY (meme) REFERENCES meme(rowid)
);