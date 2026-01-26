# 计划质量闸门（必须逐条通过）

## 代码骨架完整性标准

### 必须包含（100% 强制）
- [ ] 所有新增函数的完整签名（参数类型 + 返回类型）
- [ ] 所有新增 interface/type 的完整定义
- [ ] 所有必要的 import 语句
- [ ] 核心控制流（if/else, try/catch, switch）

### 应该包含（80% 目标）
- [ ] 关键业务逻辑的伪代码或注释
- [ ] 数据转换的具体步骤
- [ ] API 调用的 endpoint 和 payload 结构
- [ ] 错误处理的具体策略

### 可以省略（允许执行时补充）
- [ ] 详细的输入验证逻辑（如正则表达式）
- [ ] 复杂的算法实现细节
- [ ] UI 组件的样式代码

### 反例（禁止出现）
❌ `// 实现业务逻辑`
❌ `// TODO: 处理边界情况`
❌ `// 调用相关 API`

### 正例
✅
```typescript
export async function validateUser(userId: string): Promise<ValidationResult> {
  // 1. 检查用户是否存在
  const user = await db.users.findById(userId);
  if (!user) {
    return { valid: false, reason: 'USER_NOT_FOUND' };
  }

  // 2. 检查用户状态
  if (user.status !== 'active') {
    return { valid: false, reason: 'USER_INACTIVE' };
  }

  // 3. 检查权限
  const hasPermission = await checkPermission(user.role, 'access_resource');
  return { valid: hasPermission, reason: hasPermission ? null : 'INSUFFICIENT_PERMISSION' };
}
```

## 可执行性
1. 每个步骤都包含明确的文件路径与动作（Create/Modify/Delete）。
2. 每个关键步骤都包含可直接粘贴的代码骨架（函数签名、核心控制流、必要 import）。
3. 不出现“实现逻辑”“处理边界情况”等抽象描述。

## 完整性
1. 新增或修改的数据结构必须在 “Data Structures & Interfaces” 中定义。
2. 关键依赖或三方库必须在计划中明确版本/来源。
3. 计划中提到的 Critical File 均有对应代码片段。

## 验证性
1. 提供至少一条可执行的验证步骤（测试/构建/运行命令）。
2. 若当前项目已存在测试策略，说明如何复用或扩展。
3. 如果无法运行测试，明确原因与替代验证方式。

## 风险与回滚
1. 明确至少一个高风险点及其缓解措施。
2. 给出具体回滚路径（可执行命令或恢复策略）。

## 交互闭环
1. 若存在歧义，已明确列出并向用户提问。
2. 用户反馈已写入计划文件并标记在 “核心变更摘要”。
