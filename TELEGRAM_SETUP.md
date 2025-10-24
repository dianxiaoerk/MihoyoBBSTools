# Telegram 机器人推送配置指南

## 第一步: 创建 Telegram 机器人

1. 在 Telegram 中搜索 `@BotFather` (官方机器人创建工具)

2. 发送命令 `/newbot` 创建新机器人

3. 按提示操作:
   - 输入机器人的显示名称 (例如: `米游社签到助手`)
   - 输入机器人的用户名 (必须以 `bot` 结尾,例如: `miyoushe_checkin_bot`)

4. 创建成功后,BotFather 会返回一个 **Bot Token**,格式类似:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
   **重要**: 请妥善保管这个 Token,不要泄露!

## 第二步: 获取 Chat ID

### 方法1: 通过 @userinfobot (推荐)

1. 在 Telegram 中搜索 `@userinfobot`
2. 点击 `Start` 或发送任意消息
3. 机器人会返回你的用户信息,其中 `Id` 就是你的 **Chat ID**

### 方法2: 通过 API 获取

1. 先给你的机器人发送一条消息 (任意内容即可)
2. 在浏览器访问以下链接 (替换 `YOUR_BOT_TOKEN` 为你的实际 Token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. 在返回的 JSON 中找到 `"chat":{"id":123456789}`,这个数字就是你的 **Chat ID**

### 示例返回结果:
```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456,
      "message": {
        "message_id": 1,
        "from": {
          "id": 987654321,  // 这就是你的 Chat ID
          "is_bot": false,
          "first_name": "张三"
        },
        "chat": {
          "id": 987654321,  // Chat ID
          "first_name": "张三",
          "type": "private"
        }
      }
    }
  ]
}
```

## 第三步: 在 GitHub 中配置 Secrets

1. 打开你的 GitHub 仓库: https://github.com/dianxiaoerk/MihoyoBBSTools

2. 点击 `Settings` → `Secrets and variables` → `Actions`

3. 点击 `New repository secret` 添加以下两个 Secrets:

   **Secret 1:**
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: 你的机器人 Token (例如: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

   **Secret 2:**
   - Name: `TELEGRAM_CHAT_ID`
   - Value: 你的 Chat ID (例如: `987654321`)

## 第四步: 测试推送

配置完成后,你可以:

1. 前往 GitHub Actions 页面手动触发 workflow
2. 或者等待定时任务自动执行 (每天北京时间 9:00)

如果配置正确,你的 Telegram 机器人会发送签到结果消息给你!

## 推送消息格式示例

```
「米游社脚本」执行成功!

脚本执行完毕，共执行2个配置文件，成功2个，没执行0个，失败0个
没执行的配置文件：[]
执行失败的配置文件：[]
触发游戏签到验证码的配置文件：[]
```

## 常见问题

### Q1: 收不到推送消息?
- 检查 Bot Token 和 Chat ID 是否正确
- 确保给机器人发送过至少一条消息
- 查看 GitHub Actions 运行日志,看是否有推送错误

### Q2: 如何修改推送配置?
- 修改 workflow 文件中的 `push.ini` 配置
- 例如设置 `error_push_only=true` 可以只在出错时推送

### Q3: 如何使用代理?
- 如果你的服务器访问 Telegram 需要代理,在 workflow 的 push.ini 中添加:
  ```ini
  [telegram]
  http_proxy=your_proxy_address:port
  ```

### Q4: 支持群组推送吗?
- 支持! Chat ID 可以是个人 ID 或群组 ID
- 要获取群组 ID,把机器人加入群组后,用同样的方法通过 getUpdates 获取

## 其他推送方式

除了 Telegram,本项目还支持多种推送方式:
- Server酱 (ftqq)
- PushPlus
- 企业微信
- 钉钉机器人
- 飞书机器人
- Discord
- Bark
- 邮件 (SMTP)
- 等等...

详见 `config/push.ini.example` 文件。
