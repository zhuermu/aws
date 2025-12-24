# Video Understanding Test Results

**Test Time**: 2025-12-24 02:08:38

**Model**: global.amazon.nova-2-lite-v1:0

---

## Video 1

**URL**: `s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/ee51c5a7-a44f-4f0b-82d2-772736aa36f3-Screenrecorder20251107140342212.mp4`

**Cost**: 40325ms

**Result**:
```json
(N, If it meets items 1 and 2 above, it will pass. Output Y, otherwise output N.)
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "state": "N",
      "expected": "Teen Patti master Explorer slots game play",
      "actual": ""
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "state": "N",
      "expected": "Teen Patti master Explorer slots game play | Best Explorer Slots Game 2039",
      "actual": "STOP Losing Money! TeenPatti Explorer Sloo..."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "state": "N",
      "expected": "videoCreator: PVgaming00 or channelId: PVgaming00",
      "actual": "@KGaming24"
    },
    {
      "stepNo": 4,
      "stepName": "Video Play Duration",
      "segments": "[[0.0, 141.4]]"
    }
  ]
}
```

---

## Video 2

**URL**: `s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/youtube-search-aws.mp4`

**Cost**: 9789ms

**Result**:
```json
(N, If it meets items 1 and 2 above, it will pass. Output Y, otherwise output N.)
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "state": "N",
      "expected": "Teen Patti master Explorer slots game play",
      "actual": "aws"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "state": "N",
      "expected": "Teen Patti master Explorer slots game play | Best Explorer Slots Game 2039",
      "actual": "AWS SAA-C03 考试过关"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "state": "N",
      "expected": "videoCreator: PVgaming00 or channelId: PVgaming00",
      "actual": "爱上云"
    },
    {
      "stepNo": 4,
      "stepName": "Video Play Duration",
      "segments": "[[15.0, 35.0], [72.0, 98.0]]"
    }
  ]
}
```

---

## Video 3

**URL**: `s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/20251111-110712-caijian.mp4`

**Cost**: 22493ms

**Result**:
```json
(N, If it meets items 1 and 2 above, it will pass. Output Y, otherwise output N.)
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "state": "N",
      "expected": "Teen Patti master Explorer slots game play",
      "actual": "Slots Game Tricks Revealed"
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "state": "N",
      "expected": "Teen Patti master Explorer slots game play | Best Explorer Slots Game 2039",
      "actual": "STOP Losing Money! TeenPatti Explorer Slots Game Tricks Revealed"
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "state": "N",
      "expected": "videoCreator: PVgaming00 or channelId: PVgaming00",
      "actual": "K_Mater_Gaming"
    },
    {
      "stepNo": 4,
      "stepName": "Video Play Duration",
      "segments": "[[60.0, 250.0]]"
    }
  ]
}
```

---

## Video 4

**URL**: `s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/09211f8f-8d39-4038-ae0b-568b4e25bb26-FunPlay1.mp4`

**Cost**: 4154ms

**Result**:
```json
(N, The video does not show the user searching for keywords, playing a video, or verifying a creator. It only shows a tutorial on how to complete a task within an app.)
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "state": "N",
      "expected": "Teen Patti master Explorer slots game play",
      "actual": "No keyword search is shown in the video."
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "state": "N",
      "expected": "Teen Patti master Explorer slots game play | Best Explorer Slots Game 2039",
      "actual": "No video is played in the video; only instructions are given."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "state": "N",
      "expected": "videoCreator: PVgaming00 or channelId: PVgaming00",
      "actual": "No video is played, so creator verification is not applicable."
    },
    {
      "stepNo": 4,
      "stepName": "Video Play Duration",
      "segments": "[]"
    }
  ]
}
```

---

## Video 5

**URL**: `s3://bedrock-video-generation-us-east-1-pi8hu9/audit-video/6b80e970-67e6-4ee4-a51e-8ceb660e9c54-1000012057.mp4`

**Cost**: 23929ms

**Result**:
```json
(N, The video does not match the expected criteria for keyword search, title verification, or creator verification.)
{
  "auditDetails": [
    {
      "stepNo": 1,
      "stepName": "Keyword Search",
      "state": "N",
      "expected": "Teen Patti master Explorer slots game play",
      "actual": "The video does not show any keyword search activity. The visible content is a slot machine game interface and a YouTube video page."
    },
    {
      "stepNo": 2,
      "stepName": "Found Target Video - Title Verification",
      "state": "N",
      "expected": "Teen Patti master Explorer slots game play | Best Explorer Slots Game 2039",
      "actual": "The video title is 'Explore Slot Super Win Trick | Explore Slot Jackpot Trick | I Got 1000000 Sup...' which does not match the expected title."
    },
    {
      "stepNo": 3,
      "stepName": "Found Target Video - Creator Verification",
      "state": "N",
      "expected": "videoCreator: PVgaming00 or channelId: PVgaming00",
      "actual": "The creator of the video is 'Shiv_Storm', not 'PVgaming00'."
    },
    {
      "stepNo": 4,
      "stepName": "Video Play Duration",
      "segments": "[[0.0, 131.4]]",
      "actual": "The video is played from start to end (0.0 to 131.4 seconds)."
    }
  ]
}
```

---

