import os
from dotenv import load_dotenv
from bedrock_agentcore.memory import MemoryClient

# Load environment variables from .env file
load_dotenv()

# Get region from environment variable
region = os.getenv('AWS_REGION', 'us-east-1')
memory_client = MemoryClient(region_name=region)

memory = memory_client.create_memory_and_wait(
    name="CustomerSupport", 
    description="Customer support conversations",
    strategies=[]
)

# memory = memory_client.create_memory_and_wait(
#     name="CustomerSupport", 
#     description="Customer support conversations",
#     strategies=[{
#         "semanticMemoryStrategy": {
#             "name": "semanticFacts",
#             "namespaces": ["/facts/{actorId}"]
#         }
#     }]
# )

memories = memory_client.retrieve_memories(
    memory_id=memory.get("id"),
    namespace="/facts/user-123",
    query="smartphone model"
)

memory_client.create_event(
    memory_id=memory.get("id"), # Identifies the memory store
    actor_id="user-123",        # Identifies the user
    session_id="session-456",   # Identifies the session
    messages=[
        ("Hi, ...", "USER"),
        ("I'm sorry to hear that...", "ASSISTANT"),
        ("get_orders(customer_id='123')", "TOOL"),
    ]
)

conversations = memory_client.list_events(
    memory_id=memory.get("id"), # Identifies the memory store
    actor_id="user-123",        # Identifies the user 
    session_id="session-456",   # Identifies the session
    max_results=5               # Number of most recent turns to retrieve
)
