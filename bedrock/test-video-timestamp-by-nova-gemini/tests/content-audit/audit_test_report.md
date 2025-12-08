# 视频内容审核测试报告

**测试日期**: 2025-12-08 14:17:17

---

## 测试概述

本测试评估多个模型对视频内容的理解和审核能力：

- amazon.nova-lite-v1:0
- amazon.nova-2-lite-v1:0 (standard mode)
- amazon.nova-2-lite-v1:0 (reasoning mode, maxReasoningEffort=low)
- amazon.nova-pro-v1:0
- gemini-2.5-flash
- gemini-2.5-flash-lite

## 测试结果汇总

| 模型 | 视频 | 状态 | 响应时间(秒) | 输入Token | 输出Token |
|------|------|------|-------------|-----------|----------|
| amazon.nova-2-lite-v1:0 | video-1 | ✅ 成功 | 19.27 | 30946 | 285 |
| amazon.nova-2-lite-v1:0 (reasoning=low) | video-1 | ✅ 成功 | 20.24 | 30996 | 1049 |
| amazon.nova-2-lite-v1:0 | video-2 | ✅ 成功 | 2.79 | 3816 | 278 |
| amazon.nova-2-lite-v1:0 (reasoning=low) | video-2 | ✅ 成功 | 3.86 | 3866 | 649 |
| amazon.nova-2-lite-v1:0 | video-3 | ✅ 成功 | 19.27 | 63478 | 277 |
| amazon.nova-2-lite-v1:0 (reasoning=low) | video-3 | ✅ 成功 | 20.74 | 63528 | 598 |
| amazon.nova-2-lite-v1:0 | video-4 | ✅ 成功 | 40.65 | 33286 | 271 |
| amazon.nova-2-lite-v1:0 (reasoning=low) | video-4 | ✅ 成功 | 40.93 | 33336 | 678 |

## 详细结果


### 1. amazon.nova-2-lite-v1:0 - video-1

**期望值**:
- 搜索关键词: 无搜索动作
- 视频标题: Explore Slot Super Win Trick
- 作者: Shiv_Storm
- 观看时长: 2分钟

**状态**: ✅ 成功
**响应时间**: 19.27 秒
**输入Token**: 30946
**输出Token**: 285

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
      "actual": "(Keywords actually searched by the user)"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "Explore Slot Super Win Trick | Explore Slot Jackpot Trick || Got 1000000 Sup..."
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
```
```

### 2. amazon.nova-2-lite-v1:0 (reasoning=low) - video-1

**期望值**:
- 搜索关键词: 无搜索动作
- 视频标题: Explore Slot Super Win Trick
- 作者: Shiv_Storm
- 观看时长: 2分钟

**状态**: ✅ 成功
**响应时间**: 20.24 秒
**输入Token**: 30996
**输出Token**: 1049

**模型响应**:
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
      "expected": "explore slot super win trick",
      "actual": "Not shown in the video; no search interface is visible"
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

### 3. amazon.nova-2-lite-v1:0 - video-2

**期望值**:
- 搜索关键词: 无搜索动作
- 视频标题: 没观看视频
- 作者: 无作者
- 观看时长: 0分钟

**状态**: ✅ 成功
**响应时间**: 2.79 秒
**输入Token**: 3816
**输出Token**: 278

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
      "actual": "teen patti master loss recovery tricks"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "Not shown in the video"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "Not shown in the video"
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

### 4. amazon.nova-2-lite-v1:0 (reasoning=low) - video-2

**期望值**:
- 搜索关键词: 无搜索动作
- 视频标题: 没观看视频
- 作者: 无作者
- 观看时长: 0分钟

**状态**: ✅ 成功
**响应时间**: 3.86 秒
**输入Token**: 3866
**输出Token**: 649

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
      "actual": "teen patti master loss recovery tracks"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "status": "NOT_COMPLETED",
      "expected": "Explore Slot Super Win Trick",
      "actual": "No video title verification shown - only search interface displayed"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "status": "NOT_COMPLETED",
      "expected": "Shiv_Storm",
      "actual": "No video creator verification shown - only app interface displayed"
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

### 5. amazon.nova-2-lite-v1:0 - video-3

**期望值**:
- 搜索关键词: Slots Game Tricks Revealed
- 视频标题: STOP Losing Money! TeenPatti Explorer Slots Game Tricks Revealed
- 作者: K_Mater_Gaming
- 观看时长: 3分钟

**状态**: ✅ 成功
**响应时间**: 19.27 秒
**输入Token**: 63478
**输出Token**: 277

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
      "actual": "STOP Losing Money! TeenPatti Explorer Slots Game TricksRevealed"
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

### 6. amazon.nova-2-lite-v1:0 (reasoning=low) - video-3

**期望值**:
- 搜索关键词: Slots Game Tricks Revealed
- 视频标题: STOP Losing Money! TeenPatti Explorer Slots Game Tricks Revealed
- 作者: K_Mater_Gaming
- 观看时长: 3分钟

**状态**: ✅ 成功
**响应时间**: 20.74 秒
**输入Token**: 63528
**输出Token**: 598

**模型响应**:
```json
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "status": "NOT_COMPLETED",
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
      "status": "COMPLETED"
    }
  ]
}
```

### 7. amazon.nova-2-lite-v1:0 - video-4

**期望值**:
- 搜索关键词: 无搜索动作
- 视频标题: STOP Losing Money! TeenPatti Explorer Slo..
- 作者: @KGaming24
- 观看时长: 2分钟

**状态**: ✅ 成功
**响应时间**: 40.65 秒
**输入Token**: 33286
**输出Token**: 271

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

### 8. amazon.nova-2-lite-v1:0 (reasoning=low) - video-4

**期望值**:
- 搜索关键词: 无搜索动作
- 视频标题: STOP Losing Money! TeenPatti Explorer Slo..
- 作者: @KGaming24
- 观看时长: 2分钟

**状态**: ✅ 成功
**响应时间**: 40.93 秒
**输入Token**: 33336
**输出Token**: 678

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
      "actual": "No keyword search visible in the video"
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

## 评估指标

本测试主要评估以下指标：

1. **关键词搜索识别**: 模型是否能识别用户搜索的关键词
2. **视频标题识别**: 模型是否能识别用户观看的视频标题
3. **作者识别**: 模型是否能识别视频作者信息
4. **观看时长识别**: 模型是否能准确判断用户观看视频的时长
5. **响应时间**: 模型处理视频的速度
6. **输出格式**: 是否按照要求的JSON格式输出
