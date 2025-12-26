/*
 Navicat Premium Data Transfer

 Source Server         : doris
 Source Server Type    : MySQL
 Source Server Version : 50799
 Source Host           : 36.212.156.218:9030
 Source Schema         : dw_power

 Target Server Type    : MySQL
 Target Server Version : 50799
 File Encoding         : 65001

 Date: 24/12/2025 15:08:25
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for ads_bus_energy_analysis
-- ----------------------------
DROP TABLE IF EXISTS `ads_bus_energy_analysis`;
CREATE TABLE `ads_bus_energy_analysis` (
  `id` varchar(64) NULL COMMENT '生产工序id',
  `date_type` varchar(10) NULL COMMENT '时间类型1当日2当月3当年',
  `date_value` int NULL COMMENT '时间值',
  `alias_name` varchar(128) NULL COMMENT '生产工序名称',
  `actual_value` decimal(27,4) NULL COMMENT '实物量',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标量'
) ENGINE=OLAP
UNIQUE KEY(`id`, `date_type`, `date_value`)
COMMENT '能源分析报表'
DISTRIBUTED BY HASH(`id`, `date_type`, `date_value`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_bus_energy_comparison
-- ----------------------------
DROP TABLE IF EXISTS `ads_bus_energy_comparison`;
CREATE TABLE `ads_bus_energy_comparison` (
  `energy_type_code` varchar(64) NULL COMMENT '能源类型编号（根据企业用能类型）',
  `date_type` varchar(10) NULL COMMENT '时间类型1当日2当月3当年',
  `date_value` int NULL COMMENT '时间值',
  `energy_type_name` varchar(128) NULL COMMENT '能源类型名称',
  `now_value` decimal(27,4) NULL COMMENT '当前值',
  `same_value` decimal(27,4) NULL COMMENT '同比值 上日/上月/上年'
) ENGINE=OLAP
UNIQUE KEY(`energy_type_code`, `date_type`, `date_value`, `energy_type_name`)
COMMENT '能源对比报表'
DISTRIBUTED BY HASH(`energy_type_code`, `date_type`, `date_value`, `energy_type_name`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_bus_energy_consume
-- ----------------------------
DROP TABLE IF EXISTS `ads_bus_energy_consume`;
CREATE TABLE `ads_bus_energy_consume` (
  `id` varchar(64) NULL COMMENT 'id',
  `date_type` varchar(10) NULL COMMENT '时间类型1当日2当月3当年',
  `alias_name` varchar(128) NULL COMMENT '别名',
  `actual_value` decimal(27,4) NULL COMMENT '实物量',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标量',
  `use_coefficient` decimal(27,4) NULL COMMENT '使用系数',
  `company` varchar(64) NULL COMMENT '单位',
  `style` varchar(64) NULL COMMENT '样式',
  `sort` int NULL COMMENT '排序'
) ENGINE=OLAP
UNIQUE KEY(`id`, `date_type`)
COMMENT '能源消耗报表'
DISTRIBUTED BY HASH(`id`, `date_type`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_co2_fossil_comb_mon
-- ----------------------------
DROP TABLE IF EXISTS `ads_co2_fossil_comb_mon`;
CREATE TABLE `ads_co2_fossil_comb_mon` (
  `summary_time` varchar(6) NULL COMMENT '采集时间',
  `energy_type_code` varchar(64) NULL COMMENT '能源类型',
  `energy_type_name` varchar(64) NULL COMMENT '能源类型名称',
  `coefficient_value` varchar(64) NULL COMMENT '净消耗量',
  `calorific_value` varchar(64) NULL COMMENT '低位发热量',
  `activity_level` varchar(64) NULL COMMENT '活动水平',
  `carbon_content` varchar(64) NULL COMMENT '单位热值含碳量',
  `oxidation_rate` varchar(64) NULL COMMENT '碳氧化率',
  `CO2_emissions` decimal(27,4) NULL COMMENT '二氧化碳排放'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `energy_type_code`, `energy_type_name`)
COMMENT '二氧化碳排放量报告化石燃料燃烧'
DISTRIBUTED BY HASH(`summary_time`, `energy_type_code`, `energy_type_name`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_co2_indust_process_mon
-- ----------------------------
DROP TABLE IF EXISTS `ads_co2_indust_process_mon`;
CREATE TABLE `ads_co2_indust_process_mon` (
  `summary_time` varchar(6) NULL COMMENT '采集时间',
  `energy_type_code` varchar(64) NULL COMMENT '能源类型',
  `energy_type_name` varchar(64) NULL COMMENT '能源类型名称',
  `coefficient_value` varchar(64) NULL COMMENT '净消耗量',
  `carbon_content` varchar(64) NULL COMMENT '单位热值含碳量',
  `use_carbon_emission_factor` varchar(64) NULL COMMENT '排放因子',
  `calcination_ratio` varchar(64) NULL COMMENT '煅烧比例',
  `CO2_emissions` decimal(27,4) NULL COMMENT '二氧化碳排放'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `energy_type_code`, `energy_type_name`)
COMMENT '二氧化碳排放量报告工业生产过程'
DISTRIBUTED BY HASH(`summary_time`, `energy_type_code`, `energy_type_name`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_co2_net_purchases_mon
-- ----------------------------
DROP TABLE IF EXISTS `ads_co2_net_purchases_mon`;
CREATE TABLE `ads_co2_net_purchases_mon` (
  `summary_time` varchar(6) NULL COMMENT '采集时间',
  `energy_type_code` varchar(64) NULL COMMENT '能源类型',
  `energy_type_name` varchar(64) NULL COMMENT '能源类型名称',
  `coefficient_value` varchar(64) NULL COMMENT '净消耗量',
  `use_carbon_emission_factor` varchar(64) NULL COMMENT '排放因子',
  `CO2_emissions` decimal(27,4) NULL COMMENT '二氧化碳排放'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `energy_type_code`, `energy_type_name`)
COMMENT '二氧化碳排放量报告净购入电力、热力'
DISTRIBUTED BY HASH(`summary_time`, `energy_type_code`, `energy_type_name`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_energy_consume_day
-- ----------------------------
DROP TABLE IF EXISTS `ads_energy_consume_day`;
CREATE TABLE `ads_energy_consume_day` (
  `summary_time` datetime NULL COMMENT '采集时间',
  `process_code` varchar(64) NULL COMMENT '生产工序',
  `process_unit_code` varchar(64) NULL COMMENT '生产工序单元',
  `energy_type_code` varchar(64) NULL COMMENT '能源类型',
  `meter_code` varchar(64) NULL COMMENT '计量器具编号（表计编号）',
  `analysis_code` varchar(64) NULL COMMENT '分析指标',
  `equipment_code` varchar(64) NULL COMMENT '设备类型编码',
  `equipment_unit_code` varchar(64) NULL COMMENT '设备编码',
  `field_name` varchar(64) NULL COMMENT '参数名称',
  `process_name` varchar(64) NULL COMMENT '生产工序名称',
  `process_unit_name` varchar(64) NULL COMMENT '生产工序单元名称',
  `energy_type_name` varchar(64) NULL COMMENT '能源类型名称',
  `metering_name` varchar(64) NULL COMMENT '计量器具名称',
  `analysis_name` varchar(64) NULL COMMENT '分析指标名称',
  `product_name` varchar(64) NULL COMMENT '产品名称',
  `equipment_unit_name` varchar(64) NULL COMMENT '设备名称',
  `meter_value` decimal(27,4) NULL COMMENT '实物量',
  `use_coefficient` decimal(27,4) NULL COMMENT '使用系数',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标量',
  `magnification` float NULL COMMENT '倍率',
  `begin_value` decimal(27,4) NULL COMMENT '起始示数',
  `end_value` decimal(27,4) NULL COMMENT '示数值',
  `peak_electricity` decimal(27,4) NULL COMMENT '尖电量',
  `peak_electricity_fee` decimal(27,4) NULL COMMENT '尖电费',
  `high_electricity` decimal(27,4) NULL COMMENT '峰电量',
  `high_electricity_fee` decimal(27,4) NULL COMMENT '峰电费',
  `normal_electricity` decimal(27,4) NULL COMMENT '平电量',
  `normal_electricity_fee` decimal(27,4) NULL COMMENT '平电费',
  `low_electricity` decimal(27,4) NULL COMMENT '谷电量',
  `low_electricity_fee` decimal(27,4) NULL COMMENT '谷电费',
  `total_electricity` decimal(27,4) NULL COMMENT '总电量',
  `total_electricity_fee` decimal(27,4) NULL COMMENT '总电费',
  `avg_electricity_fee` decimal(27,4) NULL COMMENT '平均电费',
  `yield_value` decimal(27,4) NULL COMMENT '产量',
  `electricity_value` decimal(27,4) NULL COMMENT '电力消耗量',
  `kerosene_value` decimal(27,4) NULL COMMENT '煤油消耗量',
  `kerosene_cost` decimal(27,4) NULL COMMENT '煤油成本',
  `natural_gas_value` decimal(27,4) NULL COMMENT '天然气耗量',
  `natural_gas_cost` decimal(27,4) NULL COMMENT '天然气成本',
  `crude_oil_value` decimal(27,4) NULL COMMENT '原油耗量',
  `crude_oil_cost` decimal(27,4) NULL COMMENT '原油成本',
  `coke_value` decimal(27,4) NULL COMMENT '焦炭耗量',
  `coke_cost` decimal(27,4) NULL COMMENT '焦炭成本',
  `thermal_energy_value` decimal(27,4) NULL COMMENT '热力耗量',
  `thermal_energy_cost` decimal(27,4) NULL COMMENT '热力成本',
  `g_bituminous_coal_value` decimal(27,4) NULL COMMENT '一般烟煤耗量',
  `g_bituminous_coal_cost` decimal(27,4) NULL COMMENT '一般烟煤成本',
  `anthracite_coal_value` decimal(27,4) NULL COMMENT '无烟煤耗量',
  `anthracite_coal_cost` decimal(27,4) NULL COMMENT '无烟煤成本',
  `washed_coking_coal_value` decimal(27,4) NULL COMMENT '洗精煤耗量',
  `washed_coking_coal_cost` decimal(27,4) NULL COMMENT '洗精煤成本',
  `c_bituminous_coal_value` decimal(27,4) NULL COMMENT '炼焦烟煤耗量',
  `c_bituminous_coal_cost` decimal(27,4) NULL COMMENT '炼焦烟煤成本',
  `total_value` decimal(27,4) NULL COMMENT '综合消耗量',
  `total_cost` decimal(27,4) NULL COMMENT '综合成本',
  `device_state` varchar(2) NULL COMMENT '设备状态 X:停机 S:待机 A:运行',
  `mon_meter_value` decimal(27,4) NULL COMMENT '环比实物量 当小时数据与昨天小时数据比较',
  `yoy_meter_value` decimal(27,4) NULL COMMENT '同比实物量 小时为0'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `process_code`, `process_unit_code`, `energy_type_code`, `meter_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`, `field_name`)
COMMENT '能耗统计分析天'
DISTRIBUTED BY HASH(`summary_time`, `process_code`, `process_unit_code`, `energy_type_code`, `meter_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`, `field_name`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_energy_consume_hour
-- ----------------------------
DROP TABLE IF EXISTS `ads_energy_consume_hour`;
CREATE TABLE `ads_energy_consume_hour` (
  `summary_time` datetime NULL COMMENT '采集时间',
  `process_code` varchar(64) NULL COMMENT '生产工序',
  `process_unit_code` varchar(64) NULL COMMENT '生产工序单元',
  `energy_type_code` varchar(64) NULL COMMENT '能源类型',
  `meter_code` varchar(64) NULL COMMENT '计量器具编号（表计编号）',
  `analysis_code` varchar(64) NULL COMMENT '分析指标',
  `equipment_code` varchar(64) NULL COMMENT '设备类型编码',
  `equipment_unit_code` varchar(64) NULL COMMENT '设备编码',
  `field_name` varchar(64) NULL COMMENT '参数名称',
  `process_name` varchar(64) NULL COMMENT '生产工序名称',
  `process_unit_name` varchar(64) NULL COMMENT '生产工序单元名称',
  `energy_type_name` varchar(64) NULL COMMENT '能源类型名称',
  `metering_name` varchar(64) NULL COMMENT '计量器具名称',
  `analysis_name` varchar(64) NULL COMMENT '分析指标名称',
  `equipment_unit_name` varchar(64) NULL COMMENT '设备名称',
  `meter_value` decimal(27,4) NULL COMMENT '实物量',
  `use_coefficient` decimal(27,4) NULL COMMENT '使用系数',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标量',
  `magnification` float NULL COMMENT '倍率',
  `begin_value` decimal(27,4) NULL COMMENT '起始示数',
  `end_value` decimal(27,4) NULL COMMENT '示数值',
  `mon_meter_value` decimal(27,4) NULL COMMENT '环比实物量 当小时数据与昨天小时数据比较',
  `yoy_meter_value` decimal(27,4) NULL COMMENT '同比实物量 小时为0'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `process_code`, `process_unit_code`, `energy_type_code`, `meter_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`, `field_name`)
COMMENT '能耗统计分析小时'
DISTRIBUTED BY HASH(`summary_time`, `process_code`, `process_unit_code`, `energy_type_code`, `meter_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`, `field_name`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_energy_consume_minute
-- ----------------------------
DROP TABLE IF EXISTS `ads_energy_consume_minute`;
CREATE TABLE `ads_energy_consume_minute` (
  `summary_time` datetime NULL COMMENT '采集时间',
  `process_code` varchar(64) NULL COMMENT '生产工序',
  `process_unit_code` varchar(64) NULL COMMENT '生产工序单元',
  `energy_type_code` varchar(64) NULL COMMENT '能源类型',
  `meter_code` varchar(64) NULL COMMENT '计量器具编号（表计编号）',
  `analysis_code` varchar(64) NULL COMMENT '分析指标',
  `equipment_code` varchar(64) NULL COMMENT '设备类型编码',
  `equipment_unit_code` varchar(64) NULL COMMENT '设备编码',
  `field_name` varchar(64) NULL COMMENT '参数名称',
  `process_name` varchar(64) NULL COMMENT '生产工序名称',
  `process_unit_name` varchar(64) NULL COMMENT '生产工序单元名称',
  `energy_type_name` varchar(64) NULL COMMENT '能源类型名称',
  `metering_name` varchar(64) NULL COMMENT '计量器具名称',
  `analysis_name` varchar(64) NULL COMMENT '分析指标名称',
  `equipment_unit_name` varchar(64) NULL COMMENT '设备名称',
  `meter_value` decimal(27,4) NULL COMMENT '实物量',
  `use_coefficient` decimal(27,4) NULL COMMENT '使用系数',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标量',
  `magnification` float NULL COMMENT '倍率',
  `begin_value` decimal(27,4) NULL COMMENT '起始示数',
  `end_value` decimal(27,4) NULL COMMENT '示数值'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `process_code`, `process_unit_code`, `energy_type_code`, `meter_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`, `field_name`)
COMMENT '能耗统计分析15分钟'
DISTRIBUTED BY HASH(`summary_time`, `process_code`, `process_unit_code`, `energy_type_code`, `meter_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`, `field_name`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_energy_consume_mon
-- ----------------------------
DROP TABLE IF EXISTS `ads_energy_consume_mon`;
CREATE TABLE `ads_energy_consume_mon` (
  `summary_time` varchar(6) NULL COMMENT '采集时间',
  `enterprise_code_data_id` varchar(192) NULL COMMENT '采集数项ID',
  `process_code` varchar(64) NULL COMMENT '生产工序',
  `process_unit_code` varchar(64) NULL COMMENT '生产工序单元',
  `energy_type_code` varchar(64) NULL COMMENT '能源类型',
  `meter_code` varchar(64) NULL COMMENT '计量器具编号（表计编号）',
  `analysis_code` varchar(64) NULL COMMENT '分析指标',
  `equipment_code` varchar(64) NULL COMMENT '设备类型编码',
  `equipment_unit_code` varchar(64) NULL COMMENT '设备编码',
  `field_name` varchar(64) NULL COMMENT '参数名称',
  `process_name` varchar(64) NULL COMMENT '生产工序名称',
  `process_unit_name` varchar(64) NULL COMMENT '生产工序单元名称',
  `energy_type_name` varchar(64) NULL COMMENT '能源类型名称',
  `metering_name` varchar(64) NULL COMMENT '计量器具名称',
  `analysis_name` varchar(64) NULL COMMENT '分析指标名称',
  `product_name` varchar(64) NULL COMMENT '产品名称',
  `equipment_unit_name` varchar(64) NULL COMMENT '设备名称',
  `meter_value` decimal(27,4) NULL COMMENT '实物量',
  `use_coefficient` decimal(27,4) NULL COMMENT '使用系数',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标量',
  `magnification` float NULL COMMENT '倍率',
  `begin_value` decimal(27,4) NULL COMMENT '起始示数',
  `end_value` decimal(27,4) NULL COMMENT '示数值',
  `peak_electricity` decimal(27,4) NULL COMMENT '尖电量',
  `peak_electricity_fee` decimal(27,4) NULL COMMENT '尖电费',
  `high_electricity` decimal(27,4) NULL COMMENT '峰电量',
  `high_electricity_fee` decimal(27,4) NULL COMMENT '峰电费',
  `normal_electricity` decimal(27,4) NULL COMMENT '平电量',
  `normal_electricity_fee` decimal(27,4) NULL COMMENT '平电费',
  `low_electricity` decimal(27,4) NULL COMMENT '谷电量',
  `low_electricity_fee` decimal(27,4) NULL COMMENT '谷电费',
  `total_electricity` decimal(27,4) NULL COMMENT '总电量',
  `total_electricity_fee` decimal(27,4) NULL COMMENT '总电费',
  `avg_electricity_fee` decimal(27,4) NULL COMMENT '平均电费',
  `yield_value` decimal(27,4) NULL COMMENT '产量',
  `electricity_value` decimal(27,4) NULL COMMENT '电力消耗量',
  `kerosene_value` decimal(27,4) NULL COMMENT '煤油消耗量',
  `kerosene_cost` decimal(27,4) NULL COMMENT '煤油成本',
  `natural_gas_value` decimal(27,4) NULL COMMENT '天然气耗量',
  `natural_gas_cost` decimal(27,4) NULL COMMENT '天然气成本',
  `crude_oil_value` decimal(27,4) NULL COMMENT '原油耗量',
  `crude_oil_cost` decimal(27,4) NULL COMMENT '原油成本',
  `coke_value` decimal(27,4) NULL COMMENT '焦炭耗量',
  `coke_cost` decimal(27,4) NULL COMMENT '焦炭成本',
  `thermal_energy_value` decimal(27,4) NULL COMMENT '热力耗量',
  `thermal_energy_cost` decimal(27,4) NULL COMMENT '热力成本',
  `g_bituminous_coal_value` decimal(27,4) NULL COMMENT '一般烟煤耗量',
  `g_bituminous_coal_cost` decimal(27,4) NULL COMMENT '一般烟煤成本',
  `anthracite_coal_value` decimal(27,4) NULL COMMENT '无烟煤耗量',
  `anthracite_coal_cost` decimal(27,4) NULL COMMENT '无烟煤成本',
  `washed_coking_coal_value` decimal(27,4) NULL COMMENT '洗精煤耗量',
  `washed_coking_coal_cost` decimal(27,4) NULL COMMENT '洗精煤成本',
  `c_bituminous_coal_value` decimal(27,4) NULL COMMENT '炼焦烟煤耗量',
  `c_bituminous_coal_cost` decimal(27,4) NULL COMMENT '炼焦烟煤成本',
  `total_value` decimal(27,4) NULL COMMENT '综合消耗量',
  `total_cost` decimal(27,4) NULL COMMENT '综合成本',
  `device_state` varchar(2) NULL COMMENT '设备状态 X:停机 S:待机 A:运行',
  `mon_meter_value` decimal(27,4) NULL COMMENT '环比实物量 当小时数据与昨天小时数据比较',
  `yoy_meter_value` decimal(27,4) NULL COMMENT '同比实物量 小时为0'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `enterprise_code_data_id`, `process_code`, `process_unit_code`, `energy_type_code`, `meter_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`, `field_name`)
COMMENT '能耗统计分析月'
DISTRIBUTED BY HASH(`summary_time`, `enterprise_code_data_id`, `process_code`, `process_unit_code`, `energy_type_code`, `meter_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`, `field_name`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_energy_consume_qua
-- ----------------------------
DROP TABLE IF EXISTS `ads_energy_consume_qua`;
CREATE TABLE `ads_energy_consume_qua` (
  `summary_time` varchar(10) NULL COMMENT '采集时间季度,如20241:2024第一季度',
  `process_code` varchar(64) NULL COMMENT '生产工序',
  `process_unit_code` varchar(64) NULL COMMENT '生产工序单元',
  `energy_type_code` varchar(64) NULL COMMENT '能源类型',
  `analysis_code` varchar(64) NULL COMMENT '分析指标',
  `equipment_code` varchar(64) NULL COMMENT '设备类型编码',
  `equipment_unit_code` varchar(64) NULL COMMENT '设备编码',
  `process_name` varchar(64) NULL COMMENT '生产工序名称',
  `process_unit_name` varchar(64) NULL COMMENT '生产工序单元名称',
  `energy_type_name` varchar(64) NULL COMMENT '能源类型名称',
  `analysis_name` varchar(64) NULL COMMENT '分析指标名称',
  `equipment_unit_name` varchar(64) NULL COMMENT '设备名称',
  `meter_value` decimal(27,4) NULL COMMENT '实物量',
  `use_coefficient` decimal(27,4) NULL COMMENT '使用系数',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标量',
  `mon_meter_value` decimal(27,4) NULL COMMENT '环比实物量 当小时数据与昨天小时数据比较',
  `yoy_meter_value` decimal(27,4) NULL COMMENT '同比实物量 小时为0'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `process_code`, `process_unit_code`, `energy_type_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`)
COMMENT '能耗统计分析季度'
DISTRIBUTED BY HASH(`summary_time`, `process_code`, `process_unit_code`, `energy_type_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_energy_consume_shift
-- ----------------------------
DROP TABLE IF EXISTS `ads_energy_consume_shift`;
CREATE TABLE `ads_energy_consume_shift` (
  `summary_time` datetime NULL COMMENT '采集时间',
  `shift_type` varchar(64) NULL COMMENT '班组',
  `process_code` varchar(64) NULL COMMENT '生产工序',
  `process_unit_code` varchar(64) NULL COMMENT '生产工序单元',
  `energy_type_code` varchar(64) NULL COMMENT '能源类型',
  `meter_code` varchar(64) NULL COMMENT '计量器具编号（表计编号）',
  `analysis_code` varchar(64) NULL COMMENT '分析指标',
  `equipment_code` varchar(64) NULL COMMENT '设备类型编码',
  `equipment_unit_code` varchar(64) NULL COMMENT '设备编码',
  `process_name` varchar(64) NULL COMMENT '生产工序名称',
  `process_unit_name` varchar(64) NULL COMMENT '生产工序单元名称',
  `energy_type_name` varchar(64) NULL COMMENT '能源类型名称',
  `metering_name` varchar(64) NULL COMMENT '计量器具名称',
  `analysis_name` varchar(64) NULL COMMENT '分析指标名称',
  `equipment_unit_name` varchar(64) NULL COMMENT '设备名称',
  `meter_value` decimal(27,4) NULL COMMENT '实物量',
  `use_coefficient` decimal(27,4) NULL COMMENT '使用系数',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标量',
  `mon_meter_value` decimal(27,4) NULL COMMENT '环比实物量 当小时数据与昨天小时数据比较',
  `yoy_meter_value` decimal(27,4) NULL COMMENT '同比实物量 小时为0'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `shift_type`, `process_code`, `process_unit_code`, `energy_type_code`, `meter_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`)
COMMENT '能耗统计分析班组'
DISTRIBUTED BY HASH(`summary_time`, `shift_type`, `process_code`, `process_unit_code`, `energy_type_code`, `meter_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_energy_consume_year
-- ----------------------------
DROP TABLE IF EXISTS `ads_energy_consume_year`;
CREATE TABLE `ads_energy_consume_year` (
  `summary_time` varchar(4) NULL COMMENT '采集时间',
  `process_code` varchar(64) NULL COMMENT '生产工序',
  `process_unit_code` varchar(64) NULL COMMENT '生产工序单元',
  `energy_type_code` varchar(64) NULL COMMENT '能源类型',
  `analysis_code` varchar(64) NULL COMMENT '分析指标',
  `equipment_code` varchar(64) NULL COMMENT '设备类型编码',
  `equipment_unit_code` varchar(64) NULL COMMENT '设备编码',
  `energy_type_name` varchar(64) NULL COMMENT '能源类型名称',
  `analysis_name` varchar(64) NULL COMMENT '分析指标名称',
  `process_name` varchar(64) NULL COMMENT '生产工序名称',
  `process_unit_name` varchar(64) NULL COMMENT '生产工序单元名称',
  `equipment_unit_name` varchar(64) NULL COMMENT '设备名称',
  `meter_value` decimal(27,4) NULL COMMENT '实物量',
  `use_coefficient` decimal(27,4) NULL COMMENT '使用系数',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标量',
  `device_state` varchar(2) NULL COMMENT '设备状态 X:停机 S:待机 A:运行',
  `mon_meter_value` decimal(27,4) NULL COMMENT '环比实物量 当小时数据与昨天小时数据比较',
  `yoy_meter_value` decimal(27,4) NULL COMMENT '同比实物量 小时为0'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `process_code`, `process_unit_code`, `energy_type_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`)
COMMENT '能耗统计分析年'
DISTRIBUTED BY HASH(`summary_time`, `process_code`, `process_unit_code`, `energy_type_code`, `analysis_code`, `equipment_code`, `equipment_unit_code`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_energy_distribution
-- ----------------------------
DROP TABLE IF EXISTS `ads_energy_distribution`;
CREATE TABLE `ads_energy_distribution` (
  `id` varchar(64) NULL COMMENT 'id',
  `date_type` varchar(10) NULL COMMENT '时间类型1当日2当月3当年',
  `alias_name` varchar(128) NULL COMMENT '别名',
  `power_consumption` decimal(27,4) NULL COMMENT '实时能耗数值',
  `pre_power_consumption` decimal(27,4) NULL COMMENT '上日/上月/上年能耗数值',
  `proportion` decimal(27,4) NULL COMMENT '消耗占比'
) ENGINE=OLAP
UNIQUE KEY(`id`, `date_type`)
COMMENT '能源分布情况'
DISTRIBUTED BY HASH(`id`, `date_type`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ads_smart_energy_analysis
-- ----------------------------
DROP TABLE IF EXISTS `ads_smart_energy_analysis`;
CREATE TABLE `ads_smart_energy_analysis` (
  `id` varchar(64) NULL COMMENT '生产工序id',
  `date_type` varchar(10) NULL COMMENT '时间类型1当日2当月',
  `alias_name` varchar(128) NULL COMMENT '别名',
  `chart_order_num` varchar(50) NULL COMMENT '采集数据项分类ID',
  `chart_order_name` varchar(50) NULL COMMENT '采集数据项分类名称',
  `power_consumption` decimal(27,4) NULL COMMENT '实时能耗数值',
  `limit_value` decimal(27,4) NULL COMMENT '限额',
  `all_flag` varchar(10) NULL COMMENT '全厂标识',
  `sort` int NULL COMMENT '排序'
) ENGINE=OLAP
UNIQUE KEY(`id`, `date_type`)
COMMENT '智能用能分析'
DISTRIBUTED BY HASH(`id`, `date_type`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_alarm_setting
-- ----------------------------
DROP TABLE IF EXISTS `dim_alarm_setting`;
CREATE TABLE `dim_alarm_setting` (
  `id` varchar(96) NULL,
  `device_type` int NULL COMMENT '设备类型',
  `device_no` varchar(765) NULL COMMENT '设备名称',
  `object_no` varchar(765) NULL COMMENT '对象编号',
  `object_name` varchar(765) NULL COMMENT '对象名称',
  `indicator_name` varchar(765) NULL COMMENT '指标名称',
  `statistical_cycle` int NULL COMMENT '统计周期',
  `upper_limit` decimal(12,4) NULL COMMENT '上限',
  `lower_limit` decimal(12,4) NULL COMMENT '下限',
  `method` int NULL COMMENT '报警方式',
  `status` int NULL COMMENT '启用状态',
  `create_time` datetime NULL COMMENT '创建时间',
  `create_by` varchar(96) NULL COMMENT '创建人',
  `update_time` datetime NULL COMMENT '更新时间',
  `update_by` varchar(96) NULL COMMENT '更新人',
  `is_upload` tinyint NULL,
  `alarm_level` varchar(60) NULL COMMENT '报警等级'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '报警规则设置'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_bus_yieid_hour
-- ----------------------------
DROP TABLE IF EXISTS `dim_bus_yieid_hour`;
CREATE TABLE `dim_bus_yieid_hour` (
  `id` varchar(96) NULL,
  `bus_yieid_id` varchar(96) NULL COMMENT '产量数据填报Id',
  `year` varchar(12) NULL COMMENT '年',
  `month` varchar(6) NULL COMMENT '月',
  `day` varchar(6) NULL COMMENT '日',
  `hour` varchar(6) NULL COMMENT '小时',
  `start_time` datetime NULL COMMENT '生产开始时间',
  `end_time` datetime NULL COMMENT '生成结束时间',
  `average_value` double NULL COMMENT '平均产量',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(96) NULL COMMENT '操作人'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '产量数据填报（小时）'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_bus_yield
-- ----------------------------
DROP TABLE IF EXISTS `dim_bus_yield`;
CREATE TABLE `dim_bus_yield` (
  `id` varchar(96) NULL,
  `process_code` varchar(6) NULL COMMENT '生产工序编号2位（1-2位）',
  `process_unit_code` varchar(6) NULL COMMENT '工序单元编码2位（3-4位）',
  `energy_type_code` varchar(12) NULL COMMENT '产品代码（4位）11-14位',
  `start_time` datetime NULL COMMENT '生产开始时间',
  `end_time` datetime NULL COMMENT '生成结束时间',
  `value` varchar(765) NULL COMMENT '产量',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(96) NULL COMMENT '操作人',
  `enterprise_code_data_id` varchar(192) NULL COMMENT '采集数据项ID',
  `job_status` tinyint NULL COMMENT '是否执行job 0未执行，1已执行'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '产量数据填报'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_carbon_carbonate_material_emission_factor
-- ----------------------------
DROP TABLE IF EXISTS `dim_carbon_carbonate_material_emission_factor`;
CREATE TABLE `dim_carbon_carbonate_material_emission_factor` (
  `id` varchar(192) NULL COMMENT 'id',
  `energy_type_code` varchar(30) NULL COMMENT '物料类型编码',
  `energy_type_code_name` varchar(600) NULL,
  `ore_name` varchar(765) NULL COMMENT '矿石名称',
  `carbonate_chemical_formula` varchar(765) NULL COMMENT '碳酸盐化学式',
  `molecular_weight` varchar(300) NULL COMMENT '分子量',
  `carbon_emission_factor` varchar(300) NULL COMMENT '排放因子（吨CO2/吨碳酸盐）',
  `use_carbon_emission_factor` double NULL COMMENT '企业采用的排放因子',
  `create_time` datetime NULL COMMENT '创建时间',
  `update_time` datetime NULL COMMENT '更新时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `enterprise_code_data_id` varchar(192) NULL COMMENT '采集数据项ID',
  `input_type` tinyint NULL COMMENT '数据采集来源（4 现场仪表  5 手工填报）'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '常见碳酸盐原料的排放因子表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_carbon_fossil_fuel_calorific_value
-- ----------------------------
DROP TABLE IF EXISTS `dim_carbon_fossil_fuel_calorific_value`;
CREATE TABLE `dim_carbon_fossil_fuel_calorific_value` (
  `id` varchar(192) NULL COMMENT 'id',
  `energy_type_code` varchar(30) NULL COMMENT '燃料类型编码',
  `energy_type_name` varchar(765) NULL COMMENT '燃料类型名称',
  `avg_low_calorific_value` double NULL COMMENT '平均低位热值（参考值）',
  `use_calorific_value` double NULL COMMENT '企业采用的平均低位热值',
  `company` varchar(300) NULL COMMENT '单位',
  `create_time` datetime NULL COMMENT '创建时间',
  `update_time` datetime NULL COMMENT '更新时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `enterprise_code_data_id` varchar(192) NULL COMMENT '采集数据项ID',
  `input_type` tinyint NULL COMMENT '数据采集来源（4 现场仪表  5 手工填报）'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '化石燃料热值表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_carbon_fossil_fuel_carbon_content
-- ----------------------------
DROP TABLE IF EXISTS `dim_carbon_fossil_fuel_carbon_content`;
CREATE TABLE `dim_carbon_fossil_fuel_carbon_content` (
  `id` varchar(192) NULL COMMENT 'id',
  `energy_type_code` varchar(30) NULL COMMENT '燃料类型编码',
  `energy_type_name` varchar(765) NULL COMMENT '燃料类型名称',
  `carbon_content` double NULL COMMENT '含碳量（tC/TJ）（参考值）',
  `use_carbon_content` double NULL COMMENT '企业采用的含碳量（tC/TJ）',
  `create_time` datetime NULL COMMENT '创建时间',
  `update_time` datetime NULL COMMENT '更新时间',
  `user_id` varchar(192) NULL COMMENT '操作人'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '化石燃料含碳量表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_carbon_fossil_fuel_oxidation_rate
-- ----------------------------
DROP TABLE IF EXISTS `dim_carbon_fossil_fuel_oxidation_rate`;
CREATE TABLE `dim_carbon_fossil_fuel_oxidation_rate` (
  `id` varchar(192) NULL COMMENT 'id',
  `energy_type_code` varchar(30) NULL COMMENT '燃料类型编码',
  `energy_type_name` varchar(765) NULL COMMENT '燃料类型名称',
  `oxidation_rate` double NULL COMMENT '氧化率（参考值）',
  `use_oxidation_rate` double NULL COMMENT '企业采用的氧化率',
  `create_time` datetime NULL COMMENT '创建时间',
  `update_time` datetime NULL COMMENT '更新时间',
  `user_id` varchar(192) NULL COMMENT '操作人'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '化石燃料氧化率表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_carbon_other_material_emission_factor
-- ----------------------------
DROP TABLE IF EXISTS `dim_carbon_other_material_emission_factor`;
CREATE TABLE `dim_carbon_other_material_emission_factor` (
  `id` varchar(192) NULL COMMENT 'id',
  `energy_type_code` varchar(30) NULL COMMENT '燃料类型编码',
  `energy_type_name` varchar(765) NULL COMMENT '燃料类型名称',
  `parameter_name` varchar(765) NULL COMMENT '参数名称',
  `carbon_emission_factor` varchar(300) NULL COMMENT '二氧化碳排放因子',
  `use_carbon_emission_factor` double NULL COMMENT '企业采用的排放因子',
  `company` varchar(300) NULL COMMENT '单位',
  `create_time` datetime NULL COMMENT '创建时间',
  `update_time` datetime NULL COMMENT '更新时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `enterprise_code_data_id` varchar(192) NULL COMMENT '采集数据项ID',
  `input_type` tinyint NULL COMMENT '数据采集来源（4 现场仪表  5 手工填报）'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '其他原料排放因子推荐值表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_carbon_total_list
-- ----------------------------
DROP TABLE IF EXISTS `dim_carbon_total_list`;
CREATE TABLE `dim_carbon_total_list` (
  `id` varchar(192) NULL COMMENT 'id',
  `list_name` varchar(192) NULL COMMENT '汇总名称',
  `energy_type_code` varchar(192) NULL COMMENT '能源类型',
  `state` varchar(6) NULL COMMENT '状态 A:在用 X:停用',
  `create_time` datetime NULL COMMENT '创建时间',
  `update_time` datetime NULL COMMENT '更新时间'
) ENGINE=OLAP
UNIQUE KEY(`id`)
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_energy_hierarchy
-- ----------------------------
DROP TABLE IF EXISTS `dim_energy_hierarchy`;
CREATE TABLE `dim_energy_hierarchy` (
  `hierarchy_id` varchar(192) NULL COMMENT '层级的唯一标识符',
  `parent_hierarchy_id` varchar(192) NULL COMMENT '父层级的 ID，用于建立层级关系。顶级层级此值为 NULL',
  `path` varchar(765) NULL COMMENT '完整层级路径。',
  `level_depth` int NULL COMMENT '表示该层级在层级结构中的深度，顶级层级深度为 0',
  `level_name` varchar(384) NULL COMMENT '层级的名称',
  `remarks` varchar(765) NULL COMMENT '用于存储关于该层级的备注信息'
) ENGINE=OLAP
UNIQUE KEY(`hierarchy_id`)
COMMENT '能源位置层级表'
DISTRIBUTED BY HASH(`hierarchy_id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_code_data
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_code_data`;
CREATE TABLE `dim_enterprise_code_data` (
  `enterprise_code_data_id` varchar(192) NULL COMMENT 'id',
  `code_data_name` varchar(768) NULL COMMENT '采集数据项指标名称',
  `process_code` varchar(6) NULL COMMENT '生产工序编码1-2位',
  `process_unit_code` varchar(6) NULL COMMENT '工序单元编码3-4位',
  `equipment_code` varchar(6) NULL COMMENT '重点用能设备类型编码5-6位（设备是重点设备的类型过滤显示）',
  `equipment_unit_code` varchar(6) NULL COMMENT '重点用能设备编码7-8位',
  `energy_class_code` varchar(6) NULL COMMENT '采集数据类型9-10（6.1 采集数据类型编码）',
  `energy_type_code` varchar(12) NULL COMMENT '数据分类11-14位（见采集数据分类规则tab）',
  `data_usage_code` varchar(6) NULL COMMENT '用途编码15-16位（7 能源用途编码）',
  `enterprise_code_data_all` varchar(192) NULL COMMENT '采集数据项16位编码',
  `input_type` tinyint NULL COMMENT '数据采集来源（5 数据采集来源编码）',
  `data_value_max` float NULL COMMENT '数据最大值（空不预警）',
  `data_value_min` float NULL COMMENT '数据最小值（空不预警）',
  `stat_type` varchar(96) NULL COMMENT '采集频率（0 实时、1 日、2 月）',
  `collect_system_name` varchar(768) NULL COMMENT '采集系统名称',
  `scope` varchar(768) NULL COMMENT '范围（重点用能设备选项控制）',
  `data_code_ratio` tinyint NULL COMMENT '是否用能公式计算（1是，0否）',
  `is_report` tinyint NULL COMMENT '是否上报（1否，2是）',
  `platform` varchar(3072) NULL COMMENT '上报平台（1省节能中心，2省计量院,3运维平台）多选逗号隔开',
  `is_statistics` tinyint NULL COMMENT '是否统计(1 统计 0 不统计)',
  `remark` varchar(3072) NULL COMMENT '备注',
  `company` varchar(768) NULL COMMENT '能源单位',
  `enterprise_metering_id` varchar(192) NULL COMMENT 'enterprise_metering_id',
  `meter_code` varchar(192) NULL COMMENT '计量器具编号（表计编号）',
  `meter_value_field` varchar(192) NULL COMMENT '表计取数字段（参数配置动态生成表）',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `table_name` varchar(765) NULL COMMENT '表计'
) ENGINE=OLAP
UNIQUE KEY(`enterprise_code_data_id`)
COMMENT '采集数据项信息表'
DISTRIBUTED BY HASH(`enterprise_code_data_id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_energy
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_energy`;
CREATE TABLE `dim_enterprise_energy` (
  `id` varchar(192) NULL COMMENT 'id',
  `energy_type_code` varchar(12) NULL COMMENT '能源/耗能工质编码（6.2 能源品种编码4位）11-14位',
  `energy_type_name` varchar(768) NULL COMMENT '能源/耗能工质名称',
  `energy_type` varchar(768) NULL COMMENT '类型（10 系统计量单位及精度）',
  `company` varchar(768) NULL COMMENT '计量单位（10 系统计量单位及精度）',
  `accuracy` float NULL COMMENT '数值精度（10 系统计量单位及精度）',
  `conversion_coefficient_unit` varchar(768) NULL COMMENT '折标系数单位（10 系统计量单位及精度）',
  `conversion_coefficient_coal_accuracy` float NULL COMMENT '折标煤系数精度（10 系统计量单位及精度）',
  `reference_coefficient` float NULL COMMENT '参考折标系数（B.1 能源折标系数）',
  `use_coefficient` float NULL COMMENT '采用折标系数',
  `cost` double NULL COMMENT '能源成本',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `if_energy_breed` varchar(12) NULL COMMENT '是否能源品种',
  `conversion_factor` float NULL COMMENT '转换系数',
  `limit_energy_consumption` varchar(150) NULL,
  `class_code` varchar(12) NULL COMMENT '能源种类'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '用能类型管理表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_energy_formula
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_energy_formula`;
CREATE TABLE `dim_enterprise_energy_formula` (
  `id` varchar(192) NULL COMMENT 'id',
  `enterprise_code_data_id` varchar(192) NULL COMMENT '采集数据项表ID',
  `stat_type` tinyint NULL COMMENT '采集频率（0 实时、1 日、2 月）',
  `formula` text NULL COMMENT '计算公式',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(192) NULL COMMENT '操作人'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '用能公式设置表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_equipment
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_equipment`;
CREATE TABLE `dim_enterprise_equipment` (
  `id` varchar(192) NULL COMMENT 'id',
  `process_code` varchar(6) NULL COMMENT '生产工序编号2位（1-2位）',
  `process_unit_code` varchar(6) NULL COMMENT '工序单元编码2位（3-4位）',
  `equipment_code` varchar(6) NULL COMMENT '设备类型编码2位（5-6位）',
  `equipment_name` varchar(768) NULL COMMENT '设备类型名称',
  `equipment_unit_code` varchar(6) NULL COMMENT '设备编号2位（7-8位）',
  `equipment_unit_name` varchar(768) NULL COMMENT '设备名称',
  `equip_inside_num` varchar(60) NULL COMMENT '内部编号',
  `model` varchar(768) NULL COMMENT '型号规格',
  `use_type` varchar(768) NULL COMMENT '用能类型',
  `power` varchar(768) NULL COMMENT '额定功率',
  `enable_time` datetime NULL COMMENT '启用时间',
  `year_function` varchar(192) NULL COMMENT '年运行时间（小时）',
  `is_key` tinyint NULL COMMENT '是否重点用能设备',
  `function_current_value` varchar(768) NULL COMMENT '运行电流值',
  `standby_current_value` varchar(768) NULL COMMENT '待机电流值',
  `stop_current_value` varchar(768) NULL COMMENT '停机电流值',
  `status` tinyint NULL COMMENT '状态（1正常，2异常）',
  `voltage` varchar(768) NULL COMMENT '额定电压',
  `current_value` varchar(768) NULL COMMENT '额定电流',
  `is_backward` tinyint NULL COMMENT '是否落后设备',
  `addr` varchar(768) NULL COMMENT '安装地点',
  `img_url` varchar(768) NULL COMMENT '设备图片',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(192) NULL COMMENT '操作人'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '用能设备台账表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_manual_data
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_manual_data`;
CREATE TABLE `dim_enterprise_manual_data` (
  `id` varchar(192) NULL COMMENT 'id',
  `enterprise_code_data_id` varchar(192) NULL COMMENT '采集数据项表ID',
  `collect_time` datetime NULL COMMENT '采集时间',
  `data_value` decimal(16,4) NULL COMMENT '上报数值',
  `enterprise_code_data_all` varchar(192) NULL COMMENT '采集数据项16位编码',
  `code_data_name` varchar(768) NULL COMMENT '采集数据项名称',
  `energy_type_code` varchar(12) NULL COMMENT '能源/耗能工质编码（6.2 能源品种编码4位）11-14位',
  `energy_type_name` varchar(768) NULL COMMENT '能源/耗能工质名称',
  `company` varchar(768) NULL COMMENT '计量单位（10 系统计量单位及精度）',
  `stat_type` tinyint NULL COMMENT '采集频率（0 实时、1 日、2 月）',
  `create_time` datetime NULL COMMENT '操作时间',
  `scope` varchar(765) NULL COMMENT '数据范围',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `status` tinyint NULL COMMENT '0 还没有采集到上报表，1已经采集到上报表,默认生成为null',
  `platform` varchar(768) NULL COMMENT '平台字段冗余',
  `accuracy` float NULL COMMENT '数值精度（10 系统计量单位及精度）'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '手工数据上报表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_metering
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_metering`;
CREATE TABLE `dim_enterprise_metering` (
  `id` varchar(192) NULL COMMENT 'id',
  `metering_name` varchar(768) NULL COMMENT '计量器具名称',
  `metering_type` varchar(768) NULL COMMENT '计量器具类型(8 计量器具编码)',
  `metering_level` tinyint NULL COMMENT '器具等级(文件3  meteringLevel: 1,器具等级，1：表示进出用能计量器具 2：表示主要次级用 能计量器具 3：表示主要用能设备计量器具)',
  `enterprise_energy_id` varchar(192) NULL COMMENT '用能类型管理表 id',
  `metering_parameter` varchar(768) NULL COMMENT '计量相关参数（用能类型表取）',
  `meter_code` varchar(192) NULL COMMENT '计量器具编号（表计编号）',
  `meter_value_field` text NULL COMMENT '表计取数字段（参数配置动态生成表）',
  `enterprise_code_data_id` varchar(192) NULL COMMENT '采集数据项表ID（采集数据项采集来源为现场仪表的）一对一',
  `data_code` varchar(192) NULL COMMENT '所属上报数据组合编码',
  `next_calibration` datetime NULL COMMENT '下次检定/校准时间',
  `data_code_calculate` varchar(768) NULL COMMENT '与上报数据组合编码算术关系1加 2减3乘4除',
  `data_code_ratio` varchar(768) NULL COMMENT '与上报数据组合编码算术系数。1代表全部2代表该计量器具采集的数据跟所属的上报数据组合编码的数值有关',
  `manu_facturer` varchar(768) NULL COMMENT '计量器具的生产厂家',
  `type_specification` varchar(768) NULL COMMENT '型号规格',
  `accuracy_level` varchar(768) NULL,
  `measure_range` varchar(768) NULL COMMENT '测量范围',
  `manage_code` varchar(768) NULL COMMENT '用能单位内部的计量器具管理编号',
  `calibration_state` tinyint NULL COMMENT '检定/校准状态，填写合格或者不合格',
  `calibration_cycle` varchar(768) NULL COMMENT '检定/校准周期，按 x 月或 x 年填写',
  `lately_calibration` datetime NULL COMMENT '最近一次检定/校准时间',
  `inspection_organization` varchar(768) NULL COMMENT '检验机构',
  `not_calibration` varchar(768) NULL COMMENT '未检定/校准原因',
  `installation_site` varchar(768) NULL COMMENT '安装地点',
  `install_org` tinyint NULL COMMENT '安装方,1：用能单位 2：能源供应公司 3：第三方公司（指合同 能源管理等）',
  `install_date` datetime NULL COMMENT '安装时间',
  `usr_system` tinyint NULL COMMENT '接入系统，指该计量器具的监测数据与哪个系统连接。1：表示 用能单位自身管理系统 2：表示能源供应公司系统',
  `measure_state` tinyint NULL COMMENT '目前状态，1：正常/2：故障/3：停用',
  `measure_state_date` datetime NULL COMMENT '状态发生时间，指目前状态发生的日期，如 什么时候开始正常使用，什么时候开始发生当前故障等',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `magnification` float NULL COMMENT '倍率',
  `energy_type` tinyint NULL COMMENT '计量器具用能方式',
  `is_related_monitor` tinyint NULL COMMENT '是否与监测工作相关',
  `ct` varchar(768) NULL COMMENT 'CT',
  `pt` varchar(768) NULL COMMENT 'PT',
  `field_type` tinyint NULL COMMENT '字段类型',
  `metering_parameter_type` varchar(768) NULL COMMENT '计量参数类型'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '计量器具信息表（表计）'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_platform_dict
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_platform_dict`;
CREATE TABLE `dim_enterprise_platform_dict` (
  `id` bigint NULL,
  `dict_type` varchar(6) NULL COMMENT '00采集数据分类编码，01一次能源 02二次能源 03耗能工质 04非能源类产品 05一次能源折标系数 06二次能源折标系数 07耗能工质折标系数 08能效指标 09经济指标  10其它数据 11生产工序 12采集系统分类 13 采集数据项数据用途 14计量器具类型',
  `energy_type` varchar(6) NULL COMMENT '能源类型',
  `is_class_type` tinyint NULL COMMENT '是否分类分项(0否，1是)',
  `type_name` varchar(108) NULL COMMENT '分类名称',
  `type_code` varchar(108) NULL COMMENT '分类编码',
  `class_name` varchar(108) NULL COMMENT '分项名称',
  `class_code` varchar(108) NULL COMMENT '分项编码
',
  `unit` varchar(108) NULL COMMENT '采集项单位',
  `is_change` tinyint NULL COMMENT '是否企业可维护（0不可变更，1可变更）',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `industry_code` varchar(18) NULL COMMENT '所属行业',
  `enable` tinyint NULL COMMENT '省平台是否启用这个数据',
  `is_modify` tinyint NULL COMMENT '是否被修改(1=被修改/0=未修改)'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '平台数据字典表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_process
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_process`;
CREATE TABLE `dim_enterprise_process` (
  `id` varchar(192) NULL COMMENT 'id',
  `process_name` varchar(768) NULL COMMENT '生产工序名称',
  `process_code` varchar(6) NULL,
  `f_process_code` varchar(192) NULL COMMENT '父工序编号',
  `process_level` tinyint NULL COMMENT '层级（1级00全厂，2级工序），最大2级',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `remark` varchar(765) NULL COMMENT '备注'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '生产层级工序信息表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_process_unit
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_process_unit`;
CREATE TABLE `dim_enterprise_process_unit` (
  `id` varchar(192) NULL COMMENT 'id',
  `process_code` varchar(6) NULL COMMENT '生产工序编号2位（1-2位）',
  `process_unit_code` varchar(6) NULL COMMENT '工序单元编码2位（3-4位）',
  `process_unit_name` varchar(768) NULL COMMENT '工序单元名称',
  `investment_time` datetime NULL COMMENT '投产日期',
  `ability` varchar(768) NULL COMMENT '生产能力',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `remark` varchar(765) NULL COMMENT '备注'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '生产工序单元表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_product
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_product`;
CREATE TABLE `dim_enterprise_product` (
  `id` varchar(192) NULL COMMENT 'id',
  `product_type_name` varchar(768) NULL COMMENT '产品类型名称',
  `product_name` varchar(768) NULL COMMENT '产品名称',
  `energy_type_code` varchar(12) NULL COMMENT '产品代码（4位）11-14位',
  `company` varchar(768) NULL COMMENT '单位',
  `industry_standard` float NULL COMMENT '单位能耗行业标准',
  `domestic_standard` float NULL COMMENT '单位能耗国内标准',
  `international_standard` float NULL COMMENT '单位能耗国际标准',
  `create_time` datetime NULL COMMENT '操作时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `erp_product_code` varchar(150) NULL,
  `benchmarking_level` float NULL COMMENT '标杆水平',
  `average_level` float NULL COMMENT '平均水平',
  `limit_value` float NULL COMMENT '限定值',
  `admission_value` float NULL COMMENT '准入值',
  `advanced_value` float NULL COMMENT '先进值'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '生产产品信息表（电力，钢铁，石油石化，水泥数据初始从平台拉取）'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_enterprise_transformer
-- ----------------------------
DROP TABLE IF EXISTS `dim_enterprise_transformer`;
CREATE TABLE `dim_enterprise_transformer` (
  `id` varchar(192) NULL,
  `name` varchar(375) NULL COMMENT '变压器名称',
  `number` varchar(12) NULL COMMENT '编号（数值4位）',
  `product_code` varchar(150) NULL COMMENT '产品代码',
  `unit_type` varchar(150) NULL COMMENT '设备型号',
  `rated_frequency` int NULL COMMENT '额定频率，单位：Hz',
  `rated_capacity` int NULL COMMENT '额定容量，单位：kVa',
  `max_demand` int NULL COMMENT '最大需量',
  `install_site` varchar(192) NULL COMMENT '安装场所',
  `install_date` datetime NULL COMMENT '安装时间',
  `status` int NULL COMMENT '状态 0 离线  1在线',
  `remarks` varchar(300) NULL COMMENT '备注信息'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '变压器'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_home_gather_cfg
-- ----------------------------
DROP TABLE IF EXISTS `dim_home_gather_cfg`;
CREATE TABLE `dim_home_gather_cfg` (
  `id` varchar(192) NULL,
  `alias_name` varchar(600) NULL COMMENT '采集数据项名称',
  `enterprise_code_data_id` varchar(192) NULL,
  `module_type` varchar(12) NULL COMMENT '1-综合能源消费量，2-主营产品信息，3-能源分布情况，4-主营产品分析，5-有序用电分析',
  `show_alias` varchar(60) NULL COMMENT '展示别名',
  `if_prod` varchar(12) NULL COMMENT '0-否，1-是',
  `consume_ratio` varchar(12) NULL COMMENT '0-否，1-是',
  `chart_order_num` varchar(12) NULL COMMENT '有序用电序号',
  `user_id` varchar(192) NULL COMMENT '创建人',
  `create_time` datetime NULL,
  `style` varchar(300) NULL COMMENT '图标 颜色',
  `efficient_enterprise_code_data_id` varchar(192) NULL COMMENT '能效指标的采集数据项Id',
  `sort` int NULL
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '首页采集配置表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_parameter_manager
-- ----------------------------
DROP TABLE IF EXISTS `dim_parameter_manager`;
CREATE TABLE `dim_parameter_manager` (
  `id` varchar(192) NULL COMMENT '参数ID',
  `table_name` varchar(192) NULL COMMENT '能源表名',
  `parameter_name` varchar(90) NULL COMMENT '参数名称',
  `metering_calculate_type` varchar(3) NULL COMMENT '表头值计算类型(0为累计值，1为瞬时值)',
  `status` varchar(3) NULL COMMENT '状态（0为占用，1为不可用）',
  `pm_sort` int NULL COMMENT '排序字段',
  `text` varchar(75) NULL COMMENT '中文描述',
  `magnification_type` int NULL COMMENT '倍率类型（ 0:无，1:电压 PT，2:电流 CT，3:倍率(CT×PT) ） '
) ENGINE=OLAP
UNIQUE KEY(`id`)
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_peak_valley_bil_manage
-- ----------------------------
DROP TABLE IF EXISTS `dim_peak_valley_bil_manage`;
CREATE TABLE `dim_peak_valley_bil_manage` (
  `id` varchar(192) NULL,
  `effective_months` varchar(192) NULL COMMENT '有效的月份',
  `bill_type` varchar(6) NULL COMMENT '电费段(0 峰 1 平 2 谷 来自字典) ',
  `price` decimal(20,8) NULL COMMENT '价格',
  `create_time` datetime NULL,
  `user_id` varchar(192) NULL
) ENGINE=OLAP
UNIQUE KEY(`id`)
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_peak_valley_time
-- ----------------------------
DROP TABLE IF EXISTS `dim_peak_valley_time`;
CREATE TABLE `dim_peak_valley_time` (
  `id` varchar(192) NULL,
  `start_time` varchar(36) NULL,
  `end_time` varchar(36) NULL,
  `create_time` datetime NULL,
  `user_id` varchar(192) NULL,
  `rel_id` varchar(192) NULL COMMENT '关联ID'
) ENGINE=OLAP
UNIQUE KEY(`id`)
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_shift_config
-- ----------------------------
DROP TABLE IF EXISTS `dim_shift_config`;
CREATE TABLE `dim_shift_config` (
  `id` varchar(192) NULL,
  `shift_name` varchar(90) NULL COMMENT '早班、中班、晚班',
  `shift_name_type` varchar(12) NULL COMMENT '0-早 1-中 2-晚',
  `shift_begin_time` varchar(15) NULL,
  `shift_end_time` varchar(15) NULL,
  `data_from` varchar(30) NULL COMMENT '0-系统新增',
  `create_time` datetime NULL,
  `user_id` varchar(192) NULL,
  `state` varchar(12) NULL COMMENT '0-正常 1-禁用',
  `data_type` varchar(12) NULL COMMENT '0-固定班次 1-自定义',
  `shift_order` varchar(12) NULL COMMENT '排序'
) ENGINE=OLAP
UNIQUE KEY(`id`)
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_shift_info
-- ----------------------------
DROP TABLE IF EXISTS `dim_shift_info`;
CREATE TABLE `dim_shift_info` (
  `id` varchar(192) NULL,
  `shift_date` date NULL,
  `shift_config_id` varchar(192) NULL,
  `shift_type` varchar(300) NULL COMMENT 'A B C D',
  `user_id` varchar(192) NULL,
  `create_time` datetime NULL,
  `data_from` varchar(30) NULL COMMENT '0-系统新增'
) ENGINE=OLAP
UNIQUE KEY(`id`)
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_sys_dict
-- ----------------------------
DROP TABLE IF EXISTS `dim_sys_dict`;
CREATE TABLE `dim_sys_dict` (
  `id` varchar(96) NULL,
  `dict_name` varchar(300) NULL COMMENT '字典名称',
  `dict_code` varchar(300) NULL COMMENT '字典编码',
  `description` varchar(765) NULL COMMENT '描述',
  `del_flag` int NULL COMMENT '删除状态',
  `create_by` varchar(96) NULL COMMENT '创建人',
  `create_time` datetime NULL COMMENT '创建时间',
  `update_by` varchar(96) NULL COMMENT '更新人',
  `update_time` datetime NULL COMMENT '更新时间',
  `type` bigint NULL COMMENT '字典类型0为string,1为number'
) ENGINE=OLAP
UNIQUE KEY(`id`)
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_sys_dict_item
-- ----------------------------
DROP TABLE IF EXISTS `dim_sys_dict_item`;
CREATE TABLE `dim_sys_dict_item` (
  `id` varchar(96) NULL,
  `dict_id` varchar(96) NULL COMMENT '字典id',
  `item_text` varchar(300) NULL COMMENT '字典项文本',
  `item_value` varchar(300) NULL COMMENT '字典项值',
  `description` varchar(765) NULL COMMENT '描述',
  `sort_order` int NULL COMMENT '排序',
  `status` int NULL COMMENT '状态（1启用 0不启用）',
  `create_by` varchar(96) NULL,
  `create_time` datetime NULL,
  `update_by` varchar(96) NULL,
  `update_time` datetime NULL
) ENGINE=OLAP
UNIQUE KEY(`id`)
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dim_sys_electric_limit
-- ----------------------------
DROP TABLE IF EXISTS `dim_sys_electric_limit`;
CREATE TABLE `dim_sys_electric_limit` (
  `id` varchar(96) NULL COMMENT 'ID',
  `energy_type_code` varchar(12) NULL COMMENT '能源类型',
  `process_code` varchar(6) NULL COMMENT '生产工序',
  `process_unit_code` varchar(6) NULL COMMENT '工序单元',
  `limit_value` decimal(10,0) NULL COMMENT '限额值',
  `start_time` datetime NULL COMMENT '开始时间',
  `end_time` datetime NULL COMMENT '结束时间',
  `create_time` datetime NULL COMMENT '创建时间',
  `user_id` varchar(192) NULL COMMENT '操作人',
  `equipment_code` varchar(6) NULL,
  `equipment_unit_code` varchar(6) NULL,
  `month` varchar(150) NULL
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '限电参数表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_alarm_record
-- ----------------------------
DROP TABLE IF EXISTS `dwd_alarm_record`;
CREATE TABLE `dwd_alarm_record` (
  `alarm_time` datetime NOT NULL COMMENT '报警时间',
  `alarm_object` varchar(64) NOT NULL COMMENT '报警对象',
  `alarm_type` int NOT NULL COMMENT '报警类型',
  `stat_period` int NOT NULL COMMENT '统计周期',
  `alarm_number` varchar(64) NULL COMMENT '报警编号',
  `alarm_setting_id` varchar(64) NULL COMMENT '报警设置ID',
  `alarm_level` varchar(16) NULL COMMENT '报警级别',
  `alarm_value` decimal(27,4) NULL COMMENT '报警值',
  `alarm_lower_limit` decimal(27,4) NULL COMMENT '报警下限',
  `alarm_upper_limit` decimal(27,4) NULL COMMENT '报警上限',
  `alarm_message` varchar(256) NULL COMMENT '报警信息',
  `status` int NULL COMMENT '处理状态',
  `handle_process` varchar(1024) NULL COMMENT '处理过程',
  `is_upload` int NULL COMMENT '是否上报',
  `created_by` varchar(32) NULL COMMENT '创建人',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL COMMENT '更新时间'
) ENGINE=OLAP
UNIQUE KEY(`alarm_time`, `alarm_object`, `alarm_type`, `stat_period`)
COMMENT 'OLAP'
PARTITION BY RANGE(`alarm_time`)
(PARTITION p202506 VALUES [('2025-06-01 00:00:00'), ('2025-07-01 00:00:00')),
PARTITION p202507 VALUES [('2025-07-01 00:00:00'), ('2025-08-01 00:00:00')),
PARTITION p202508 VALUES [('2025-08-01 00:00:00'), ('2025-09-01 00:00:00')),
PARTITION p202509 VALUES [('2025-09-01 00:00:00'), ('2025-10-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`alarm_object`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-6",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "true",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_code_data_summary_day
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_code_data_summary_day`;
CREATE TABLE `dwd_enterprise_code_data_summary_day` (
  `summary_time` datetime NOT NULL COMMENT '采集的结束时间(汇总时间)',
  `enterprise_code_data_id` varchar(64) NOT NULL COMMENT '采集数据项ID',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `field_name` varchar(40) NULL COMMENT '参数名称',
  `table_field` varchar(255) NULL COMMENT '表字段',
  `start_time` datetime NULL COMMENT '采集的开始时间',
  `process_code` varchar(2) NULL COMMENT '生产工序',
  `process_unit_code` varchar(2) NULL COMMENT '工序单元',
  `energy_type_code` varchar(4) NULL COMMENT '数据分类11-14位',
  `meter_value` decimal(27,4) NULL COMMENT '实际值',
  `meter_display_value` decimal(27,4) NULL COMMENT '示数值',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标煤值',
  `begin_value` decimal(27,4) NULL COMMENT '开始值',
  `end_value` decimal(27,4) NULL COMMENT '结束值',
  `count` int NULL COMMENT '采集次数',
  `handle_type` int NULL COMMENT '处理类型',
  `install_site` varchar(128) NULL COMMENT '安装地址',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL COMMENT '更新时间'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `enterprise_code_data_id`)
COMMENT 'OLAP'
PARTITION BY RANGE(`summary_time`)
(PARTITION p202412 VALUES [('2024-12-01 00:00:00'), ('2025-01-01 00:00:00')),
PARTITION p202501 VALUES [('2025-01-01 00:00:00'), ('2025-02-01 00:00:00')),
PARTITION p202502 VALUES [('2025-02-01 00:00:00'), ('2025-03-01 00:00:00')),
PARTITION p202503 VALUES [('2025-03-01 00:00:00'), ('2025-04-01 00:00:00')),
PARTITION p202504 VALUES [('2025-04-01 00:00:00'), ('2025-05-01 00:00:00')),
PARTITION p202505 VALUES [('2025-05-01 00:00:00'), ('2025-06-01 00:00:00')),
PARTITION p202506 VALUES [('2025-06-01 00:00:00'), ('2025-07-01 00:00:00')),
PARTITION p202507 VALUES [('2025-07-01 00:00:00'), ('2025-08-01 00:00:00')),
PARTITION p202508 VALUES [('2025-08-01 00:00:00'), ('2025-09-01 00:00:00')),
PARTITION p202509 VALUES [('2025-09-01 00:00:00'), ('2025-10-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`enterprise_code_data_id`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-12",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "true",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_code_data_summary_hour
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_code_data_summary_hour`;
CREATE TABLE `dwd_enterprise_code_data_summary_hour` (
  `summary_time` datetime NOT NULL COMMENT '采集的结束时间(汇总时间)',
  `enterprise_code_data_id` varchar(64) NOT NULL COMMENT '采集数据项ID',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `field_name` varchar(40) NULL COMMENT '参数名称',
  `table_field` varchar(255) NULL COMMENT '表字段',
  `start_time` datetime NULL COMMENT '采集的开始时间',
  `process_code` varchar(2) NULL COMMENT '生产工序',
  `process_unit_code` varchar(2) NULL COMMENT '工序单元',
  `energy_type_code` varchar(4) NULL COMMENT '数据分类11-14位',
  `meter_value` decimal(27,4) NULL COMMENT '实际值',
  `meter_display_value` decimal(27,4) NULL COMMENT '示数值',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标煤值',
  `begin_value` decimal(27,4) NULL COMMENT '开始值',
  `end_value` decimal(27,4) NULL COMMENT '结束值',
  `count` int NULL COMMENT '采集次数',
  `handle_type` int NULL COMMENT '处理类型',
  `install_site` varchar(128) NULL COMMENT '安装地址',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL COMMENT '更新时间'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `enterprise_code_data_id`)
COMMENT 'OLAP'
PARTITION BY RANGE(`summary_time`)
(PARTITION p202412 VALUES [('2024-12-01 00:00:00'), ('2025-01-01 00:00:00')),
PARTITION p202501 VALUES [('2025-01-01 00:00:00'), ('2025-02-01 00:00:00')),
PARTITION p202502 VALUES [('2025-02-01 00:00:00'), ('2025-03-01 00:00:00')),
PARTITION p202503 VALUES [('2025-03-01 00:00:00'), ('2025-04-01 00:00:00')),
PARTITION p202504 VALUES [('2025-04-01 00:00:00'), ('2025-05-01 00:00:00')),
PARTITION p202505 VALUES [('2025-05-01 00:00:00'), ('2025-06-01 00:00:00')),
PARTITION p202506 VALUES [('2025-06-01 00:00:00'), ('2025-07-01 00:00:00')),
PARTITION p202507 VALUES [('2025-07-01 00:00:00'), ('2025-08-01 00:00:00')),
PARTITION p202508 VALUES [('2025-08-01 00:00:00'), ('2025-09-01 00:00:00')),
PARTITION p202509 VALUES [('2025-09-01 00:00:00'), ('2025-10-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`enterprise_code_data_id`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-12",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "true",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_code_data_summary_minute
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_code_data_summary_minute`;
CREATE TABLE `dwd_enterprise_code_data_summary_minute` (
  `summary_time` datetime NOT NULL COMMENT '采集的结束时间(汇总时间)',
  `enterprise_code_data_id` varchar(64) NOT NULL COMMENT '采集数据项ID',
  `start_time` datetime NULL COMMENT '采集的开始时间',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `field_name` varchar(40) NULL COMMENT '参数名称',
  `table_field` varchar(255) NULL COMMENT '表字段',
  `process_code` varchar(2) NULL COMMENT '生产工序',
  `process_unit_code` varchar(2) NULL COMMENT '工序单元',
  `energy_type_code` varchar(4) NULL COMMENT '数据分类11-14位',
  `meter_value` decimal(27,4) NULL COMMENT '实际值',
  `meter_display_value` decimal(27,4) NULL COMMENT '示数值',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标煤值',
  `begin_value` decimal(27,4) NULL COMMENT '开始值',
  `end_value` decimal(27,4) NULL COMMENT '结束值',
  `count` int NULL COMMENT '采集次数',
  `metering_calculate_type` varchar(1) NULL COMMENT '表头值类型(1为瞬时值，0为累计值)',
  `summary_type` int NULL COMMENT '统计类型',
  `handle_type` int NULL COMMENT '处理类型',
  `install_site` varchar(128) NULL COMMENT '安装地址',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL COMMENT '更新时间'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `enterprise_code_data_id`)
COMMENT 'OLAP'
PARTITION BY RANGE(`summary_time`)
(PARTITION p202412 VALUES [('2024-12-01 00:00:00'), ('2025-01-01 00:00:00')),
PARTITION p202501 VALUES [('2025-01-01 00:00:00'), ('2025-02-01 00:00:00')),
PARTITION p202502 VALUES [('2025-02-01 00:00:00'), ('2025-03-01 00:00:00')),
PARTITION p202503 VALUES [('2025-03-01 00:00:00'), ('2025-04-01 00:00:00')),
PARTITION p202504 VALUES [('2025-04-01 00:00:00'), ('2025-05-01 00:00:00')),
PARTITION p202505 VALUES [('2025-05-01 00:00:00'), ('2025-06-01 00:00:00')),
PARTITION p202506 VALUES [('2025-06-01 00:00:00'), ('2025-07-01 00:00:00')),
PARTITION p202507 VALUES [('2025-07-01 00:00:00'), ('2025-08-01 00:00:00')),
PARTITION p202508 VALUES [('2025-08-01 00:00:00'), ('2025-09-01 00:00:00')),
PARTITION p202509 VALUES [('2025-09-01 00:00:00'), ('2025-10-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`enterprise_code_data_id`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-12",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "true",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_code_data_summary_month
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_code_data_summary_month`;
CREATE TABLE `dwd_enterprise_code_data_summary_month` (
  `summary_time` varchar(8) NOT NULL COMMENT '采集的结束时间(汇总时间)',
  `enterprise_code_data_id` varchar(64) NOT NULL COMMENT '采集数据项ID',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `field_name` varchar(40) NULL COMMENT '参数名称',
  `table_field` varchar(255) NULL COMMENT '表字段',
  `start_time` datetime NULL COMMENT '采集的开始时间',
  `process_code` varchar(2) NULL COMMENT '生产工序',
  `process_unit_code` varchar(2) NULL COMMENT '工序单元',
  `energy_type_code` varchar(4) NULL COMMENT '数据分类11-14位',
  `meter_value` decimal(27,4) NULL COMMENT '实际值',
  `meter_display_value` decimal(27,4) NULL COMMENT '示数值',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标煤值',
  `begin_value` decimal(27,4) NULL COMMENT '开始值',
  `end_value` decimal(27,4) NULL COMMENT '结束值',
  `count` int NULL COMMENT '采集次数',
  `handle_type` int NULL COMMENT '处理类型',
  `install_site` varchar(128) NULL COMMENT '安装地址',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL COMMENT '更新时间'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `enterprise_code_data_id`)
COMMENT 'OLAP'
DISTRIBUTED BY HASH(`enterprise_code_data_id`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_code_data_summary_year
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_code_data_summary_year`;
CREATE TABLE `dwd_enterprise_code_data_summary_year` (
  `summary_time` varchar(4) NOT NULL COMMENT '采集的结束时间(汇总时间)',
  `enterprise_code_data_id` varchar(64) NOT NULL COMMENT '采集数据项ID',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `field_name` varchar(40) NULL COMMENT '参数名称',
  `table_field` varchar(255) NULL COMMENT '表字段',
  `start_time` datetime NULL COMMENT '采集的开始时间',
  `process_code` varchar(2) NULL COMMENT '生产工序',
  `process_unit_code` varchar(2) NULL COMMENT '工序单元',
  `energy_type_code` varchar(4) NULL COMMENT '数据分类11-14位',
  `meter_value` decimal(27,4) NULL COMMENT '实际值',
  `meter_display_value` decimal(27,4) NULL COMMENT '示数值',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标煤值',
  `begin_value` decimal(27,4) NULL COMMENT '开始值',
  `end_value` decimal(27,4) NULL COMMENT '结束值',
  `count` int NULL COMMENT '采集次数',
  `handle_type` int NULL COMMENT '处理类型',
  `install_site` varchar(128) NULL COMMENT '安装地址',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL COMMENT '更新时间'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `enterprise_code_data_id`)
COMMENT 'OLAP'
DISTRIBUTED BY HASH(`enterprise_code_data_id`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_meter
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_meter`;
CREATE TABLE `dwd_enterprise_meter` (
  `summary_time` datetime NULL COMMENT '采集时间',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `install_site` varchar(128) NULL COMMENT '地址ID',
  `level_depth` int NULL COMMENT '地址深度',
  `level_name` varchar(384) NULL COMMENT '地址名称',
  `path` varchar(765) NULL COMMENT '地址路径',
  `positive_power` decimal(27,4) NULL COMMENT '正向有功电量实际值(kWh)',
  `positive_display_power` decimal(27,4) NULL COMMENT '正向有功电量示数值(kWh)',
  `positive_power_endvalue` decimal(27,4) NULL COMMENT '正向有功电量表码',
  `negative_power` decimal(27,4) NULL COMMENT '反向有功电量实际值(kWh)',
  `negative_display_power` decimal(27,4) NULL COMMENT '反向有功电量示数值(kWh)',
  `negative_power_endvalue` decimal(27,4) NULL COMMENT '反向有功电量表码',
  `positive_reactive_power` decimal(27,4) NULL COMMENT '正向无功电量实际值(kvarh)',
  `positive_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `positive_reactive_power_endvalue` decimal(27,4) NULL COMMENT '正向无功电量表码',
  `negative_reactive_power` decimal(27,4) NULL COMMENT '反向无功电量实际值(kvarh)',
  `negative_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `negative_reactive_power_endvalue` decimal(27,4) NULL COMMENT '反向无功电量表码',
  `total_power` decimal(27,4) NULL COMMENT '总有功功率(kW)实际值',
  `total_display_power` decimal(27,4) NULL COMMENT '总有功功率(kW)示数值',
  `total_power_pd` decimal(27,4) NULL COMMENT '总有功功率实时需量实际值',
  `total_power_pd_d` decimal(27,4) NULL COMMENT '总有功功率实时需量示数值',
  `phase_a_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)实际值',
  `phase_a_display_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)示数值',
  `phase_b_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)实际值',
  `phase_b_display_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)示数值',
  `phase_c_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)实际值',
  `phase_c_display_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)示数值',
  `reactive_power` decimal(27,4) NULL COMMENT '总无功功率(kW)实际值',
  `reactive_display_power` decimal(27,4) NULL COMMENT '总无功功率(kW)示数值',
  `phase_a_reactive_power` decimal(27,4) NULL COMMENT 'A相无功功率实际值',
  `phase_a_reactive_display_power` decimal(27,4) NULL COMMENT 'A相无功功率示数值',
  `phase_b_reactive_power` decimal(27,4) NULL COMMENT 'B相无功功率实际值',
  `phase_b_reactive_display_power` decimal(27,4) NULL COMMENT 'B相无功功率示数值',
  `phase_c_reactive_power` decimal(27,4) NULL COMMENT 'C相无功功率实际值',
  `phase_c_reactive_display_power` decimal(27,4) NULL COMMENT 'C相无功功率示数值',
  `peak_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)实际值',
  `peak_display_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)示数值',
  `reverse_peak_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)实际值',
  `reverse_peak_display_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)示数值',
  `high_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)实际值',
  `high_display_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)示数值',
  `reverse_high_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)实际值',
  `reverse_high_display_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)示数值',
  `normal_power` decimal(27,4) NULL COMMENT '平时电量(kWh)实际值',
  `normal_display_power` decimal(27,4) NULL COMMENT '平时电量(kWh)示数值',
  `reverse_normal_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)实际值',
  `reverse_normal_display_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)示数值',
  `low_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)实际值',
  `low_display_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)示数值',
  `reverse_low_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)实际值',
  `reverse_low_display_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)示数值',
  `total_apparent_power` decimal(27,4) NULL COMMENT '总视在功率实际值',
  `total_apparent_power_d` decimal(27,4) NULL COMMENT '总视在功率示数值',
  `phase_a_apparent_power` decimal(27,4) NULL COMMENT 'A相视在功率实际值',
  `phase_a_apparent_power_d` decimal(27,4) NULL COMMENT 'A相视在功率示数值',
  `phase_b_apparent_power` decimal(27,4) NULL COMMENT 'B相视在功率实际值',
  `phase_b_apparent_power_d` decimal(27,4) NULL COMMENT 'B相视在功率示数值',
  `phase_c_apparent_power` decimal(27,4) NULL COMMENT 'C相视在功率实际值',
  `phase_c_apparent_power_d` decimal(27,4) NULL COMMENT 'C相视在功率示数值',
  `total_power_factor` decimal(27,4) NULL COMMENT '总功率因数实际值',
  `total_power_factor_d` decimal(27,4) NULL COMMENT '总功率因数示数值',
  `phase_a_power_factor` decimal(27,4) NULL COMMENT 'A相功率因数实际值',
  `phase_a_power_factor_d` decimal(27,4) NULL COMMENT 'A相功率因数示数值',
  `phase_b_power_factor` decimal(27,4) NULL COMMENT 'B相功率因数实际值',
  `phase_b_power_factor_d` decimal(27,4) NULL COMMENT 'B相功率因数示数值',
  `phase_c_power_factor` decimal(27,4) NULL COMMENT 'C相功率因数实际值',
  `phase_c_power_factor_d` decimal(27,4) NULL COMMENT 'C相功率因数示数值',
  `max_positive_active_demand` decimal(27,4) NULL COMMENT '正向有功总最大需量实际值',
  `max_positive_active_demand_d` decimal(27,4) NULL COMMENT '正向有功总最大需量示数值',
  `phase_a_voltage` decimal(27,4) NULL COMMENT 'A相电压实际值',
  `phase_a_voltage_d` decimal(27,4) NULL COMMENT 'A相电压示数值',
  `phase_b_voltage` decimal(27,4) NULL COMMENT 'B相电压实际值',
  `phase_b_voltage_d` decimal(27,4) NULL COMMENT 'B相电压示数值',
  `phase_c_voltage` decimal(27,4) NULL COMMENT 'C相电压实际值',
  `phase_c_voltage_d` decimal(27,4) NULL COMMENT 'C相电压示数值',
  `voltage_unbalance` decimal(27,4) NULL COMMENT '电压不平衡度实际值',
  `voltage_unbalance_d` decimal(27,4) NULL COMMENT '电压不平衡度示数值',
  `line_voltage_uab` decimal(27,4) NULL COMMENT '线电压Uab',
  `line_voltage_uab_d` decimal(27,4) NULL COMMENT '线电压Uab示数值',
  `line_voltage_ubc` decimal(27,4) NULL COMMENT '线电压Ubc',
  `line_voltage_ubc_d` decimal(27,4) NULL COMMENT '线电压Ubc示数值',
  `line_voltage_uca` decimal(27,4) NULL COMMENT '线电压Uca',
  `line_voltage_uca_d` decimal(27,4) NULL COMMENT '线电压Uca示数值',
  `line_voltage_unbalance` decimal(27,4) NULL COMMENT '线电压不平衡度实际值',
  `line_voltage_unbalance_d` decimal(27,4) NULL COMMENT '线电压不平衡度示数值',
  `phase_a_current` decimal(27,4) NULL COMMENT 'A相电流实际值',
  `phase_a_current_d` decimal(27,4) NULL COMMENT 'A相电流示数值',
  `phase_b_current` decimal(27,4) NULL COMMENT 'B相电流实际值',
  `phase_b_current_d` decimal(27,4) NULL COMMENT 'B相电流示数值',
  `phase_c_current` decimal(27,4) NULL COMMENT 'C相电流实际值',
  `phase_c_current_d` decimal(27,4) NULL COMMENT 'C相电流示数值',
  `current_unbalance` decimal(27,4) NULL COMMENT '电流不平衡度实际值',
  `current_unbalance_d` decimal(27,4) NULL COMMENT '电流不平衡度示数值',
  `frequency` decimal(27,4) NULL COMMENT '频率实际值',
  `frequency_d` decimal(27,4) NULL COMMENT '频率示数值',
  `quadrant1_reactive_energy` decimal(27,4) NULL COMMENT '第一象限无功总电能实际值',
  `quadrant1_reactive_energy_d` decimal(27,4) NULL COMMENT '第一象限无功总电能示数值',
  `quadrant1_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第一象限无功总电能表码',
  `quadrant2_reactive_energy` decimal(27,4) NULL COMMENT '第二象限无功总电能实际值',
  `quadrant2_reactive_energy_d` decimal(27,4) NULL COMMENT '第二象限无功总电能示数值',
  `quadrant2_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第二象限无功总电能表码',
  `quadrant3_reactive_energy` decimal(27,4) NULL COMMENT '第三象限无功总电能实际值',
  `quadrant3_reactive_energy_d` decimal(27,4) NULL COMMENT '第三象限无功总电能示数值',
  `quadrant3_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第三象限无功总电能表码',
  `quadrant4_reactive_energy` decimal(27,4) NULL COMMENT '第四象限无功总电能实际值',
  `quadrant4_reactive_energy_d` decimal(27,4) NULL COMMENT '第四象限无功总电能示数值',
  `quadrant4_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第四象限无功总电能表码',
  `input_reactive_energy` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)实际值',
  `input_reactive_energy_d` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)示数值',
  `output_reactive_energy` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)实际值',
  `output_reactive_energy_d` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)示数值',
  `peak_electricity_fee` decimal(27,4) NULL COMMENT '尖电费实际值',
  `peak_electricity_fee_d` decimal(27,4) NULL COMMENT '尖电费示数值',
  `high_electricity_fee` decimal(27,4) NULL COMMENT '峰电费实际值',
  `high_electricity_fee_d` decimal(27,4) NULL COMMENT '峰电费示数值',
  `normal_electricity_fee` decimal(27,4) NULL COMMENT '平电费实际值',
  `normal_electricity_fee_d` decimal(27,4) NULL COMMENT '平电费示数值',
  `low_electricity_fee` decimal(27,4) NULL COMMENT '谷电费实际值',
  `low_electricity_fee_d` decimal(27,4) NULL COMMENT '谷电费示数值',
  `total_electricity_fee` decimal(27,4) NULL COMMENT '总电费实际值',
  `total_electricity_fee_d` decimal(27,4) NULL COMMENT '总电费示数值',
  `stop_state` int NULL COMMENT '停机状态',
  `standby_state` int NULL COMMENT '待机状态',
  `run_state` int NULL COMMENT '运行状态',
  `is_abnormal` varchar(65533) NULL COMMENT '是否异常 0 无异常 1 有异常'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `meter_code`)
COMMENT 'OLAP'
PARTITION BY RANGE(`summary_time`)
(PARTITION p202409 VALUES [('0000-01-01 00:00:00'), ('2024-09-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`summary_time`, `meter_code`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-2147483648",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "false",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_meter_day
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_meter_day`;
CREATE TABLE `dwd_enterprise_meter_day` (
  `summary_time` datetime NULL COMMENT '采集时间',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `install_site` varchar(128) NULL COMMENT '地址ID',
  `level_depth` int NULL COMMENT '地址深度',
  `level_name` varchar(384) NULL COMMENT '地址名称',
  `path` varchar(765) NULL COMMENT '地址路径',
  `positive_power` decimal(27,4) NULL COMMENT '正向有功电量实际值(kWh)',
  `positive_display_power` decimal(27,4) NULL COMMENT '正向有功电量示数值(kWh)',
  `positive_power_endvalue` decimal(27,4) NULL COMMENT '正向有功电量表码',
  `negative_power` decimal(27,4) NULL COMMENT '反向有功电量实际值(kWh)',
  `negative_display_power` decimal(27,4) NULL COMMENT '反向有功电量示数值(kWh)',
  `negative_power_endvalue` decimal(27,4) NULL COMMENT '反向有功电量表码',
  `positive_reactive_power` decimal(27,4) NULL COMMENT '正向无功电量实际值(kvarh)',
  `positive_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `positive_reactive_power_endvalue` decimal(27,4) NULL COMMENT '正向无功电量表码',
  `negative_reactive_power` decimal(27,4) NULL COMMENT '反向无功电量实际值(kvarh)',
  `negative_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `negative_reactive_power_endvalue` decimal(27,4) NULL COMMENT '反向无功电量表码',
  `total_power` decimal(27,4) NULL COMMENT '总有功功率(kW)实际值',
  `total_display_power` decimal(27,4) NULL COMMENT '总有功功率(kW)示数值',
  `total_power_pd` decimal(27,4) NULL COMMENT '总有功功率实时需量实际值',
  `total_power_pd_d` decimal(27,4) NULL COMMENT '总有功功率实时需量示数值',
  `phase_a_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)实际值',
  `phase_a_display_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)示数值',
  `phase_b_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)实际值',
  `phase_b_display_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)示数值',
  `phase_c_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)实际值',
  `phase_c_display_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)示数值',
  `reactive_power` decimal(27,4) NULL COMMENT '总无功功率(kW)实际值',
  `reactive_display_power` decimal(27,4) NULL COMMENT '总无功功率(kW)示数值',
  `phase_a_reactive_power` decimal(27,4) NULL COMMENT 'A相无功功率实际值',
  `phase_a_reactive_display_power` decimal(27,4) NULL COMMENT 'A相无功功率示数值',
  `phase_b_reactive_power` decimal(27,4) NULL COMMENT 'B相无功功率实际值',
  `phase_b_reactive_display_power` decimal(27,4) NULL COMMENT 'B相无功功率示数值',
  `phase_c_reactive_power` decimal(27,4) NULL COMMENT 'C相无功功率实际值',
  `phase_c_reactive_display_power` decimal(27,4) NULL COMMENT 'C相无功功率示数值',
  `peak_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)实际值',
  `peak_display_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)示数值',
  `reverse_peak_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)实际值',
  `reverse_peak_display_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)示数值',
  `high_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)实际值',
  `high_display_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)示数值',
  `reverse_high_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)实际值',
  `reverse_high_display_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)示数值',
  `normal_power` decimal(27,4) NULL COMMENT '平时电量(kWh)实际值',
  `normal_display_power` decimal(27,4) NULL COMMENT '平时电量(kWh)示数值',
  `reverse_normal_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)实际值',
  `reverse_normal_display_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)示数值',
  `low_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)实际值',
  `low_display_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)示数值',
  `reverse_low_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)实际值',
  `reverse_low_display_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)示数值',
  `total_apparent_power` decimal(27,4) NULL COMMENT '总视在功率实际值',
  `total_apparent_power_d` decimal(27,4) NULL COMMENT '总视在功率示数值',
  `phase_a_apparent_power` decimal(27,4) NULL COMMENT 'A相视在功率实际值',
  `phase_a_apparent_power_d` decimal(27,4) NULL COMMENT 'A相视在功率示数值',
  `phase_b_apparent_power` decimal(27,4) NULL COMMENT 'B相视在功率实际值',
  `phase_b_apparent_power_d` decimal(27,4) NULL COMMENT 'B相视在功率示数值',
  `phase_c_apparent_power` decimal(27,4) NULL COMMENT 'C相视在功率实际值',
  `phase_c_apparent_power_d` decimal(27,4) NULL COMMENT 'C相视在功率示数值',
  `total_power_factor` decimal(27,4) NULL COMMENT '总功率因数实际值',
  `total_power_factor_d` decimal(27,4) NULL COMMENT '总功率因数示数值',
  `phase_a_power_factor` decimal(27,4) NULL COMMENT 'A相功率因数实际值',
  `phase_a_power_factor_d` decimal(27,4) NULL COMMENT 'A相功率因数示数值',
  `phase_b_power_factor` decimal(27,4) NULL COMMENT 'B相功率因数实际值',
  `phase_b_power_factor_d` decimal(27,4) NULL COMMENT 'B相功率因数示数值',
  `phase_c_power_factor` decimal(27,4) NULL COMMENT 'C相功率因数实际值',
  `phase_c_power_factor_d` decimal(27,4) NULL COMMENT 'C相功率因数示数值',
  `max_positive_active_demand` decimal(27,4) NULL COMMENT '正向有功总最大需量实际值',
  `max_positive_active_demand_d` decimal(27,4) NULL COMMENT '正向有功总最大需量示数值',
  `phase_a_voltage` decimal(27,4) NULL COMMENT 'A相电压实际值',
  `phase_a_voltage_d` decimal(27,4) NULL COMMENT 'A相电压示数值',
  `phase_b_voltage` decimal(27,4) NULL COMMENT 'B相电压实际值',
  `phase_b_voltage_d` decimal(27,4) NULL COMMENT 'B相电压示数值',
  `phase_c_voltage` decimal(27,4) NULL COMMENT 'C相电压实际值',
  `phase_c_voltage_d` decimal(27,4) NULL COMMENT 'C相电压示数值',
  `voltage_unbalance` decimal(27,4) NULL COMMENT '电压不平衡度实际值',
  `voltage_unbalance_d` decimal(27,4) NULL COMMENT '电压不平衡度示数值',
  `line_voltage_uab` decimal(27,4) NULL COMMENT '线电压Uab',
  `line_voltage_uab_d` decimal(27,4) NULL COMMENT '线电压Uab示数值',
  `line_voltage_ubc` decimal(27,4) NULL COMMENT '线电压Ubc',
  `line_voltage_ubc_d` decimal(27,4) NULL COMMENT '线电压Ubc示数值',
  `line_voltage_uca` decimal(27,4) NULL COMMENT '线电压Uca',
  `line_voltage_uca_d` decimal(27,4) NULL COMMENT '线电压Uca示数值',
  `line_voltage_unbalance` decimal(27,4) NULL COMMENT '线电压不平衡度实际值',
  `line_voltage_unbalance_d` decimal(27,4) NULL COMMENT '线电压不平衡度示数值',
  `phase_a_current` decimal(27,4) NULL COMMENT 'A相电流实际值',
  `phase_a_current_d` decimal(27,4) NULL COMMENT 'A相电流示数值',
  `phase_b_current` decimal(27,4) NULL COMMENT 'B相电流实际值',
  `phase_b_current_d` decimal(27,4) NULL COMMENT 'B相电流示数值',
  `phase_c_current` decimal(27,4) NULL COMMENT 'C相电流实际值',
  `phase_c_current_d` decimal(27,4) NULL COMMENT 'C相电流示数值',
  `current_unbalance` decimal(27,4) NULL COMMENT '电流不平衡度实际值',
  `current_unbalance_d` decimal(27,4) NULL COMMENT '电流不平衡度示数值',
  `frequency` decimal(27,4) NULL COMMENT '频率实际值',
  `frequency_d` decimal(27,4) NULL COMMENT '频率示数值',
  `quadrant1_reactive_energy` decimal(27,4) NULL COMMENT '第一象限无功总电能实际值',
  `quadrant1_reactive_energy_d` decimal(27,4) NULL COMMENT '第一象限无功总电能示数值',
  `quadrant1_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第一象限无功总电能表码',
  `quadrant2_reactive_energy` decimal(27,4) NULL COMMENT '第二象限无功总电能实际值',
  `quadrant2_reactive_energy_d` decimal(27,4) NULL COMMENT '第二象限无功总电能示数值',
  `quadrant2_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第二象限无功总电能表码',
  `quadrant3_reactive_energy` decimal(27,4) NULL COMMENT '第三象限无功总电能实际值',
  `quadrant3_reactive_energy_d` decimal(27,4) NULL COMMENT '第三象限无功总电能示数值',
  `quadrant3_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第三象限无功总电能表码',
  `quadrant4_reactive_energy` decimal(27,4) NULL COMMENT '第四象限无功总电能实际值',
  `quadrant4_reactive_energy_d` decimal(27,4) NULL COMMENT '第四象限无功总电能示数值',
  `quadrant4_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第四象限无功总电能表码',
  `input_reactive_energy` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)实际值',
  `input_reactive_energy_d` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)示数值',
  `output_reactive_energy` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)实际值',
  `output_reactive_energy_d` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)示数值',
  `peak_electricity_fee` decimal(27,4) NULL COMMENT '尖电费实际值',
  `peak_electricity_fee_d` decimal(27,4) NULL COMMENT '尖电费示数值',
  `high_electricity_fee` decimal(27,4) NULL COMMENT '峰电费实际值',
  `high_electricity_fee_d` decimal(27,4) NULL COMMENT '峰电费示数值',
  `normal_electricity_fee` decimal(27,4) NULL COMMENT '平电费实际值',
  `normal_electricity_fee_d` decimal(27,4) NULL COMMENT '平电费示数值',
  `low_electricity_fee` decimal(27,4) NULL COMMENT '谷电费实际值',
  `low_electricity_fee_d` decimal(27,4) NULL COMMENT '谷电费示数值',
  `total_electricity_fee` decimal(27,4) NULL COMMENT '总电费实际值',
  `total_electricity_fee_d` decimal(27,4) NULL COMMENT '总电费示数值',
  `stop_state` int NULL COMMENT '停机状态',
  `standby_state` int NULL COMMENT '待机状态',
  `run_state` int NULL COMMENT '运行状态'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `meter_code`)
COMMENT 'OLAP'
PARTITION BY RANGE(`summary_time`)
(PARTITION p202509 VALUES [('0000-01-01 00:00:00'), ('2025-10-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`summary_time`, `meter_code`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-2147483648",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "false",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_meter_hour
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_meter_hour`;
CREATE TABLE `dwd_enterprise_meter_hour` (
  `summary_time` datetime NULL COMMENT '采集时间',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `install_site` varchar(128) NULL COMMENT '地址ID',
  `level_depth` int NULL COMMENT '地址深度',
  `level_name` varchar(384) NULL COMMENT '地址名称',
  `path` varchar(765) NULL COMMENT '地址路径',
  `positive_power` decimal(27,4) NULL COMMENT '正向有功电量实际值(kWh)',
  `positive_display_power` decimal(27,4) NULL COMMENT '正向有功电量示数值(kWh)',
  `positive_power_endvalue` decimal(27,4) NULL COMMENT '正向有功电量表码',
  `negative_power` decimal(27,4) NULL COMMENT '反向有功电量实际值(kWh)',
  `negative_display_power` decimal(27,4) NULL COMMENT '反向有功电量示数值(kWh)',
  `negative_power_endvalue` decimal(27,4) NULL COMMENT '反向有功电量表码',
  `positive_reactive_power` decimal(27,4) NULL COMMENT '正向无功电量实际值(kvarh)',
  `positive_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `positive_reactive_power_endvalue` decimal(27,4) NULL COMMENT '正向无功电量表码',
  `negative_reactive_power` decimal(27,4) NULL COMMENT '反向无功电量实际值(kvarh)',
  `negative_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `negative_reactive_power_endvalue` decimal(27,4) NULL COMMENT '反向无功电量表码',
  `total_power` decimal(27,4) NULL COMMENT '总有功功率(kW)实际值',
  `total_display_power` decimal(27,4) NULL COMMENT '总有功功率(kW)示数值',
  `total_power_pd` decimal(27,4) NULL COMMENT '总有功功率实时需量实际值',
  `total_power_pd_d` decimal(27,4) NULL COMMENT '总有功功率实时需量示数值',
  `phase_a_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)实际值',
  `phase_a_display_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)示数值',
  `phase_b_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)实际值',
  `phase_b_display_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)示数值',
  `phase_c_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)实际值',
  `phase_c_display_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)示数值',
  `reactive_power` decimal(27,4) NULL COMMENT '总无功功率(kW)实际值',
  `reactive_display_power` decimal(27,4) NULL COMMENT '总无功功率(kW)示数值',
  `phase_a_reactive_power` decimal(27,4) NULL COMMENT 'A相无功功率实际值',
  `phase_a_reactive_display_power` decimal(27,4) NULL COMMENT 'A相无功功率示数值',
  `phase_b_reactive_power` decimal(27,4) NULL COMMENT 'B相无功功率实际值',
  `phase_b_reactive_display_power` decimal(27,4) NULL COMMENT 'B相无功功率示数值',
  `phase_c_reactive_power` decimal(27,4) NULL COMMENT 'C相无功功率实际值',
  `phase_c_reactive_display_power` decimal(27,4) NULL COMMENT 'C相无功功率示数值',
  `peak_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)实际值',
  `peak_display_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)示数值',
  `reverse_peak_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)实际值',
  `reverse_peak_display_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)示数值',
  `high_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)实际值',
  `high_display_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)示数值',
  `reverse_high_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)实际值',
  `reverse_high_display_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)示数值',
  `normal_power` decimal(27,4) NULL COMMENT '平时电量(kWh)实际值',
  `normal_display_power` decimal(27,4) NULL COMMENT '平时电量(kWh)示数值',
  `reverse_normal_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)实际值',
  `reverse_normal_display_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)示数值',
  `low_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)实际值',
  `low_display_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)示数值',
  `reverse_low_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)实际值',
  `reverse_low_display_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)示数值',
  `total_apparent_power` decimal(27,4) NULL COMMENT '总视在功率实际值',
  `total_apparent_power_d` decimal(27,4) NULL COMMENT '总视在功率示数值',
  `phase_a_apparent_power` decimal(27,4) NULL COMMENT 'A相视在功率实际值',
  `phase_a_apparent_power_d` decimal(27,4) NULL COMMENT 'A相视在功率示数值',
  `phase_b_apparent_power` decimal(27,4) NULL COMMENT 'B相视在功率实际值',
  `phase_b_apparent_power_d` decimal(27,4) NULL COMMENT 'B相视在功率示数值',
  `phase_c_apparent_power` decimal(27,4) NULL COMMENT 'C相视在功率实际值',
  `phase_c_apparent_power_d` decimal(27,4) NULL COMMENT 'C相视在功率示数值',
  `total_power_factor` decimal(27,4) NULL COMMENT '总功率因数实际值',
  `total_power_factor_d` decimal(27,4) NULL COMMENT '总功率因数示数值',
  `phase_a_power_factor` decimal(27,4) NULL COMMENT 'A相功率因数实际值',
  `phase_a_power_factor_d` decimal(27,4) NULL COMMENT 'A相功率因数示数值',
  `phase_b_power_factor` decimal(27,4) NULL COMMENT 'B相功率因数实际值',
  `phase_b_power_factor_d` decimal(27,4) NULL COMMENT 'B相功率因数示数值',
  `phase_c_power_factor` decimal(27,4) NULL COMMENT 'C相功率因数实际值',
  `phase_c_power_factor_d` decimal(27,4) NULL COMMENT 'C相功率因数示数值',
  `max_positive_active_demand` decimal(27,4) NULL COMMENT '正向有功总最大需量实际值',
  `max_positive_active_demand_d` decimal(27,4) NULL COMMENT '正向有功总最大需量示数值',
  `phase_a_voltage` decimal(27,4) NULL COMMENT 'A相电压实际值',
  `phase_a_voltage_d` decimal(27,4) NULL COMMENT 'A相电压示数值',
  `phase_b_voltage` decimal(27,4) NULL COMMENT 'B相电压实际值',
  `phase_b_voltage_d` decimal(27,4) NULL COMMENT 'B相电压示数值',
  `phase_c_voltage` decimal(27,4) NULL COMMENT 'C相电压实际值',
  `phase_c_voltage_d` decimal(27,4) NULL COMMENT 'C相电压示数值',
  `voltage_unbalance` decimal(27,4) NULL COMMENT '电压不平衡度实际值',
  `voltage_unbalance_d` decimal(27,4) NULL COMMENT '电压不平衡度示数值',
  `line_voltage_uab` decimal(27,4) NULL COMMENT '线电压Uab',
  `line_voltage_uab_d` decimal(27,4) NULL COMMENT '线电压Uab示数值',
  `line_voltage_ubc` decimal(27,4) NULL COMMENT '线电压Ubc',
  `line_voltage_ubc_d` decimal(27,4) NULL COMMENT '线电压Ubc示数值',
  `line_voltage_uca` decimal(27,4) NULL COMMENT '线电压Uca',
  `line_voltage_uca_d` decimal(27,4) NULL COMMENT '线电压Uca示数值',
  `line_voltage_unbalance` decimal(27,4) NULL COMMENT '线电压不平衡度实际值',
  `line_voltage_unbalance_d` decimal(27,4) NULL COMMENT '线电压不平衡度示数值',
  `phase_a_current` decimal(27,4) NULL COMMENT 'A相电流实际值',
  `phase_a_current_d` decimal(27,4) NULL COMMENT 'A相电流示数值',
  `phase_b_current` decimal(27,4) NULL COMMENT 'B相电流实际值',
  `phase_b_current_d` decimal(27,4) NULL COMMENT 'B相电流示数值',
  `phase_c_current` decimal(27,4) NULL COMMENT 'C相电流实际值',
  `phase_c_current_d` decimal(27,4) NULL COMMENT 'C相电流示数值',
  `current_unbalance` decimal(27,4) NULL COMMENT '电流不平衡度实际值',
  `current_unbalance_d` decimal(27,4) NULL COMMENT '电流不平衡度示数值',
  `frequency` decimal(27,4) NULL COMMENT '频率实际值',
  `frequency_d` decimal(27,4) NULL COMMENT '频率示数值',
  `quadrant1_reactive_energy` decimal(27,4) NULL COMMENT '第一象限无功总电能实际值',
  `quadrant1_reactive_energy_d` decimal(27,4) NULL COMMENT '第一象限无功总电能示数值',
  `quadrant1_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第一象限无功总电能表码',
  `quadrant2_reactive_energy` decimal(27,4) NULL COMMENT '第二象限无功总电能实际值',
  `quadrant2_reactive_energy_d` decimal(27,4) NULL COMMENT '第二象限无功总电能示数值',
  `quadrant2_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第二象限无功总电能表码',
  `quadrant3_reactive_energy` decimal(27,4) NULL COMMENT '第三象限无功总电能实际值',
  `quadrant3_reactive_energy_d` decimal(27,4) NULL COMMENT '第三象限无功总电能示数值',
  `quadrant3_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第三象限无功总电能表码',
  `quadrant4_reactive_energy` decimal(27,4) NULL COMMENT '第四象限无功总电能实际值',
  `quadrant4_reactive_energy_d` decimal(27,4) NULL COMMENT '第四象限无功总电能示数值',
  `quadrant4_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第四象限无功总电能表码',
  `input_reactive_energy` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)实际值',
  `input_reactive_energy_d` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)示数值',
  `output_reactive_energy` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)实际值',
  `output_reactive_energy_d` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)示数值',
  `peak_electricity_fee` decimal(27,4) NULL COMMENT '尖电费实际值',
  `peak_electricity_fee_d` decimal(27,4) NULL COMMENT '尖电费示数值',
  `high_electricity_fee` decimal(27,4) NULL COMMENT '峰电费实际值',
  `high_electricity_fee_d` decimal(27,4) NULL COMMENT '峰电费示数值',
  `normal_electricity_fee` decimal(27,4) NULL COMMENT '平电费实际值',
  `normal_electricity_fee_d` decimal(27,4) NULL COMMENT '平电费示数值',
  `low_electricity_fee` decimal(27,4) NULL COMMENT '谷电费实际值',
  `low_electricity_fee_d` decimal(27,4) NULL COMMENT '谷电费示数值',
  `total_electricity_fee` decimal(27,4) NULL COMMENT '总电费实际值',
  `total_electricity_fee_d` decimal(27,4) NULL COMMENT '总电费示数值',
  `stop_state` int NULL COMMENT '停机状态',
  `standby_state` int NULL COMMENT '待机状态',
  `run_state` int NULL COMMENT '运行状态'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `meter_code`)
COMMENT 'OLAP'
PARTITION BY RANGE(`summary_time`)
(PARTITION p202509 VALUES [('0000-01-01 00:00:00'), ('2025-10-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`summary_time`, `meter_code`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-2147483648",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "false",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_meter_minute
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_meter_minute`;
CREATE TABLE `dwd_enterprise_meter_minute` (
  `summary_time` datetime NULL COMMENT '采集时间',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `install_site` varchar(128) NULL COMMENT '地址ID',
  `level_depth` int NULL COMMENT '地址深度',
  `level_name` varchar(384) NULL COMMENT '地址名称',
  `path` varchar(765) NULL COMMENT '地址路径',
  `positive_power` decimal(27,4) NULL COMMENT '正向有功电量实际值(kWh)',
  `positive_display_power` decimal(27,4) NULL COMMENT '正向有功电量示数值(kWh)',
  `positive_power_endvalue` decimal(27,4) NULL COMMENT '正向有功电量表码',
  `negative_power` decimal(27,4) NULL COMMENT '反向有功电量实际值(kWh)',
  `negative_display_power` decimal(27,4) NULL COMMENT '反向有功电量示数值(kWh)',
  `negative_power_endvalue` decimal(27,4) NULL COMMENT '反向有功电量表码',
  `positive_reactive_power` decimal(27,4) NULL COMMENT '正向无功电量实际值(kvarh)',
  `positive_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `positive_reactive_power_endvalue` decimal(27,4) NULL COMMENT '正向无功电量表码',
  `negative_reactive_power` decimal(27,4) NULL COMMENT '反向无功电量实际值(kvarh)',
  `negative_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `negative_reactive_power_endvalue` decimal(27,4) NULL COMMENT '反向无功电量表码',
  `total_power` decimal(27,4) NULL COMMENT '总有功功率(kW)实际值',
  `total_display_power` decimal(27,4) NULL COMMENT '总有功功率(kW)示数值',
  `total_power_pd` decimal(27,4) NULL COMMENT '总有功功率实时需量实际值',
  `total_power_pd_d` decimal(27,4) NULL COMMENT '总有功功率实时需量示数值',
  `phase_a_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)实际值',
  `phase_a_display_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)示数值',
  `phase_b_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)实际值',
  `phase_b_display_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)示数值',
  `phase_c_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)实际值',
  `phase_c_display_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)示数值',
  `reactive_power` decimal(27,4) NULL COMMENT '总无功功率(kW)实际值',
  `reactive_display_power` decimal(27,4) NULL COMMENT '总无功功率(kW)示数值',
  `phase_a_reactive_power` decimal(27,4) NULL COMMENT 'A相无功功率实际值',
  `phase_a_reactive_display_power` decimal(27,4) NULL COMMENT 'A相无功功率示数值',
  `phase_b_reactive_power` decimal(27,4) NULL COMMENT 'B相无功功率实际值',
  `phase_b_reactive_display_power` decimal(27,4) NULL COMMENT 'B相无功功率示数值',
  `phase_c_reactive_power` decimal(27,4) NULL COMMENT 'C相无功功率实际值',
  `phase_c_reactive_display_power` decimal(27,4) NULL COMMENT 'C相无功功率示数值',
  `peak_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)实际值',
  `peak_display_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)示数值',
  `reverse_peak_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)实际值',
  `reverse_peak_display_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)示数值',
  `high_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)实际值',
  `high_display_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)示数值',
  `reverse_high_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)实际值',
  `reverse_high_display_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)示数值',
  `normal_power` decimal(27,4) NULL COMMENT '平时电量(kWh)实际值',
  `normal_display_power` decimal(27,4) NULL COMMENT '平时电量(kWh)示数值',
  `reverse_normal_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)实际值',
  `reverse_normal_display_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)示数值',
  `low_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)实际值',
  `low_display_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)示数值',
  `reverse_low_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)实际值',
  `reverse_low_display_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)示数值',
  `total_apparent_power` decimal(27,4) NULL COMMENT '总视在功率实际值',
  `total_apparent_power_d` decimal(27,4) NULL COMMENT '总视在功率示数值',
  `phase_a_apparent_power` decimal(27,4) NULL COMMENT 'A相视在功率实际值',
  `phase_a_apparent_power_d` decimal(27,4) NULL COMMENT 'A相视在功率示数值',
  `phase_b_apparent_power` decimal(27,4) NULL COMMENT 'B相视在功率实际值',
  `phase_b_apparent_power_d` decimal(27,4) NULL COMMENT 'B相视在功率示数值',
  `phase_c_apparent_power` decimal(27,4) NULL COMMENT 'C相视在功率实际值',
  `phase_c_apparent_power_d` decimal(27,4) NULL COMMENT 'C相视在功率示数值',
  `total_power_factor` decimal(27,4) NULL COMMENT '总功率因数实际值',
  `total_power_factor_d` decimal(27,4) NULL COMMENT '总功率因数示数值',
  `phase_a_power_factor` decimal(27,4) NULL COMMENT 'A相功率因数实际值',
  `phase_a_power_factor_d` decimal(27,4) NULL COMMENT 'A相功率因数示数值',
  `phase_b_power_factor` decimal(27,4) NULL COMMENT 'B相功率因数实际值',
  `phase_b_power_factor_d` decimal(27,4) NULL COMMENT 'B相功率因数示数值',
  `phase_c_power_factor` decimal(27,4) NULL COMMENT 'C相功率因数实际值',
  `phase_c_power_factor_d` decimal(27,4) NULL COMMENT 'C相功率因数示数值',
  `max_positive_active_demand` decimal(27,4) NULL COMMENT '正向有功总最大需量实际值',
  `max_positive_active_demand_d` decimal(27,4) NULL COMMENT '正向有功总最大需量示数值',
  `phase_a_voltage` decimal(27,4) NULL COMMENT 'A相电压实际值',
  `phase_a_voltage_d` decimal(27,4) NULL COMMENT 'A相电压示数值',
  `phase_b_voltage` decimal(27,4) NULL COMMENT 'B相电压实际值',
  `phase_b_voltage_d` decimal(27,4) NULL COMMENT 'B相电压示数值',
  `phase_c_voltage` decimal(27,4) NULL COMMENT 'C相电压实际值',
  `phase_c_voltage_d` decimal(27,4) NULL COMMENT 'C相电压示数值',
  `voltage_unbalance` decimal(27,4) NULL COMMENT '电压不平衡度实际值',
  `voltage_unbalance_d` decimal(27,4) NULL COMMENT '电压不平衡度示数值',
  `line_voltage_uab` decimal(27,4) NULL COMMENT '线电压Uab',
  `line_voltage_uab_d` decimal(27,4) NULL COMMENT '线电压Uab示数值',
  `line_voltage_ubc` decimal(27,4) NULL COMMENT '线电压Ubc',
  `line_voltage_ubc_d` decimal(27,4) NULL COMMENT '线电压Ubc示数值',
  `line_voltage_uca` decimal(27,4) NULL COMMENT '线电压Uca',
  `line_voltage_uca_d` decimal(27,4) NULL COMMENT '线电压Uca示数值',
  `line_voltage_unbalance` decimal(27,4) NULL COMMENT '线电压不平衡度实际值',
  `line_voltage_unbalance_d` decimal(27,4) NULL COMMENT '线电压不平衡度示数值',
  `phase_a_current` decimal(27,4) NULL COMMENT 'A相电流实际值',
  `phase_a_current_d` decimal(27,4) NULL COMMENT 'A相电流示数值',
  `phase_b_current` decimal(27,4) NULL COMMENT 'B相电流实际值',
  `phase_b_current_d` decimal(27,4) NULL COMMENT 'B相电流示数值',
  `phase_c_current` decimal(27,4) NULL COMMENT 'C相电流实际值',
  `phase_c_current_d` decimal(27,4) NULL COMMENT 'C相电流示数值',
  `current_unbalance` decimal(27,4) NULL COMMENT '电流不平衡度实际值',
  `current_unbalance_d` decimal(27,4) NULL COMMENT '电流不平衡度示数值',
  `frequency` decimal(27,4) NULL COMMENT '频率实际值',
  `frequency_d` decimal(27,4) NULL COMMENT '频率示数值',
  `quadrant1_reactive_energy` decimal(27,4) NULL COMMENT '第一象限无功总电能实际值',
  `quadrant1_reactive_energy_d` decimal(27,4) NULL COMMENT '第一象限无功总电能示数值',
  `quadrant1_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第一象限无功总电能表码',
  `quadrant2_reactive_energy` decimal(27,4) NULL COMMENT '第二象限无功总电能实际值',
  `quadrant2_reactive_energy_d` decimal(27,4) NULL COMMENT '第二象限无功总电能示数值',
  `quadrant2_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第二象限无功总电能表码',
  `quadrant3_reactive_energy` decimal(27,4) NULL COMMENT '第三象限无功总电能实际值',
  `quadrant3_reactive_energy_d` decimal(27,4) NULL COMMENT '第三象限无功总电能示数值',
  `quadrant3_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第三象限无功总电能表码',
  `quadrant4_reactive_energy` decimal(27,4) NULL COMMENT '第四象限无功总电能实际值',
  `quadrant4_reactive_energy_d` decimal(27,4) NULL COMMENT '第四象限无功总电能示数值',
  `quadrant4_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第四象限无功总电能表码',
  `input_reactive_energy` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)实际值',
  `input_reactive_energy_d` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)示数值',
  `output_reactive_energy` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)实际值',
  `output_reactive_energy_d` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)示数值',
  `peak_electricity_fee` decimal(27,4) NULL COMMENT '尖电费实际值',
  `peak_electricity_fee_d` decimal(27,4) NULL COMMENT '尖电费示数值',
  `high_electricity_fee` decimal(27,4) NULL COMMENT '峰电费实际值',
  `high_electricity_fee_d` decimal(27,4) NULL COMMENT '峰电费示数值',
  `normal_electricity_fee` decimal(27,4) NULL COMMENT '平电费实际值',
  `normal_electricity_fee_d` decimal(27,4) NULL COMMENT '平电费示数值',
  `low_electricity_fee` decimal(27,4) NULL COMMENT '谷电费实际值',
  `low_electricity_fee_d` decimal(27,4) NULL COMMENT '谷电费示数值',
  `total_electricity_fee` decimal(27,4) NULL COMMENT '总电费实际值',
  `total_electricity_fee_d` decimal(27,4) NULL COMMENT '总电费示数值'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `meter_code`)
COMMENT 'OLAP'
PARTITION BY RANGE(`summary_time`)
(PARTITION p202401 VALUES [('0000-01-01 00:00:00'), ('2024-03-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`summary_time`, `meter_code`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-2147483648",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "false",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_meter_month
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_meter_month`;
CREATE TABLE `dwd_enterprise_meter_month` (
  `summary_time` varchar(7) NULL COMMENT '采集时间',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `install_site` varchar(128) NULL COMMENT '地址ID',
  `level_depth` int NULL COMMENT '地址深度',
  `level_name` varchar(384) NULL COMMENT '地址名称',
  `path` varchar(765) NULL COMMENT '地址路径',
  `positive_power` decimal(27,4) NULL COMMENT '正向有功电量实际值(kWh)',
  `positive_display_power` decimal(27,4) NULL COMMENT '正向有功电量示数值(kWh)',
  `positive_power_endvalue` decimal(27,4) NULL COMMENT '正向有功电量表码',
  `negative_power` decimal(27,4) NULL COMMENT '反向有功电量实际值(kWh)',
  `negative_display_power` decimal(27,4) NULL COMMENT '反向有功电量示数值(kWh)',
  `negative_power_endvalue` decimal(27,4) NULL COMMENT '反向有功电量表码',
  `positive_reactive_power` decimal(27,4) NULL COMMENT '正向无功电量实际值(kvarh)',
  `positive_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `positive_reactive_power_endvalue` decimal(27,4) NULL COMMENT '正向无功电量表码',
  `negative_reactive_power` decimal(27,4) NULL COMMENT '反向无功电量实际值(kvarh)',
  `negative_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `negative_reactive_power_endvalue` decimal(27,4) NULL COMMENT '反向无功电量表码',
  `total_power` decimal(27,4) NULL COMMENT '总有功功率(kW)实际值',
  `total_display_power` decimal(27,4) NULL COMMENT '总有功功率(kW)示数值',
  `total_power_pd` decimal(27,4) NULL COMMENT '总有功功率实时需量实际值',
  `total_power_pd_d` decimal(27,4) NULL COMMENT '总有功功率实时需量示数值',
  `phase_a_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)实际值',
  `phase_a_display_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)示数值',
  `phase_b_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)实际值',
  `phase_b_display_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)示数值',
  `phase_c_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)实际值',
  `phase_c_display_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)示数值',
  `reactive_power` decimal(27,4) NULL COMMENT '总无功功率(kW)实际值',
  `reactive_display_power` decimal(27,4) NULL COMMENT '总无功功率(kW)示数值',
  `phase_a_reactive_power` decimal(27,4) NULL COMMENT 'A相无功功率实际值',
  `phase_a_reactive_display_power` decimal(27,4) NULL COMMENT 'A相无功功率示数值',
  `phase_b_reactive_power` decimal(27,4) NULL COMMENT 'B相无功功率实际值',
  `phase_b_reactive_display_power` decimal(27,4) NULL COMMENT 'B相无功功率示数值',
  `phase_c_reactive_power` decimal(27,4) NULL COMMENT 'C相无功功率实际值',
  `phase_c_reactive_display_power` decimal(27,4) NULL COMMENT 'C相无功功率示数值',
  `peak_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)实际值',
  `peak_display_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)示数值',
  `reverse_peak_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)实际值',
  `reverse_peak_display_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)示数值',
  `high_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)实际值',
  `high_display_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)示数值',
  `reverse_high_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)实际值',
  `reverse_high_display_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)示数值',
  `normal_power` decimal(27,4) NULL COMMENT '平时电量(kWh)实际值',
  `normal_display_power` decimal(27,4) NULL COMMENT '平时电量(kWh)示数值',
  `reverse_normal_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)实际值',
  `reverse_normal_display_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)示数值',
  `low_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)实际值',
  `low_display_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)示数值',
  `reverse_low_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)实际值',
  `reverse_low_display_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)示数值',
  `total_apparent_power` decimal(27,4) NULL COMMENT '总视在功率实际值',
  `total_apparent_power_d` decimal(27,4) NULL COMMENT '总视在功率示数值',
  `phase_a_apparent_power` decimal(27,4) NULL COMMENT 'A相视在功率实际值',
  `phase_a_apparent_power_d` decimal(27,4) NULL COMMENT 'A相视在功率示数值',
  `phase_b_apparent_power` decimal(27,4) NULL COMMENT 'B相视在功率实际值',
  `phase_b_apparent_power_d` decimal(27,4) NULL COMMENT 'B相视在功率示数值',
  `phase_c_apparent_power` decimal(27,4) NULL COMMENT 'C相视在功率实际值',
  `phase_c_apparent_power_d` decimal(27,4) NULL COMMENT 'C相视在功率示数值',
  `total_power_factor` decimal(27,4) NULL COMMENT '总功率因数实际值',
  `total_power_factor_d` decimal(27,4) NULL COMMENT '总功率因数示数值',
  `phase_a_power_factor` decimal(27,4) NULL COMMENT 'A相功率因数实际值',
  `phase_a_power_factor_d` decimal(27,4) NULL COMMENT 'A相功率因数示数值',
  `phase_b_power_factor` decimal(27,4) NULL COMMENT 'B相功率因数实际值',
  `phase_b_power_factor_d` decimal(27,4) NULL COMMENT 'B相功率因数示数值',
  `phase_c_power_factor` decimal(27,4) NULL COMMENT 'C相功率因数实际值',
  `phase_c_power_factor_d` decimal(27,4) NULL COMMENT 'C相功率因数示数值',
  `max_positive_active_demand` decimal(27,4) NULL COMMENT '正向有功总最大需量实际值',
  `max_positive_active_demand_d` decimal(27,4) NULL COMMENT '正向有功总最大需量示数值',
  `phase_a_voltage` decimal(27,4) NULL COMMENT 'A相电压实际值',
  `phase_a_voltage_d` decimal(27,4) NULL COMMENT 'A相电压示数值',
  `phase_b_voltage` decimal(27,4) NULL COMMENT 'B相电压实际值',
  `phase_b_voltage_d` decimal(27,4) NULL COMMENT 'B相电压示数值',
  `phase_c_voltage` decimal(27,4) NULL COMMENT 'C相电压实际值',
  `phase_c_voltage_d` decimal(27,4) NULL COMMENT 'C相电压示数值',
  `voltage_unbalance` decimal(27,4) NULL COMMENT '电压不平衡度实际值',
  `voltage_unbalance_d` decimal(27,4) NULL COMMENT '电压不平衡度示数值',
  `line_voltage_uab` decimal(27,4) NULL COMMENT '线电压Uab',
  `line_voltage_uab_d` decimal(27,4) NULL COMMENT '线电压Uab示数值',
  `line_voltage_ubc` decimal(27,4) NULL COMMENT '线电压Ubc',
  `line_voltage_ubc_d` decimal(27,4) NULL COMMENT '线电压Ubc示数值',
  `line_voltage_uca` decimal(27,4) NULL COMMENT '线电压Uca',
  `line_voltage_uca_d` decimal(27,4) NULL COMMENT '线电压Uca示数值',
  `line_voltage_unbalance` decimal(27,4) NULL COMMENT '线电压不平衡度实际值',
  `line_voltage_unbalance_d` decimal(27,4) NULL COMMENT '线电压不平衡度示数值',
  `phase_a_current` decimal(27,4) NULL COMMENT 'A相电流实际值',
  `phase_a_current_d` decimal(27,4) NULL COMMENT 'A相电流示数值',
  `phase_b_current` decimal(27,4) NULL COMMENT 'B相电流实际值',
  `phase_b_current_d` decimal(27,4) NULL COMMENT 'B相电流示数值',
  `phase_c_current` decimal(27,4) NULL COMMENT 'C相电流实际值',
  `phase_c_current_d` decimal(27,4) NULL COMMENT 'C相电流示数值',
  `current_unbalance` decimal(27,4) NULL COMMENT '电流不平衡度实际值',
  `current_unbalance_d` decimal(27,4) NULL COMMENT '电流不平衡度示数值',
  `frequency` decimal(27,4) NULL COMMENT '频率实际值',
  `frequency_d` decimal(27,4) NULL COMMENT '频率示数值',
  `quadrant1_reactive_energy` decimal(27,4) NULL COMMENT '第一象限无功总电能实际值',
  `quadrant1_reactive_energy_d` decimal(27,4) NULL COMMENT '第一象限无功总电能示数值',
  `quadrant1_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第一象限无功总电能表码',
  `quadrant2_reactive_energy` decimal(27,4) NULL COMMENT '第二象限无功总电能实际值',
  `quadrant2_reactive_energy_d` decimal(27,4) NULL COMMENT '第二象限无功总电能示数值',
  `quadrant2_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第二象限无功总电能表码',
  `quadrant3_reactive_energy` decimal(27,4) NULL COMMENT '第三象限无功总电能实际值',
  `quadrant3_reactive_energy_d` decimal(27,4) NULL COMMENT '第三象限无功总电能示数值',
  `quadrant3_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第三象限无功总电能表码',
  `quadrant4_reactive_energy` decimal(27,4) NULL COMMENT '第四象限无功总电能实际值',
  `quadrant4_reactive_energy_d` decimal(27,4) NULL COMMENT '第四象限无功总电能示数值',
  `quadrant4_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第四象限无功总电能表码',
  `input_reactive_energy` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)实际值',
  `input_reactive_energy_d` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)示数值',
  `output_reactive_energy` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)实际值',
  `output_reactive_energy_d` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)示数值',
  `peak_electricity_fee` decimal(27,4) NULL COMMENT '尖电费实际值',
  `peak_electricity_fee_d` decimal(27,4) NULL COMMENT '尖电费示数值',
  `high_electricity_fee` decimal(27,4) NULL COMMENT '峰电费实际值',
  `high_electricity_fee_d` decimal(27,4) NULL COMMENT '峰电费示数值',
  `normal_electricity_fee` decimal(27,4) NULL COMMENT '平电费实际值',
  `normal_electricity_fee_d` decimal(27,4) NULL COMMENT '平电费示数值',
  `low_electricity_fee` decimal(27,4) NULL COMMENT '谷电费实际值',
  `low_electricity_fee_d` decimal(27,4) NULL COMMENT '谷电费示数值',
  `total_electricity_fee` decimal(27,4) NULL COMMENT '总电费实际值',
  `total_electricity_fee_d` decimal(27,4) NULL COMMENT '总电费示数值',
  `stop_state` int NULL COMMENT '停机状态',
  `standby_state` int NULL COMMENT '待机状态',
  `run_state` int NULL COMMENT '运行状态'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `meter_code`)
COMMENT 'OLAP'
DISTRIBUTED BY HASH(`summary_time`, `meter_code`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dwd_enterprise_meter_year
-- ----------------------------
DROP TABLE IF EXISTS `dwd_enterprise_meter_year`;
CREATE TABLE `dwd_enterprise_meter_year` (
  `summary_time` varchar(4) NULL COMMENT '采集时间',
  `meter_code` varchar(64) NULL COMMENT '表计编号',
  `install_site` varchar(128) NULL COMMENT '地址ID',
  `level_depth` int NULL COMMENT '地址深度',
  `level_name` varchar(384) NULL COMMENT '地址名称',
  `path` varchar(765) NULL COMMENT '地址路径',
  `positive_power` decimal(27,4) NULL COMMENT '正向有功电量实际值(kWh)',
  `positive_display_power` decimal(27,4) NULL COMMENT '正向有功电量示数值(kWh)',
  `positive_power_endvalue` decimal(27,4) NULL COMMENT '正向有功电量表码',
  `negative_power` decimal(27,4) NULL COMMENT '反向有功电量实际值(kWh)',
  `negative_display_power` decimal(27,4) NULL COMMENT '反向有功电量示数值(kWh)',
  `negative_power_endvalue` decimal(27,4) NULL COMMENT '反向有功电量表码',
  `positive_reactive_power` decimal(27,4) NULL COMMENT '正向无功电量实际值(kvarh)',
  `positive_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `positive_reactive_power_endvalue` decimal(27,4) NULL COMMENT '正向无功电量表码',
  `negative_reactive_power` decimal(27,4) NULL COMMENT '反向无功电量实际值(kvarh)',
  `negative_reactive_display_power` decimal(27,4) NULL COMMENT '正向无功电量示数值(kvarh)',
  `negative_reactive_power_endvalue` decimal(27,4) NULL COMMENT '反向无功电量表码',
  `total_power` decimal(27,4) NULL COMMENT '总有功功率(kW)实际值',
  `total_display_power` decimal(27,4) NULL COMMENT '总有功功率(kW)示数值',
  `total_power_pd` decimal(27,4) NULL COMMENT '总有功功率实时需量实际值',
  `total_power_pd_d` decimal(27,4) NULL COMMENT '总有功功率实时需量示数值',
  `phase_a_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)实际值',
  `phase_a_display_power` decimal(27,4) NULL COMMENT 'A相有功功率(kW)示数值',
  `phase_b_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)实际值',
  `phase_b_display_power` decimal(27,4) NULL COMMENT 'B相有功功率(kW)示数值',
  `phase_c_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)实际值',
  `phase_c_display_power` decimal(27,4) NULL COMMENT 'C相有功功率(kW)示数值',
  `reactive_power` decimal(27,4) NULL COMMENT '总无功功率(kW)实际值',
  `reactive_display_power` decimal(27,4) NULL COMMENT '总无功功率(kW)示数值',
  `phase_a_reactive_power` decimal(27,4) NULL COMMENT 'A相无功功率实际值',
  `phase_a_reactive_display_power` decimal(27,4) NULL COMMENT 'A相无功功率示数值',
  `phase_b_reactive_power` decimal(27,4) NULL COMMENT 'B相无功功率实际值',
  `phase_b_reactive_display_power` decimal(27,4) NULL COMMENT 'B相无功功率示数值',
  `phase_c_reactive_power` decimal(27,4) NULL COMMENT 'C相无功功率实际值',
  `phase_c_reactive_display_power` decimal(27,4) NULL COMMENT 'C相无功功率示数值',
  `peak_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)实际值',
  `peak_display_power` decimal(27,4) NULL COMMENT '尖时电量(kWh)示数值',
  `reverse_peak_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)实际值',
  `reverse_peak_display_power` decimal(27,4) NULL COMMENT '反向尖时电量(kWh)示数值',
  `high_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)实际值',
  `high_display_power` decimal(27,4) NULL COMMENT '峰时电量(kWh)示数值',
  `reverse_high_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)实际值',
  `reverse_high_display_power` decimal(27,4) NULL COMMENT '反向峰时电量(kWh)示数值',
  `normal_power` decimal(27,4) NULL COMMENT '平时电量(kWh)实际值',
  `normal_display_power` decimal(27,4) NULL COMMENT '平时电量(kWh)示数值',
  `reverse_normal_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)实际值',
  `reverse_normal_display_power` decimal(27,4) NULL COMMENT '反向平时电量(kWh)示数值',
  `low_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)实际值',
  `low_display_power` decimal(27,4) NULL COMMENT '谷时电量(kWh)示数值',
  `reverse_low_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)实际值',
  `reverse_low_display_power` decimal(27,4) NULL COMMENT '反向谷时电量(kWh)示数值',
  `total_apparent_power` decimal(27,4) NULL COMMENT '总视在功率实际值',
  `total_apparent_power_d` decimal(27,4) NULL COMMENT '总视在功率示数值',
  `phase_a_apparent_power` decimal(27,4) NULL COMMENT 'A相视在功率实际值',
  `phase_a_apparent_power_d` decimal(27,4) NULL COMMENT 'A相视在功率示数值',
  `phase_b_apparent_power` decimal(27,4) NULL COMMENT 'B相视在功率实际值',
  `phase_b_apparent_power_d` decimal(27,4) NULL COMMENT 'B相视在功率示数值',
  `phase_c_apparent_power` decimal(27,4) NULL COMMENT 'C相视在功率实际值',
  `phase_c_apparent_power_d` decimal(27,4) NULL COMMENT 'C相视在功率示数值',
  `total_power_factor` decimal(27,4) NULL COMMENT '总功率因数实际值',
  `total_power_factor_d` decimal(27,4) NULL COMMENT '总功率因数示数值',
  `phase_a_power_factor` decimal(27,4) NULL COMMENT 'A相功率因数实际值',
  `phase_a_power_factor_d` decimal(27,4) NULL COMMENT 'A相功率因数示数值',
  `phase_b_power_factor` decimal(27,4) NULL COMMENT 'B相功率因数实际值',
  `phase_b_power_factor_d` decimal(27,4) NULL COMMENT 'B相功率因数示数值',
  `phase_c_power_factor` decimal(27,4) NULL COMMENT 'C相功率因数实际值',
  `phase_c_power_factor_d` decimal(27,4) NULL COMMENT 'C相功率因数示数值',
  `max_positive_active_demand` decimal(27,4) NULL COMMENT '正向有功总最大需量实际值',
  `max_positive_active_demand_d` decimal(27,4) NULL COMMENT '正向有功总最大需量示数值',
  `phase_a_voltage` decimal(27,4) NULL COMMENT 'A相电压实际值',
  `phase_a_voltage_d` decimal(27,4) NULL COMMENT 'A相电压示数值',
  `phase_b_voltage` decimal(27,4) NULL COMMENT 'B相电压实际值',
  `phase_b_voltage_d` decimal(27,4) NULL COMMENT 'B相电压示数值',
  `phase_c_voltage` decimal(27,4) NULL COMMENT 'C相电压实际值',
  `phase_c_voltage_d` decimal(27,4) NULL COMMENT 'C相电压示数值',
  `voltage_unbalance` decimal(27,4) NULL COMMENT '电压不平衡度实际值',
  `voltage_unbalance_d` decimal(27,4) NULL COMMENT '电压不平衡度示数值',
  `line_voltage_uab` decimal(27,4) NULL COMMENT '线电压Uab',
  `line_voltage_uab_d` decimal(27,4) NULL COMMENT '线电压Uab示数值',
  `line_voltage_ubc` decimal(27,4) NULL COMMENT '线电压Ubc',
  `line_voltage_ubc_d` decimal(27,4) NULL COMMENT '线电压Ubc示数值',
  `line_voltage_uca` decimal(27,4) NULL COMMENT '线电压Uca',
  `line_voltage_uca_d` decimal(27,4) NULL COMMENT '线电压Uca示数值',
  `line_voltage_unbalance` decimal(27,4) NULL COMMENT '线电压不平衡度实际值',
  `line_voltage_unbalance_d` decimal(27,4) NULL COMMENT '线电压不平衡度示数值',
  `phase_a_current` decimal(27,4) NULL COMMENT 'A相电流实际值',
  `phase_a_current_d` decimal(27,4) NULL COMMENT 'A相电流示数值',
  `phase_b_current` decimal(27,4) NULL COMMENT 'B相电流实际值',
  `phase_b_current_d` decimal(27,4) NULL COMMENT 'B相电流示数值',
  `phase_c_current` decimal(27,4) NULL COMMENT 'C相电流实际值',
  `phase_c_current_d` decimal(27,4) NULL COMMENT 'C相电流示数值',
  `current_unbalance` decimal(27,4) NULL COMMENT '电流不平衡度实际值',
  `current_unbalance_d` decimal(27,4) NULL COMMENT '电流不平衡度示数值',
  `frequency` decimal(27,4) NULL COMMENT '频率实际值',
  `frequency_d` decimal(27,4) NULL COMMENT '频率示数值',
  `quadrant1_reactive_energy` decimal(27,4) NULL COMMENT '第一象限无功总电能实际值',
  `quadrant1_reactive_energy_d` decimal(27,4) NULL COMMENT '第一象限无功总电能示数值',
  `quadrant1_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第一象限无功总电能表码',
  `quadrant2_reactive_energy` decimal(27,4) NULL COMMENT '第二象限无功总电能实际值',
  `quadrant2_reactive_energy_d` decimal(27,4) NULL COMMENT '第二象限无功总电能示数值',
  `quadrant2_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第二象限无功总电能表码',
  `quadrant3_reactive_energy` decimal(27,4) NULL COMMENT '第三象限无功总电能实际值',
  `quadrant3_reactive_energy_d` decimal(27,4) NULL COMMENT '第三象限无功总电能示数值',
  `quadrant3_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第三象限无功总电能表码',
  `quadrant4_reactive_energy` decimal(27,4) NULL COMMENT '第四象限无功总电能实际值',
  `quadrant4_reactive_energy_d` decimal(27,4) NULL COMMENT '第四象限无功总电能示数值',
  `quadrant4_reactive_energy_endvalue` decimal(27,4) NULL COMMENT '第四象限无功总电能表码',
  `input_reactive_energy` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)实际值',
  `input_reactive_energy_d` decimal(27,4) NULL COMMENT '输入无功总电能(一、四)示数值',
  `output_reactive_energy` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)实际值',
  `output_reactive_energy_d` decimal(27,4) NULL COMMENT '输出无功总电能(二、三)示数值',
  `peak_electricity_fee` decimal(27,4) NULL COMMENT '尖电费实际值',
  `peak_electricity_fee_d` decimal(27,4) NULL COMMENT '尖电费示数值',
  `high_electricity_fee` decimal(27,4) NULL COMMENT '峰电费实际值',
  `high_electricity_fee_d` decimal(27,4) NULL COMMENT '峰电费示数值',
  `normal_electricity_fee` decimal(27,4) NULL COMMENT '平电费实际值',
  `normal_electricity_fee_d` decimal(27,4) NULL COMMENT '平电费示数值',
  `low_electricity_fee` decimal(27,4) NULL COMMENT '谷电费实际值',
  `low_electricity_fee_d` decimal(27,4) NULL COMMENT '谷电费示数值',
  `total_electricity_fee` decimal(27,4) NULL COMMENT '总电费实际值',
  `total_electricity_fee_d` decimal(27,4) NULL COMMENT '总电费示数值'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `meter_code`)
COMMENT 'OLAP'
DISTRIBUTED BY HASH(`summary_time`, `meter_code`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dws_enterprise_meter_summary
-- ----------------------------
DROP TABLE IF EXISTS `dws_enterprise_meter_summary`;
CREATE TABLE `dws_enterprise_meter_summary` (
  `summary_time` datetime NOT NULL COMMENT '采集的结束时间(汇总时间)',
  `meter_code` varchar(64) NOT NULL COMMENT '表计编号',
  `field_name` varchar(40) NOT NULL COMMENT '参数名称',
  `table_field` varchar(255) NULL COMMENT '表字段',
  `start_time` datetime NULL COMMENT '采集的开始时间',
  `enterprise_code_data_id` varchar(64) NULL COMMENT '采集数据项ID',
  `process_unit_code` varchar(2) NULL COMMENT '工序单元',
  `process_code` varchar(2) NULL COMMENT '生产工序',
  `energy_type_code` varchar(4) NULL COMMENT '数据分类11-14位',
  `meter_value` decimal(27,4) NULL COMMENT '实际值',
  `meter_display_value` decimal(27,4) NULL COMMENT '示数值',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标煤值',
  `begin_value` decimal(27,4) NULL COMMENT '开始值',
  `end_value` decimal(27,4) NULL COMMENT '结束值',
  `count` int NULL COMMENT '采集次数',
  `summary_type` int NULL COMMENT '统计类型',
  `metering_calculate_type` varchar(1) NULL COMMENT '表头值类型(1为瞬时值，0为累计值)',
  `install_site` varchar(128) NULL COMMENT '安装地址',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL COMMENT '更新时间'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `meter_code`, `field_name`)
COMMENT 'OLAP'
PARTITION BY RANGE(`summary_time`)
(PARTITION p202412 VALUES [('2024-12-01 00:00:00'), ('2025-01-01 00:00:00')),
PARTITION p202501 VALUES [('2025-01-01 00:00:00'), ('2025-02-01 00:00:00')),
PARTITION p202502 VALUES [('2025-02-01 00:00:00'), ('2025-03-01 00:00:00')),
PARTITION p202503 VALUES [('2025-03-01 00:00:00'), ('2025-04-01 00:00:00')),
PARTITION p202504 VALUES [('2025-04-01 00:00:00'), ('2025-05-01 00:00:00')),
PARTITION p202505 VALUES [('2025-05-01 00:00:00'), ('2025-06-01 00:00:00')),
PARTITION p202506 VALUES [('2025-06-01 00:00:00'), ('2025-07-01 00:00:00')),
PARTITION p202507 VALUES [('2025-07-01 00:00:00'), ('2025-08-01 00:00:00')),
PARTITION p202508 VALUES [('2025-08-01 00:00:00'), ('2025-09-01 00:00:00')),
PARTITION p202509 VALUES [('2025-09-01 00:00:00'), ('2025-10-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`meter_code`, `field_name`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-12",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "true",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for dws_enterprise_meter_summary_minute
-- ----------------------------
DROP TABLE IF EXISTS `dws_enterprise_meter_summary_minute`;
CREATE TABLE `dws_enterprise_meter_summary_minute` (
  `summary_time` datetime NOT NULL COMMENT '采集的结束时间(汇总时间)',
  `meter_code` varchar(64) NOT NULL COMMENT '表计编号',
  `field_name` varchar(40) NOT NULL COMMENT '参数名称',
  `table_field` varchar(255) NULL COMMENT '表字段',
  `start_time` datetime NULL COMMENT '采集的开始时间',
  `enterprise_code_data_id` varchar(64) NULL COMMENT '采集数据项ID',
  `process_unit_code` varchar(2) NULL COMMENT '工序单元',
  `process_code` varchar(2) NULL COMMENT '生产工序',
  `energy_type_code` varchar(4) NULL COMMENT '数据分类11-14位',
  `meter_value` decimal(27,4) NULL COMMENT '实际值',
  `meter_display_value` decimal(27,4) NULL COMMENT '示数值',
  `coefficient_value` decimal(27,4) NULL COMMENT '折标煤值',
  `begin_value` decimal(27,4) NULL COMMENT '开始值',
  `end_value` decimal(27,4) NULL COMMENT '结束值',
  `count` int NULL COMMENT '采集次数',
  `summary_type` int NULL COMMENT '统计类型',
  `metering_calculate_type` varchar(1) NULL COMMENT '表头值类型(1为瞬时值，0为累计值)',
  `install_site` varchar(128) NULL COMMENT '安装地址',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL COMMENT '更新时间'
) ENGINE=OLAP
UNIQUE KEY(`summary_time`, `meter_code`, `field_name`)
COMMENT 'OLAP'
PARTITION BY RANGE(`summary_time`)
(PARTITION p202412 VALUES [('2024-12-01 00:00:00'), ('2025-01-01 00:00:00')),
PARTITION p202501 VALUES [('2025-01-01 00:00:00'), ('2025-02-01 00:00:00')),
PARTITION p202502 VALUES [('2025-02-01 00:00:00'), ('2025-03-01 00:00:00')),
PARTITION p202503 VALUES [('2025-03-01 00:00:00'), ('2025-04-01 00:00:00')),
PARTITION p202504 VALUES [('2025-04-01 00:00:00'), ('2025-05-01 00:00:00')),
PARTITION p202505 VALUES [('2025-05-01 00:00:00'), ('2025-06-01 00:00:00')),
PARTITION p202506 VALUES [('2025-06-01 00:00:00'), ('2025-07-01 00:00:00')),
PARTITION p202507 VALUES [('2025-07-01 00:00:00'), ('2025-08-01 00:00:00')),
PARTITION p202508 VALUES [('2025-08-01 00:00:00'), ('2025-09-01 00:00:00')),
PARTITION p202509 VALUES [('2025-09-01 00:00:00'), ('2025-10-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`meter_code`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-12",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "true",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for ods_stb_energy
-- ----------------------------
DROP TABLE IF EXISTS `ods_stb_energy`;
CREATE TABLE `ods_stb_energy` (
  `ts` bigint NULL COMMENT '时间戳',
  `meter_code` varchar(32) NULL COMMENT '表计编号',
  `collection_time` datetime NULL COMMENT '采集时间',
  `parameter_name` varchar(32) NULL COMMENT '参数名称',
  `param_value` varchar(128) NULL COMMENT '参数值',
  `original_data` text NULL COMMENT '原始数据',
  `meter` varchar(32) NULL COMMENT '表计',
  `real_value` varchar(128) NULL COMMENT '实际值',
  `protocol_type` varchar(32) NULL COMMENT '协议类型',
  `ext_msg` varchar(1024) NULL COMMENT '扩展消息',
  `energy_type` varchar(32) NULL COMMENT '能源类型',
  `status` int NULL COMMENT '状态',
  `table_name` varchar(32) NULL COMMENT '表名',
  `ext_flag` varchar(32) NULL COMMENT '扩展标志',
  INDEX idx_original_data (`original_data`) USING INVERTED PROPERTIES("parser" = "unicode", "lower_case" = "true", "support_phrase" = "true") COMMENT '原始数据倒排索引'
) ENGINE=OLAP
DUPLICATE KEY(`ts`, `meter_code`)
COMMENT 'ODS层能源数据表 - 存储从各种能源设备采集的原始数据'
PARTITION BY RANGE(`collection_time`)
(PARTITION p202509 VALUES [('2025-09-01 00:00:00'), ('2025-10-01 00:00:00')),
PARTITION p202510 VALUES [('2025-10-01 00:00:00'), ('2025-11-01 00:00:00')),
PARTITION p202511 VALUES [('2025-11-01 00:00:00'), ('2025-12-01 00:00:00')),
PARTITION p202512 VALUES [('2025-12-01 00:00:00'), ('2026-01-01 00:00:00')),
PARTITION p202601 VALUES [('2026-01-01 00:00:00'), ('2026-02-01 00:00:00')),
PARTITION p202602 VALUES [('2026-02-01 00:00:00'), ('2026-03-01 00:00:00')),
PARTITION p202603 VALUES [('2026-03-01 00:00:00'), ('2026-04-01 00:00:00')))
DISTRIBUTED BY HASH(`meter_code`) BUCKETS 10
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"dynamic_partition.enable" = "true",
"dynamic_partition.time_unit" = "MONTH",
"dynamic_partition.time_zone" = "Asia/Shanghai",
"dynamic_partition.start" = "-2147483648",
"dynamic_partition.end" = "3",
"dynamic_partition.prefix" = "p",
"dynamic_partition.replication_allocation" = "tag.location.default: 1",
"dynamic_partition.buckets" = "10",
"dynamic_partition.create_history_partition" = "false",
"dynamic_partition.history_partition_num" = "-1",
"dynamic_partition.hot_partition_num" = "0",
"dynamic_partition.reserved_history_periods" = "NULL",
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728"
);;

-- ----------------------------
-- Table structure for peak_valley_bil_manage_new
-- ----------------------------
DROP TABLE IF EXISTS `peak_valley_bil_manage_new`;
CREATE TABLE `peak_valley_bil_manage_new` (
  `id` varchar(64) NOT NULL,
  `effective_months` varchar(64) NULL COMMENT '有效月份',
  `bill_type` char(2) NULL COMMENT '电费段(0 峰 1 平 2 谷 来自字典) ',
  `price` decimal(20,8) NULL COMMENT '价格',
  `create_time` datetime NULL,
  `user_id` varchar(64) NULL
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '临时表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for peak_valley_time
-- ----------------------------
DROP TABLE IF EXISTS `peak_valley_time`;
CREATE VIEW `peak_valley_time` AS SELECT 
        `internal`.`dw_power`.`a`.`start_time`,
        `internal`.`dw_power`.`a`.`end_time`,
        `internal`.`dw_power`.`b`.`bill_type`
    FROM `internal`.`dw_power`.`dim_peak_valley_time` `a`
    JOIN `internal`.`dw_power`.`dim_peak_valley_bil_manage` `b` ON `internal`.`dw_power`.`a`.`rel_id` = `internal`.`dw_power`.`b`.`id`;;

-- ----------------------------
-- Table structure for peak_valley_time_new
-- ----------------------------
DROP TABLE IF EXISTS `peak_valley_time_new`;
CREATE TABLE `peak_valley_time_new` (
  `id` varchar(64) NOT NULL,
  `start_time` varchar(12) NULL,
  `end_time` varchar(12) NULL,
  `create_time` datetime NULL,
  `user_id` varchar(64) NULL,
  `rel_id` varchar(64) NULL COMMENT '关联ID'
) ENGINE=OLAP
UNIQUE KEY(`id`)
COMMENT '临时表'
DISTRIBUTED BY HASH(`id`) BUCKETS AUTO
PROPERTIES (
"replication_allocation" = "tag.location.default: 1",
"min_load_replica_num" = "-1",
"is_being_synced" = "false",
"storage_medium" = "hdd",
"storage_format" = "V2",
"inverted_index_storage_format" = "V1",
"enable_unique_key_merge_on_write" = "true",
"light_schema_change" = "true",
"disable_auto_compaction" = "false",
"enable_single_replica_compaction" = "false",
"group_commit_interval_ms" = "10000",
"group_commit_data_bytes" = "134217728",
"enable_mow_light_delete" = "false"
);;

-- ----------------------------
-- Table structure for v_dim_energy_hierarchy
-- ----------------------------
DROP TABLE IF EXISTS `v_dim_energy_hierarchy`;
CREATE VIEW `v_dim_energy_hierarchy` AS SELECT 
    `internal`.`dw_power`.`h`.`hierarchy_id`,
    `internal`.`dw_power`.`h`.`parent_hierarchy_id`,
    `internal`.`dw_power`.`h`.`level_depth`,
    `internal`.`dw_power`.`h`.`level_name`,
    `internal`.`dw_power`.`h`.`remarks`,
    CONCAT_WS(',', 
        NULLIF(`internal`.`dw_power`.`p4`.`parent_hierarchy_id`, ''),
        NULLIF(`internal`.`dw_power`.`p3`.`parent_hierarchy_id`, ''),
        NULLIF(`internal`.`dw_power`.`p2`.`parent_hierarchy_id`, ''),
        NULLIF(`internal`.`dw_power`.`p1`.`parent_hierarchy_id`, ''),
        NULLIF(`internal`.`dw_power`.`h`.`parent_hierarchy_id`, ''),
        `internal`.`dw_power`.`h`.`hierarchy_id`  -- 添加自身ID
    ) as `parent_path_str`
FROM `internal`.`dw_power`.`dim_energy_hierarchy` `h`
LEFT JOIN `internal`.`dw_power`.`dim_energy_hierarchy` `p1` ON `internal`.`dw_power`.`h`.`parent_hierarchy_id` = `internal`.`dw_power`.`p1`.`hierarchy_id`
LEFT JOIN `internal`.`dw_power`.`dim_energy_hierarchy` `p2` ON `internal`.`dw_power`.`p1`.`parent_hierarchy_id` = `internal`.`dw_power`.`p2`.`hierarchy_id`
LEFT JOIN `internal`.`dw_power`.`dim_energy_hierarchy` `p3` ON `internal`.`dw_power`.`p2`.`parent_hierarchy_id` = `internal`.`dw_power`.`p3`.`hierarchy_id`
LEFT JOIN `internal`.`dw_power`.`dim_energy_hierarchy` `p4` ON `internal`.`dw_power`.`p3`.`parent_hierarchy_id` = `internal`.`dw_power`.`p4`.`hierarchy_id`;;

SET FOREIGN_KEY_CHECKS = 1;
