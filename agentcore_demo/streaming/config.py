from bedrock_agentcore_starter_toolkit import Runtime

agentcore_runtime = Runtime()

response = agentcore_runtime.configure(
    entrypoint="streaming_agent.py",
    execution_role=your_iam_role_arn,
    auto_create_ecr=True,
    requirements_file="requirements.txt"
)