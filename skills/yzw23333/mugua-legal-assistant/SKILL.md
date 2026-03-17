# 木瓜法律咨询

## 简介
对接木瓜法律API，提供专业的法律咨询、案件要素提取和案件完整分析能力。

## 功能
- **法律咨询**：针对用户法律问题提供专业解答
- **案件要素提取**：从文本或文件中自动提取案件关键要素
- **案件完整分析**：基于当事人信息、案由、事实和诉求生成完整案件分析报告

## 调用示例
### 法律咨询
```json
{
  "action": "legal_chat",
  "prompt": "员工被口头辞退，我该如何维权？",
  "stream": false,
  "enable_network": false
}
```

### 案件要素提取
```json
{
  "action": "case_analysis",
  "analysis_mode": "element_extract",
  "input_text": "张三于2024年1月入职A公司，未签订劳动合同，2024年6月被口头辞退。"
}
```

## 配置说明
- `base_url`: 木瓜API基础地址，默认为 `https://api.test.mugua.muguafabao.com/`
- `api_key`: 木瓜API鉴权Token（Bearer Token），必须填写平台分配的完整Token值

## 许可证
MIT-0

## 数据安全与隐私提示
- 本Skill会将用户提供的案件文本、上传文件及配置的`api_key`发送至您指定的`base_url`服务端，请务必确认该服务是您信任的官方服务。
- 请勿在未阅读并同意木瓜法律API隐私政策前，发送包含敏感个人信息的案件数据。
- 建议仅在隔离环境中测试，使用模拟数据验证功能后再处理真实案件。

## 安装前必看
1.  确认`base_url`为官方可信端点（当前默认是测试环境）。
2.  必须配置`api_key`（Bearer Token）才能正常调用API。
3.  妥善保管`api_key`，避免泄露。