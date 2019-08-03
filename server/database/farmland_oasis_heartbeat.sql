DROP TABLE IF EXISTS `OASIS_HEARTBEAT`;
CREATE TABLE `OASIS_HEARTBEAT` (
  `NODE_ID` varchar(32) NOT NULL,
  `LAST_UPDATE` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`NODE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
