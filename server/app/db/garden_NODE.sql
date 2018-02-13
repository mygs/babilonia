-- MySQL dump 10.13  Distrib 5.7.21, for Linux (x86_64)
--
-- Host: 192.168.1.60    Database: garden
-- ------------------------------------------------------
-- Server version	5.7.21-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `NODE`
--

DROP TABLE IF EXISTS `NODE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `NODE` (
  `ID` varchar(64) NOT NULL,
  `TEMPERATURE_THRESHOLD` decimal(8,4) NOT NULL DEFAULT '25.0000',
  `MOISTURE_THRESHOLD` varchar(64) DEFAULT NULL,
  `MASK_CRON_LIGHT_ON` varchar(64) NOT NULL DEFAULT '0 11 * *',
  `MASK_CRON_LIGHT_OFF` varchar(64) NOT NULL DEFAULT '0 20 * * *',
  `MASK_CRON_CTRL` varchar(64) NOT NULL DEFAULT '*/2 * * * *',
  `LAST_UPDATE` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-02-04  7:27:25
INSERT INTO NODE (ID,TEMPERATURE_THRESHOLD,MASK_CRON_LIGHT_ON,MASK_CRON_LIGHT_OFF,MASK_CRON_CTRL,LAST_UPDATE)
 					VALUES ('3765036',25,'0 11 * * *','0 20 * * *','* * * * *','1516559314');
INSERT INTO NODE (ID,TEMPERATURE_THRESHOLD,MASK_CRON_LIGHT_ON,MASK_CRON_LIGHT_OFF,MASK_CRON_CTRL,LAST_UPDATE)
					VALUES ('3766664',25,'0 12 * * *','0 22 * * *','*/3 * * * *','1515921048');
COMMIT;
