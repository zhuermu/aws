import os
import asyncio
import base64
import json
import uuid
import pyaudio
from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient, InvokeModelWithBidirectionalStreamOperationInput
from aws_sdk_bedrock_runtime.models import InvokeModelWithBidirectionalStreamInputChunk, BidirectionalInputPayloadPart, ModelStreamErrorException
from aws_sdk_bedrock_runtime.config import Config, HTTPAuthSchemeResolver, SigV4AuthScheme
from smithy_aws_core.credentials_resolvers.environment import EnvironmentCredentialsResolver
from dotenv import load_dotenv
from weather_tool import WeatherTool

load_dotenv()
# Audio configuration
INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_SIZE = 1024

class SimpleNovaSonic:
    def __init__(self, model_id='amazon.nova-sonic-v1:0', region='us-east-1'):
        self.model_id = model_id
        self.region = region
        self.client = None
        self.stream = None
        self.response = None
        self.is_active = False
        self.prompt_name = str(uuid.uuid4())
        self.content_name = str(uuid.uuid4())
        self.audio_content_name = str(uuid.uuid4())
        self.audio_queue = asyncio.Queue()
        self.display_assistant_text = False
        self.weather_tool = WeatherTool()
        self.tool_use_id = None

    def _initialize_client(self):
        """Initialize the Bedrock client."""
        config = Config(
            endpoint_uri=f"https://bedrock-runtime.{self.region}.amazonaws.com",
            region=self.region,
            aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
            http_auth_scheme_resolver=HTTPAuthSchemeResolver(),
            http_auth_schemes={"aws.auth#sigv4": SigV4AuthScheme()}
        )
        self.client = BedrockRuntimeClient(config=config)

    async def send_event(self, event_json):
        """Send an event to the stream."""
        event = InvokeModelWithBidirectionalStreamInputChunk(
            value=BidirectionalInputPayloadPart(bytes_=event_json.encode('utf-8'))
        )
        await self.stream.input_stream.send(event)
    async def start_session(self):
        """Start a new session with Nova Sonic."""
        if not self.client:
            self._initialize_client()
            
        # Initialize the stream
        self.stream = await self.client.invoke_model_with_bidirectional_stream(
            InvokeModelWithBidirectionalStreamOperationInput(model_id=self.model_id)
        )
        self.is_active = True
        
        # Send session start event
        session_start = '''
        {
          "event": {
            "sessionStart": {
              "inferenceConfiguration": {
                "maxTokens": 1024,
                "topP": 0.9,
                "temperature": 0.7
              }
            }
          }
        }
        '''
        await self.send_event(session_start)

        weather_schema = json.dumps({
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city to get weather for"
                }
            },
            "required": ["city"]
        })
        # Send prompt start event with tool configuration
        prompt_start = {
            "event": {
                "promptStart": {
                    "promptName": self.prompt_name,
                    "textOutputConfiguration": {
                        "mediaType": "text/plain"
                    },
                    "audioOutputConfiguration": {
                        "mediaType": "audio/lpcm",
                        "sampleRateHertz": 24000,
                        "sampleSizeBits": 16,
                        "channelCount": 1,
                        "voiceId": "matthew",
                        "encoding": "base64",
                        "audioType": "SPEECH"
                    },
                    "toolUseOutputConfiguration": {
                        "mediaType": "application/json"
                    },
                    "toolConfiguration": {
                        "tools": [
                            
                            {
                                "toolSpec": {
                                    "name": "get_weather",
                                    "description": "Get current weather information for a city",
                                    "inputSchema": {
                                    "json": weather_schema
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        print("Tool configuration:", json.dumps(prompt_start))
        await self.send_event(json.dumps(prompt_start))
        
        # Send system prompt
        text_content_start = f'''
        {{
            "event": {{
                "contentStart": {{
                    "promptName": "{self.prompt_name}",
                    "contentName": "{self.content_name}",
                    "type": "TEXT",
                    "interactive": true,
                    "role": "SYSTEM",
                    "textInputConfiguration": {{
                        "mediaType": "text/plain"
                    }}
                }}
            }}
        }}
        '''
        await self.send_event(text_content_start)
        
        system_prompt = "You are a friendly assistant. The user and you will engage in a spoken dialog " \
            "exchanging the transcripts of a natural real-time conversation. Keep your responses short, " \
            "generally two or three sentences for chatty scenarios. You can use the get_weather tool to " \
            "provide weather information when asked."
        
        text_input = f'''
        {{
            "event": {{
                "textInput": {{
                    "promptName": "{self.prompt_name}",
                    "contentName": "{self.content_name}",
                    "content": "{system_prompt}"
                }}
            }}
        }}
        '''
        await self.send_event(text_input)
        
        text_content_end = f'''
        {{
            "event": {{
                "contentEnd": {{
                    "promptName": "{self.prompt_name}",
                    "contentName": "{self.content_name}"
                }}
            }}
        }}
        '''
        await self.send_event(text_content_end)
        
        # Start processing responses
        self.response = asyncio.create_task(self._process_responses())

    async def start_audio_input(self):
        """Start audio input stream."""
        audio_content_start = f'''
        {{
            "event": {{
                "contentStart": {{
                    "promptName": "{self.prompt_name}",
                    "contentName": "{self.audio_content_name}",
                    "type": "AUDIO",
                    "interactive": true,
                    "role": "USER",
                    "audioInputConfiguration": {{
                        "mediaType": "audio/lpcm",
                        "sampleRateHertz": 16000,
                        "sampleSizeBits": 16,
                        "channelCount": 1,
                        "audioType": "SPEECH",
                        "encoding": "base64"
                    }}
                }}
            }}
        }}
        '''
        await self.send_event(audio_content_start)
    
    async def send_audio_chunk(self, audio_bytes):
        """Send an audio chunk to the stream."""
        if not self.is_active:
            return
            
        blob = base64.b64encode(audio_bytes)
        audio_event = f'''
        {{
            "event": {{
                "audioInput": {{
                    "promptName": "{self.prompt_name}",
                    "contentName": "{self.audio_content_name}",
                    "content": "{blob.decode('utf-8')}"
                }}
            }}
        }}
        '''
        await self.send_event(audio_event)
    
    async def end_audio_input(self):
        """End audio input stream."""
        audio_content_end = f'''
        {{
            "event": {{
                "contentEnd": {{
                    "promptName": "{self.prompt_name}",
                    "contentName": "{self.audio_content_name}"
                }}
            }}
        }}
        '''
        await self.send_event(audio_content_end)
    async def end_session(self):
        """End the session."""
        if not self.is_active:
            return
            
        prompt_end = f'''
        {{
            "event": {{
                "promptEnd": {{
                    "promptName": "{self.prompt_name}"
                }}
            }}
        }}
        '''
        await self.send_event(prompt_end)
        
        session_end = '''
        {
            "event": {
                "sessionEnd": {}
            }
        }
        '''
        await self.send_event(session_end)
        # close the stream
        await self.stream.input_stream.close()

    async def _process_responses(self):
        """Process responses from the stream."""
        retry_count = 0
        max_retries = 3
        
        try:
            while self.is_active:
                try:
                    output = await self.stream.await_output()
                    if not output:
                        print("Received empty output from stream")
                        retry_count += 1
                        if retry_count >= max_retries:
                            print("Max retries reached, attempting to reconnect...")
                            await self._reconnect()
                            retry_count = 0
                        continue
                        
                    result = await output[1].receive()
                    if not result:
                        print("Received empty result from stream")
                        retry_count += 1
                        if retry_count >= max_retries:
                            print("Max retries reached, attempting to reconnect...")
                            await self._reconnect()
                            retry_count = 0
                        continue
                    
                    # Reset retry count on successful result
                    retry_count = 0
                    
                    if not hasattr(result, 'value') or not result.value:
                        print("Received result without value")
                        continue
                        
                    if not hasattr(result.value, 'bytes_'):
                        print("Received result without bytes")
                        continue
                    
                    response_data = result.value.bytes_.decode('utf-8')
                    try:
                        json_data = json.loads(response_data)
                        
                        if 'event' in json_data:
                            # Handle content start event
                            if 'contentStart' in json_data['event']:
                                content_start = json_data['event']['contentStart'] 
                                # set role
                                self.role = content_start['role']
                                # Check for speculative content
                                if 'additionalModelFields' in content_start:
                                    additional_fields = json.loads(content_start['additionalModelFields'])
                                    if additional_fields.get('generationStage') == 'SPECULATIVE':
                                        self.display_assistant_text = True
                                    else:
                                        self.display_assistant_text = False
                                    
                            # Handle text output event
                            elif 'textOutput' in json_data['event']:
                                text = json_data['event']['textOutput']['content']    
                               
                                if (self.role == "ASSISTANT" and self.display_assistant_text):
                                    print(f"Assistant: {text}")
                                elif self.role == "USER":
                                    print(f"User: {text}")
                            
                            # Handle audio output
                            elif 'audioOutput' in json_data['event']:
                                audio_content = json_data['event']['audioOutput']['content']
                                audio_bytes = base64.b64decode(audio_content)
                                await self.audio_queue.put(audio_bytes)
                                
                            # Handle tool use
                            elif 'toolUse' in json_data['event']:
                                try:
                                    tool_use = json_data['event']['toolUse']
                                    self.tool_use_id = tool_use['toolUseId']
                                    tool_name = tool_use['toolName']
                                    tool_input = json.loads(tool_use['content'])
                                    
                                    if tool_name == 'get_weather':
                                        weather_result = self.weather_tool.get_weather(tool_input['city'])
                                        
                                        # Send tool result
                                        tool_result = f'''
                                        {{
                                            "event": {{
                                                "toolResult": {{
                                                    "promptName": "{self.prompt_name}",
                                                    "contentName": "{self.content_name}",
                                                    "content": "{json.dumps(weather_result)}"
                                                }}
                                            }}
                                        }}
                                        '''
                                        await self.send_event(tool_result)
                                except Exception as tool_error:
                                    print(f"Error processing tool use: {tool_error}")
                                    print(f"Tool use data: {json.dumps(json_data['event']['toolUse'], indent=2)}")
                    except json.JSONDecodeError as json_error:
                        print(f"Error decoding JSON: {json_error}")
                        print(f"Raw response data: {response_data}")
                except ModelStreamErrorException as stream_error:
                    print(f"Stream error: {stream_error}")
                    await self._reconnect()
                except Exception as stream_error:
                    print(f"Unexpected stream error: {stream_error}")
                    print(f"Error type: {type(stream_error)}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
                    await self._reconnect()
        except Exception as e:
            print(f"Error processing responses: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            self.is_active = False

    async def _reconnect(self):
        """Attempt to reconnect the stream."""
        try:
            print("Attempting to reconnect...")
            await self.end_session()
            await asyncio.sleep(2)  # Add a longer delay before reconnecting
            await self.start_session()
            print("Reconnected successfully")
        except Exception as reconnect_error:
            print(f"Error reconnecting: {reconnect_error}")
            self.is_active = False

    async def play_audio(self):
        """Play audio responses."""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=OUTPUT_SAMPLE_RATE,
            output=True
        )
        
        try:
            while self.is_active:
                audio_data = await self.audio_queue.get()
                stream.write(audio_data)
        except Exception as e:
            print(f"Error playing audio: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    async def capture_audio(self):
        """Capture audio from microphone and send to Nova Sonic."""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=INPUT_SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        print("Starting audio capture. Speak into your microphone...")
        print("Press Enter to stop...")
        
        await self.start_audio_input()
        
        try:
            while self.is_active:
                audio_data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                await self.send_audio_chunk(audio_data)
                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"Error capturing audio: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            print("Audio capture stopped.")
            await self.end_audio_input()
async def main():
    # Create Nova Sonic client
    nova_client = SimpleNovaSonic()
    
    # Start session
    await nova_client.start_session()
    
    # Start audio playback task
    playback_task = asyncio.create_task(nova_client.play_audio())
    
    # Start audio capture task
    capture_task = asyncio.create_task(nova_client.capture_audio())
    
    # Wait for user to press Enter to stop
    await asyncio.get_event_loop().run_in_executor(None, input)
    
    # End session
    nova_client.is_active = False
    
    # First cancel the tasks
    tasks = []
    if not playback_task.done():
        tasks.append(playback_task)
    if not capture_task.done():
        tasks.append(capture_task)
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    
    # cancel the response task
    if nova_client.response and not nova_client.response.done():
        nova_client.response.cancel()
    
    await nova_client.end_session()
    print("Session ended")

if __name__ == "__main__":  
    # Set AWS credentials if not using environment variables
    # os.environ['AWS_ACCESS_KEY_ID'] = "your-access-key"
    # os.environ['AWS_SECRET_ACCESS_KEY'] = "your-secret-key"
    # os.environ['AWS_DEFAULT_REGION'] = "us-east-1"

    asyncio.run(main())