/*
 Navicat Premium Data Transfer

 Source Server         : camel_lu
 Source Server Type    : MySQL
 Source Server Version : 80026
 Source Host           : localhost:3306
 Source Schema         : anchor_plan

 Target Server Type    : MySQL
 Target Server Version : 80026
 File Encoding         : 65001

 Date: 21/11/2021 01:01:38
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for fund_morning_base
-- ----------------------------
DROP TABLE IF EXISTS `fund_morning_base`;
CREATE TABLE `fund_morning_base` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `fund_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '基金代码',
  `morning_star_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '晨星专属基金代码',
  `fund_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金名称',
  `fund_cat` varchar(64) DEFAULT NULL COMMENT '基金分类',
  `company` varchar(16) DEFAULT NULL COMMENT '基金公司',
  `found_date` date DEFAULT NULL COMMENT '成立时间',
  `is_archive` tinyint NOT NULL DEFAULT '0' COMMENT '基金是否结算或者归档. 0表示正常状态，1表示已结算，2代表海外基金',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `fund_code` (`fund_code`),
  UNIQUE KEY `morning_star_code` (`morning_star_code`) USING BTREE,
  KEY `fk_fund_detail_code` (`fund_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for fund_morning_manager
-- ----------------------------
DROP TABLE IF EXISTS `fund_morning_manager`;
CREATE TABLE `fund_morning_manager` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `manager_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '基金经理id',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '基金经理名称',
  `brife` varchar(5120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金简介',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `manager_id` (`manager_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for fund_morning_quarter
-- ----------------------------
DROP TABLE IF EXISTS `fund_morning_quarter`;
CREATE TABLE `fund_morning_quarter` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `fund_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '基金代码',
  `quarter_index` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '季度编号',
  `investname_style` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '投资风格',
  `total_asset` decimal(8,2) DEFAULT NULL COMMENT '总资产',
  `manager_id` varchar(12) DEFAULT NULL COMMENT '基金经理id',
  `manager_start_date` date DEFAULT NULL COMMENT '基金经理管理起始时间',
  `three_month_retracement` decimal(8,2) DEFAULT NULL COMMENT '最差三个月回报',
  `june_month_retracement` decimal(8,2) DEFAULT NULL COMMENT '最差六个月回报',
  `risk_statistics_alpha` decimal(8,2) DEFAULT NULL COMMENT '风险统计-阿尔法',
  `risk_statistics_beta` decimal(8,2) DEFAULT NULL COMMENT '风险统计-贝塔',
  `risk_statistics_r_square` decimal(8,2) DEFAULT NULL COMMENT '风险统计-R平方',
  `risk_assessment_standard_deviation` decimal(8,2) DEFAULT NULL COMMENT '风险评估-标准差',
  `risk_assessment_risk_coefficient` decimal(8,2) DEFAULT NULL COMMENT '风险评估-晨星风险系数',
  `risk_assessment_sharpby` decimal(8,2) DEFAULT NULL COMMENT '风险评估-夏普比例',
  `risk_rating_2` int DEFAULT NULL COMMENT '风险评价-二年',
  `risk_rating_3` int DEFAULT NULL COMMENT '风险评价-三年',
  `risk_rating_5` int DEFAULT NULL COMMENT '风险评价-五年',
  `risk_rating_10` int DEFAULT NULL COMMENT '风险评价-十年',
  `stock_position_total` decimal(8,2) DEFAULT '0.00' COMMENT '股票总仓位',
  `stock_position_ten` decimal(8,2) DEFAULT '0.00' COMMENT '股票十大持仓占位',
  `bond_position_total` decimal(8,2) DEFAULT '0.00' COMMENT '债券总仓位',
  `bond_position_five` decimal(8,2) DEFAULT '0.00' COMMENT '债券五大持仓占位',
  `morning_star_rating_3` int DEFAULT NULL COMMENT '晨星评级-三年',
  `morning_star_rating_5` int DEFAULT NULL COMMENT '晨星评级-五年',
  `morning_star_rating_10` int DEFAULT NULL COMMENT '晨星评级-十年',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_code_number` (`fund_code`,`quarter_index`),
  KEY `fk_season_manager_id` (`manager_id`),
  CONSTRAINT `fk_season_base_code` FOREIGN KEY (`fund_code`) REFERENCES `fund_morning_base` (`fund_code`),
  CONSTRAINT `fk_season_manager_id` FOREIGN KEY (`manager_id`) REFERENCES `fund_morning_manager` (`manager_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for fund_morning_snapshot
-- ----------------------------
DROP TABLE IF EXISTS `fund_morning_snapshot`;
CREATE TABLE `fund_morning_snapshot` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `fund_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金代码',
  `morning_star_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '晨星专属基金代码',
  `fund_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金名称',
  `fund_cat` varchar(64) DEFAULT NULL COMMENT '基金分类',
  `fund_rating_3` int DEFAULT NULL COMMENT '晨星三年评级',
  `fund_rating_5` int DEFAULT NULL COMMENT '晨星五年评级',
  `rate_of_return` decimal(8,0) DEFAULT NULL COMMENT '今年以来收益率',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fund_code` (`fund_code`),
  UNIQUE KEY `morning_star_code` (`morning_star_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for fund_morning_snapshot_2021_q1
-- ----------------------------
DROP TABLE IF EXISTS `fund_morning_snapshot_2021_q1`;
CREATE TABLE `fund_morning_snapshot_2021_q1` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `fund_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金代码',
  `morning_star_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '晨星专属基金代码',
  `fund_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金名称',
  `fund_cat` varchar(64) DEFAULT NULL COMMENT '基金分类',
  `fund_rating_3` int DEFAULT NULL COMMENT '晨星三年评级',
  `fund_rating_5` int DEFAULT NULL COMMENT '晨星五年评级',
  `rate_of_return` decimal(8,0) DEFAULT NULL COMMENT '今年以来收益率',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fund_code` (`fund_code`),
  UNIQUE KEY `morning_star_code` (`morning_star_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for fund_morning_snapshot_2021_q2
-- ----------------------------
DROP TABLE IF EXISTS `fund_morning_snapshot_2021_q2`;
CREATE TABLE `fund_morning_snapshot_2021_q2` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `fund_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金代码',
  `morning_star_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '晨星专属基金代码',
  `fund_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金名称',
  `fund_cat` varchar(64) DEFAULT NULL COMMENT '基金分类',
  `fund_rating_3` int DEFAULT NULL COMMENT '晨星三年评级',
  `fund_rating_5` int DEFAULT NULL COMMENT '晨星五年评级',
  `rate_of_return` decimal(8,0) DEFAULT NULL COMMENT '今年以来收益率',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fund_code` (`fund_code`),
  UNIQUE KEY `morning_star_code` (`morning_star_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for fund_morning_snapshot_2021_q3
-- ----------------------------
DROP TABLE IF EXISTS `fund_morning_snapshot_2021_q3`;
CREATE TABLE `fund_morning_snapshot_2021_q3` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `fund_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金代码',
  `morning_star_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '晨星专属基金代码',
  `fund_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金名称',
  `fund_cat` varchar(64) DEFAULT NULL COMMENT '基金分类',
  `fund_rating_3` int DEFAULT NULL COMMENT '晨星三年评级',
  `fund_rating_5` int DEFAULT NULL COMMENT '晨星五年评级',
  `rate_of_return` decimal(8,0) DEFAULT NULL COMMENT '今年以来收益率',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fund_code` (`fund_code`),
  UNIQUE KEY `morning_star_code` (`morning_star_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for fund_morning_stock_info
-- ----------------------------
DROP TABLE IF EXISTS `fund_morning_stock_info`;
CREATE TABLE `fund_morning_stock_info` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `fund_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基金代码',
  `quarter_index` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '季度编号',
  `stock_position_total` decimal(8,2) DEFAULT NULL COMMENT '股票持仓比例',
  `top_stock_0_code` varchar(32) DEFAULT NULL,
  `top_stock_0_name` varchar(255) DEFAULT NULL,
  `top_stock_0_portion` decimal(8,2) DEFAULT NULL COMMENT '股票所占比率',
  `top_stock_0_market` varchar(16) DEFAULT NULL,
  `top_stock_1_code` varchar(32) DEFAULT NULL,
  `top_stock_1_name` varchar(255) DEFAULT NULL,
  `top_stock_1_portion` decimal(8,2) DEFAULT NULL COMMENT '股票所占比率',
  `top_stock_1_market` varchar(16) DEFAULT NULL,
  `top_stock_2_code` varchar(32) DEFAULT NULL,
  `top_stock_2_name` varchar(255) DEFAULT NULL,
  `top_stock_2_portion` decimal(8,2) DEFAULT NULL COMMENT '股票所占比率',
  `top_stock_2_market` varchar(16) DEFAULT NULL,
  `top_stock_3_code` varchar(32) DEFAULT NULL,
  `top_stock_3_name` varchar(255) DEFAULT NULL,
  `top_stock_3_portion` decimal(8,2) DEFAULT NULL COMMENT '股票所占比率',
  `top_stock_3_market` varchar(16) DEFAULT NULL,
  `top_stock_4_code` varchar(32) DEFAULT NULL,
  `top_stock_4_name` varchar(255) DEFAULT NULL,
  `top_stock_4_portion` decimal(8,2) DEFAULT NULL COMMENT '股票所占比率',
  `top_stock_4_market` varchar(16) DEFAULT NULL,
  `top_stock_5_code` varchar(32) DEFAULT NULL,
  `top_stock_5_name` varchar(255) DEFAULT NULL,
  `top_stock_5_portion` decimal(8,2) DEFAULT NULL COMMENT '股票所占比率',
  `top_stock_5_market` varchar(16) DEFAULT NULL,
  `top_stock_6_code` varchar(32) DEFAULT NULL,
  `top_stock_6_name` varchar(255) DEFAULT NULL,
  `top_stock_6_portion` decimal(8,2) DEFAULT NULL COMMENT '股票所占比率',
  `top_stock_6_market` varchar(16) DEFAULT NULL,
  `top_stock_7_code` varchar(32) DEFAULT NULL,
  `top_stock_7_name` varchar(255) DEFAULT NULL,
  `top_stock_7_portion` decimal(8,2) DEFAULT NULL COMMENT '股票所占比率',
  `top_stock_7_market` varchar(16) DEFAULT NULL,
  `top_stock_8_code` varchar(32) DEFAULT NULL,
  `top_stock_8_name` varchar(255) DEFAULT NULL,
  `top_stock_8_portion` decimal(8,2) DEFAULT NULL COMMENT '股票所占比率',
  `top_stock_8_market` varchar(16) DEFAULT NULL,
  `top_stock_9_code` varchar(32) DEFAULT NULL,
  `top_stock_9_name` varchar(255) DEFAULT NULL,
  `top_stock_9_portion` decimal(8,2) DEFAULT NULL COMMENT '股票所占比率',
  `top_stock_9_market` varchar(16) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uni_fund_code_season` (`fund_code`,`quarter_index`),
  KEY `fk_fund_detail_code` (`fund_code`),
  CONSTRAINT `fk_fund_season_code` FOREIGN KEY (`fund_code`) REFERENCES `fund_morning_base` (`fund_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
