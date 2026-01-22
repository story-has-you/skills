# 安全规约

## 输入验证

### 用户输入验证
- 隶属于用户个人的页面或者功能必须进行权限控制校验
- 用户敏感数据禁止直接展示，必须对展示数据进行脱敏
- 用户输入的 SQL 参数严格使用参数绑定或者 METADATA 字段值限定，防止 SQL 注入，禁止字符串拼接 SQL 访问数据库
- 用户请求传入的任何参数必须做有效性验证
- 禁止向 HTML 页面输出未经安全过滤或未正确转义的用户数据

### 参数校验
- 表单、AJAX 提交必须执行 CSRF 安全验证
- 在使用平台资源，譬如短信、邮件、电话、下单、支付，必须实现正确的防重放的机制
- 发贴、评论、发送即时消息等用户生成内容的场景必须实现防刷、文本内容违禁词过滤等风控策略

## 数据安全

### 敏感信息处理
- 用户敏感数据禁止直接展示，必须对展示数据进行脱敏
- 用户输入的 SQL 参数严格使用参数绑定或者 METADATA 字段值限定，防止 SQL 注入
- 用户个人信息、订单信息等敏感数据，必须加密传输
- 在使用平台资源，譬如短信、邮件、电话、下单、支付，必须实现正确的防重放的机制

### 密码安全
- 用户密码必须使用加密存储，禁止明文存储
- 密码加密算法推荐使用 BCrypt、PBKDF2、Argon2 等
- 密码传输必须使用 HTTPS 协议
- 密码重置必须验证用户身份

## SQL 注入防护

### 参数绑定
```java
// 正确：使用参数绑定
String sql = "SELECT * FROM user WHERE user_name = ?";
PreparedStatement ps = connection.prepareStatement(sql);
ps.setString(1, userName);

// 错误：字符串拼接
String sql = "SELECT * FROM user WHERE user_name = '" + userName + "'";
```

### MyBatis 防注入
```xml
<!-- 正确：使用 #{} 参数绑定 -->
<select id="selectByUserName" resultMap="BaseResultMap">
    SELECT * FROM user WHERE user_name = #{userName}
</select>

<!-- 错误：使用 ${} 字符串拼接 -->
<select id="selectByUserName" resultMap="BaseResultMap">
    SELECT * FROM user WHERE user_name = '${userName}'
</select>
```

## XSS 防护

### 输出转义
```java
// 使用 OWASP Java Encoder 进行 HTML 转义
import org.owasp.encoder.Encode;

String safeOutput = Encode.forHtml(userInput);

// 使用 Spring HtmlUtils
import org.springframework.web.util.HtmlUtils;

String safeOutput = HtmlUtils.htmlEscape(userInput);
```

### 富文本过滤
```java
// 使用 OWASP Java HTML Sanitizer
import org.owasp.html.PolicyFactory;
import org.owasp.html.Sanitizers;

PolicyFactory policy = Sanitizers.FORMATTING.and(Sanitizers.LINKS);
String safeHTML = policy.sanitize(untrustedHTML);
```

## CSRF 防护

### Spring Security CSRF
```java
// 启用 CSRF 保护
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.csrf().csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse());
    }
}
```

### 前端 CSRF Token
```html
<!-- 在表单中包含 CSRF Token -->
<form method="post" action="/submit">
    <input type="hidden" name="${_csrf.parameterName}" value="${_csrf.token}"/>
    <!-- 其他表单字段 -->
</form>
```

## 权限控制

### 接口权限校验
```java
// 使用 Spring Security 注解
@PreAuthorize("hasRole('ADMIN')")
@GetMapping("/admin/users")
public List<User> listUsers() {
    return userService.listAll();
}

// 使用自定义权限校验
@RequirePermission("user:delete")
@DeleteMapping("/users/{id}")
public void deleteUser(@PathVariable Long id) {
    userService.deleteById(id);
}
```

### 数据权限控制
```java
// 确保用户只能访问自己的数据
public Order getOrder(Long orderId, Long userId) {
    Order order = orderDao.selectById(orderId);
    if (order == null) {
        throw new NotFoundException("订单不存在");
    }
    if (!order.getUserId().equals(userId)) {
        throw new ForbiddenException("无权访问该订单");
    }
    return order;
}
```

## 敏感信息脱敏

### 手机号脱敏
```java
public class SensitiveInfoUtils {
    /**
     * 手机号脱敏：保留前3位和后4位
     */
    public static String maskMobile(String mobile) {
        if (StringUtils.isEmpty(mobile) || mobile.length() != 11) {
            return mobile;
        }
        return mobile.substring(0, 3) + "****" + mobile.substring(7);
    }

    /**
     * 身份证号脱敏：保留前6位和后4位
     */
    public static String maskIdCard(String idCard) {
        if (StringUtils.isEmpty(idCard) || idCard.length() < 10) {
            return idCard;
        }
        return idCard.substring(0, 6) + "********" + idCard.substring(idCard.length() - 4);
    }

    /**
     * 银行卡号脱敏：保留前4位和后4位
     */
    public static String maskBankCard(String bankCard) {
        if (StringUtils.isEmpty(bankCard) || bankCard.length() < 8) {
            return bankCard;
        }
        return bankCard.substring(0, 4) + " **** **** " + bankCard.substring(bankCard.length() - 4);
    }
}
```

## 加密存储

### 密码加密
```java
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class PasswordService {
    private BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    /**
     * 加密密码
     */
    public String encryptPassword(String rawPassword) {
        return passwordEncoder.encode(rawPassword);
    }

    /**
     * 验证密码
     */
    public boolean matches(String rawPassword, String encodedPassword) {
        return passwordEncoder.matches(rawPassword, encodedPassword);
    }
}
```

### AES 加密
```java
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

public class AESUtils {
    private static final String ALGORITHM = "AES";

    /**
     * AES 加密
     */
    public static String encrypt(String data, String key) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key.getBytes(), ALGORITHM);
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        byte[] encrypted = cipher.doFinal(data.getBytes());
        return Base64.getEncoder().encodeToString(encrypted);
    }

    /**
     * AES 解密
       public static String decrypt(String encryptedData, String key) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key.getBytes(), ALGORITHM);
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        cipher.init(Cipher.DECRYPT_MODE, secretKey);
        byte[] decrypted = cipher.doFinal(Base64.getDecoder().decode(encryptedData));
        return new String(decrypted);
    }
}
```

## 防重放攻击

### 接口防重放
```java
@Aspect
@Component
public class ReplayAttackAspect {
    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @Around("@annotation(com.example.annotation.PreventReplay)")
    public Object preventReplay(ProceedingJoinPoint joinPoint) throws Throwable {
        HttpServletRequest request = ((ServletRequestAttributes) RequestContextHolder.getRequestAttributes()).getRequest();

        String timestamp = request.getHeader("X-Timestamp");
        String nonce = request.getHeader("X-Nonce");
        String signature = request.getHeader("X-Signature");

        // 验证时间戳（5分钟内有效）
        long requestTime = Long.parseLong(timestamp);
        long currentTime = System.currentTimeMillis();
        if (Math.abs(currentTime - requestTime) > 5 * 60 * 1000) {
            throw new SecurityException("请求已过期");
        }

        // 验证 nonce 是否已使用
        String nonceKey = "nonce:" + nonce;
        if (redisTemplate.hasKey(nonceKey)) {
            throw new SecurityException("请求重复");
        }

        // 验证签名
        String expectedSignature = calculateSignature(timestamp, nonce);
        if (!signature.equals(expectedSignature)) {
            throw new SecurityException("签名验证失败");
        }

        // 记录 nonce（5分钟过期）
        redisTemplate.opsForValue().set(nonceKey, "1", 5, TimeUnit.MINUTE

        return joinPoint.proceed();
    }

    private String calculateSignature(String timestamp, String nonce) {
        // 实现签名计算逻辑
        return DigestUtils.md5Hex(timestamp + nonce + SECRET_KEY);
    }
}
```

## 文件上传安全

### 文件类型验证
```java
public class FileUploadService {
    private static final List<String> ALLOWED_EXTENSIONS = Arrays.asList("jpg", "jpeg", "png", "gif", "pdf");
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

    public String uploadFile(MultipartFile file) {
        // 验证文件是否为空
        if (file.isEmpty()) {
            throw new IllegantException("文件不能为空");
        }

        // 验证文件大小
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new IllegalArgumentException("文件大小不能超过10MB");
        }

        // 验证文件扩展名
        String originalFilename = file.getOriginalFilename();
        String extension = FilenameUtils.getExtension(originalFilename).toLowerCase();
        if (!ALLOWED_EXTENSIONS.contains(extension)) {
            throw new IllegalArgumentException("不支持的文件类型");
        }

        // 验证文件内容类型
        String contentType = file.getContentType();
        if (!isValidContentType(contentType, extension)) {
 throw new IllegalArgumentException("文件内容与扩展名不匹配");
        }

        // 生成安全的文件名
        String safeFilename = UUID.randomUUID().toString() + "." + extension;

        // 保存文件
        // ...

        return safeFilename;
    }

    private boolean isValidContentType(String contentType, String extension) {
        // 实现内容类型验证逻辑
        return true;
    }
}
```
