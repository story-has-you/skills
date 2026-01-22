# 单元测试规范

## 测试基本原则

### AIR 原则
- A：Automatic（自动化）
- I：Independent（独立性）
- R：Repeatable（可重复）

### 单元测试规范
- 好的单元测试宏观上来说，具有自动化、独立性、可重复执行的特点
- 单元测试应该是全自动执行的，并且非交互式的
- 测试用例之间决不能互相调用，也不能依赖执行的先后次序
- 单元测试是可以重复执行的，不能受到外界环境的影响
- 对于单元测试，保证测试粒度足够小，有助于精确定位问题
- 核心业务、核心应用、核心模块的增量代码确保单元测试通过
- 单元测试代码必须写在如下工程目录：src/test/java，不允许写在业务代码目录下

## 测试命名规范

### 测试类命名
- 测试类命名：被测试类名 + Test
- 测试方法命名：test + 被测试方法名

### 示例
```java
// 被测试类
public class UserService {
    public User getUserById(Long id) {
        // ...
    }
}

// 测试类
public class UserServiceTest {
    @Test
    public void testGetUserById() {
        // ...
    }
}
```

## 测试覆盖率

### 覆盖率要求
- 单元测试的基本目标：语句覆盖率达到 70%；核心模块的语句覆盖率和分支覆盖率都要达到 100%
- 在工程规约的应用分层中提到的 DAO 层，Manager 层，可重用度高的 Service，都应该进行单元测试
- 单元测试作为一种质量保障手段，在项目提测前完成单元测试，不建议项目发布后补充单元测试用例

### 覆盖率统计
- 使用 JaCoCo 或 Cobertura 等工具统计测试覆盖率
- 在持续集成中集成覆盖率检查

## 测试框架

### JUnit 5
```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

@DisplayName("用户服务测试")
public class UserServiceTest {

    private UserService userService;

    @BeforeEach
    public void setUp() {
        userService = new UserService();
    }

    @AfterEach
    public void tearDown() {
        userService = null;
    }

    @Test
    @DisplayName("根据ID获取用户")
    public void testGetUserById() {
        Long userId = 1L;
        User user = userService.getUserById(userId);
        assertNotNull(user);
        assertEquals(userId, user.getId());
    }
}
```

### Mockito
```java
import org.mockito.Mock;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;
import org.junit.jupiter.api.extension.ExtendWith;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class UserServiceTest {

    @Mock
    private UserDao userDao;

    @InjectMocks
    private UserService userService;

    @Test
    public void testGetUserById() {
        Long userId = 1L;
        User mockUser = new User();
        mockUser.setId(userId);
        mockUser.setUserName("test");

        when(userDao.selectById(userId)).thenReturn(mockUser);

        User user = userService.getUserById(userId);

        assertNotNull(user);
        assertEquals(userId, user.getId());
        verify(userDao, times(1)).selectById(userId);
    }
}
```

## 测试数据准备

### 测试数据隔离
- 为了保证单元测试稳定可靠且便于维护，单元测试用例之间决不能互相调用，也不能依赖执行的先后次序
- 单元测试是可以重复执行的，不能受到外界环境的影响
- 对于数据库场景的单元测试，使用程序插入或者导入数据的方式来准备数据
- 准备数据的 SQL 文件放在 test/resources 目录下

### H2 内存数据库
```java
@SpringBootTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
public class UserDaoTest {

    @Autowired
    private UserDao userDao;

    @Test
    public void testInsert() {
        User user = new User();
        user.setUserName("test");
        user.setMobile("13800138000");

        int result = userDao.insert(user);

        assertEquals(1, result);
        assertNotNull(user.getId());
    }
}
```

## 断言使用

### 常用断言
```java
// 相等断言
assertEquals(expected, actual);
assertEquals(expected, actual, "错误消息");

// 不相等断言
assertNotEquals(unexpected, actual);

// 真假断言
assertTrue(condition);
assertFalse(condition);

// 空值断言
assertNull(object);
assertNotNull(object);

// 异常断言
assertThrows(IllegalArgumentException.class, () -> {
    userService.getUserById(null);
});

// 超时断言
assertTimeout(Duration.ofSeconds(1), () -> {
    userService.getUserById(1L);
});

// 组合断言
assertAll("user",
    () -> assertEquals("test", user.getUserName()),
    () -> assertEquals("13800138000", user.getMobile())
);
```

### AssertJ 流式断言
```java
import static org.assertj.core.api.Assertions.*;

@Test
public void testGetUserById() {
    User user = userService.getUserById(1L);

    assertThat(user)
        .isNotNull()
        .extracting(User::getId, User::getUserName)
        .containsExactly(1L, "test");
}
```

## 测试最佳实践

### BCDE 原则
- B：Border，边界值测试，包括循环边界、特殊取值、特殊时间点、数据顺序等
- C：Correct，正确的输入，并得到预期的结果
- D：Design，与设计文档相结合，来编写单元测试
- E：Error，强制错误信息输入（如：非法数据、异常流程、业务允许外等），并得到预期的结果

### 边界值测试
```java
@Test
public void testGetUsersByPage() {
    // 测试第一页
    List<User> page1 = userService.getUsersByPage(1, 10);
    assertThat(page1).hasSize(10);

    // 测试最后一页
    List<User> lastPage = userService.getUsersByPage(10, 10);
    assertThat(lastPage).hasSizeLessThanOrEqualTo(10);

    // 测试空页
    List<User> emptyPage = userService.getUsersByPage(100, 10);
    assertThat(emptyPage).isEmpty();

    // 测试非法参数
    assertThrows(IllegalArgumentException.class, () -> {
        userService.getUsersByPage(0, 10);
    });

    assertThrows(IllegalArgumentException.class, () -> {
        userService.getUsersByPage(1, 0);
    });
}
```

### 异常测试
```java
@Test
public void testGetUserByIdWithNull() {
    assertThrows(IllegalArgumentException.class, () -> {
        userService.getUserById(null);
    });
}

@Test
public void testGetUserByIdNotFound() {
    Long userId = 999L;
    when(userDao.selectById(userId)).thenReturn(null);

    assertThrows(NotFoundException.class, () -> {
        userService.getUserById(userId);
    });
}
```

### 参数化测试
```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.jupiter.params.provider.CsvSource;

@ParameterizedTest
@ValueSource(strings = {"13800138000", "13900139000", "13700137000"})
public void testValidateMobile(String mobile) {
    assertTrue(ValidationUtils.isValidMobile(mobile));
}

@ParameterizedTest
@CsvSource({
    "1, test1",
    "2, test2",
    "3, test3"
})
public void testGetUserById(Long id, String expectedName) {
    User user = userService.getUserById(id);
    assertEquals(expectedName, user.getUserName());
}
```

## Spring Boot 测试

### Controller 测试
```java
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(UserController.class)
public class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    public void testGetUser() throws Exception {
        Long userId = 1L;
        User mockUser = new User();
        mockUser.setId(userId);
        mockUser.setUserName("test");

        when(userService.getUserById(userId)).thenReturn(mockUser);

        mockMvc.perform(get("/users/{id}", userId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(userId))
            .andExpect(jsonPath("$.userName").value("test"));
    }
}
```

### Service 测试
```java
@SpringBootTest
public class UserServiceTest {

    @Autowired
    private UserService userService;

    @MockBean
    private UserDao userDao;

    @Test
    public void testSaveUser() {
        User user = new User();
        user.setUserName("test");
        user.setMobile("13800138000");

        when(userDao.insert(any(User.class))).thenReturn(1);

        userService.saveUser(user);

        verify(userDao, times(1)).insert(any(User.class));
    }
}
```

### Repository 测试
```java
@DataJpaTest
public class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    public void testFindByUserName() {
        User user = new User();
        user.setUserName("test");
        user.setMobile("13800138000");
        userRepository.save(user);

        User found = userRepository.findByUserName("test");

        assertNotNull(found);
        assertEquals("test", found.getUserName());
    }
}
```

## 测试注意事项

### 避免的做法
- 不要编写没有断言的测试用例
- 不要在测试用例中使用 System.out.println() 来验证结果
- 不要在测试用例中使用 Thread.sleep() 来等待异步操作
- 不要在测试用例中依赖外部环境（如网络、文件系统等）
- 不要在测试用例中使用随机数，除非是测试随机数生成器本身

### 推荐的做法
- 使用 @BeforeEach 和 @AfterEach 来准备和清理测试数据
- 使用 Mock 对象来隔离外部依赖
- 使用参数化测试来测试多组输入
- 使用 @DisplayName 来提供清晰的测试描述
- 使用 AssertJ 等流式断言库来提高测试可读性
