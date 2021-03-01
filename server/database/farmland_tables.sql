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

DROP TABLE IF EXISTS `USER`;
CREATE TABLE `USER` (
  `USERNAME` varchar(8) NOT NULL,
  `PASSWORD` varchar(8) NOT NULL,
  PRIMARY KEY (`USERNAME`)
);

DROP TABLE IF EXISTS `OASIS_TRAINING`;
CREATE TABLE `OASIS_TRAINING` (
  `NODE_ID` varchar(32) NOT NULL,
  `VALUE` varchar(32) NOT NULL,
  `MESSAGE_ID` varchar(32) NOT NULL,
  `TIMESTAMP` varchar(64) NOT NULL,
  PRIMARY KEY (`NODE_ID`,`VALUE`)
);

DROP TABLE IF EXISTS `OASIS_ANALYTIC`;
CREATE TABLE `OASIS_ANALYTIC` (
  `TIMESTAMP` varchar(64) NOT NULL,
  `TYPE` varchar(32) NOT NULL,
  `DATA` json DEFAULT NULL,
  PRIMARY KEY (`TIMESTAMP`,`TYPE`)
);

DROP TABLE IF EXISTS `MONITOR`;
CREATE TABLE `MONITOR` (
  `TIMESTAMP` varchar(64) NOT NULL,
  `TYPE` varchar(32) NOT NULL, --IRRIGATION, ANALYSIS, WATER_TANK
  `DATA` json DEFAULT NULL,
  PRIMARY KEY (`TIMESTAMP`,`TYPE`)
);

DROP TABLE IF EXISTS `PRICES`;
CREATE TABLE `PRICES` (
  `SOURCE` VARCHAR(16) NOT NULL,
  `DATE` DATE NOT NULL,
  `DATA` JSON NULL,
  PRIMARY KEY (`SOURCE`, `DATE`));

-- MANAGEMENT STUFF
DROP TABLE IF EXISTS `CROP`;
CREATE TABLE `CROP` (
  `CODE` int(8) NOT NULL AUTO_INCREMENT,
  `DATE` DATE NOT NULL,
  `STATUS` varchar(16) NOT NULL,
  `NOTES` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`CODE`)
);
ALTER TABLE `CROP` AUTO_INCREMENT=10000001;

DROP TABLE IF EXISTS `SUPPLIER`;
CREATE TABLE `SUPPLIER` (
  `NAME` varchar(64) NOT NULL,
  `TYPE` varchar(32) DEFAULT NULL,
  `PHONE` varchar(16) DEFAULT NULL,
  `EMAIL` varchar(32) DEFAULT NULL,
  `CITY` varchar(32) DEFAULT NULL,
  `STATE` varchar(2) DEFAULT NULL,
  `NOTES` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`NAME`)
);
