# 设计规约

## 设计原则

### 存储方案和底层数据结构的设计
- 存储方案和底层数据结构的设计获得评审一致通过，并沉淀成为文档
- 在需求分析阶段，如果与系统交互的 User 超过一个类型，并且相关的 Use Case 超过 5 个，使用用例图来表达更加清晰的结构化需求
- 如果某个业务对象的状态超过 3 个，使用状态图来表达并且明确状态变化的各个触发条件

### 系统架构设计
- 系统架构设计时明确以下目标：
  - 确定系统边界：确定系统的功能边界和非功能边界
  - 确定系统内模块之间的关系：模块之间的依赖关系、调用关系
  - 确定模块之间的接口：接口的定义、接口的实现
  - 确定模块的实现方案：技术选型、实现方式
- 需求分析与系统设计在考虑主干功能的同时，需要充分评估异常流程与业务边界

### 类设计原则
- 类在设计与实现时要符合单一原则
- 谨慎使用继承的方式来进行扩展，优先使用聚合/组合的方式来实现
- 系统设计时，注意进行分层设计，上层依赖于下层，禁止下层依赖于上层，禁止循环依赖
- 系统设计时，共性业务或公共行为抽取出来公共模块、公共配置、公共类、公共方法等，避免出现重复代码或重复配置的情况

## 分层领域模型规约

### 分层架构
- 应用分层：展现层、应用层、领域层、基础设施层
- 展现层：负责向用户显示信息和解释用户命令
- 应用层：定义软件要完成的任务，并且指挥表达领域概念的对象来解决问题
- 领域层：负责表达业务概念，业务状态信息以及业务规则
- 基础设施层：为其他层提供通用的技术能力

### 领域模型
- DO（Data Object）：此对象与数据库表结构一一对应，通过 DAO 层向上传输数据源对象
- DTO（Data Transfer Object）：数据传输对象，Service 或 Manager 向外传输的对象
- BO（Business Object）：业务对象，由 Service 层输出的封装业务逻辑的对象
- AO（Application Object）：应用对象，在 Web 层与 Service 层之间抽象的复用对象模型
- VO（View Object）：显示层对象，通常是 Web 向模板渲染引擎层传输的对象
- Query：数据查询对象，各层接收上层的查询请求

### 分层领域模型转换
```
展现层 VO <-> 应用层 DTO <-> 领域层 DO
```

## 设计模式

### 单例模式
```java
// 饿汉式单例
public class Singleton {
    private static final Singleton INSTANCE = new Singleton();

    private Singleton() {}

    public static Singleton getInstance() {
        return INSTANCE;
    }
}

// 双重检查锁单例
public class Singleton {
    private static volatile Singleton instance;

    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}

// 枚举单例（推荐）
public enum Singleton {
    INSTANCE;

    public void doSomething() {
        // ...
    }
}
```

### 工厂模式
```java
// 简单工厂
public class PaymentFactory {
    public static Payment createPayment(String type) {
        switch (type) {
            case "alipay":
                return new AlipayPayment();
            case "wechat":
                retuchatPayment();
            default:
                throw new IllegalArgumentException("Unknown payment type: " + type);
        }
    }
}

// 工厂方法
public interface PaymentFactory {
    Payment createPayment();
}

public class AlipayFactory implements PaymentFactory {
    @Override
    public Payment createPayment() {
        return new AlipayPayment();
    }
}
```

### 策略模式
```java
// 策略接口
public interface DiscountStrategy {
    BigDecimal calculate(BigDecimal amount);
}

// 具体策略
public class VipDiscountStrategy implements DiscountStrategy {
    @Override
    public BigDecimal calculate(BigDecimal amount) {
        return amount.multiply(new BigDecimal("0.9"));
    }
}

public class NewUserDiscountStrategy implements DiscountStrategy {
    @Override
    public BigDecimal calculate(BigDecimal amount) {
        return amount.multiply(new BigDecimal("0.8"));
    }
}

// 上下文
public class PriceCalculator {
    private DiscountStrategy strategy;

    public void setStrategy(DiscountStrategy strategy) {
        this.strategy = strategy;
    }

    public BigDecimal calculate(BigDecimal amount) {
        return strategy.calculate(amount);
    }
}
```

### 模板方法模式
```java
public abstract class AbstractOrderProcessor {
    // 模板方法
    public final void processOrder(Order order) {
        validateOrder(order);
        calculatePrice(order);
        saveOrder(order);
        sendNotification(order);
    }

    protected abstract void validateOrder(Order order);

    protected abstract void calculatePrice(Order order);

    protected void saveOrder(Order order) {
        // 默认实现
        orderDao.insert(order);
    }

    protected void sendNotification(Order order) {
        // 默认实现
        notificationService.send(order);
    }
}

public class NormalOrderProcessor extends AbstractOrderProcessor {
    @Override
    protected void validateOrder(Order order) {
        // 普通订单验证逻辑
    }

    @Override
    protected void calculatePrice(Order order) {
        // 普通订单价格计算逻辑
    }
}
```

### 责任链模式
```java
public abstract class Handler {
    protected Handler next;

    public void setNext(Handler next) {
        this.next = next;
    }

    public abstract void handle(Request request);
}

public class AuthHandler extends Handler {
    @Override
    public void handle(Request request) {
        // 认证处理
        if (!request.isAuthenticated()) {
            throw new UnauthorizedException();
        }
        if (next != null) {
            next.handle(request);
        }
    }
}

public class ValidationHandler extends Handler {
    @Override
    public void handle(Request request) {
        // 参数验证
        if (!request.isValid()) {
            throw new ValidationException();
        }
        if (next != null) {
            next.handle(request);
        }
    }
}

// 使用
Handler authHandler = new AuthHandler();
Handler validationHandler = new ValidationHandler();
Handler businessHandler = new BusinessHandler();

authHandler.setNext(validationHandler);
validationHandler.setNext(businessHandler);

authHandler.handle(request);
```

### 观察者模式
```java
// 事件
public class OrderCreatedEvent {
    private Order order;

    public OrderCreatedEvent(Order order) {
        this.order = order;
    }

    public Order getOrder() {
        return order;
    }
}

// 监听器
@Component
public class OrderCreatedListener {
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        Order order = event.getOrder();
        // 发送通知
        notificationService.sendOrderNotification(order);
    }
}

// 发布事件
@Service
public class OrderService {
    @Autowired
    private ApplicationEventPublisher eventPublisher;

    public void createOrder(Order order) {
        orderDao.insert(order);
        eventPublisher.publishEvent(new OrderCreatedEvent(order));
    }
}
```

## 二方库依赖

### 二方库定义
- 二方库：公司内部的依赖库，一般指公司内部的其他项目发布的 jar 包
- 二方库的 groupId 和 artifactId 都要符合规范
- 线上应用不要依赖 SNAPSHOT 版本（安全包除外）
- 二方库的新增或升级，保持除功能点之外的其它 jar 包仲裁结果不变

### 依赖管理
- 二方库里可以定义枚举类型，参数可以使用枚举类型，但是接口返回值不允许使用枚举类型或者包含枚举类型的 POJO 对象
- 依赖于一个二方库群时，必须定义一个统一的版本变量，避免版本号不一致
- 禁止在子项目的 pom 依赖中出现相同的 GroupId，相同的 ArtifactId，但是不同的 Version
- 底层基础技术框架、核心数据管理平台、或近硬件端系统谨慎引入第三方实现

### 版本管理
```xml
<properties>
    <spring.version>5.3.20</spring.version>
</properties>

<dependencies>
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-core</artifactId>
        <version>${spring.version}</version>
    </dependency>
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-context</artifactId>
        <version>${spring.version}</version>
    </dependency>
</dependencies>
```

## 服务器规约

### 高并发服务器建议
- 高并发服务器建议调小 TCP 协议的 time_wait 超时时间
- 调大服务器所支持的最大文件句柄数（File Descriptor，简写为 fd）
- 给 JVM 环境参数设置 -XX:+HeapDumpOnOutOfMemoryError 参数，让 JVM 碰到 OOM 场景时输出 dump 信息
- 在线上生产环境，JVM 的 Xms 和 Xmx 设置一样大小的内存容量，避免在 GC 后调整堆大小带来的压力
- 服务器内部重定向必须使用 forward；外部重定向地址必须使用 URL Broker 生成，否则因线上采用 HTTPS 协议而导致浏览器提示"不安全"

### JVM 参数配置
```bash
# 堆内存设置
-Xms4g -Xmx4g

# 新生代设置
-Xmn2g

# 元空间设置
-XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=512m

# GC 日志
-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:/path/to/gc.log

# OOM 时生成 dump
-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/path/to/dump

# GC 算法选择（G1）
-XX:+UseG1GC -XX:MaxGCPauseMillis=200
```

## API 设计规约

### RESTful API 设计
- 使用名词复数形式表示资源：/users、/orders
- 使用 HTTP 方法表示操作：GET（查询）、POST（创建）、PUT（更新）、DELETE（删除）
- 使用 HTTP 状态码表示结果：200（成功）、201（创建成功）、400（参数错误）、401（未认证）、403（无权限）、404（不存在）、500（服务器错误）
- 使用查询参数进行过滤、排序、分页：/users?page=1&size=10&sort=createTime,desc
- 版本控制：/v1/users、/v2/users

### API 响应格式
```java
// 统一响应格式
public class Result<T> {
    private Integer code;
    private String message;
    private T data;

    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>();
        result.setCode(200);
        result.setMessage("success");
        result.setData(data);
        return result;
    }

    public static <T> Result<T> error(Integer code, String message) {
        Result<T> result = new Result<>();
        result.setCode(code);
        result.setMessage(message);
        return result;
    }
}

// 分页响应
public class PageResult<T> {
    private Long total;
    private List<T> records;
    private Integer pageNum;
    private Integer pageSize;
}
```

### API 文档
- 使用 Swagger/OpenAPI 生成 API 文档
- 接口必须有清晰的描述和示例
- 参数必须有类型、是否必填、默认值等说明
- 响应必须有状态码、数据结构等说明

```java
@RestController
@RequestMapping("/api/v1/users")
@Api(tags = "用户管理")
public class UserController {

    @GetMapping("/{id}")
    @ApiOperation("根据ID获取用户")
    @ApiImplicitParam(name = "id", value = "用户ID", required = true, dataType = "Long")
    public Result<User> getUser(@PathVariable Long id) {
        User user = userService.getUserById(id);
        return Result.success(user);
    }

    @PostMapping
    @ApiOperation("创建用户")
    public Result<User> createUser(@RequestBody @Valid UserCreateRequest request) {
        User user = userService.createUser(request);
        return Result.success(user);
    }
}
```
