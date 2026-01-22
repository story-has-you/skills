# 并发处理规范

## 并发基础

### 线程命名
- 创建线程或线程池时请指定有意义的线程名称，方便出错时回溯
- 线程资源必须通过线程池提供，不允许在应用中自行显式创建线程
- 线程池不允许使用 Executors 去创建，而是通过 ThreadPoolExecutor 的方式，这样的处理方式让写的同学更加明确线程池的运行规则，规避资源耗尽的风险

### 线程安全
- SimpleDateFormat 是线程不安全的类，一般不要定义为 static 变量，如果定义为 static，必须加锁，或者使用 DateUtils 工具类
- 必须回收自定义的 ThreadLocal 变量，尤其在线程池场景下，线程经常会被复用，如果不清理自定义的 ThreadLocal 变量，可能会影响后续业务逻辑和造成内存泄露等问题
- 高并发时，同步调用应该去考量锁的性能损耗。能用无锁数据结构，就不要用锁；能锁区块，就不要锁整个方法体；能用对象锁，就不要用类锁

## 锁使用规范

### 加锁规则
- 对多个资源、数据库表、对象同时加锁时，需要保持一致的加锁顺序，否则可能会造成死锁
- 在使用阻塞等待获取锁的方式中，必须在 try 代码块之外，并且在加锁方法与 try 代码块之间没有任何可能抛出异常的方法调用，避免加锁成功后，在 finally 中无法解锁
- 在使用尝试机制来获取锁的方式中，进入业务代码块之前，必须先判断当前线程是否持有锁。锁的释放规则与锁的阻塞等待方式相同
- 并发修改同一记录时，避免更新丢失，需要加锁。要么在应用层加锁，要么在缓存加锁，要么在数据库层使用乐观锁，使用 version 作为更新依据
- 多线程并行处理定时任务时，Timer 运行多个 TimeTask 时，只要其中之一没有捕获抛出的异常，其它任务便会自动终止运行，使用 ScheduledExecutorService 则没有这个问题

## 线程池使用

### 线程池配置
- 资源对象的 close()方法，分为幂等和非幂等。对于非幂等的 close()，必须保证逻辑上只调用一次
- 推荐的线程池创建方式：
```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    corePoolSize,
    maximumPoolSize,
    keepAliveTime,
    TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(queueCapacity),
    new ThreadFactoryBuilder().setNameFormat("XX-task-%d").build(),
    new ThreadPoolExecutor.AbortPolicy()
);
```

### 线程池参数
- corePoolSize：核心线程数
- maximumPoolSize：最大线程数
- keepAliveTime：线程空闲时间
- workQueue：工作队列
- threadFactory：线程工厂
- handler：拒绝策略

## 并发工具类

### CountDownLatch
- 用于某个线程等待若干个其他线程执行完任务之后，它才执行
- 通过一个计数器来实现，计数器初始值为线程的数量
- 当每一个线程完成自己任务后，计数器的值就会减一
- 当计数器的值为 0 时，表示所有的线程都已经完成了任务，然后在 CountDownLatch 上等待的线程就可以恢复执行任务

### CyclicBarrier
- 让一组线程到达一个屏障时被阻塞，直到最后一个线程到达屏障时，屏障才会开门，所有被屏障拦截的线程才会继续运行
- CyclicBarrier 默认的构造方法是 CyclicBarrier(int parties)，其参数表示屏障拦截的线程数量
- 每个线程调用 await 方法告诉 CyclicBarrier 已经到达屏障位置，线程被阻塞

### Semaphore
- 用于控制同时访问特定资源的线程数量，通过协调各个线程，以保证合理的使用资源
- Semaphore 可以用于做流量控制，特别是公用资源有限的应用场景

## volatile 关键字

### 使用场景
- volatile 解决多线程内存不可见问题
- 对于一写多读，是可以解决变量同步问题
- 但是如果多写，同样无法解决线程安全问题
- 如果是 count++操作，使用 AtomicInteger 类
- 如果是 JDK8，推荐使用 LongAdder 对象，比 AtomicLong 性能更好（减少乐观锁的重试次数）

## 线程安全集合

### ConcurrentHashMap
- 线程安全的 HashMap
- 不允许 null 值
- 使用分段锁技术提高并发性能

### CopyOnWriteArrayList
- 线程安全的 ArrayList
- 读操作无锁，写操作加锁
- 适用于读多写少的场景

### BlockingQueue
- 阻塞队列，支持阻塞的插入和移除方法
- 常用实现：ArrayBlockingQueue、LinkedBlockingQueue、PriorityBlockingQueue
