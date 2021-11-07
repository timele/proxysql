-- common settings
SET global log_output = 'file';
SET global general_log = 1;
SET global connect_timeout = 600; -- connection establish timeout
SET global tls_version='TLSv1.3';

create database if not exists testdatabase;
use testdatabase;

-- table cats
CREATE TABLE if not exists cats
(
  id              INT unsigned NOT NULL AUTO_INCREMENT, -- Unique ID for the record
  name            VARCHAR(150) NOT NULL,                -- Name of the cat
  owner           VARCHAR(150) NOT NULL,                -- Owner of the cat
  birth           DATE NOT NULL,                        -- Birthday of the cat
  PRIMARY KEY     (id)                                  -- Make the id the primary key
);

-- cats data
INSERT INTO cats ( name, owner, birth) VALUES
  ( 'Sandy', 'Lennon', '2015-01-03' ),
  ( 'Cookie', 'Casey', '2013-11-13' ),
  ( 'Charlie', 'River', '2016-05-21' );

-- access privileges
CREATE USER testuser@'%' IDENTIFIED BY 'testuser';
GRANT ALL PRIVILEGES ON testdatabase.* TO 'testuser'@'%';
GRANT ALL PRIVILEGES ON testdatabase.* TO 'root'@'%';
-- allow passwordless login for root from localhost
-- ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '';
FLUSH PRIVILEGES;
