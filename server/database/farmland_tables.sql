DROP TABLE IF EXISTS `OASIS_HEARTBEAT`;
CREATE TABLE `OASIS_HEARTBEAT` (
  `NODE_ID` varchar(32) NOT NULL,
  `LAST_UPDATE` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`NODE_ID`)
);


DROP TABLE IF EXISTS `OASIS_DATA`;
CREATE TABLE `OASIS_DATA` (
  `NODE_ID` VARCHAR(32) NOT NULL,
  `TIMESTAMP` VARCHAR(64) NOT NULL,
  `DATA` JSON NULL,
  PRIMARY KEY (`NODE_ID`, `TIMESTAMP`));
