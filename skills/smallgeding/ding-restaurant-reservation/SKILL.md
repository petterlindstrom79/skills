
---
name: DINGs 托管式 AI 电话助手（中国餐厅预订）
description: |
  DINGs 托管式 AI 电话助手 - 中国餐厅全自动 AI 电话预订技能，只要你告诉我您的用餐需求，并提供需要预订的餐厅电话号码，我就可以帮您自动拨打餐厅电话完成您的预订任务。

  当用户提到以下意图时使用此技能：
  「预订中国餐厅」「订餐厅」「餐厅预约」「帮我订个中餐」
  「AI 电话预订餐厅」「自动打电话订中餐」「托管式餐厅预订」
  「查餐厅预订结果」「我的预订成功了吗」「查看订餐凭证」

  支持：中国餐厅 AI 电话自动外呼预订、预订结果回调通知、预订状态查询、通话记录查看、电子凭证生成。
metadata: {"openclaw": {"requires": {"env": ["TRIPNOW_API_KEY"]}, "optionalEnv": ["TRIPNOW_BASE_URL", "CALLBACK_URL"], "primaryEnv": "TRIPNOW_API_KEY", "baseUrl": "https://tripnowengine.133.cn/tripnow/v1", "homepage": "https://tripnowengine.133.cn/tripnow-ai-open-platform/"}}

---

DINGs 托管式 AI 电话助手（中国餐厅专版）API

⚠️ 必读约束

🌐 Base URL（重要！所有 API 共用）

https://tripnowengine.133.cn/tripnow/v1

所有 API 请求必须使用此 Base URL。


---

🔑 首次安装配置

在 ~/.openclaw/openclaw.json 中添加：

{
  "skills": {
    "entries": {
      "dings-restaurant-booking-cn": {
        "apiKey": "sk_你的 key",
        "env": {
          "TRIPNOW_BASE_URL": "https://tripnowengine.133.cn/tripnow/v1",
          "CALLBACK_URL": "https://your-server.com/callback（可选，用于接收预订结果回调）"
        }
      }
    }
  }
}

获取凭证：前往 TripNow 开放平台 控制台，在「API 密钥管理」页面创建 API Key（格式：sk-xxx）。


---

🔒 安全规则

- API Key 属于敏感凭证，不在群聊中展示
- 预订任务创建建议间隔 30 秒以上，避免触发限流
- 用户隐私数据（电话号码、预订信息）不持久化存储
- 回调地址必须使用 HTTPS
- API Key 请勿在客户端代码中暴露
  

---

认证

请求头：
- Authorization: Bearer $TRIPNOW_API_KEY（格式：sk-xxx）
  
Scope 权限

Scope
说明
voice.outbound
创建 AI 电话预订任务
voice.query
查询预订订单结果


---

快速决策

Base URL: https://tripnowengine.133.cn/tripnow/v1

用户意图
接口
关键点
「预订中国餐厅」
POST /voice/outbound
异步任务，需回调或查询获取结果
「查预订结果」
GET /voice/callback_find
传入订单ID查询最终状态+凭证


---

API 详情

1. 创建AI电话预订任务

端点： POST /voice/outbound

接口说明： 发起全自动 AI 电话预订任务，异步执行，可通过回调或主动查询获取结果。

请求参数：
参数
类型
必填
说明
model
string
是
固定值：tripnow-voice-cn-restaurant
to_number
string
是
餐厅电话号码
task_context
object
是
预订上下文信息（见下表）
callback_url
string
否
结果回调地址（HTTPS）

task_context 子参数：
参数
类型
必填
说明
restId
string
否
餐厅ID
restCountry
string
是
国家代码（固定值：zh）
customerName
string
是
顾客姓名
customerPhone
string
是
顾客电话
customerSex
string
是
顾客性别（男/女）
orderLang
string
是
沟通语言（固定值：zh）
diningTime
string
是
就餐时间（格式：YYYY-MM-DDTHH:MM:SS）
restaurantSeat
string
是
座位偏好（比如靠窗、包间等）
customerCount
string
是
成人数
childrenCount
string
是
儿童数（无则填0）
acceptChangeTime
string
是
是否接受时间调整（1=是，0=否）

请求示例：
curl -X POST "https://tripnowengine.133.cn/tripnow/v1/voice/outbound" \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tripnow-voice-cn-restaurant",
    "to_number": "18525518667",
    "task_context": {
      "restId": "67231",
      "restCountry": "zh",
      "customerName": "张三",
      "customerPhone": "13613661366",
      "customerSex": "男",
      "orderLang": "zh",
      "diningTime": "2026-01-01T04:00:00",
      "restaurantSeat": "包间",
      "customerCount": "2",
      "childrenCount": "0",
      "acceptChangeTime": "1"
    },
    "callback_url": "https://your-server.com/callback"
  }'

响应示例：
{
    "task_id": "voice_998d1cce6e1d",
    "status": "order_created",
    "message": "ok",
    "order_id": "RESORD216873707229",
    "requestId": "req_1bdbf779fd2b"
}

状态说明：
状态
说明
order_created
订单已创建，等待AI外呼
calling
正在向餐厅发起通话
negotiating
与餐厅沟通预订细节
completed
通话结束，预订结果已生成


---

2. 回调结构说明

说明： 任务结束后，平台会向配置的 callback_url 推送 JSON 数据，包含最终预订结果、通话记录和凭证信息。

回调示例（预订成功）：
{
  "msg": "宝子🥰，你心心念念的餐厅【宫宴(前门大街店)】，我已经帮你订好啦！请保存好订座凭证，到店出示给店员看。\n请注意，无故迟到的话预约可能会被取消，建议提前15分钟到，请提前规划出行路线哈～",
  "orderId": "RESORD216873707229",
  "phoneDialogPageUrl": "https://dingstest.133.cn/dings/call-detail?id=RESORD216873707229&lang=zh&naviBarHidden=0&debug=true",
  "diningVoucherUrl": "https://dings.133.cn/basic/files/RESORD216873707229_2025-12-18-16-51-25.png",
  "status": "预定成功",
  "usage": {
    "duration_seconds": 28,
    "duration_tokens": 93333,
    "interaction_tokens": 60000,
    "success_tokens": 500000,
    "total_tokens": 653333
  }
}

回调示例（预订失败）：
{
  "msg": "宝子😟，太不好意思啦！餐厅【宫宴(前门大街店)】目前不支持预订哦，宝子可以直接到店享受美味，或者重新挑家餐厅下单哦～ 这单权益已帮您自动退回。",
  "orderId": "RESORD216873707229",
  "phoneDialogPageUrl": "https://dingstest.133.cn/dings/call-detail?id=RESORD216873707229&lang=zh&naviBarHidden=0&debug=true",
  "status": "预定失败",
  "usage": {
    "duration_seconds": 28,
    "duration_tokens": 93333,
    "interaction_tokens": 60000,
    "success_tokens": 500000,
    "total_tokens": 653333
  }
}


---

3. 查询订单数据

端点： GET /voice/callback_find

接口说明： 根据订单ID查询预订结果、通话记录、凭证等完整信息。

请求参数：
参数
类型
必填
说明
order_id
string
是
订单ID（创建任务返回的order_id）
token
string
是
API Key（sk-xxx格式）

请求示例：
curl -X GET "https://tripnowengine.133.cn/tripnow/v1/voice/callback_find?order_id=RESORD216873707229&token=sk-live-**************************a2aMg" \
  -H "Authorization: Bearer sk-your-api-key"

响应示例（成功）：
{
    "status": "ok",
    "message": "查询成功",
    "data": {
        "order_id": "RESORD216873707229",
        "response_data": {
            "msg": "宝子🥰，你心心念念的餐厅【宫宴(前门大街店)】，我已经帮你订好啦！请保存好订座凭证，到店出示给店员看。\n请注意，无故迟到的话预约可能会被取消，建议提前15分钟到，请提前规划出行路线哈～",
            "orderId": "RESORD216873707229",
            "status": "预定成功",
            "usage": {
                "duration_seconds": 120,
                "duration_tokens": 100,
                "interaction_tokens": 50,
                "success_tokens": 10,
                "total_tokens": 160
            },
            "phoneDialogPageUrl": "https://dingstest.133.cn/dings/call-detail?id=RESORD216873707229&lang=zh&naviBarHidden=0&debug=true",
            "diningVoucherUrl": "https://dings.133.cn/basic/files/RESORD216873707229_2025-12-18-16-51-25.png"
        },
        "error_message": null
    }
}

响应字段说明：
层级
字段名
类型
描述
外层
status
string
请求状态（ok=成功）
外层
message
string
状态描述
外层
data
object
业务数据
data
order_id
string
订单ID
data
response_data
object
预订结果详情
data
error_message
string/null
错误信息（有则返回）
response_data
msg
string
人性化结果提示
response_data
status
string
预订状态（预定成功/预定失败）
response_data
phoneDialogPageUrl
string
通话记录页面URL
response_data
diningVoucherUrl
string
就餐凭证URL
response_data
usage
object
计费token统计


---

错误码

HTTP 状态码
错误码
说明
处理建议
200
成功
-
400
请求参数错误
检查必填参数（如order_id不能为空）
404
资源未找到
确认订单ID是否正确，订单是否存在
500
服务器内部错误
稍后重试，或联系平台客服

业务状态码
状态值
说明
处理建议
order_created
订单已创建
等待AI外呼完成（约1-5分钟）
预定成功
预订完成
告知用户并推送凭证URL
预定失败
预订失败
根据msg提示用户失败原因


---

使用示例

完整预订流程
# 1. 创建AI电话预订任务
POST /voice/outbound
{
    "model": "tripnow-voice-cn-restaurant",
    "to_number": "18525518667",
    "task_context": {
      "restId": "67231",
      "restCountry": "zh",
      "customerName": "张三",
      "customerPhone": "13613661366",
      "customerSex": "男",
      "orderLang": "zh",
      "diningTime": "2026-01-01T04:00:00",
      "restaurantSeat": "包间",
      "customerCount": "2",
      "childrenCount": "0",
      "acceptChangeTime": "1"
    },
    "callback_url": "https://your-server.com/callback"
}

# 2. 接收回调结果（任务完成后自动推送）
# 或主动查询订单结果
GET /voice/callback_find?order_id=RESORD216873707229&token=sk-your-api-key


---

最佳实践

1. 预订成功率优化
- 时间格式校验：确保diningTime符合 YYYY-MM-DDTHH:MM:SS 格式
- 接受时间调整：设置 acceptChangeTime: "1" 可大幅提高热门餐厅预订成功率
- 提前预订：热门中餐厅建议提前1-3天发起预订
- 信息完整：确保customerPhone、diningLocation等参数准确，减少沟通成本
  
2. 轮询策略（无回调时）
// 推荐轮询间隔（针对创建任务后的主动查询）
const pollIntervals = [
  { maxAttempts: 12, intervalMs: 5000 },   // 前 60 秒：每 5 秒
  { maxAttempts: 6, intervalMs: 10000 },   // 接下来 60 秒：每 10 秒
  { maxAttempts: 10, intervalMs: 30000 }   // 之后：每 30 秒
];

3. 回调处理
- 确保回调地址可公网访问且支持HTTPS
- 回调接收后需返回200状态码，避免平台重复推送
- 解析回调中的status字段区分预订成功/失败，通过msg向用户推送人性化提示
  

---

触发词

当用户消息包含以下意图时触发此技能：

预订触发
- 「预订中餐厅」「订中餐」「帮我订个中国餐厅」
- 「AI代打电话订餐厅」「自动打电话预订中餐」
- 「餐厅订位」「帮我预约包间」「订生日宴餐厅」
  
查询触发
- 「查我的餐厅预订」「预订成功了吗」
- 「查看订餐凭证」「餐厅预订结果」
- 「我的订座信息」「通话记录」
  
场景触发
- 「商务宴请订中餐」「家庭聚餐订餐厅」
- 「生日宴订包间」「朋友聚会订中餐」
  

---

配置示例

{
  "skills": {
    "entries": {
      "dings-restaurant-booking-cn": {
        "apiKey": "sk_live_xxxxxxxxxxxxx",
        "env": {
          "TRIPNOW_BASE_URL": "https://tripnowengine.133.cn/tripnow/v1",
          "CALLBACK_URL": "https://your-domain.com/webhook/tripnow"
        }
      }
    }
  }
}


---

支持语言

- 中文（简体）：核心支持，适配所有中国餐厅沟通场景
- 中文（繁体）：兼容适配，支持港澳台地区餐厅预订
  

---

计费说明

服务
计费方式
说明
AI 电话预订
Token 计费
按通话时长、交互量、成功状态综合计费
订单查询
免费
无额外费用
通话记录查看
免费
包含在预订服务中
电子凭证生成
免费
预订成功后自动生成，无额外费用

Token 说明：
- duration_tokens：按通话时长计费
- interaction_tokens：按AI与餐厅交互轮次计费
- success_tokens：预订成功额外计费
- 具体费率请参考 TripNow 开放平台「计费中心」
  

---

注意事项

1. 时区处理：就餐时间使用中国标准时间（CST/UTC+8）
2. 隐私保护：用户电话号码仅用于本次预订，完成后需按合规要求清理
3. 凭证有效期：diningVoucherUrl 生成的凭证仅在预订日期前有效，需提醒用户及时保存
4. 取消政策：部分餐厅支持取消预订，需在预订结果中告知用户取消方式
5. 紧急支持：预订问题可联系 TripNow 平台客服：support@tripnowengine.133.cn
  

---

技能版本：v1.0.0 | 最后更新：2026-03-16