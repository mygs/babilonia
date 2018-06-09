DROP TABLE IF EXISTS `NODE`;
CREATE TABLE `NODE` (
  `ID` varchar(64) NOT NULL,
  `NAME` varchar(64) DEFAULT NULL,
  `TEMPERATURE_THRESHOLD` decimal(4,2) NOT NULL DEFAULT '25.00',
  `MOISTURE_THRESHOLD` varchar(64) DEFAULT NULL,
  `MASK_CRON_LIGHT_ON` varchar(64) NOT NULL DEFAULT '0 11 * *',
  `MASK_CRON_LIGHT_OFF` varchar(64) NOT NULL DEFAULT '0 20 * * *',
  `MASK_CRON_CTRL` varchar(64) NOT NULL DEFAULT '*/2 * * * *',
  `SLEEP_TIME_SPRINKLE` varchar(64) DEFAULT '29000000',
  `LAST_UPDATE` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


INSERT INTO `NODE` (`ID`,`NAME`,`TEMPERATURE_THRESHOLD`,`MASK_CRON_LIGHT_ON`,`MASK_CRON_LIGHT_OFF`,`MASK_CRON_CTRL`,`LAST_UPDATE`)
    VALUES ('3765036','OASIS 1',25.00,'0 21 * * *','0 21 * * *','* * * * *','1521298304');
INSERT INTO `NODE` (`ID`,`NAME`,`TEMPERATURE_THRESHOLD`,`MASK_CRON_LIGHT_ON`,`MASK_CRON_LIGHT_OFF`,`MASK_CRON_CTRL`,`LAST_UPDATE`)
    VALUES ('3766664','OASIS 2',30.00,'0 12 * * *','0 20 * * *','*/10 * * * *','1526595770');
INSERT INTO `NODE` (`ID`,`NAME`,`TEMPERATURE_THRESHOLD`,`MASK_CRON_LIGHT_ON`,`MASK_CRON_LIGHT_OFF`,`MASK_CRON_CTRL`,`LAST_UPDATE`)
    VALUES ('3767310','OASIS 3',25.00,'0 11 * * *','0 20 * * *','*/10 * * * *','1528023949');


COMMIT;
