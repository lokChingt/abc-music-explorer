DROP TABLE IF EXISTS tunes;
CREATE TABLE tunes
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    book            VARCHAR(10) NOT NULL,
    tune_id         VARCHAR(20) NOT NULL,
    title           VARCHAR(255),
    tune_type       VARCHAR(50),
    key_signature   VARCHAR(20),
    notation        TEXT
);

DROP TABLE IF EXISTS tune_alt_titles;
CREATE TABLE tune_alt_titles
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    tune_id         INT,
    alt_title       VARCHAR(255),
    FOREIGN KEY (tune_id) REFERENCES tunes(id)
);