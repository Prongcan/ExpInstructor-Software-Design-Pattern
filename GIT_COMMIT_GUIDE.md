# Git 提交指南 - Strategy 模式重构

## 分支信息
- 分支名称：`zyydev`
- 基于分支：`main` (或 `master`)
- 功能：Strategy 模式重构

## 提交步骤

### 1. 创建并切换到新分支

```bash
# 确保在项目根目录
cd F:\31\软设\project\ExpInstructor-Software-Design-Pattern

# 查看当前状态
git status

# 创建并切换到 zyydev 分支
git checkout -b zyydev

# 确认当前分支
git branch
```

### 2. 添加修改的文件

```bash
# 添加新创建的策略文件
git add service/strategies.py

# 添加重构后的文件
git add Retrive_Generate/graph_retrieval_system.py
git add Evaluation_utils/eval_novelty.py
git add Evaluation_utils/eval_significance.py
git add Evaluation_utils/eval_feasibility_score.py
git add Evaluation_utils/eval_feasibility.py

# 添加文档
git add STRATEGY_PATTERN_REFACTORING.md
git add STRATEGY_REFACTORING_CHECKLIST.md
git add GIT_COMMIT_GUIDE.md

# 或者一次性添加所有修改（谨慎使用）
# git add .
```

### 3. 查看即将提交的更改

```bash
# 查看已暂存的文件
git status

# 查看具体的修改内容
git diff --cached
```

### 4. 提交更改

```bash
git commit -m "feat: implement Strategy Pattern refactoring

- Add strategy interfaces and implementations (service/strategies.py)
  * RetrievalRankingStrategy: CosineSimilarity, LLMRerank, BM25, Hybrid
  * ScoringStrategy: Novelty, Significance, Feasibility
  * CoverageCompareStrategy: LLM, Embedding

- Refactor graph_retrieval_system.py to use ranking strategies
  * Support pluggable ranking strategies
  * Maintain backward compatibility with default strategy

- Refactor Evaluation_utils to use scoring strategies
  * eval_novelty.py uses NoveltyScoringStrategy
  * eval_significance.py uses SignificanceScoringStrategy
  * eval_feasibility_score.py uses FeasibilityScoringStrategy
  * eval_feasibility.py uses coverage comparison strategies

- Add comprehensive documentation
  * STRATEGY_PATTERN_REFACTORING.md: implementation summary
  * STRATEGY_REFACTORING_CHECKLIST.md: verification checklist

Benefits:
- Flexible strategy switching based on resource/performance needs
- No changes required to core workflow
- Easy to extend with new strategies
- Improved testability and maintainability
"
```

### 5. 推送到 GitHub

```bash
# 第一次推送新分支
git push -u origin zyydev

# 后续推送（如果有更多修改）
git push
```

## 提交信息说明

### 提交类型
- `feat`: 新功能
- `refactor`: 重构
- `docs`: 文档
- `fix`: 修复
- `test`: 测试

### 本次提交
- **类型**: `feat` (新功能 - Strategy 模式实现)
- **范围**: 整体架构重构
- **主要改动**:
  1. 新增策略模式实现（10个策略类）
  2. 重构检索排序系统
  3. 重构评分系统
  4. 重构覆盖度对比系统

## 文件变更摘要

### 新增文件 (3)
```
service/strategies.py                      # 所有策略实现 (811 行)
STRATEGY_PATTERN_REFACTORING.md           # 重构总结文档
STRATEGY_REFACTORING_CHECKLIST.md         # 完成检查清单
```

### 修改文件 (5)
```
Retrive_Generate/graph_retrieval_system.py # 使用检索排序策略
Evaluation_utils/eval_novelty.py           # 使用新颖性评分策略
Evaluation_utils/eval_significance.py      # 使用重要性评分策略
Evaluation_utils/eval_feasibility_score.py # 使用可行性评分策略
Evaluation_utils/eval_feasibility.py       # 使用覆盖度对比策略
```

## 验证清单

在提交前，请确认：

- [x] 所有代码通过 Lint 检查
- [x] 所有策略接口已实现
- [x] 向后兼容性已测试
- [x] 文档已更新
- [x] 没有包含临时文件或敏感信息

## 后续操作

### 创建 Pull Request
1. 访问 GitHub 仓库
2. 点击 "Pull requests" -> "New pull request"
3. 选择 base: `main` <- compare: `zyydev`
4. 填写 PR 描述：
   ```
   ## Strategy Pattern 重构
   
   ### 概述
   实现了策略模式重构，提升了代码的可扩展性和可维护性。
   
   ### 主要改动
   - ✅ 检索排序策略（4种实现）
   - ✅ 评分策略（3种实现）
   - ✅ 覆盖度对比策略（2种实现）
   
   ### 测试情况
   - 所有代码通过 Lint 检查
   - 向后兼容性已保证
   
   ### 文档
   - 添加了详细的实现文档
   - 添加了完整的验证清单
   
   详见 `STRATEGY_PATTERN_REFACTORING.md`
   ```

### 如果需要合并到主分支
```bash
# 切换到 main 分支
git checkout main

# 拉取最新代码
git pull origin main

# 合并 zyydev 分支
git merge zyydev

# 推送到远程
git push origin main
```

## 常见问题

### Q: 如果有文件冲突怎么办？
A: 
```bash
# 查看冲突文件
git status

# 手动解决冲突后
git add <冲突文件>
git commit -m "resolve conflicts"
```

### Q: 如何撤销某个文件的修改？
A:
```bash
# 撤销暂存
git reset HEAD <文件名>

# 撤销修改
git checkout -- <文件名>
```

### Q: 如何修改最后一次提交？
A:
```bash
# 修改文件后
git add <文件>
git commit --amend

# 如果只是修改提交信息
git commit --amend -m "新的提交信息"
```

## 注意事项

1. **确保 .gitignore 正确配置**
   - 不要提交 `__pycache__/` 目录
   - 不要提交 `.pyc` 文件
   - 不要提交 IDE 配置文件（如 `.vscode/`, `.idea/`）
   - 不要提交 API keys 或敏感信息

2. **提交前检查**
   ```bash
   # 查看将要提交的文件
   git status
   
   # 查看具体改动
   git diff
   ```

3. **分支命名规范**
   - 功能分支：`feature/功能名`
   - 修复分支：`fix/问题描述`
   - 个人开发分支：`开发者名字` (如 `zyydev`)

## 快速命令参考

```bash
# 创建并切换分支
git checkout -b zyydev

# 查看状态
git status

# 添加所有修改
git add .

# 提交
git commit -m "your message"

# 推送到远程
git push -u origin zyydev

# 查看日志
git log --oneline

# 查看分支
git branch -a
```

