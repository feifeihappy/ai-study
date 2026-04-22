# Qoder CLI 进阶使用指南

## 1. Skills（技能）

Skill 是将**专业知识打包成可复用功能**的机制，相当于给 AI 安装"专业技能包"。

### SKILL.md 格式

```yaml
---
name: api-mocker
description: 根据 API 字段定义生成 Mock 测试数据
---

# 核心指令

当你需要为 API 接口生成 Mock 数据时，遵循以下规则：
1. 根据字段类型推断合理的测试值
2. ...
```

采用**渐进式披露**设计：

- 第 1 层：`name` + `description`（始终加载，判断是否触发）
- 第 2 层：`SKILL.md` 正文（触发后加载）
- 第 3 层：`scripts/`、`references/`、`assets/`（按需加载）

### 存放位置

| 级别 | 路径 | 说明 |
|------|------|------|
| 全局 | `~/.qoder/skills/{skill-name}/SKILL.md` | 所有项目生效 |
| 项目 | `.qoder/skills/{skill-name}/SKILL.md` | 仅当前项目，可随代码共享 |

### 目录结构示例

```
.qoder/skills/
└── api-mocker/
    ├── SKILL.md          # 必需：技能定义
    ├── scripts/          # 可选：辅助脚本
    │   └── generate.sh
    ├── references/       # 可选：参考文档
    │   └── api-spec.md
    └── assets/           # 可选：模板/资源
        └── template.json
```

### 使用方式

- **自动触发**：输入匹配 `description` 时自动使用
- **手动调用**：输入 `/skill-name`
- **浏览技能**：输入 `/skills`

### 创建自定义 Skill

1. 在 `.qoder/skills/` 下创建新目录
2. 编写 `SKILL.md`，包含 YAML frontmatter 和核心指令
3. 按需添加 `scripts/`、`references/`、`assets/` 子目录

也可以使用内置的 `create-skill` 技能来辅助创建。

---

## 2. Subagents（子代理）

专门处理**特定任务**的 AI Agent，主 Agent 负责任务分解，Subagent 负责执行专项任务，各有不同的**工具访问权限**。

### 内置类型

| 类型 | 用途 | 工具权限 |
|------|------|---------|
| `code-reviewer` | 代码审查 | Read（只读） |
| `general-purpose` | 通用任务 | 全部 |
| `task-executor` | 实现任务 | 全部 |
| `design-agent` | 设计文档 | Read + Write |

### 自定义 Subagent

在 `.qoder/agents/` 下创建 Markdown 文件：

```markdown
# .qoder/agents/test-writer.md
---
name: test-writer
description: 专门编写单元测试的子代理
tools:
  read: true
  write: true
  bash: false
---

你是一名 JUnit 5 测试工程师。测试类命名 {ClassName}Test，覆盖率不低于 80%。
```

---

## 3. Hooks（钩子）

在 Agent 执行的**特定事件节点**注入自定义 Shell 命令。

### 支持的事件

| 事件 | 触发时机 | 能否阻断 |
|------|---------|---------|
| `UserPromptSubmit` | 用户输入后、处理前 | 否 |
| `PreToolUse` | 工具使用之前 | **是**（exit code 2） |
| `PostToolUse` | 工具成功执行后 | 否 |
| `PostToolUseFailure` | 工具调用失败后 | 否 |
| `Stop` | Agent 完成回复后 | 否 |

### 配置示例

在 `.qoder/settings.json` 中：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "security-check.sh" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "command": "mvn spotless:apply" }]
      }
    ],
    "Stop": [
      {
        "hooks": [{ "type": "command", "command": "notify-done.sh" }]
      }
    ]
  }
}
```

### 安全拦截示例

`PreToolUse` + exit code 2 阻断危险操作：

```bash
#!/bin/bash
# security-check.sh - 阻止危险命令
read input
if echo "$input" | grep -qE "rm -rf|chmod 777"; then
  exit 2  # 阻断执行
fi
exit 0
```

### 自动格式化示例

`PostToolUse` 在文件写入后自动格式化：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "command": "mvn spotless:apply" }]
      }
    ]
  }
}
```

### 配置优先级

`settings.local.json`（本地） > `settings.json`（项目） > `settings.json`（用户全局）

| 级别 | 路径 | 说明 |
|------|------|------|
| 用户级 | `~/.qoder/settings.json` | 全局生效 |
| 项目级 | `.qoder/settings.json` | 项目共享，可提交到 Git |
| 项目本地 | `.qoder/settings.local.json` | 仅本地，通常 gitignore |

---

## 4. MCP Servers（Model Context Protocol）

MCP 让 AI 连接外部数据源和服务（数据库、API 等）。

### 配置文件

| 级别 | 路径 |
|------|------|
| 全局 | `~/.qoder/mcp-settings.json` |
| 项目 | `.vscode/mcp.json` |

### 配置示例

```json
{
  "mcpServers": {
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-mysql"],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "your_password",
        "MYSQL_DATABASE": "omsx"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "E:\\project\\ecovacs-omsx"]
    }
  }
}
```

### 常用 MCP Server

| Server | 用途 | 安装方式 |
|--------|------|---------|
| `@modelcontextprotocol/server-filesystem` | 文件系统访问 | `npx -y @modelcontextprotocol/server-filesystem <目录>` |
| `@modelcontextprotocol/server-mysql` | MySQL 数据库 | `npx -y @modelcontextprotocol/server-mysql` |
| `@modelcontextprotocol/server-postgres` | PostgreSQL | `npx -y @modelcontextprotocol/server-postgres` |
| `@modelcontextprotocol/server-fetch` | 网页抓取 | `npx -y @modelcontextprotocol/server-fetch` |
| `@modelcontextprotocol/server-github` | GitHub API | 需配置 token |

配置后需**完全重启 Qoder CLI** 生效。

---

## 5. Rules 系统

`.qoder/rules/` 目录下的 `.md` 文件会被自动加载，约束 AI 行为。

### 加载机制

1. Qoder CLI 启动时自动扫描 `.qoder/rules/` 目录
2. 加载所有 `.md` 规则文件
3. 在后续对话中，AI 会遵循这些规则生成代码

### 组织多个规则文件

如需拆分，建议按关注点组织：

```
.qoder/rules/
├── project-overview.md    # 项目概述
├── coding-standards.md    # 编码规范
├── architecture.md        # 架构约束
├── naming-conventions.md  # 命名约定
└── security-rules.md      # 安全规则
```

---

## 6. AGENTS.md（记忆文件）

相当于 AI 的**项目笔记**，帮助快速理解项目上下文，减少重复解释。

### 自动生成

执行 `/init` 命令，AI 会分析项目结构并自动生成 `AGENTS.md`。

如需生成中文内容：`/init 生成内容请使用中文`

### 手动编写

```markdown
# AGENTS.md

## 项目信息
- 名称：ecovacs-omsx（订单管理系统）
- 技术栈：Spring Boot 3.3.6 + Spring Cloud + JPA
- Java 版本：17

## 构建命令
- 编译模块：`mvn compile -pl eco-oms -am`
- 打包：`mvn package -pl eco-oms -am -DskipTests`

## 代码规范
- 使用构造器注入，禁止 @Autowired
- 实体继承 BaseEntity
- 时间字段使用 Long（毫秒时间戳）

## Lint/TypeCheck 命令
- 代码格式化：`mvn spotless:apply`
- 检查：`mvn spotless:check`
```

关键用途：记录 **lint/typecheck 命令**，让 AI 在完成任务后自动执行检查。

---

## 7. 配置管理（/config 命令）

在 Qoder CLI 交互界面输入 `/config` 查看/修改配置。

### 可配置项

| 配置项 | 说明 |
|--------|------|
| 模型选择 | 设置默认 AI 模型 |
| API 端点 | 配置 API 服务地址 |
| 代理设置 | HTTP/HTTPS 代理 |
| 超时设置 | 请求超时时间 |
| Hooks | 钩子配置 |
| MCP | MCP 服务器配置 |

---

## 8. 常用命令速查

| 命令 | 功能 |
|------|------|
| `/help` | 显示帮助信息 |
| `/config` | 查看/修改配置 |
| `/model` | 查看/切换 AI 模型 |
| `/init` | 分析项目结构，生成 AGENTS.md |
| `/skills` | 管理已安装的 Skills |
| `/compact` | 压缩对话历史，节省 token |
| `/resume` | 恢复之前的对话 |
| `/clear` | 清空当前会话 |
| `/export` | 导出会话到文件 |
| `/memory` | 管理记忆文件 |
| `/quit` | 退出 CLI |

---

## 9. 上下文管理

| 方式 | 说明 |
|------|------|
| `/init` | 建立项目基线上下文 |
| `/compact` | 压缩过长历史，保留关键信息（可指定关注重点） |
| `/memory` | 管理 AGENTS.md 等记忆文件 |
| Rules | 通过 `.qoder/rules/` 注入持久化上下文 |
| Skills | 通过 `.qoder/skills/` 注入领域知识 |

---

## 10. 各功能推荐配置路径

| 需求 | 方案 | 文件路径 |
|------|------|---------|
| 项目编码规范 | Rules | `.qoder/rules/rules.md` |
| 领域知识/工作流 | Skills | `.qoder/skills/{name}/SKILL.md` |
| 专项任务代理 | Subagents | `.qoder/agents/{name}.md` |
| 项目记忆/上下文 | AGENTS.md | `AGENTS.md` |
| 外部服务集成 | MCP | `~/.qoder/mcp-settings.json` 或 `.vscode/mcp.json` |
| 事件钩子/自动化 | Hooks | `.qoder/settings.json` 中的 `hooks` 字段 |
| 个人偏好设置 | Settings | `~/.qoder/settings.json` |
