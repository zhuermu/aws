from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

# Configure your agent with tools
@tool
def get_weather():
    """Get current weather"""
    return "sunny"

model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-20250514-v1:0")
agent = Agent(model=model, tools=[get_weather])

@app.entrypoint
async def streaming_agent(payload):
    """
    Streaming entrypoint - yields chunks as they become available
    """
    user_input = payload.get("prompt")

    try:
        # Stream each chunk using async generator
        async for event in agent.stream_async(user_input):
            if "data" in event:
                yield event["data"]
    except Exception as e:
        # Handle errors in streaming context
        yield {"error": str(e), "type": "stream_error"}