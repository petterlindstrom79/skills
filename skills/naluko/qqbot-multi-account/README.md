# qqbot-multi-account

QQBot 多账号运维排障技能，适用于 OpenClaw 多机器人、多 Agent 部署场景。

## 功能

- 多账号 QQBot 路由配置指导
- 双机器人 / 双 Agent 绑定模式
- 重复会话根因分析
- 主动发送与文件投递说明
- 本地 `qqbot` 插件打包导出

## 适用场景

- 管理多个 QQ 机器人账号的 OpenClaw 运维
- 调试消息跨路由或重复会话问题
- 需要移交、备份或发布本地修改的 `qqbot` 插件

## 包含文件

- `SKILL.md` — 触发元数据与工作流程
- `agents/openai.yaml` — UI 元数据
- `references/multi-account-routing.md` — 路由与隔离说明
- `references/proactive-send.md` — 主动发送与文件投递说明
- `scripts/inspect-qqbot.sh` — 快速检查部署状态
- `scripts/export-local-qqbot.sh` — 导出本地插件到 `dist/`

## 使用方法

```bash
bash scripts/inspect-qqbot.sh
bash scripts/export-local-qqbot.sh
```

## 发布建议

- 通过 `clawhub publish` 直接发布整个 skill 目录
- 发布时显式传入 `--slug`、`--name`、`--version`
- 示例中的 `appId` 与密钥路径均为占位符，不包含真实密钥
- 如果你的 `dist/` 下后续生成了额外文件，建议用 `.clawhubignore` 排除
