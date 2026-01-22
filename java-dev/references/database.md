# MySQL数据库规范

## 建表规约

### 表设计规范
- 表达是与否概念的字段，必须使用 is_xxx 的方式命名，数据类型是 unsigned tinyint（1 表示是，0 表示否）
- 表名、字段名必须使用小写字母或数字，禁止出现数字开头，禁止两个下划线中间只出现数字
- 表名不使用复数名词
- 禁用保留字，如 desc、range、match、delayed 等，请参考 MySQL 官方保留字
- 主键索引名为 pk_字段名；唯一索引名为 uk_字段名；普通索引名则为 idx_字段名
- 小数类型为 decimal，禁止使用 float 和 double
- 如果存储的字符串长度几乎相等，使用 char 定长字符串类型
- varchar 是可变长字符串，不预先分配存储空间，长度不要超过 5000
- 如果存储的字符串长度超过 5000，使用 text 类型，独立出来一张表，用主键来对应，避免影响其它字段索引效率
- 表必备三字段：id, create_time, update_time
- 表的命名最好是遵循"业务名称_表的作用"

### 字段设计规范
- 字段允许适当冗余，以提高查询性能，但必须考虑数据一致性
- 单表行数超过 500 万行或者单表容量超过 2GB，才推荐进行分库分表
- 合适的字符存储长度，不但节约数据库表空间、节约索引存储，更重要的是提升检索速度
- 字段的默认值不要设为 NULL
- 在数据库中不能使用物理删除操作，要使用逻辑删除

### 数据类型选择
- 任何字段如果为非负数，必须是 unsigned
- 禁止使用小数存储货币，使用整数，单位为分
- 如果存储的字符串长度几乎相等，使用 char 定长字符串类型
- varchar 是可变长字符串，不预先分配存储空间，长度不要超过 5000
- 表达是与否概念的字段，必须使用 is_xxx 的方式命名，数据类型是 unsigned tinyint

## 索引规约

### 索引设计原则
- 业务上具有唯一特性的字段，即使是组合字段，也必须建成唯一索引
- 超过三个表禁止 join。需要 join 的字段，数据类型保持绝对一致；多表关联查询时，保证被关联的字段需要有索引
- 在 varchar 字段上建立索引时，必须指定索引长度，没必要对全字段建立索引，根据实际文本区分度决定索引长度
- 页面搜索严禁左模糊或者全模糊，如果需要请走搜索引擎来解决
- 如果有 order by 的场景，请注意利用索引的有序性。order by 最后的字段是组合索引的一部分，并且放在索引组合顺序的最后，避免出现 file_sort 的情况
- 利用覆盖索引来进行查询操作，避免回表
- 利用延迟关联或者子查询优化超多分页场景
- SQL 性能优化的目标：至少要达到 range 级别，要求是 ref 级别，如果可以是 consts 最好

### 索引使用规范
- 防止因字段类型不同造成的隐式转换，导致索引失效
- 创建索引时避免有如下极端误解：
  - 索引宁滥勿缺。认为一个查询就需要建一个索引
  - 吝啬索引的创建。认为索引会消耗空间、严重拖慢记录的更新以及行的新增速度
  - 抵制唯一索引。认为唯一索引一律需要在应用层通过"先查后插"方式解决
- 不要使用 count(列名)或 count(常量)来替代 count(*)
- count(*)会统计值为 NULL 的行，而 count(列名)不会统计此列为 NULL 值的行
- 当某一列的值全是 NULL 时，count(col)的返回结果为 0，但 sum(col)的返回结果为 NULL
- 使用 ISNULL()来判断是否为 NULL 值

## SQL 语句规约

### SQL 编写规范
- 不要使用 count(列名)或 count(常量)来替代 count(*)，count(*)是 SQL92 定义的标准统计行数的语法
- count(distinct col) 计算该列除 NULL 之外的不重复行数
- 当某一列的值全是 NULL 时，count(col)的返回结果为 0，但 sum(col)的返回结果为 NULL
- 使用 ISNULL()来判断是否为 NULL 值
- 代码中写分页查询逻辑时，若 count 为 0 应直接返回，避免执行后面的分页语句
- 不得使用外键与级联，一切外键概念必须在应用层解决
- 禁止使用存储过程，存储过程难以调试和扩展，更没有移植性
- 数据订正（特别是删除或修改记录操作）时，要先 select，避免出现误删除
- 对于数据库中表记录的查询和变更，只要涉及多个表，都需要在列名前加表的别名（或表名）进行限定

### SQL 性能优化
- in 操作能避免则避免，若实在避免不了，需要仔细评估 in 后边的集合元素数量，控制在 1000 个之内
- 如果有国际化需要，所有的字符存储与表示，均采用 utf8 字符集
- TRUNCATE TABLE 比 DELETE 速度快，且使用的系统和事务日志资源少，但 TRUNCATE 无事务且不触发 trigger
- 在表查询中，一律不要使用 * 作为查询的字段列表，需要哪些字段必须明确写明
- POJO 类的布尔属性不能加 is，而数据库字段必须加 is_，要求在 resultMap 中进行字段与属性之间的映射
- 不要写一个大而全的数据更新接口。传入为 POJO 类，不管是不是自己的目标更新字段，都进行 update table set c1=value1,c2=value2,c3=value3
- @Transactional 事务不要滥用。事务会影响数据库的 QPS，另外使用事务的地方需要考虑各方面的回滚方案

### 查询优化
- 避免在 where 子句中对字段进行 null 值判断，否则将导致引擎放弃使用索引而进行全表扫描
- 应尽量避免在 where 子句中使用!=或<>操作符，否则将引擎放弃使用索引而进行全表扫描
- 应尽量避免在 where 子句中使用 or 来连接条件，否则将导致引擎放弃使用索引而进行全表扫描
- in 和 not in 也要慎用，否则会导致全表扫描
- 应尽量避免在 where 子句中对字段进行表达式操作，这将导致引擎放弃使用索引而进行全表扫描
- 应尽量避免在 where 子句中对字段进行函数操作，这将导致引擎放弃使用索引而进行全表扫描
- 不要在 where 子句中的"="左边进行函数、算术运算或其他表达式运算

## ORM 映射规约

### MyBatis 规范
- 在表查询中，一律不要使用 * 作为查询的字段列表，需要哪些字段必须明确写明
- POJO 类的布尔属性不能加 is，而数据库字段必须加 is_，要求在 resultMap 中进行字段与属性之间的映射
- 不要用 resultClass 当返回参数，即使所有类属性名与数据库字段一一对应，也需要定义<resultMap>
- sql.xml 配置参数使用：#{}，#param# 不要使用${} 此种方式容易出现 SQL 注入
- iBATIS 自带的 queryForList(String statementName,int start,int size)不推荐使用
- 不允许直接拿 HashMap 与 Hashtable 作为查询结果集的输出
- 更新数据表记录时，必须同时更新记录对应的 update_time 字段值为当前时间
- 不要写一个大而全的数据更新接口。传入为 POJO 类，不管是不是自己的目标更新字段，都进行 update table set c1=value1,c2=value2,c3=value3

### 示例代码
```xml
<!-- 正确的 resultMap 定义 -->
<resultMap id="BaseResultMap" type="com.example.User">
    <id column="id" property="id" jdbcType="BIGINT"/>
    <result column="user_name" property="userName" jdbcType="VARCHAR"/>
    <result column="is_deleted" property="deleted" jdbcType="TINYINT"/>
    <result column="create_time" property="createTime" jdbcType="TIMESTAMP"/>
    <result column="update_time" property="updateTime" jdbcType="TIMESTAMP"/>
</resultMap>

<!-- 正确的查询语句 -->
<select id="selectById" resultMap="BaseResultMap">
    SELECT id, user_name, is_deleted, create_time, update_time
    FROM user
    WHERE id = #{id}
</select>

<!-- 正确的更新语句 -->
<update id="updateById">
    UPDATE user
    SET user_name = #{userName},
        update_time = NOW()
    WHERE id = #{id}
</update>
```

## 数据库设计示例

### 用户表设计
```sql
CREATE TABLE `user` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_name` varchar(64) NOT NULL COMMENT '用户名',
  `real_name` varchar(64) DEFAULT NULL COMMENT '真实姓名',
  `mobile` varchar(20) DEFAULT NULL COMMENT '手机号',
  `email` varchar(128) DEFAULT NULL COMMENT '邮箱',
  `is_deleted` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否删除：0-否，1-是',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_name` (`user_name`),
  KEY `idx_mobile` (`mobile`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

### 订单表设计
```sql
CREATE TABLE `order` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `order_no` varchar(64) NOT NULL COMMENT '订单号',
  `user_id` bigint(20) unsigned NOT NULL COMMENT '用户ID',
  `total_amount` bigint(20) unsigned NOT NULL COMMENT '订单总金额（单位：分）',
  `status` tinyint(2) unsigned NOT NULL COMMENT '订单状态：1-待支付，2-已支付，3-已取消',
  `is_deleted` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否删除：0-否，1-是',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';
```
