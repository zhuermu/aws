import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Bedrock AgentCore client
region = os.getenv('AWS_REGION', 'us-east-1')
agent_core_client = boto3.client('bedrock-agentcore', region_name=region)

def test_agent(prompt, test_name):
    """Test the agent with a specific prompt"""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"Prompt: {prompt}")
    print(f"{'='*60}")
    
    payload = {"prompt": prompt}
    
    try:
        agent_runtime_arn = os.getenv('AGENT_RUNTIME_ARN')
        if not agent_runtime_arn:
            raise ValueError("AGENT_RUNTIME_ARN environment variable is not set. Please check your .env file.")
        
        response = agent_core_client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            qualifier="DEFAULT",
            payload=json.dumps(payload)
        )
        
        # Print response metadata
        print(f"Response Status: {response['statusCode']}")
        print(f"Session ID: {response.get('runtimeSessionId')}")
        
        # Handle the streaming response body
        if 'response' in response:
            response_body = response['response']
            if hasattr(response_body, 'read'):
                response_content = response_body.read().decode('utf-8')
                # Try to parse as JSON, fallback to raw text
                try:
                    response_json = json.loads(response_content)
                    print(f"Agent Response: {response_json}")
                except json.JSONDecodeError:
                    print(f"Agent Response: {response_content}")
            else:
                print(f"Agent Response: {response_body}")
        
        print(f"Status: ✅ SUCCESS")
        return True
        
    except Exception as e:
        print(f"Status: ❌ ERROR - {e}")
        print("Make sure your agent is deployed and running.")
        print("Also ensure your .env file is properly configured with AGENT_RUNTIME_ARN.")
        return False

def run_basic_test():
    """Run the basic test from original test_my_agent.py"""
    return test_agent("Hello, how can you assist me today?", "Basic Connection Test")

def run_comprehensive_tests():
    """Run comprehensive test scenarios"""
    tests = [
        ("Hello, how can you assist me today?", "Basic Greeting"),
        ("Hi, I need help with my order. My email is me@example.net", "Customer Order Inquiry"),
        ("Can you check my recent orders? My email is me@example.net", "Order History Check"),
        ("How do I install the smartphone cover?", "Product Information - Cover Installation"),
        ("Tell me about the smartphone charger specifications", "Product Information - Charger Specs"),
        ("Can you calculate 25 * 4 + 10?", "Calculator Tool Test"),
        ("What time is it now?", "Current Time Query"),
        ("I have a problem with my smartphone cover, can you help?", "Customer Support Issue")
    ]
    
    results = []
    for prompt, test_name in tests:
        success = test_agent(prompt, test_name)
        results.append((test_name, success))
    
    return results

# Main execution
if __name__ == "__main__":
    print("🚀 Starting AWS Bedrock AgentCore Customer Support Assistant Tests")
    print("=" * 80)
    
    # First run basic connectivity test
    print("\n📋 Phase 1: Basic Connectivity Test")
    basic_success = run_basic_test()
    
    if basic_success:
        print("\n📋 Phase 2: Comprehensive Feature Tests")
        results = run_comprehensive_tests()
        
        # Summary
        print(f"\n{'='*80}")
        print("📊 TEST SUMMARY")
        print(f"{'='*80}")
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\nOverall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your agent is working perfectly.")
        else:
            print("⚠️  Some tests failed. Please check the error messages above.")
    else:
        print("\n❌ Basic connectivity test failed. Please check your configuration.")
        print("Make sure:")
        print("1. Your .env file exists and contains AGENT_RUNTIME_ARN")
        print("2. Your AWS credentials are properly configured")
        print("3. Your agent is deployed and running")
    
    print(f"\n{'='*80}")
    print("Tests completed!")
    print(f"{'='*80}")
