CREATE DATABASE farmland;
CREATE USER 'babilonia'@'localhost' IDENTIFIED BY 'mypass';
CREATE USER 'babilonia'@'%' IDENTIFIED BY 'mypass';
GRANT ALL ON farmland.* TO 'babilonia'@'localhost';
GRANT ALL ON farmland.* TO 'babilonia'@'%';
flush privileges;
