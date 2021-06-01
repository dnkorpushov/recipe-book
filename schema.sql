DROP TABLE IF EXISTS recipe_fts;
DROP TABLE IF EXISTS tag;

CREATE VIRTUAL TABLE recipe_fts USING fts5 (
    title, tags, content, mdfile, created
);

CREATE TABLE tag (
    tag TEXT NOT NULL,
    recipe_id INTEGER 
);

