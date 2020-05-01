CREATE TABLE `bar` (
  `id` INT(10) NOT NULL AUTO_INCREMENT,
  `bar_id` VARCHAR(100) NOT NULL COMMENT '美团酒吧id',
  `bar_name` VARCHAR(300) NOT NULL DEFAULT '',
  `bar_score` VARCHAR(45) NOT NULL DEFAULT '' COMMENT '评分',
  `bar_phone` VARCHAR(45) NOT NULL DEFAULT '' COMMENT '电话',
  `city` VARCHAR(50) NOT NULL DEFAULT '昆明' COMMENT '城市名字',
  `area` VARCHAR(50) NOT NULL DEFAULT '盘龙区' COMMENT '市/县',
  `business` VARCHAR(50) NOT NULL DEFAULT '同德昆明广场' COMMENT '商圈',
  `bar_address` VARCHAR(100) NOT NULL COMMENT '地址',
  `lng` FLOAT DEFAULT NULL COMMENT '经度',
  `lat` FLOAT DEFAULT NULL COMMENT '纬度',
  `tuan` VARCHAR(2) NOT NULL DEFAULT '1' COMMENT '团',
  `juan` VARCHAR(2) NOT NULL DEFAULT '0' COMMENT '卷',
  `wai` VARCHAR(2) NOT NULL DEFAULT '0' COMMENT '外',
  `bar_update_time` INT(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `BAR_ID_UNIQUE` (`bar_id`)
) ENGINE=INNODB AUTO_INCREMENT=1583 DEFAULT CHARSET=utf8mb4;



CREATE TABLE `bar_package` (
  `id` INT(10) NOT NULL AUTO_INCREMENT,
  `package_id` VARCHAR(100) NOT NULL COMMENT '套餐id',
  `bar_id` VARCHAR(100) NOT NULL COMMENT '酒吧id',
  `package_name` VARCHAR(300) NOT NULL DEFAULT '' COMMENT '套餐名称',
  `package_price` DECIMAL(10,2) NOT NULL DEFAULT '0.00' COMMENT '套餐价格',
  `package_unit` VARCHAR(5) NOT NULL DEFAULT '元' COMMENT '价格单位',
  `activity` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '活动',
  `limit_price` DECIMAL(10,2) NOT NULL DEFAULT '0.00' COMMENT '限时抢购价格',
  `market_price` DECIMAL(10,2) NOT NULL DEFAULT '0.00' COMMENT '门市价',
  `sales_volume` INT(10) NOT NULL DEFAULT '0' COMMENT '已售数量',
  `sales_time_period` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '时间段已售数量',
  `effective_start_date` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '有效起始日期',
  `effective_end_date` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '有效结束日期',
  `package_title` VARCHAR(300) NOT NULL DEFAULT '' COMMENT '套餐标题名称',
  `package_rule` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '套餐规则',
  `package_update_time` INT(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `PACKAGE_ID_UNIQUE` (`package_id`)
) ENGINE=INNODB AUTO_INCREMENT=2016 DEFAULT CHARSET=utf8mb4;




CREATE TABLE `bar_package_item` (
  `id` INT(10) NOT NULL AUTO_INCREMENT,
  `item_name` VARCHAR(300) NOT NULL DEFAULT '' COMMENT '商品名称',
  `item_price` DECIMAL(10,2) NOT NULL DEFAULT '0.00' COMMENT '商品价格',
  `item_unit` VARCHAR(5) NOT NULL DEFAULT '元' COMMENT '价格单位',
  `copies_nm` INT(10) NOT NULL DEFAULT '0' COMMENT '份数',
  `item_rule` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '商品规则',
  `package_id` VARCHAR(100) NOT NULL COMMENT '套餐id',
  `item_update_time` INT(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ITEM_ID_UNIQUE` (`id`)
) ENGINE=INNODB AUTO_INCREMENT=2016 DEFAULT CHARSET=utf8mb4;






# 时间戳转换为时间格式：
# FROM_UNIXTIME(bar_update_time, '%Y-%m-%d %H:%i:%S')




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




SELECT a.`bar_id`, a.bar_name AS '酒吧名称',a.bar_score AS '得分',a.bar_phone AS '电话',a.city AS '城市',a.area AS '区',a.business AS '商圈',a.bar_address AS '地址',a.tuan AS '团购',a.juan AS '优惠劵',a.wai AS '外卖',FROM_UNIXTIME(a.bar_update_time, '%Y-%m-%d %H:%i:%S') AS '更新时间',
b.package_id, b.package_name AS '套餐名称', b.package_price AS '套餐价格', b.package_unit AS '套餐价格单位',b.`activity` AS '活动',b.`limit_price` AS '限时抢购价',b.`market_price` AS '市场价',b.`sales_volume` AS '已售数量',b.`sales_time_period` AS '半年消费数量',b.`effective_start_date` AS '有效期起始时间',b.`effective_end_date` AS '有效期结束时间',b.`package_title` AS '套餐标题',b.`package_rule` AS '套餐规则',
c.`id`, c.item_name AS '商品名称',c.`item_price` AS '商品价格',c.`item_unit` AS '商品价格单位',c.`copies_nm` AS '份数',c.`item_rule` AS '商品规则'
FROM `bar` a LEFT JOIN `bar_package` b ON a.`bar_id` = b.`bar_id` LEFT JOIN `bar_package_item` c ON b.`package_id` = c.`package_id`
ORDER BY a.`bar_score` DESC, b.`package_name` DESC, c.`item_price` DESC



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