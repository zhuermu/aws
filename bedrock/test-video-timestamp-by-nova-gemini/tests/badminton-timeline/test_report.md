# 视频时间线理解测试报告
**测试日期**: 2025-11-18 14:45:05
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
| amazon.nova-lite-v1:0 | video-1-person | ✅ 成功 | 46.20 | 87511 | 2048 |
| amazon.nova-2-lite-v1:0 | video-1-person | ✅ 成功 | 38.99 | 76203 | 2000 |
| amazon.nova-2-lite-v1:0 (reasoning=low) | video-1-person | ❌ 失败 | 85.86 | N/A | N/A |
| amazon.nova-pro-v1:0 | video-1-person | ✅ 成功 | 52.51 | 86928 | 1119 |
| amazon.nova-lite-v1:0 | video-2-match | ✅ 成功 | 36.74 | 87511 | 932 |
| amazon.nova-2-lite-v1:0 | video-2-match | ✅ 成功 | 34.40 | 76463 | 1566 |
| amazon.nova-2-lite-v1:0 (reasoning=low) | video-2-match | ✅ 成功 | 42.16 | 76513 | 3847 |
| amazon.nova-pro-v1:0 | video-2-match | ✅ 成功 | 53.40 | 86928 | 1078 |

## 详细结果

### 1. amazon.nova-lite-v1:0 - video-1-person
**状态**: ✅ 成功
**响应时间**: 46.20 秒
**输入Token**: 87511
**输出Token**: 2048

**模型响应**:
```json
{"segments": [
{"start": "00:01", "end": "00:04", "reason": "shuttlecock out of bounds"},
{"start": "00:10", "end": "00:22", "reason": "shuttlecock out of bounds"},
{"start": "00:22", "end": "00:23", "reason": "service fault"},
{"start": "00:24", "end": "00:25", "reason": "shuttlecock out of bounds"},
{"start": "00:29", "end": "00:31", "reason": "double hit"},
{"start": "00:33", "end": "00:34", "reason": "shuttlecock out of bounds"},
{"start": "00:36", "end": "00:37", "reason": "shuttlecock out of bounds"},
{"start": "00:46", "end": "00:47", "reason": "shuttlecock out of bounds"},
{"start": "00:49", "end": "00:50", "reason": "service fault"},
{"start": "01:05", "end": "01:05", "reason": "shuttlecock out of bounds"},
{"start": "01:08", "end": "01:09", "reason": "shuttlecock out of bounds"},
{"start": "01:10", "end": "01:12", "reason": "shuttlecock out of bounds"},
{"start": "01:15", "end": "01:18", "reason": "shuttlecock out of bounds"},
{"start": "01:23", "end": "01:24", "reason": "unforced error"},
{"start": "01:33", "end": "01:34", "reason": "shuttlecock out of bounds"},
{"start": "01:44", "end": "01:47", "reason": "shuttlecock out of bounds"},
{"start": "01:58", "end": "01:59", "reason": "shuttlecock out of bounds"},
{"start": "02:01", "end": "02:02", "reason": "unforced error"},
{"start": "02:07", "end": "02:09", "reason": "shuttlecock out of bounds"},
{"start": "02:18", "end": "02:20", "reason": "unforced error"},
{"start": "02:21", "end": "02:27", "reason": "shuttlecock out of bounds"},
{"start": "02:27", "end": "02:28", "reason": "shuttlecock out of bounds"},
{"start": "02:32", "end": "02:32", "reason": "shuttlecock out of bounds"},
{"start": "02:33", "end": "02:34", "reason": "shuttlecock lands on wrong side"},
{"start": "02:38", "end": "02:42", "reason": "shuttlecock out of bounds"},
{"start": "03:14", "end": "03:18", "reason": "shuttlecock out of bounds"},
{"start": "03:18", "end": "03:21", "reason": "shuttlecock out of bounds"},
{"start": "03:21", "end": "03:21", "reason": "shuttlecock out of bounds"},
{"start": "03:23", "end": "03:26", "reason": "shuttlecock out of bounds"},
{"start": "03:33", "end": "03:34", "reason": "shuttlecock lands on wrong side"},
{"start": "04:43", "end": "04:43", "reason": "shuttlecock out of bounds"},
{"start": "04:44", "end": "04:46", "reason": "shuttlecock out of bounds"},
{"start": "05:08", "end": "05:10", "reason": "shuttlecock out of bounds"},
{"start": "05:11", "end": "05:12", "reason": "net fault"},
{"start": "05:20", "end": "05:22", "reason": "shuttlecock out of bounds"},
{"start": "05:24", "end": "05:27", "reason": "service fault"},
{"start": "05:31", "end": "05:39", "reason": "shuttlecock out of bounds"},
{"start": "05:40", "end": "05:40", "reason": "shuttlecock out of bounds"},
{"start": "05:44", "end": "05:45", "reason": "double hit"},
{"start": "05:51", "end": "05:53", "reason": "smash winner"},
{"start": "05:55", "end": "05:58", "reason": "shuttlecock out of bounds"},
{"start": "06:00", "end": "06:01", "reason": "shuttlecock out of bounds"},
{"start": "06:06", "end": "06:08", "reason": "shuttlecock out of bounds"},
{"start": "06:20", "end": "06:21", "reason": "unforced error"},
{"start": "06:26", "end": "06:27", "reason": "unforced error"},
{"start": "07:13", "end": "07:16", "reason": "shuttlecock out of bounds"},
{"start": "07:21", "end": "07:22", "reason": "double hit"},
{"start": "07:24", "end": "07:26", "reason": "shuttlecock out of bounds"},
{"start": "07:34", "end": "07:35", "reason": "drop shot winner"},
{"start": "07:36", "end": "07:38", "reason": "double hit"},
{"start": "07:40", "end": "07:41", "reason": "shuttlecock out of bounds"},
{"start": "07:46", "end": "07:47", "reason": "shuttlecock out of bounds"},
{"start": "07:49", "end": "07:49", "reason": "shuttlecock lands on wrong side"},
{"start": "08:03", "end": "08:05", "reason": "service fault"},
{"start": "08:10", "end": "08:10", "reason": "shuttlecock lands on wrong side"},
{"start": "08:20", "end": "08:21", "reason": "shuttlecock out of bounds"},
{"start": "09:47", "end": "09:50", "reason": "service fault"},
{"start": "09:52", "end": "09:54", "reason": "shuttlecock out of bounds"},
{"start": "09:55", "end": "09:56", "reason": "double hit"},
{"start": "10:07", "end": "10:11", "reason": "shuttlecock out of bounds"},
{"start": "11:26", "end": "11:27", "reason": "shuttlecock out of bounds"},
{"start": "11:30", "end": "11:32", "reason": "shuttlecock out of bounds"},
{"start": "11:33", "end": "11:34", "reason": "unforced error"},
{"start": "11:35", "end": "11:38", "reason": "shuttlecock lands on wrong side"},
{"start": "11:38", "end": "11:38", "reason": "double hit"},
{"start": "12:08", "end": "12:15", "reason": "shuttlecock out of bounds"},
{"start": "12:16", "end": "12:20", "reason": "shuttlecock out of bounds"},
{"start": "12:39", "end": "12:46", "reason": "shuttlecock out of bounds"},
{"start":
```

### 2. amazon.nova-2-lite-v1:0 - video-1-person
**状态**: ✅ 成功
**响应时间**: 38.99 秒
**输入Token**: 76203
**输出Token**: 2000

**模型响应**:
```json
```json
{
  "segments": [
    {"start": "00:00", "end": "00:05", "reason": "smash winner"},
    {"start": "00:05", "end": "00:06", "reason": "smash winner"},
    {"start": "00:06", "end": "00:07", "reason": "smash winner"},
    {"start": "00:07", "end": "00:08", "reason": "smash winner"},
    {"start": "00:08", "end": "00:09", "reason": "smash winner"},
    {"start": "00:09", "end": "00:10", "reason": "smash winner"},
    {"start": "00:10", "end": "00:11", "reason": "smash winner"},
    {"start": "00:11", "end": "00:12", "reason": "smash winner"},
    {"start": "00:12", "end": "00:13", "reason": "smash winner"},
    {"start": "00:13", "end": "00:14", "reason": "smash winner"},
    {"start": "00:14", "end": "00:15", "reason": "smash winner"},
    {"start": "00:15", "end": "00:16", "reason": "smash winner"},
    {"start": "00:16", "end": "00:17", "reason": "smash winner"},
    {"start": "00:17", "end": "00:18", "reason": "smash winner"},
    {"start": "00:18", "end": "00:19", "reason": "smash winner"},
    {"start": "00:19", "end": "00:20", "reason": "smash winner"},
    {"start": "00:20", "end": "00:21", "reason": "smash winner"},
    {"start": "00:21", "end": "00:22", "reason": "smash winner"},
    {"start": "00:22", "end": "00:23", "reason": "smash winner"},
    {"start": "00:23", "end": "00:24", "reason": "smash winner"},
    {"start": "00:24", "end": "00:25", "reason": "smash winner"},
    {"start": "00:25", "end": "00:26", "reason": "smash winner"},
    {"start": "00:26", "end": "00:27", "reason": "smash winner"},
    {"start": "00:27", "end": "00:28", "reason": "smash winner"},
    {"start": "00:28", "end": "00:29", "reason": "smash winner"},
    {"start": "00:29", "end": "00:30", "reason": "smash winner"},
    {"start": "00:30", "end": "00:31", "reason": "smash winner"},
    {"start": "00:31", "end": "00:32", "reason": "smash winner"},
    {"start": "00:32", "end": "00:33", "reason": "smash winner"},
    {"start": "00:33", "end": "00:34", "reason": "smash winner"},
    {"start": "00:34", "end": "00:35", "reason": "smash winner"},
    {"start": "00:35", "end": "00:36", "reason": "smash winner"},
    {"start": "00:36", "end": "00:37", "reason": "smash winner"},
    {"start": "00:37", "end": "00:38", "reason": "smash winner"},
    {"start": "00:38", "end": "00:39", "reason": "smash winner"},
    {"start": "00:39", "end": "00:40", "reason": "smash winner"},
    {"start": "00:40", "end": "00:41", "reason": "smash winner"},
    {"start": "00:41", "end": "00:42", "reason": "smash winner"},
    {"start": "00:42", "end": "00:43", "reason": "smash winner"},
    {"start": "00:43", "end": "00:44", "reason": "smash winner"},
    {"start": "00:44", "end": "00:45", "reason": "smash winner"},
    {"start": "00:45", "end": "00:46", "reason": "smash winner"},
    {"start": "00:46", "end": "00:47", "reason": "smash winner"},
    {"start": "00:47", "end": "00:48", "reason": "smash winner"},
    {"start": "00:48", "end": "00:49", "reason": "smash winner"},
    {"start": "00:49", "end": "00:50", "reason": "smash winner"},
    {"start": "00:50", "end": "00:51", "reason": "smash winner"},
    {"start": "00:51", "end": "00:52", "reason": "smash winner"},
    {"start": "00:52", "end": "00:53", "reason": "smash winner"},
    {"start": "00:53", "end": "00:54", "reason": "smash winner"},
    {"start": "00:54", "end": "00:55", "reason": "smash winner"},
    {"start": "00:55", "end": "00:56", "reason": "smash winner"},
    {"start": "00:56", "end": "00:57", "reason": "smash winner"},
    {"start": "00:57", "end": "00:58", "reason": "smash winner"},
    {"start": "00:58", "end": "00:59", "reason": "smash winner"},
    {"start": "00:59", "end": "01:00", "reason": "smash winner"},
    {"start": "01:00", "end": "01:01", "reason": "smash winner"},
    {"start": "01:01", "end": "01:02", "reason": "smash winner"},
    {"start": "01:02", "end": "01:03", "reason": "smash winner"},
    {"start": "01:03", "end": "01:04", "reason": "smash winner"},
    {"start": "01:04", "end": "01:05", "reason": "smash winner"},
    {"start": "01:05", "end": "01:06", "reason": "smash winner"},
    {"start": "01:06", "end": "01:07", "reason": "smash winner"},
    {"start": "01:07", "end": "01:08", "reason": "smash winner"},
    {"start": "01:08", "end": "01:09", "reason": "smash winner"},
    {"start": "01:09", "end": "01:10", "reason": "smash winner"},
    {"start": "01:10", "end": "01:11", "reason": "smash winner"},
    {"start": "01:11", "end": "01:12", "reason": "smash winner"},
    {"start": "01:12", "end": "01:13", "reason": "smash winner"},
    {"start": "01:13", "end": "01:14", "reason": "smash winner"},
    {"start": "01:14", "end": "01:15", "reason": "smash winner"},
    {"start": "01:15", "end": "01:16", "reason": "smash winner"},
    {"start": "01:16", "end": "01:17", "reason": "smash winner"},
    {"start": "01:17", "end": "01:18", "reason": "smash winner"},
    {"start": "01:18", "end": "01:19", "reason": "smash winner"},
    {"start": "01:19", "end": "01:20", "reason": "smash winner"},
    {"start": "01:20", "end": "01:21", "reason": "smash winner"},
    {"start": "01:21", "end": "01:22", "reason": "smash winner"},
    {"start": "01:22", "end": "01:23", "reason": "smash winner"},
    {"start": "01:23", "end": "01:
```

### 3. amazon.nova-2-lite-v1:0 (reasoning=low) - video-1-person
**状态**: ❌ 失败
**错误信息**: AWSHTTPSConnectionPool(host='bedrock-runtime.us-east-1.amazonaws.com', port=443): Read timed out.

### 4. amazon.nova-pro-v1:0 - video-1-person
**状态**: ✅ 成功
**响应时间**: 52.51 秒
**输入Token**: 86928
**输出Token**: 1119

**模型响应**:
```json
{
  "segments": [
    {
      "start": "00:05",
      "end": "00:12",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "00:15",
      "end": "00:23",
      "reason": "net fault"
    },
    {
      "start": "00:25",
      "end": "00:32",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "00:35",
      "end": "00:42",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "00:45",
      "end": "00:52",
      "reason": "net fault"
    },
    {
      "start": "00:55",
      "end": "01:02",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "01:05",
      "end": "01:12",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "01:15",
      "end": "01:22",
      "reason": "net fault"
    },
    {
      "start": "01:25",
      "end": "01:32",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "01:35",
      "end": "01:42",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "01:45",
      "end": "01:52",
      "reason": "net fault"
    },
    {
      "start": "01:55",
      "end": "02:02",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "02:05",
      "end": "02:12",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "02:15",
      "end": "02:22",
      "reason": "net fault"
    },
    {
      "start": "02:25",
      "end": "02:32",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "02:35",
      "end": "02:42",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "02:45",
      "end": "02:52",
      "reason": "net fault"
    },
    {
      "start": "02:55",
      "end": "03:02",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "03:05",
      "end": "03:12",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "03:15",
      "end": "03:22",
      "reason": "net fault"
    },
    {
      "start": "03:25",
      "end": "03:32",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "03:35",
      "end": "03:42",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "03:45",
      "end": "03:52",
      "reason": "net fault"
    },
    {
      "start": "03:55",
      "end": "04:02",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "04:05",
      "end": "04:12",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "04:15",
      "end": "04:22",
      "reason": "net fault"
    },
    {
      "start": "04:25",
      "end": "04:32",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "04:35",
      "end": "04:42",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "04:45",
      "end": "04:52",
      "reason": "net fault"
    },
    {
      "start": "04:55",
      "end": "05:00",
      "reason": "shuttlecock out of bounds"
    }
  ]
}
```

### 5. amazon.nova-lite-v1:0 - video-2-match
**状态**: ✅ 成功
**响应时间**: 36.74 秒
**输入Token**: 87511
**输出Token**: 932

**模型响应**:
```json
{"segments": [
{"start": "00:01", "end": "00:14", "reason": "shuttlecock out of bounds"},
{"start": "00:16", "end": "00:29", "reason": "shuttlecock out of bounds"},
{"start": "00:31", "end": "00:38", "reason": "smash winner"},
{"start": "00:38", "end": "00:45", "reason": "service fault"},
{"start": "00:47", "end": "00:53", "reason": "shuttlecock out of bounds"},
{"start": "00:55", "end": "01:03", "reason": "double hit"},
{"start": "01:05", "end": "01:11", "reason": "service fault"},
{"start": "01:12", "end": "01:22", "reason": "shuttlecock out of bounds"},
{"start": "01:23", "end": "01:40", "reason": "unforced error"},
{"start": "01:42", "end": "02:02", "reason": "unforced error"},
{"start": "02:05", "end": "02:11", "reason": "service fault"},
{"start": "02:13", "end": "02:15", "reason": "double hit"},
{"start": "02:15", "end": "02:19", "reason": "shuttlecock out of bounds"},
{"start": "02:20", "end": "02:24", "reason": "double hit"},
{"start": "02:25", "end": "02:37", "reason": "unforced error"},
{"start": "02:37", "end": "02:48", "reason": "let (replay point)"},
{"start": "02:48", "end": "03:01", "reason": "service fault"},
{"start": "03:04", "end": "03:16", "reason": "net fault (shuttlecock hits net)"},
{"start": "03:18", "end": "03:25", "reason": "shuttlecock out of bounds"},
{"start": "03:28", "end": "03:32", "reason": "double hit"},
{"start": "03:35", "end": "03:41", "reason": "service fault"},
{"start": "03:44", "end": "03:50", "reason": "overhead smash winner"},
{"start": "03:52", "end": "03:57", "reason": "unforced error"},
{"start": "04:02", "end": "04:08", "reason": "service fault"},
{"start": "04:10", "end": "04:13", "reason": "shuttlecock out of bounds"},
{"start": "04:14", "end": "04:18", "reason": "service fault"},
{"start": "04:19", "end": "04:24", "reason": "shuttlecock out of bounds"},
{"start": "04:26", "end": "04:28", "reason": "net fault (shuttlecock hits net)"},
{"start": "04:29", "end": "04:36", "reason": "service fault"},
{"start": "04:41", "end": "04:50", "reason": "unforced error"},
{"start": "04:52", "end": "04:58", "reason": "shuttlecock lands on wrong side"},
{"start": "04:58", "end": "05:05", "reason": "overhead smash winner"}
]}
```

### 6. amazon.nova-2-lite-v1:0 - video-2-match
**状态**: ✅ 成功
**响应时间**: 34.40 秒
**输入Token**: 76463
**输出Token**: 1566

**模型响应**:
```json
```json
{
  "segments": [
    {
      "start": "00:00",
      "end": "00:12",
      "reason": "smash winner"
    },
    {
      "start": "00:12",
      "end": "00:18",
      "reason": "smash winner"
    },
    {
      "start": "00:18",
      "end": "00:23",
      "reason": "smash winner"
    },
    {
      "start": "00:23",
      "end": "00:29",
      "reason": "smash winner"
    },
    {
      "start": "00:29",
      "end": "00:33",
      "reason": "smash winner"
    },
    {
      "start": "00:33",
      "end": "00:39",
      "reason": "smash winner"
    },
    {
      "start": "00:39",
      "end": "00:45",
      "reason": "smash winner"
    },
    {
      "start": "00:45",
      "end": "00:51",
      "reason": "smash winner"
    },
    {
      "start": "00:51",
      "end": "00:57",
      "reason": "smash winner"
    },
    {
      "start": "00:57",
      "end": "01:03",
      "reason": "smash winner"
    },
    {
      "start": "01:03",
      "end": "01:09",
      "reason": "smash winner"
    },
    {
      "start": "01:09",
      "end": "01:15",
      "reason": "smash winner"
    },
    {
      "start": "01:15",
      "end": "01:21",
      "reason": "smash winner"
    },
    {
      "start": "01:21",
      "end": "01:27",
      "reason": "smash winner"
    },
    {
      "start": "01:27",
      "end": "01:33",
      "reason": "smash winner"
    },
    {
      "start": "01:33",
      "end": "01:39",
      "reason": "smash winner"
    },
    {
      "start": "01:39",
      "end": "01:45",
      "reason": "smash winner"
    },
    {
      "start": "01:45",
      "end": "01:51",
      "reason": "smash winner"
    },
    {
      "start": "01:51",
      "end": "01:57",
      "reason": "smash winner"
    },
    {
      "start": "01:57",
      "end": "02:03",
      "reason": "smash winner"
    },
    {
      "start": "02:03",
      "end": "02:09",
      "reason": "smash winner"
    },
    {
      "start": "02:09",
      "end": "02:15",
      "reason": "smash winner"
    },
    {
      "start": "02:15",
      "end": "02:21",
      "reason": "smash winner"
    },
    {
      "start": "02:21",
      "end": "02:27",
      "reason": "smash winner"
    },
    {
      "start": "02:27",
      "end": "02:33",
      "reason": "smash winner"
    },
    {
      "start": "02:33",
      "end": "02:39",
      "reason": "smash winner"
    },
    {
      "start": "02:39",
      "end": "02:45",
      "reason": "smash winner"
    },
    {
      "start": "02:45",
      "end": "02:51",
      "reason": "smash winner"
    },
    {
      "start": "02:51",
      "end": "02:57",
      "reason": "smash winner"
    },
    {
      "start": "02:57",
      "end": "03:03",
      "reason": "smash winner"
    },
    {
      "start": "03:03",
      "end": "03:09",
      "reason": "smash winner"
    },
    {
      "start": "03:09",
      "end": "03:15",
      "reason": "smash winner"
    },
    {
      "start": "03:15",
      "end": "03:21",
      "reason": "smash winner"
    },
    {
      "start": "03:21",
      "end": "03:27",
      "reason": "smash winner"
    },
    {
      "start": "03:27",
      "end": "03:33",
      "reason": "smash winner"
    },
    {
      "start": "03:33",
      "end": "03:39",
      "reason": "smash winner"
    },
    {
      "start": "03:39",
      "end": "03:45",
      "reason": "smash winner"
    },
    {
      "start": "03:45",
      "end": "03:51",
      "reason": "smash winner"
    },
    {
      "start": "03:51",
      "end": "03:57",
      "reason": "smash winner"
    },
    {
      "start": "03:57",
      "end": "04:03",
      "reason": "smash winner"
    },
    {
      "start": "04:03",
      "end": "04:09",
      "reason": "smash winner"
    },
    {
      "start": "04:09",
      "end": "04:15",
      "reason": "smash winner"
    },
    {
      "start": "04:15",
      "end": "04:21",
      "reason": "smash winner"
    },
    {
      "start": "04:21",
      "end": "04:27",
      "reason": "smash winner"
    },
    {
      "start": "04:27",
      "end": "04:33",
      "reason": "smash winner"
    },
    {
      "start": "04:33",
      "end": "04:39",
      "reason": "smash winner"
    },
    {
      "start": "04:39",
      "end": "04:45",
      "reason": "smash winner"
    },
    {
      "start": "04:45",
      "end": "04:51",
      "reason": "smash winner"
    },
    {
      "start": "04:51",
      "end": "04:57",
      "reason": "smash winner"
    },
    {
      "start": "04:57",
      "end": "05:03",
      "reason": "smash winner"
    }
  ]
}
```
```

### 7. amazon.nova-2-lite-v1:0 (reasoning=low) - video-2-match
**状态**: ✅ 成功
**响应时间**: 42.16 秒
**输入Token**: 76513
**输出Token**: 3847

**模型响应**:
```json
```json
{"segments": [
    {"start": "00:05", "end": "00:12", "reason": "shuttlecock out of bounds"},
    {"start": "00:15", "end": "00:23", "reason": "net fault"},
    {"start": "00:24", "end": "00:32", "reason": "smash winner"},
    {"start": "00:33", "end": "00:39", "reason": "shuttlecock out of bounds"},
    {"start": "00:40", "end": "00:48", "reason": "unforced error"},
    {"start": "00:49", "end": "00:57", "reason": "net fault"},
    {"start": "00:58", "end": "01:06", "reason": "smash winner"},
    {"start": "01:07", "end": "01:15", "reason": "shuttlecock out of bounds"},
    {"start": "01:16", "end": "01:24", "reason": "drop shot winner"},
    {"start": "01:25", "end": "01:33", "reason": "shuttlecock out of bounds"},
    {"start": "01:34", "end": "01:42", "reason": "net fault"},
    {"start": "01:43", "end": "01:51", "reason": "smash winner"},
    {"start": "01:52", "end": "02:00", "reason": "shuttlecock out of bounds"},
    {"start": "02:01", "end": "02:09", "reason": "unforced error"},
    {"start": "02:10", "end": "02:18", "reason": "net fault"},
    {"start": "02:19", "end": "02:27", "reason": "smash winner"},
    {"start": "02:28", "end": "02:36", "reason": "shuttlecock out of bounds"},
    {"start": "02:37", "end": "02:37", "reason": "service fault"},
    {"start": "02:46", "end": "02:54", "reason": "smash winner"},
    {"start": "02:55", "end": "03:03", "reason": "shuttlecock out of bounds"},
    {"start": "03:04", "end": "03:12", "reason": "net fault"},
    {"start": "03:13", "end": "03:21", "reason": "drop shot winner"},
    {"start": "03:22", "end": "03:30", "reason": "shuttlecock out of bounds"},
    {"start": "03:31", "end": "03:39", "reason": "smash winner"},
    {"start": "03:40", "end": "03:48", "reason": "unforced error"},
    {"start": "03:49", "end": "03:57", "reason": "net fault"},
    {"start": "03:58", "end": "04:06", "reason": "shuttlecock out of bounds"},
    {"start": "04:07", "end": "04:15", "reason": "smash winner"},
    {"start": "04:16", "end": "04:24", "reason": "shuttlecock out of bounds"},
    {"start": "04:25", "end": "04:33", "reason": "net fault"},
    {"start": "04:34", "end": "04:42", "reason": "drop shot winner"},
    {"start": "04:43", "end": "04:51", "reason": "smash winner"},
    {"start": "04:52", "end": "04:59", "reason": "shuttlecock out of bounds"}
]}
```
```

### 8. amazon.nova-pro-v1:0 - video-2-match
**状态**: ✅ 成功
**响应时间**: 53.40 秒
**输入Token**: 86928
**输出Token**: 1078

**模型响应**:
```json
{
  "segments": [
    {
      "start": "00:05",
      "end": "00:12",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "00:15",
      "end": "00:23",
      "reason": "net fault"
    },
    {
      "start": "00:25",
      "end": "00:32",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "00:35",
      "end": "00:42",
      "reason": "double hit"
    },
    {
      "start": "00:45",
      "end": "00:52",
      "reason": "smash winner"
    },
    {
      "start": "00:55",
      "end": "01:02",
      "reason": "drop shot winner"
    },
    {
      "start": "01:05",
      "end": "01:12",
      "reason": "clear out of bounds"
    },
    {
      "start": "01:15",
      "end": "01:22",
      "reason": "service fault"
    },
    {
      "start": "01:25",
      "end": "01:32",
      "reason": "let (replay point)"
    },
    {
      "start": "01:35",
      "end": "01:42",
      "reason": "unforced error"
    },
    {
      "start": "01:45",
      "end": "01:52",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "01:55",
      "end": "02:02",
      "reason": "net fault"
    },
    {
      "start": "02:05",
      "end": "02:12",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "02:15",
      "end": "02:22",
      "reason": "double hit"
    },
    {
      "start": "02:25",
      "end": "02:32",
      "reason": "smash winner"
    },
    {
      "start": "02:35",
      "end": "02:42",
      "reason": "drop shot winner"
    },
    {
      "start": "02:45",
      "end": "02:52",
      "reason": "clear out of bounds"
    },
    {
      "start": "02:55",
      "end": "03:02",
      "reason": "service fault"
    },
    {
      "start": "03:05",
      "end": "03:12",
      "reason": "let (replay point)"
    },
    {
      "start": "03:15",
      "end": "03:22",
      "reason": "unforced error"
    },
    {
      "start": "03:25",
      "end": "03:32",
      "reason": "shuttlecock out of bounds"
    },
    {
      "start": "03:35",
      "end": "03:42",
      "reason": "net fault"
    },
    {
      "start": "03:45",
      "end": "03:52",
      "reason": "shuttlecock lands on wrong side"
    },
    {
      "start": "03:55",
      "end": "04:02",
      "reason": "double hit"
    },
    {
      "start": "04:05",
      "end": "04:12",
      "reason": "smash winner"
    },
    {
      "start": "04:15",
      "end": "04:22",
      "reason": "drop shot winner"
    },
    {
      "start": "04:25",
      "end": "04:32",
      "reason": "clear out of bounds"
    },
    {
      "start": "04:35",
      "end": "04:42",
      "reason": "service fault"
    },
    {
      "start": "04:45",
      "end": "04:52",
      "reason": "let (replay point)"
    },
    {
      "start": "04:55",
      "end": "05:00",
      "reason": "unforced error"
    }
  ]
}
```

## 评估指标
本测试主要评估以下指标：
1. **时间戳准确性**: 模型识别的比赛回合起止时间是否准确
2. **回合识别完整性**: 是否识别出所有比赛回合
3. **结束原因准确性**: 对每个回合结束原因的判断是否正确
4. **响应时间**: 模型处理视频的速度
5. **输出格式**: 是否按照要求的JSON格式输出
