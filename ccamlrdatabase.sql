-- phpMyAdmin SQL Dump
-- version 2.11.2.1
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2018 年 06 月 15 日 05:24
-- 服务器版本: 5.0.45
-- PHP 版本: 5.2.5

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- 数据库: `ccamlrnews`
--

-- --------------------------------------------------------

--
-- 表的结构 `news`
--

CREATE TABLE `news` (
  `newsId` int(11) NOT NULL auto_increment,
  `newsTitle` varchar(150) NOT NULL,
  `newsURL` varchar(150) NOT NULL,
  `newsDate` varchar(30) NOT NULL,
  `newsContent` varchar(10240) NOT NULL,
  PRIMARY KEY  (`newsId`),
  UNIQUE KEY `newsTitle_UNIQUE` (`newsTitle`),
  UNIQUE KEY `newsURL_UNIQUE` (`newsURL`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 导出表中的数据 `news`
--

