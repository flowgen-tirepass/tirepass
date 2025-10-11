/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-12.0.2-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: itire_db
-- ------------------------------------------------------
-- Server version	12.0.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `customer_discounts`
--

DROP TABLE IF EXISTS `customer_discounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_discounts` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customer_code` varchar(10) NOT NULL COMMENT '고객 코드',
  `brand` varchar(50) NOT NULL COMMENT '브랜드명',
  `group_id` bigint(20) DEFAULT NULL COMMENT '그룹ID',
  `discount_rate` decimal(5,2) DEFAULT 0.00 COMMENT '할인율(%)',
  `priority` int(11) DEFAULT 0 COMMENT '우선순위',
  `start_date` date DEFAULT NULL COMMENT '시작일',
  `end_date` date DEFAULT NULL COMMENT '종료일',
  `memo` text DEFAULT NULL COMMENT '메모',
  `is_active` tinyint(1) DEFAULT 1 COMMENT '활성화 여부',
  `created_at` datetime DEFAULT current_timestamp() COMMENT '생성일시',
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '수정일시',
  `created_by` varchar(50) DEFAULT NULL COMMENT '생성자',
  `updated_by` varchar(50) DEFAULT NULL COMMENT '수정자',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_customer_brand_group` (`customer_code`,`brand`,`group_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `customer_discounts_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `brand_groups` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `customer_product_discounts`
--

DROP TABLE IF EXISTS `customer_product_discounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_product_discounts` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customer_code` varchar(10) NOT NULL,
  `product_code` varchar(20) NOT NULL,
  `additional_discount_rate` decimal(5,2) NOT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `memo` longtext DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `priority` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `brand` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `customer_product_discoun_customer_code_product_co_6fd29911_uniq` (`customer_code`,`product_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `year_allocations`
--

DROP TABLE IF EXISTS `year_allocations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `year_allocations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `goods_code` varchar(20) NOT NULL,
  `year_2025` int(11) NOT NULL,
  `year_2024` int(11) NOT NULL,
  `year_2023` int(11) NOT NULL,
  `year_2022` int(11) NOT NULL,
  `year_2021_before` int(11) NOT NULL,
  `year_2024_discount` decimal(5,2) DEFAULT 0.00 COMMENT '2024년 할인율(%)',
  `year_2023_discount` decimal(5,2) DEFAULT 0.00 COMMENT '2023년 할인율(%)',
  `year_2022_discount` decimal(5,2) DEFAULT 0.00 COMMENT '2022년 할인율(%)',
  `year_2021_before_discount` decimal(5,2) DEFAULT 0.00 COMMENT '2021년 이전 할인율(%)',
  `last_updated` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `year_allocations_goods_code_81a5f7ce_uniq` (`goods_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `discount_history`
--

DROP TABLE IF EXISTS `discount_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `discount_history` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customer_code` varchar(10) NOT NULL COMMENT '고객 코드',
  `product_code` varchar(50) NOT NULL COMMENT '상품 코드',
  `brand` varchar(50) DEFAULT NULL COMMENT '브랜드',
  `group_id` bigint(20) DEFAULT NULL COMMENT '그룹ID',
  `basic_discount` decimal(5,2) DEFAULT NULL COMMENT '기본 할인율',
  `customer_discount` decimal(5,2) DEFAULT NULL COMMENT '고객 할인율',
  `applied_discount` decimal(5,2) DEFAULT NULL COMMENT '적용 할인율',
  `original_price` decimal(10,2) DEFAULT NULL COMMENT '원가',
  `final_price` decimal(10,2) DEFAULT NULL COMMENT '최종가격',
  `transaction_date` datetime DEFAULT current_timestamp() COMMENT '거래일시',
  PRIMARY KEY (`id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `discount_history_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `brand_groups` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-10-09 14:35:56
