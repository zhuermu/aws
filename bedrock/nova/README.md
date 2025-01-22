# nova agents
This is a simple agent system for the [Nova]

Nava is a multimodal large model provided by Amazon through the interface provided by bedrock

# install
python version 3.9 or later is required
```bash
pip install boto3
pip install fastapi
```

# run server
```bash
uvicorn main:app --reload
```

# features
- [x] input text
- [x] input image
- [x] input video
- [x] ouptut text

**note:** 
- the characters of upload file just support a-z, A-Z, 0-9, -, _ 
