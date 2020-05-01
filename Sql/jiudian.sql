CREATE TABLE `hotel` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `hotel_id` int(10) NOT NULL COMMENT '美团酒店id',
  `name` varchar(500) NOT NULL DEFAULT '',
  `score` varchar(45) NOT NULL DEFAULT '' COMMENT '评分',
  `area` varchar(500) NOT NULL DEFAULT '' COMMENT '所在区域名称',
  `address` varchar(500) NOT NULL COMMENT '地址',
  `city` varchar(50) NOT NULL DEFAULT '' COMMENT '城市名字',
  `update_time` int(10) NOT NULL DEFAULT '0',
  `lng` float DEFAULT NULL COMMENT '经度',
  `lat` float DEFAULT NULL COMMENT '纬度',
  `introduction` text COMMENT '具体描述',
  `hotelStar` varchar(255) DEFAULT NULL COMMENT '酒店类型',
  `poiAttrTagList` varchar(255) DEFAULT NULL COMMENT '酒店主题',
  `useRuleTime` varchar(255) DEFAULT NULL COMMENT '入住退房规则',
  `positionDesc` varchar(255) DEFAULT NULL COMMENT '位置具体描述',
  PRIMARY KEY (`id`),
  UNIQUE KEY `hotel_id_UNIQUE` (`hotel_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1583 DEFAULT CHARSET=utf8mb4;



CREATE TABLE `hotel_desc` (
  `hotel_id` int(10) NOT NULL COMMENT '美团酒店id',
  `name` varchar(500) NOT NULL DEFAULT '',
  `score` varchar(45) NOT NULL DEFAULT '' COMMENT '评分',
  `area` varchar(500) NOT NULL DEFAULT '' COMMENT '所在区域名称',
  `address` varchar(500) NOT NULL COMMENT '地址',
  `city` varchar(50) NOT NULL DEFAULT '' COMMENT '城市名字',
  `update_time` int(10) NOT NULL DEFAULT '0',
  `lng` float DEFAULT NULL COMMENT '经度',
  `lat` float DEFAULT NULL COMMENT '纬度',
  `introduction` text COMMENT '具体描述',
  `hotelStar` varchar(255) DEFAULT NULL COMMENT '酒店类型',
  `poiAttrTagList` varchar(255) DEFAULT NULL COMMENT '酒店主题',
  `useRuleTime` varchar(255) DEFAULT NULL COMMENT '入住退房规则',
  `positionDesc` varchar(255) DEFAULT NULL COMMENT '位置具体描述',
  `goods_id` int(10) NOT NULL COMMENT '美团的房间id',
  `room_name` varchar(200) NOT NULL DEFAULT '',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `inv_remain` varchar(45) NOT NULL DEFAULT '' COMMENT '剩余房间数  -1不可用,0满房，inf:可预定（不知道有多少剩余房间）',
  `desc` varchar(500) NOT NULL DEFAULT '' COMMENT '拼接的描述信息',
  `use_time` varchar(300) NOT NULL DEFAULT '' COMMENT '入住时间（可用时间）',
  `rooms_update_time` int(10) NOT NULL DEFAULT '0' COMMENT '数据写入时间',
  KEY `hotel_id` (`hotel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



CREATE TABLE `hotel_room` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `goods_id` int(10) NOT NULL COMMENT '美团的房间id',
  `hotel_id` int(10) NOT NULL COMMENT '对应的酒店id',
  `name` varchar(200) NOT NULL DEFAULT '',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `inv_remain` varchar(45) NOT NULL DEFAULT '' COMMENT '剩余房间数  -1不可用,0满房，inf:可预定（不知道有多少剩余房间）',
  `desc` varchar(500) NOT NULL DEFAULT '' COMMENT '拼接的描述信息',
  `use_time` varchar(300) NOT NULL DEFAULT '' COMMENT '入住时间（可用时间）',
  `time` int(10) NOT NULL DEFAULT '0' COMMENT '数据写入时间',
  PRIMARY KEY (`id`),
  KEY `hotel_id` (`hotel_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2016 DEFAULT CHARSET=utf8mb4;




SELECT  * FROM `hotel` WHERE NAME='致远电竞酒店'


SELECT a.`hotel_id`,a.`name`,a.`score`,a.`area`,a.`address`,a.`city`,a.`update_time`, a.`lng`, a.`lat`, a.`introduction`, a.`hotelStar`, a.`poiAttrTagList`, a.`useRuleTime`, a.`positionDesc`, b.`goods_id`,b.`name` AS room_name,b.`price`,b.`inv_remain`,b.`desc`,b.`use_time`,b.`time` AS rooms_update_time FROM hotel a LEFT JOIN hotel_room b ON a.`hotel_id` = b.`hotel_id`


SELECT * FROM (SELECT a.`hotel_id`,a.`name`,a.`score`,a.`area`,a.`address`,a.`city`,a.`update_time`, a.`lng`, a.`lat`, a.`introduction`, a.`hotelStar`, a.`poiAttrTagList`, a.`useRuleTime`, a.`positionDesc`, b.`goods_id`,b.`name` AS room_name,b.`price`,b.`inv_remain`,b.`desc`,b.`use_time`,b.`time` AS rooms_update_time FROM hotel a LEFT JOIN hotel_room b ON a.`hotel_id` = b.`hotel_id`) AS temp


INSERT INTO hotel_desc SELECT * FROM (SELECT a.`hotel_id`,a.`name`,a.`score`,a.`area`,a.`address`,a.`city`,a.`update_time`, a.`lng`, a.`lat`, a.`introduction`, a.`hotelStar`, a.`poiAttrTagList`, a.`useRuleTime`, a.`positionDesc`, b.`goods_id`,b.`name` AS room_name,b.`price`,b.`inv_remain`,b.`desc`,b.`use_time`,b.`time` AS rooms_update_time FROM hotel a LEFT JOIN hotel_room b ON a.`hotel_id` = b.`hotel_id`) AS temp


SELECT COUNT(*) FROM `hotel_desc`

SELECT `hotel_id`,`name`,`score`,`area`,`address`,`city`,`update_time`, `lng`, `lat`, `hotelStar`, `poiAttrTagList`, `useRuleTime`, `positionDesc`, `goods_id`, room_name, `price`, `inv_remain`,`desc`,`use_time`, rooms_update_time FROM hotel_desc 





SELECT * FROM `hotel_desc` WHERE NAME =  '海韵电竞酒店'

SELECT COUNT(*) FROM hotel

SELECT COUNT(*) FROM `hotel_room`



DELETE FROM `hotel`

DELETE FROM `hotel_room`

DELETE FROM `hotel_desc`



中午11点 到 凌晨2点结束 每2小时