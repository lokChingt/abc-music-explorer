DROP DATABASE IF EXISTS tunes;
CREATE TABLE tunes
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    book            INT,
    tune_id         VARCHAR(20),
    title           VARCHAR(255),
    alt_title       VARCHAR(255),
    tune_type       VARCHAR(50),
    key_signature   VARCHAR(20),
    notation        TEXT
);

DROP DATABASE IF EXISTS tune_alt_titles;
CREATE TABLE tune_alt_titles
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    book            INT,
    tune_id         VARCHAR(20),
    alt_title       VARCHAR(255),
);