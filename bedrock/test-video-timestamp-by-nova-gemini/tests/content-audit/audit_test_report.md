# 视频内容审核测试报告

**测试日期**: 2025-11-18 11:31:22

---

## 测试概述

本测试评估多个模型对视频内容的理解和审核能力：

- amazon.nova-lite-v1:0
- amazon.nova-2-lite-v1:0 (standard mode)
- amazon.nova-2-lite-v1:0 (reasoning mode, maxReasoningEffort=low)
- amazon.nova-pro-v1:0
- gemini-2.5-flash
- gemini-2.5-flash-lite


## VIDEO-1

**期望值**:
- 搜索关键词: 无搜索动作
- 视频标题: Explore Slot Super Win Trick
- 作者: Shiv_Storm
- 观看时长: 2分钟

### 测试结果汇总

| 模型 | 状态 | 响应时间(秒) | 输入Token | 输出Token |
|------|------|-------------|-----------|----------|
| amazon.nova-lite-v1:0 | ✅ | 28.10 | 37763 | 299 |
| amazon.nova-2-lite-v1:0 | ✅ | 30.35 | 30686 | 285 |
| amazon.nova-2-lite-v1:0 (reasoning=low) | ✅ | 22.28 | 30736 | 867 |
| amazon.nova-pro-v1:0 | ✅ | 26.06 | 37180 | 271 |
| gemini-2.5-flash | ✅ | 47.04 | N/A | N/A |
| gemini-2.5-flash-lite | ✅ | 12.51 | N/A | N/A |

### 详细响应


#### 1. amazon.nova-lite-v1:0

**状态**: ✅ 成功
**响应时间**: 28.10 秒

**模型响应**:
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "The video does not provide information on the keywords entered by the user."
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "The title of the video being played is 'Explore Slot Super Win Trick Explore'."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "The creator of the video being played is 'Shiv_Storm'."
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 6,
      
... (已截断)
```

#### 2. amazon.nova-2-lite-v1:0

**状态**: ✅ 成功
**响应时间**: 30.35 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "(Not shown in the video)"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "Explore Slot Super Win Trick | Explore Slot Jackpot Trick || Got 1000000s Sup..."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "Shiv_Storm"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
`
... (已截断)
```

#### 3. amazon.nova-2-lite-v1:0 (reasoning=low)

**状态**: ✅ 成功
**响应时间**: 22.28 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": ""
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "Explore Slot Super Win Trick | Explore Slot Jackpot Trick || Got 1000000s Sup..."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "Shiv_Storm"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

#### 4. amazon.nova-pro-v1:0

**状态**: ✅ 成功
**响应时间**: 26.06 秒

**模型响应**:
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "explore slot super win trick"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "Explore Slot Super Win Trick"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "Not visible in the video"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "COMPLETED"
    }
  ]
}
```

#### 5. gemini-2.5-flash

**状态**: ✅ 成功
**响应时间**: 47.04 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "Not shown"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "Explore Slot Super Win Trick | Explore Slot Jackpot Trick | I Got 100000Rs Sup..."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "Shiv_Storm"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

#### 6. gemini-2.5-flash-lite

**状态**: ✅ 成功
**响应时间**: 12.51 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": null
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "Explore Slot Super Win Trick | Explore Slot Jackpot Trick | I Got 100000Rs Sup..."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "Shiv_Storm"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED",
      "actual": null
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED",
      "actual": null
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "N
... (已截断)
```

## VIDEO-2

**期望值**:
- 搜索关键词: 无搜索动作
- 视频标题: 没观看视频
- 作者: 无作者
- 观看时长: 0分钟

### 测试结果汇总

| 模型 | 状态 | 响应时间(秒) | 输入Token | 输出Token |
|------|------|-------------|-----------|----------|
| amazon.nova-lite-v1:0 | ✅ | 3.89 | 4575 | 288 |
| amazon.nova-2-lite-v1:0 | ✅ | 2.71 | 3646 | 266 |
| amazon.nova-2-lite-v1:0 (reasoning=low) | ✅ | 6.76 | 3696 | 804 |
| amazon.nova-pro-v1:0 | ✅ | 5.62 | 4575 | 284 |
| gemini-2.5-flash | ✅ | 22.79 | N/A | N/A |
| gemini-2.5-flash-lite | ✅ | 6.90 | N/A | N/A |

### 详细响应


#### 1. amazon.nova-lite-v1:0

**状态**: ✅ 成功
**响应时间**: 3.89 秒

**模型响应**:
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "No keyword search was observed in the video."
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "No video was played in the video."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "No video was played in the video."
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```

#### 2. amazon.nova-2-lite-v1:0

**状态**: ✅ 成功
**响应时间**: 2.71 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "teen patti master loss recover tricks"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": ""
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": ""
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

#### 3. amazon.nova-2-lite-v1:0 (reasoning=low)

**状态**: ✅ 成功
**响应时间**: 6.76 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "teen patti master loss recover tracks"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": ""
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": ""
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

#### 4. amazon.nova-pro-v1:0

**状态**: ✅ 成功
**响应时间**: 5.62 秒

**模型响应**:
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "No keywords entered by the user were shown."
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "No video title was shown."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "No video creator was shown."
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```

#### 5. gemini-2.5-flash

**状态**: ✅ 成功
**响应时间**: 22.79 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "teen patti master loss recover tricks"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "No video played"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "No video played"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

#### 6. gemini-2.5-flash-lite

**状态**: ✅ 成功
**响应时间**: 6.90 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "teen patti master loss recover tricks"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "null"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "null"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

## VIDEO-3

**期望值**:
- 搜索关键词: Slots Game Tricks Revealed
- 视频标题: STOP Losing Money! TeenPatti Explorer Slots Game Tricks Revealed
- 作者: K_Mater_Gaming
- 观看时长: 3分钟

### 测试结果汇总

| 模型 | 状态 | 响应时间(秒) | 输入Token | 输出Token |
|------|------|-------------|-----------|----------|
| amazon.nova-lite-v1:0 | ✅ | 22.22 | 76098 | 268 |
| amazon.nova-2-lite-v1:0 | ✅ | 25.75 | 63186 | 279 |
| amazon.nova-2-lite-v1:0 (reasoning=low) | ✅ | 43.61 | 63236 | 3236 |
| amazon.nova-pro-v1:0 | ✅ | 28.25 | 75515 | 269 |
| gemini-2.5-flash | ✅ | 71.11 | N/A | N/A |
| gemini-2.5-flash-lite | ✅ | 17.95 | N/A | N/A |

### 详细响应


#### 1. amazon.nova-lite-v1:0

**状态**: ✅ 成功
**响应时间**: 22.22 秒

**模型响应**:
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "explore slot super win trick"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "Explore Slot Super Win Trick"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "Shiv_Storm"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "COMPLETED"
    }
  ]
}
```

#### 2. amazon.nova-2-lite-v1:0

**状态**: ✅ 成功
**响应时间**: 25.75 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "Slots Game Tricks Revealed"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "STOP Losing Money! TeenPatti Explorer Slots Game Tricks Revealed"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "K_Mater_Gaming"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

#### 3. amazon.nova-2-lite-v1:0 (reasoning=low)

**状态**: ✅ 成功
**响应时间**: 43.61 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "slots game tricks revealed"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "STOP Losing Money! TeenPatti Explorer Slots Game Tricks Revealed"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "K_Mater_Gaming"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "COMPLETED"
    }
  ]
}
```
```

#### 4. amazon.nova-pro-v1:0

**状态**: ✅ 成功
**响应时间**: 28.25 秒

**模型响应**:
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "explore slot super win trick"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "Explore Slot Super Win Trick"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "Teen Patti Explorer"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "COMPLETED"
    }
  ]
}
```

#### 5. gemini-2.5-flash

**状态**: ✅ 成功
**响应时间**: 71.11 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "slots game tricks revealed"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "STOP Losing Money! TeenPatti Explorer Slots Game Tricks Revealed ✨|explorer slots jitn..."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "K_Mater_Gaming"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "COMPLETED
... (已截断)
```

#### 6. gemini-2.5-flash-lite

**状态**: ✅ 成功
**响应时间**: 17.95 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "Slots Game Tricks Revealed"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "STOP Losing Money! TeenPatti Explorer Slots Game Tricks Revealed"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "K_Mater_Gaming"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED",
      "expected": null,
      "actual": null
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED",
      "expected": null,
      "actual": null
    },
    {
      "stepNo": 6,
 
... (已截断)
```

## VIDEO-4

**期望值**:
- 搜索关键词: 无搜索动作
- 视频标题: STOP Losing Money! TeenPatti Explorer Slo..
- 作者: @KGaming24
- 观看时长: 2分钟

### 测试结果汇总

| 模型 | 状态 | 响应时间(秒) | 输入Token | 输出Token |
|------|------|-------------|-----------|----------|
| amazon.nova-lite-v1:0 | ✅ | 58.87 | 41261 | 301 |
| amazon.nova-2-lite-v1:0 | ✅ | 42.07 | 33026 | 271 |
| amazon.nova-2-lite-v1:0 (reasoning=low) | ✅ | 58.58 | 33076 | 3007 |
| amazon.nova-pro-v1:0 | ✅ | 54.21 | 40095 | 289 |
| gemini-2.5-flash | ✅ | 100.85 | N/A | N/A |
| gemini-2.5-flash-lite | ✅ | 10.96 | N/A | N/A |

### 详细响应


#### 1. amazon.nova-lite-v1:0

**状态**: ✅ 成功
**响应时间**: 58.87 秒

**模型响应**:
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "The video does not provide information on the keywords entered by the user."
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "The video does not provide information on the title of the video being played."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "The video does not provide information on the creator of the video being played."
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    
... (已截断)
```

#### 2. amazon.nova-2-lite-v1:0

**状态**: ✅ 成功
**响应时间**: 42.07 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": ""
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "STOP Losing Money! TeenPatti Explorer Sloo..."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "@KGaming24"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

#### 3. amazon.nova-2-lite-v1:0 (reasoning=low)

**状态**: ✅ 成功
**响应时间**: 58.58 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": ""
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "STOP Losing Money! TeenPatti Explorer Sloo..."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "Aman Khurana Viogs"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

#### 4. amazon.nova-pro-v1:0

**状态**: ✅ 成功
**响应时间**: 54.21 秒

**模型响应**:
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "No keywords entered by the user are shown"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "The video title does not start with 'Explore Slot Super Win Trick'"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "The creator of the video is not shown"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "CO
... (已截断)
```

#### 5. gemini-2.5-flash

**状态**: ✅ 成功
**响应时间**: 100.85 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "No keyword search shown"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "STOP Losing Money! TeenPatti Explorer Slo..."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "@Kgaming-x8f"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

#### 6. gemini-2.5-flash-lite

**状态**: ✅ 成功
**响应时间**: 10.96 秒

**模型响应**:
```json
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "None"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "STOP Losing Money! TeenPatti Explorer Slo..."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "Kgaming-x8f"
    },
    {
      "stepNo": 4,
      "stepName": "Watched for 1 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 5,
      "stepName": "Watched for 2 minute",
      "status": "NOT_COMPLETED"
    },
    {
      "stepNo": 6,
      "stepName": "Watched for 3 minute",
      "status": "NOT_COMPLETED"
    }
  ]
}
```
```

---

## 总体统计

- **总测试数**: 24
- **成功**: 24 (100%)
- **失败**: 0

### 按模型统计

| 模型 | 成功率 | 平均响应时间 |
|------|--------|-------------|
| amazon.nova-2-lite-v1:0 | 4/4 | 25.22s |
| amazon.nova-2-lite-v1:0 (reasoning=low) | 4/4 | 32.81s |
| amazon.nova-lite-v1:0 | 4/4 | 28.27s |
| amazon.nova-pro-v1:0 | 4/4 | 28.54s |
| gemini-2.5-flash | 4/4 | 60.45s |
| gemini-2.5-flash-lite | 4/4 | 12.08s |
