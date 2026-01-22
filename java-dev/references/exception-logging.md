# 异常和日志规范

## 异常处理

### 异常基本规则
- Java 类库中定义的可以通过预检查方式规避的 RuntimeException 异常不应该通过 catch 的方式来处理，如：NullPointerException，IndexOutOfBoundsException 等等
- 异常不要用来做流程控制，条件控制
- catch 时请分清稳定代码和非稳定代码，稳定代码指的是无论如何不会出错的代码。对于非稳定代码的 catch 尽可能进行区分异常类型，再做对应的异常处理
- 捕获异常是为了处理它，不要捕获了却什么都不处理而抛弃之，如果不想处理它，请将该异常抛给它的调用者
- 事务场景中，抛出异常被 catch 后，如果需要回滚，一定要注意手动回滚事务
- finally 块必须对资源对象、流对象进行关闭，有异常也要做 try-catch
- 不要在 finally 块中使用 return
- 捕获异常与抛异常，必须是完全匹配，或者捕获异常是抛异常的父类
- 在调用 RPC、二方包、或动态生成类的相关方法时，捕捉异常必须使用 Throwable 类来进行拦截

### 异常定义规范
- 方法的返回值可以为 null，不强制返回空集合，或者空对象等，必须添加注释充分说明什么情况下会返回 null 值
- 防止 NPE，是程序员的基本修养，注意 NPE 产生的场景：
  - 返回类型为基本数据类型，return 包装数据类型的对象时，自动拆箱有可能产生 NPE
  - 数据库的查询结果可能为 null
  - 集合里的元素即使 isNotEmpty，取出的数据元素也可能为 null
  - 远程调用返回对象时，一律要求进行空指针判断，防止 NPE
  - 对于 Session 中获取的数据，建议进行 NPE 检查，避免空指针
  - 级联调用 obj.getA().getB().getC()；一连串调用，易产生 NPE
- 定义时区分 unchecked / checked 异常，避免直接抛出 new RuntimeException()，更不允许抛出 Exception 或者 Throwable
- 对于公司外的 http/api 开放接口必须使用错误码；而应用内部推荐异常抛出；跨应用间 RPC 调用优先考虑使用 Result 方式，封装 isSuccess()方法、错误码、错误简短信息
- 避免出现重复的代码（Don't Repeat Yourself），即 DRY 原则

### 异常处理最佳实践
- 异常信息应该包括两类信息：案发现场信息和异常堆栈信息。如果不处理，那么通过关键字 throws 往上抛出
- 有 try 块放到了事务代码中，catch 异常后，如果需要回滚事务，一定要注意手动回滚事务
- 不要在 finally 块中使用 return，finally 块中的 return 返回后方法结束执行，不会再执行 try 块中的 return 语句

## 日志规约

### 日志框架选择
- 应用中不可直接使用日志系统（Log4j、Logback）中的 API，而应依赖使用日志框架（SLF4J、JCL--Jakarta Commons Logging）中的 API
- 使用门面模式的日志框架，有利于维护和各个类的日志处理方式统一
- 推荐使用 SLF4J + Logback 组合

### 日志级别
- 日志级别从低到高：TRACE < DEBUG < INFO < WARN < ERROR
- 生产环境禁止输出 debug 日志；有选择地输出 info 日志
- 如果使用 warn 来记录刚上线时的业务行为信息，一定要注意日志输出量的问题，避免把服务器磁盘撑爆
- 应用中的扩展日志（如打点、临时监控、访问日志等）命名方式：appName_logType_logName.log

### 日志内容规范
- 在日志输出时，字符串变量之间的拼接使用占位符的方式
```java
logger.debug("Processing trade with id: {} and symbol: {}", id, symbol);
```
- 对于 trace/debug/info 级别的日志输出，必须进行日志级别的开关判断
```java
if (logger.isDebugEnabled()) {
    logger.debug("Current ID is: {} and name is: {}", id, getName());
}
```
- 避免重复打印日志，浪费磁盘空间，务必在日志配置文件中设置 additivity=false
- 异常信息应该包括两类信息：案发现场信息和异常堆栈信息。如果不处理，那么通过关键字 throws 往上抛出
```java
logger.error("Input data error, id: {}", id, e);
```
- 谨慎地记录日志。生产环境禁止输出 debug 日志；有选择地输出 info 日志
- 可以使用 warn 日志级别来记录用户输入参数错误的情况，避免用户投诉时，无所适从
- 尽量用英文来描述日志错误信息，如果日志中的错误信息用英文描述不清楚的话使用中文描述即可

### 日志文件管理
- 生产环境禁止使用 System.out 或 System.err 输出或使用 e.printStackTrace()打印
- 日志文件至少保存 15 天，因为有些异常具备以"周"为频次发生的特点
- 应用中的扩展日志（如打点、临时监控、访问日志等）命名方式：appName_logType_logName.log
- 对于敏感信息，如身份证号、手机号、银行卡号等，需要进行脱敏处理后再输出到日志

## 异常处理示例

### 正确示例
```java
// 正确的异常处理
public void processOrder(Order order) {
    if (order == null) {
        logger.warn("Order is null, skip processing");
        return;
    }

    try {
        // 业务逻辑
        orderService.save(order);
        logger.info("Order saved successfully, orderId: {}", order.getId());
    } catch (DuplicateKeyException e) {
        logger.error("Duplicate order, orderId: {}", order.getId(), e);
        throw new BusinessException("订单已存在");
    } catch (Exception e) {
        logger.error("Failed to save order, orderId: {}", order.getId(), e);
        throw new SystemException("系统异常，请稍后重试");
    }
}
```

### 错误示例
```java
// 错误：捕获异常但不处理
try {
    // 业务逻辑
} catch (Exception e) {
    // 什么都不做
}

// 错误：在 finally 中使用 return
try {
    return success();
} finally {
    return fail(); // 会覆盖 try 中的返回值
}

// 错误：直接使用 Log4j API
import org.apache.log4j.Logger;
Logger logger = Logger.getLogger(XXX.class);
```

## 日志输出示例

### 正确示例
```java
// 正确的日志输出
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class UserService {
    private static final Logger logger = LoggerFactory.getLogger(UserService.class);

    public User getUser(Long userId) {
        logger.info("Getting user, userId: {}", userId);

        if (userId == null) {
            logger.warn("UserId is null");
            return null;
        }

        try {
            User user = userDao.selectById(userId);
            if (user == null) {
                logger.warn("User not found, userId: {}", userId);
            }
            return user;
        } catch (Exception e) {
            logger.error("Failed to get user, userId: {}", userId, e);
            throw new SystemException("查询用户失败", e);
        }
    }
}
```

### 错误示例
```java
// 错误：使用字符串拼接
logger.info("Getting user, userId: " + userId); // 应使用占位符

// 错误：没有判断日志级别
logger.debug("Current user: " + user.toString()); // 应先判断 isDebugEnabled()

// 错误：使用 System.out
System.out.println("User: " + user); // 应使用 logger

// 错误：使用 printStackTrace
try {
    // ...
} catch (Exception e) {
    e.printStackTrace(); // 应使用 logger.error
}
```
