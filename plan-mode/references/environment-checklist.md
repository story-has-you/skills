# 环境与依赖检查清单

## 1. 包管理器检查
- [ ] Node.js 项目：`package.json` 存在且 `node_modules/` 已安装
- [ ] Python 项目：`requirements.txt` 或 `pyproject.toml` 存在
- [ ] Go 项目：`go.mod` 存在且 `go mod verify` 通过
- [ ] Rust 项目：`Cargo.toml` 存在且 `cargo check` 通过

## 2. 构建工具检查
- [ ] TypeScript：`tsc --noEmit` 无错误
- [ ] ESLint：`npm run lint` 或 `eslint .` 通过
- [ ] Prettier：代码格式一致

## 3. 测试状态检查
- [ ] 运行现有测试套件：`npm test` 或 `pytest`
- [ ] 记录当前通过率（例如：95/100 tests passing）
- [ ] 识别已知失败的测试（避免误判）

## 4. 版本控制检查
- [ ] Git 工作区干净（无未提交的更改）
- [ ] 当前分支已知（避免在 detached HEAD 状态工作）
- [ ] 远程分支同步状态

## 5. 环境变量检查
- [ ] `.env` 文件存在（如果项目需要）
- [ ] 关键环境变量已设置（例如：DATABASE_URL, API_KEY）

## 检查失败的处理策略
如果任何检查失败，计划文件的**第一步**必须是：
```markdown
### 步骤 0: 修复环境问题
- **问题**: TypeScript 编译失败，存在 3 个类型错误
- **修复**:
  1. 修复 `src/types/user.ts:15` 的类型不匹配
  2. 添加缺失的 `@types/node` 依赖
  3. 重新运行 `tsc --noEmit` 确认通过
```
