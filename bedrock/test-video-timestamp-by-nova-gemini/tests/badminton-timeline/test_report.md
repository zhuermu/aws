# 视频时间线理解测试报告
**测试日期**: 2025-12-08 15:10:27
---
## 测试概述
本测试评估多个模型对羽毛球比赛视频的时间线理解能力：
- amazon.nova-lite-v1:0
- amazon.nova-2-lite-v1:0 (standard mode)
- amazon.nova-2-lite-v1:0 (reasoning mode, maxReasoningEffort=low)
- amazon.nova-pro-v1:0
- gemini-2.5-flash
- gemini-2.5-flash-lite

## 测试结果汇总
| 模型 | 视频 | 状态 | 响应时间(秒) | 输入Token | 输出Token |
|------|------|------|-------------|-----------|----------|
| amazon.nova-2-lite-v1:0 | video-1-person | ✅ 成功 | 22.03 | 76315 | 8 |
| amazon.nova-2-lite-v1:0 (reasoning=medium) | video-1-person | ✅ 成功 | 44.20 | 76350 | 4736 |
| amazon.nova-2-lite-v1:0 (reasoning=medium) | video-2-match | ✅ 成功 | 35.12 | 76606 | 3456 |

## 详细结果

### 1. amazon.nova-2-lite-v1:0 - video-1-person
**状态**: ✅ 成功
**响应时间**: 22.03 秒
**输入Token**: 76315
**输出Token**: 8

**模型响应**:
```json
{"segments": []}
```

### 2. amazon.nova-2-lite-v1:0 (reasoning=medium) - video-1-person
**状态**: ✅ 成功
**响应时间**: 44.20 秒
**输入Token**: 76350
**输出Token**: 4736

**模型响应**:
```json
```json
{
  "segments": [
    {"start": "00:00", "end": "00:05", "reason": "smash winner"},
    {"start": "00:10", "end": "00:16", "reason": "smash winner"},
    {"start": "00:16", "end": "00:35", "reason": "smash winner"},
    {"start": "00:47", "end": "00:53", "reason": "smash winner"},
    {"start": "01:06", "end": "01:26", "reason": "unforced error"},
    {"start": "01:26", "end": "01:32", "reason": "smash winner"},
    {"start": "02:13", "end": "02:27", "reason": "smash winner"},
    {"start": "02:46", "end": "03:11", "reason": "smash winner"},
    {"start": "03:30", "end": "03:46", "reason": "smash winner"},
    {"start": "04:06", "end": "04:09", "reason": "smash winner"}
  ]
}
```
```

### 3. amazon.nova-2-lite-v1:0 (reasoning=medium) - video-2-match
**状态**: ✅ 成功
**响应时间**: 35.12 秒
**输入Token**: 76606
**输出Token**: 3456

**模型响应**:
```json
```json
{
  "segments": [
    {"start": "00:00", "end": "00:12", "reason": "shuttlecock out of bounds"},
    {"start": "00:12", "end": "00:23", "reason": "net fault"},
    {"start": "00:23", "end": "00:33", "reason": "shuttlecock out of bounds"},
    {"start": "00:33", "end": "00:43", "reason": "smash winner"},
    {"start": "00:43", "end": "00:53", "reason": "shuttlecock out of bounds"},
    {"start": "00:53", "end": "01:03", "reason": "net fault"},
    {"start": "01:03", "end": "01:13", "reason": "shuttlecock lands on wrong side"},
    {"start": "01:13", "end": "01:23", "reason": "net fault"},
    {"start": "01:23", "end": "01:33", "reason": "shuttlecock out of bounds"},
    {"start": "01:33", "end": "01:43", "reason": "smash winner"},
    {"start": "01:43", "end": "01:53", "reason": "shuttlecock out of bounds"},
    {"start": "01:53", "end": "02:03", "reason": "net fault"},
    {"start": "02:03", "end": "02:13", "reason": "shuttlecock out of bounds"},
    {"start": "02:13", "end": "02:23", "reason": "smash winner"},
    {"start": "02:23", "end": "02:33", "reason": "shuttlecock out of bounds"},
    {"start": "02:33", "end": "02:43", "reason": "net fault"},
    {"start": "02:43", "end": "02:53", "reason": "shuttlecock out of bounds"},
    {"start": "02:53", "end": "03:03", "reason": "smash winner"},
    {"start": "03:03", "end": "03:13", "reason": "shuttlecock out of bounds"},
    {"start": "03:13", "end": "03:23", "reason": "net fault"},
    {"start": "03:23", "end": "03:33", "reason": "shuttlecock out of bounds"},
    {"start": "03:33", "end": "03:43", "reason": "smash winner"},
    {"start": "03:43", "end": "03:53", "reason": "shuttlecock out of bounds"},
    {"start": "03:53", "end": "04:03", "reason": "net fault"},
    {"start": "04:03", "end": "04:13", "reason": "shuttlecock out of bounds"},
    {"start": "04:13", "end": "04:23", "reason": "smash winner"},
    {"start": "04:23", "end": "04:33", "reason": "shuttlecock out of bounds"},
    {"start": "04:33", "end": "04:43", "reason": "net fault"},
    {"start": "04:43", "end": "04:49", "reason": "shuttlecock out of bounds"}
  ]
}
```
```

## 评估指标
本测试主要评估以下指标：
1. **时间戳准确性**: 模型识别的比赛回合起止时间是否准确
2. **回合识别完整性**: 是否识别出所有比赛回合
3. **结束原因准确性**: 对每个回合结束原因的判断是否正确
4. **响应时间**: 模型处理视频的速度
5. **输出格式**: 是否按照要求的JSON格式输出
