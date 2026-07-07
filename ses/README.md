# 使用 AWS SES 实现邮箱验证码功能

本文档介绍如何基于 **Amazon SES (Simple Email Service)** 实现「发送验证码验证邮箱」的完整功能，包含架构设计、AWS 控制台配置步骤、后端代码实现，以及官方参考文档。

---

## 目录

- [1. 功能概述](#1-功能概述)
- [2. 整体架构](#2-整体架构)
- [3. AWS SES 配置步骤](#3-aws-ses-配置步骤)
- [4. 后端代码实现](#4-后端代码实现)
- [5. 安全与最佳实践](#5-安全与最佳实践)
- [6. 常见问题（FAQ）](#6-常见问题faq)
- [7. 费用说明](#7-费用说明)
- [8. 参考文档](#8-参考文档)

---

## 1. 功能概述

Amazon SES 是一个云端邮件发送服务。它**本身不提供验证码的生成与校验逻辑**，但可以作为可靠的邮件发送通道。完整的邮箱验证码功能需要开发者自行实现以下部分：

| 职责 | 由谁完成 |
|------|----------|
| 生成验证码 | 后端服务 |
| 存储验证码（含过期时间） | Redis / DynamoDB 等 |
| 发送验证码邮件 | **AWS SES** |
| 校验用户提交的验证码 | 后端服务 |

> 💡 如果你希望「开箱即用」的完整邮箱验证流程，可以考虑 **Amazon Cognito**（其底层同样使用 SES 发送邮件）。本文聚焦于自建方案，灵活性更高。

---

## 2. 整体架构

```
┌──────────┐     ①输入邮箱      ┌──────────────┐
│  客户端   │ ─────────────────▶│   后端服务    │
│ (浏览器)  │                    │              │
└──────────┘                    │ ②生成验证码   │
      ▲                          │ ③存入 Redis   │
      │                          │   (5min TTL) │
      │                          └──────┬───────┘
      │                                 │ ④调用 SES 发送
      │                                 ▼
      │                          ┌──────────────┐
      │      ⑤收到验证码邮件       │   AWS SES    │
      └──────────────────────────┤              │
                                 └──────────────┘

  ⑥用户提交验证码 ─▶ 后端校验 Redis 中的值 ─▶ 验证通过/失败
```

---

## 3. AWS SES 配置步骤

### 步骤 1：开通 Amazon SES

1. 登录 [AWS 管理控制台](https://console.aws.amazon.com/ses/)。
2. 在顶部选择一个支持 SES 的区域（如 `us-east-1`、`ap-southeast-1` 等）。
3. 进入 **Amazon SES** 服务页面。

### 步骤 2：验证发件身份（Identity）

你必须验证「发件邮箱地址」或「发件域名」后才能从其发送邮件。**推荐验证整个域名**（更专业、可发任意 `@yourdomain.com` 地址）。

**方式 A：验证单个邮箱地址（快速测试用）**

1. 左侧菜单 → **Verified identities** → **Create identity**。
2. 选择 **Email address**，输入发件邮箱（如 `noreply@yourdomain.com`）。
3. 点击 **Create identity**，SES 会向该邮箱发送一封确认邮件。
4. 打开邮件并点击确认链接，状态变为 **Verified** 即完成。

**方式 B：验证域名（生产环境推荐）**

1. 左侧菜单 → **Verified identities** → **Create identity**。
2. 选择 **Domain**，输入你的域名（如 `yourdomain.com`）。
3. 启用 **Easy DKIM**（推荐）。
4. SES 会生成一组 DNS 记录（CNAME / TXT）。
5. 在你的 DNS 服务商（Route 53、Cloudflare 等）中添加这些记录。
6. 等待验证通过（通常几分钟到几十分钟），状态变为 **Verified**。
7. （可选）配置 **SPF** 和 **DMARC** 记录以提升送达率。

### 步骤 3：申请移出沙盒模式（Sandbox）

> ⚠️ **重要**：新账户默认处于**沙盒模式**，此时只能向**已验证过的邮箱**发送邮件。要向任意用户邮箱发送验证码，必须申请移出沙盒。

1. 左侧菜单 → **Account dashboard**。
2. 找到 **Request production access**，点击进入申请页面。
3. 填写申请表单：
   - **Mail type**：选择 `Transactional`（验证码属于事务性邮件）。
   - **Website URL**：你的网站地址。
   - **Use case description**：清晰描述用途，例如「向注册用户发送邮箱验证码，用户主动请求，包含退订机制」。
   - **Compliance**：说明如何处理退信和投诉。
4. 提交后，AWS 通常在 **24 小时内**审核。通过后即可向任意邮箱发送。

### 步骤 4：创建 IAM 凭证

为后端服务创建具有最小权限的 IAM 用户或角色。

1. 进入 **IAM** 控制台 → **Users** → **Create user**。
2. 附加以下最小权限策略（仅允许发送邮件）：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

3. 生成 **Access Key ID** 和 **Secret Access Key**，妥善保存（用于后端配置）。

> 💡 **最佳实践**：若后端运行在 EC2 / ECS / Lambda 上，优先使用 **IAM Role** 而非静态密钥，避免密钥泄露风险。

### 步骤 5：（可选）配置发送配额与限流

- 在 **Account dashboard** 查看当前的 **Sending quota**（每日发送上限）和 **Sending rate**（每秒发送上限）。
- 生产环境可申请提高配额。

---

## 4. 后端代码实现

以下示例使用 **Node.js + AWS SDK v3**。其他语言（Python boto3、Java SDK 等）逻辑一致。

### 4.1 安装依赖

```bash
npm install @aws-sdk/client-ses ioredis
```

### 4.2 环境变量配置（`.env`）

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
SES_FROM_EMAIL=noreply@yourdomain.com
REDIS_URL=redis://localhost:6379
```

### 4.3 核心实现（`emailVerification.js`）

```javascript
import { SESClient, SendEmailCommand } from "@aws-sdk/client-ses";
import Redis from "ioredis";
import crypto from "crypto";

const sesClient = new SESClient({ region: process.env.AWS_REGION });
const redis = new Redis(process.env.REDIS_URL);

const CODE_TTL_SECONDS = 300;        // 验证码有效期 5 分钟
const RESEND_COOLDOWN_SECONDS = 60;  // 同一邮箱重发冷却 60 秒
const MAX_ATTEMPTS = 5;              // 最大校验尝试次数

// 生成 6 位数字验证码（加密安全随机数）
function generateCode() {
  return crypto.randomInt(100000, 1000000).toString();
}

// 构造验证码邮件 HTML
function buildEmailHtml(code) {
  return `
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;">
      <h2>邮箱验证</h2>
      <p>您好，您的验证码为：</p>
      <p style="font-size: 28px; font-weight: bold; letter-spacing: 4px; color: #2563eb;">
        ${code}
      </p>
      <p style="color: #666;">验证码 5 分钟内有效，请勿泄露给他人。</p>
      <p style="color: #999; font-size: 12px;">如非本人操作，请忽略此邮件。</p>
    </div>
  `;
}

// ① 发送验证码
export async function sendVerificationCode(email) {
  // 重发频率限制
  const cooldownKey = `verify:cooldown:${email}`;
  if (await redis.exists(cooldownKey)) {
    throw new Error("请求过于频繁，请稍后再试");
  }

  const code = generateCode();

  // 存储验证码 + 重置尝试次数
  await redis.setex(`verify:code:${email}`, CODE_TTL_SECONDS, code);
  await redis.del(`verify:attempts:${email}`);
  await redis.setex(cooldownKey, RESEND_COOLDOWN_SECONDS, "1");

  // 通过 SES 发送
  const command = new SendEmailCommand({
    Source: process.env.SES_FROM_EMAIL,
    Destination: { ToAddresses: [email] },
    Message: {
      Subject: { Data: "您的邮箱验证码", Charset: "UTF-8" },
      Body: {
        Html: { Data: buildEmailHtml(code), Charset: "UTF-8" },
      },
    },
  });

  await sesClient.send(command);
  return { success: true, message: "验证码已发送" };
}

// ② 校验验证码
export async function verifyCode(email, userCode) {
  const attemptsKey = `verify:attempts:${email}`;
  const attempts = parseInt((await redis.get(attemptsKey)) || "0", 10);

  if (attempts >= MAX_ATTEMPTS) {
    throw new Error("尝试次数过多，请重新获取验证码");
  }

  const storedCode = await redis.get(`verify:code:${email}`);
  if (!storedCode) {
    throw new Error("验证码不存在或已过期");
  }

  if (storedCode !== userCode) {
    await redis.incr(attemptsKey);
    await redis.expire(attemptsKey, CODE_TTL_SECONDS);
    throw new Error("验证码错误");
  }

  // 校验成功，清理
  await redis.del(`verify:code:${email}`, attemptsKey);
  return { success: true, verified: true };
}
```

### 4.4 Express 路由示例（`routes.js`）

```javascript
import express from "express";
import { sendVerificationCode, verifyCode } from "./emailVerification.js";

const router = express.Router();

// 发送验证码
router.post("/api/verify/send", async (req, res) => {
  try {
    const { email } = req.body;
    if (!email || !/^[^@]+@[^@]+\.[^@]+$/.test(email)) {
      return res.status(400).json({ error: "邮箱格式不正确" });
    }
    const result = await sendVerificationCode(email);
    res.json(result);
  } catch (err) {
    res.status(429).json({ error: err.message });
  }
});

// 校验验证码
router.post("/api/verify/check", async (req, res) => {
  try {
    const { email, code } = req.body;
    const result = await verifyCode(email, code);
    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

export default router;
```

### 4.5 Python (boto3) 版本发送片段

```python
import boto3
from botocore.exceptions import ClientError

ses = boto3.client("ses", region_name="us-east-1")

def send_verification_email(to_email: str, code: str):
    try:
        ses.send_email(
            Source="noreply@yourdomain.com",
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": "您的邮箱验证码", "Charset": "UTF-8"},
                "Body": {
                    "Html": {
                        "Data": f"<p>您的验证码是：<strong>{code}</strong>，5 分钟内有效。</p>",
                        "Charset": "UTF-8",
                    }
                },
            },
        )
    except ClientError as e:
        raise RuntimeError(e.response["Error"]["Message"])
```

---

## 5. 安全与最佳实践

| 类别 | 建议 |
|------|------|
| **验证码生成** | 使用加密安全随机数（`crypto.randomInt` / `secrets`），避免 `Math.random()` |
| **有效期** | 设置合理过期时间（5–10 分钟） |
| **尝试次数** | 限制校验失败次数（如 5 次），防暴力破解 |
| **发送频率** | 同一邮箱设置重发冷却（如 60 秒），防骚扰与滥用 |
| **凭证管理** | 优先使用 IAM Role；静态密钥使用最小权限并定期轮换 |
| **域名信誉** | 配置 DKIM / SPF / DMARC，提升送达率、避免进垃圾箱 |
| **退信/投诉处理** | 通过 SNS 订阅 Bounce / Complaint 通知，及时清理无效地址 |
| **邮件内容** | 提供清晰的品牌信息与「如非本人操作请忽略」提示 |

---

## 6. 常见问题（FAQ）

**Q1：为什么邮件发送失败，提示 "Email address not verified"？**
A：说明你仍处于沙盒模式，或发件/收件地址未验证。请完成域名/邮箱验证，并申请移出沙盒。

**Q2：邮件进了垃圾箱怎么办？**
A：确保配置了 DKIM、SPF、DMARC 记录；使用已验证的自有域名作为发件地址；保持良好的发送信誉（低退信率）。

**Q3：验证码应该存哪里？**
A：推荐 Redis（自带 TTL 过期机制）。也可用 DynamoDB 配合 TTL 属性。**不要**只存在内存中（多实例部署会丢失）。

**Q4：SES 有发送速率限制吗？**
A：有。沙盒模式限制较低；生产环境有每日配额和每秒速率限制，可在控制台申请提高。

**Q5：可以用 SMTP 方式而不是 API 吗？**
A：可以。SES 同时提供 SMTP 接口，适合已有的邮件发送库集成。API 方式更适合程序化调用。

---

## 7. 费用说明

- SES 定价约为 **每 1,000 封邮件 $0.10**（具体以 AWS 官方定价为准）。
- 从 EC2 发送时可能有额外的少量数据传输费用。
- 相比第三方邮件服务，SES 成本通常更低。

> 定价详情请查阅：[Amazon SES Pricing](https://aws.amazon.com/ses/pricing/)

---

## 8. 参考文档

- [Amazon SES 开发者指南（官方）](https://docs.aws.amazon.com/ses/latest/dg/Welcome.html)
- [创建并验证发件身份（Identities）](https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html)
- [使用 SES API 发送邮件](https://docs.aws.amazon.com/ses/latest/dg/send-email-api.html)
- [SES 邮件发送错误排查](https://docs.aws.amazon.com/ses/latest/dg/troubleshoot-error-messages.html)
- [SendCustomVerificationEmail API 参考](https://docs.aws.amazon.com/ses/latest/APIReference-V2/API_SendCustomVerificationEmail.html)
- [AWS SDK for JavaScript v3 - SES 客户端](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/client/ses/)
- [boto3 SES 文档（Python）](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html)
- [Amazon SES 定价](https://aws.amazon.com/ses/pricing/)

> 部分内容参考自 AWS 官方文档，为符合许可要求已进行改写与整理。

---

_文档生成日期：2026-07-07_
