/*
 Navicat Premium Data Transfer

 Source Server         : camel_lu
 Source Server Type    : MySQL
 Source Server Version : 80026
 Source Host           : localhost:3306
 Source Schema         : anchor_plan_stock

 Target Server Type    : MySQL
 Target Server Version : 80026
 File Encoding         : 65001

 Date: 21/11/2021 01:01:51
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for shen_wan_industry
-- ----------------------------
DROP TABLE IF EXISTS `shen_wan_industry`;
CREATE TABLE `shen_wan_industry` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `industry_code` varchar(10) NOT NULL COMMENT '行业代码',
  `industry_name` varchar(24) NOT NULL COMMENT '行业名称',
  `industry_type` tinyint(1) NOT NULL COMMENT '行业类型，0：一级分类；1：二级类型；2：三级类型',
  `p_industry_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '父级行业行业代码，如果是一级行业，为’S’',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uni_industry_code` (`industry_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for stock_industry
-- ----------------------------
DROP TABLE IF EXISTS `stock_industry`;
CREATE TABLE `stock_industry` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `stock_code` varchar(10) NOT NULL COMMENT '股票代码',
  `stock_name` varchar(24) NOT NULL COMMENT '股票名称',
  `industry_code_first` varchar(10) NOT NULL COMMENT '一级行业代码',
  `industry_name_first` varchar(255) NOT NULL COMMENT '一级行业名称',
  `industry_code_second` varchar(10) NOT NULL COMMENT '二级级行业代码',
  `industry_name_second` varchar(255) NOT NULL COMMENT '二级行业名称',
  `industry_code_third` varchar(10) NOT NULL COMMENT '二级级行业代码',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `industry_name_third` varchar(255) NOT NULL COMMENT '三级行业名称',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uni_stock_code` (`stock_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
