# 🔒 安全配置指南

**重要：** 请仔细阅读本安全指南，确保正确配置敏感信息！

---

## ⚠️ 安全原则

### ❌ 禁止行为

1. **不要硬编码敏感信息**
   ```python
   # ❌ 错误示例
   APPID = 'wx50ccea6fe909ee09'
   SECRET = 'd948e42096116e4d2d78ba262b881a90'
   
   # ✅ 正确示例
   import os
   APPID = os.environ.get('WX_APPID')
   SECRET = os.environ.get('WX_SECRET')
   ```

2. **不要提交 .env 文件到 Git**
   ```bash
   # .env 文件包含敏感信息，已在 .gitignore 中忽略
   # 不要手动添加到 Git！
   ```

3. **不要在日志中打印敏感信息**
   ```python
   # ❌ 错误示例
   print(f"Secret: {SECRET}")
   
   # ✅ 正确示例
   print(f"Secret: {'*' * len(SECRET)}")
   ```

4. **不要通过 URL 传递敏感参数**
   ```bash
   # ❌ 错误示例
   curl https://api.example.com?secret=xxx
   
   # ✅ 正确示例
   curl -H "Authorization: Bearer $TOKEN" https://api.example.com
   ```

---

## 🔐 配置方式

### 方式 1：环境变量（推荐）

```bash
# 临时配置（当前终端会话有效）
export WX_APPID="your_appid"
export WX_SECRET="your_secret"

# 永久配置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export WX_APPID="your_appid"' >> ~/.bashrc
echo 'export WX_SECRET="your_secret"' >> ~/.bashrc
source ~/.bashrc
```

### 方式 2：.env 文件

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件
cat > .env << EOF
WX_APPID=your_appid
WX_SECRET=your_secret
EOF

# 设置文件权限（仅所有者可读写）
chmod 600 .env
```

### 方式 3：密钥管理服务（生产环境）

**AWS Secrets Manager:**
```python
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='wechat-mp-xk')
```

**HashiCorp Vault:**
```python
import hvac
client = hvac.Client()
secret = client.secrets.kv.v2.read_secret_version(path='wechat-mp-xk')
```

---

## 📋 环境变量列表

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| **WX_APPID** | 公众号 AppID | ✅ | - |
| **WX_SECRET** | 公众号 AppSecret | ✅ | - |
| **WX_OUTPUT_DIR** | 输出目录 | ❌ | `./.wxgzh` |
| **WX_TOKEN_FILE** | Token 缓存文件 | ❌ | `/tmp/wechat_token.json` |
| **WX_DEFAULT_AUTHOR** | 默认作者名 | ❌ | `黑白` |

---

## 🔒 文件权限

```bash
# 设置 .env 文件权限（仅所有者可读写）
chmod 600 .env

# 检查权限
ls -la .env
# 应显示：-rw------- 1 user user ... .env
```

---

## 🗑️ 密钥轮换

**建议每 90 天轮换一次密钥：**

1. 登录公众号后台
2. 生成新的 AppSecret
3. 更新环境变量
4. 验证新密钥有效
5. 删除旧密钥记录

---

## 📊 安全检查清单

- [ ] 代码中无硬编码敏感信息
- [ ] .env 文件已添加到 .gitignore
- [ ] .env 文件权限设置为 600
- [ ] 日志中无敏感信息泄露
- [ ] 使用 HTTPS 传输敏感数据
- [ ] 定期轮换密钥（90 天）

---

## 🔗 参考资料

- [12-Factor App: Config](https://12factor.net/config)
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

**版本：** v1.0  
**创建时间：** 2026-03-20  
**作者：** 九章快手团队
