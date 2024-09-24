-- MySQL dump 10.13  Distrib 8.0.39, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: vin
-- ------------------------------------------------------
-- Server version	9.0.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Dashboard`
--

DROP TABLE IF EXISTS `Dashboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Dashboard` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `recorded_date_time` varchar(255) NOT NULL,
  `count` bigint NOT NULL,
  `defects_id` bigint NOT NULL,
  `department_id` bigint NOT NULL,
  `machines_id` bigint NOT NULL,
  `plant_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Dashboard_defects_id_ad8149c4_fk_Defects_id` (`defects_id`),
  KEY `Dashboard_department_id_e9e101a1_fk_Department_id` (`department_id`),
  KEY `Dashboard_machines_id_4ae7d5b7_fk_Machines_id` (`machines_id`),
  KEY `Dashboard_plant_id_5756615a_fk_Plant_id` (`plant_id`),
  KEY `Dashboard_product_id_9c456f9a_fk_Products_id` (`product_id`),
  KEY `Dashboard_recorde_603b18_idx` (`recorded_date_time`),
  CONSTRAINT `Dashboard_defects_id_ad8149c4_fk_Defects_id` FOREIGN KEY (`defects_id`) REFERENCES `Defects` (`id`),
  CONSTRAINT `Dashboard_department_id_e9e101a1_fk_Department_id` FOREIGN KEY (`department_id`) REFERENCES `Department` (`id`),
  CONSTRAINT `Dashboard_machines_id_4ae7d5b7_fk_Machines_id` FOREIGN KEY (`machines_id`) REFERENCES `Machines` (`id`),
  CONSTRAINT `Dashboard_plant_id_5756615a_fk_Plant_id` FOREIGN KEY (`plant_id`) REFERENCES `Plant` (`id`),
  CONSTRAINT `Dashboard_product_id_9c456f9a_fk_Products_id` FOREIGN KEY (`product_id`) REFERENCES `Products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=364 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Dashboard`
--

/*!40000 ALTER TABLE `Dashboard` DISABLE KEYS */;
INSERT INTO `Dashboard` VALUES (1,'2024-07-29',133,35,2,5,3,5),(2,'2024-07-29',833,32,2,5,3,5),(258,'2024-07-29',506,33,2,5,3,5),(281,'2024-07-21',28,33,2,5,3,5),(282,'2024-07-21',2362,34,2,5,3,5),(283,'2024-07-21',199,32,2,5,3,5),(284,'2024-07-22',3955,34,2,5,3,5),(285,'2024-07-22',877,32,2,5,3,5),(286,'2024-07-22',54,33,2,5,3,5),(287,'2024-07-22',80,35,2,5,3,5),(288,'2024-07-23',978,32,2,5,3,5),(289,'2024-07-23',176,35,2,5,3,5),(290,'2024-07-23',190,33,2,5,3,5),(291,'2024-07-23',65,34,2,5,3,5),(292,'2024-07-24',1980,32,2,5,3,5),(293,'2024-07-24',318,33,2,5,3,5),(294,'2024-07-24',229,34,2,5,3,5),(295,'2024-07-25',158,34,2,5,3,5),(296,'2024-07-25',1845,32,2,5,3,5),(297,'2024-07-25',352,33,2,5,3,5),(298,'2024-07-25',67,35,2,5,3,5),(299,'2024-07-26',795,32,2,5,3,5),(300,'2024-07-26',146,33,2,5,3,5),(301,'2024-07-26',453,34,2,5,3,5),(302,'2024-07-26',207,35,2,5,3,5),(303,'2024-07-26',21,37,2,5,3,5),(304,'2024-07-27',250,35,2,5,3,5),(305,'2024-07-27',787,32,2,5,3,5),(306,'2024-07-27',133,34,2,5,3,5),(307,'2024-07-27',173,33,2,5,3,5),(308,'2024-07-27',73,37,2,5,3,5),(309,'2024-07-28',224,35,2,5,3,5),(310,'2024-07-28',1485,32,2,5,3,5),(311,'2024-07-28',67,33,2,5,3,5),(312,'2024-07-28',31,34,2,5,3,5),(313,'2024-07-28',1,37,2,5,3,5),(314,'2024-07-29',27,34,2,5,3,5),(315,'2024-07-29',197,37,2,5,3,5),(316,'2024-07-30',498,35,2,5,3,5),(317,'2024-07-30',877,32,2,5,3,5),(318,'2024-07-30',918,33,2,5,3,5),(319,'2024-07-30',302,34,2,5,3,5),(320,'2024-07-31',1172,32,2,5,3,5),(321,'2024-07-31',359,35,2,5,3,5),(322,'2024-07-31',73,34,2,5,3,5),(323,'2024-07-31',74,33,2,5,3,5),(324,'2024-08-01',408,35,2,5,3,5),(325,'2024-08-01',80,33,2,5,3,5),(326,'2024-08-01',381,32,2,5,3,5),(327,'2024-08-01',63,34,2,5,3,5),(328,'2024-08-01',13,37,2,5,3,5),(329,'2024-08-02',61,34,2,5,3,5),(330,'2024-08-02',193,33,2,5,3,5),(331,'2024-08-02',812,32,2,5,3,5),(332,'2024-08-02',226,35,2,5,3,5),(333,'2024-08-02',94,37,2,5,3,5),(334,'2024-08-03',895,32,2,5,3,5),(335,'2024-08-03',288,35,2,5,3,5),(336,'2024-08-03',53,33,2,5,3,5),(337,'2024-08-03',29,37,2,5,3,5),(338,'2024-08-03',5,34,2,5,3,5),(339,'2024-08-04',318,35,2,5,3,5),(340,'2024-08-04',1023,32,2,5,3,5),(341,'2024-08-04',23,34,2,5,3,5),(342,'2024-08-04',49,37,2,5,3,5),(343,'2024-08-04',43,33,2,5,3,5),(344,'2024-08-05',159,35,2,5,3,5),(345,'2024-08-05',212,37,2,5,3,5),(346,'2024-08-05',74,34,2,5,3,5),(347,'2024-08-05',678,32,2,5,3,5),(348,'2024-08-05',497,33,2,5,3,5),(349,'2024-08-06',123,33,2,5,3,5),(350,'2024-08-06',900,32,2,5,3,5),(351,'2024-08-06',117,35,2,5,3,5),(352,'2024-08-06',90,34,2,5,3,5),(353,'2024-08-06',7,37,2,5,3,5),(354,'2024-08-07',61,35,2,5,3,5),(355,'2024-08-07',297,33,2,5,3,5),(356,'2024-08-07',25,34,2,5,3,5),(357,'2024-08-07',747,32,2,5,3,5),(358,'2024-08-07',1,37,2,5,3,5),(359,'2024-08-08',143,33,2,5,3,5),(360,'2024-08-08',1310,32,2,5,3,5),(361,'2024-08-08',107,35,2,5,3,5),(362,'2024-08-08',79,34,2,5,3,5),(363,'2024-08-08',9,37,2,5,3,5);
/*!40000 ALTER TABLE `Dashboard` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-08 17:13:37
