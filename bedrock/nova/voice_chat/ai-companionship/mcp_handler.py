import os
import json
import requests
import asyncio
from pathlib import Path
from fastapi import FastAPI, APIRouter
from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("Amazon Sonic Tools", stateless_http=True)

# Weather tool
@mcp.tool()
def get_weather(location: str) -> str:
    """Get the current weather for a location"""
    print(f"[mcp_handler] get_weather({location})")
    try:
        endpoint = "https://wttr.in"
        response = requests.get(f"{endpoint}/{location}?format=j1", timeout=5)
        if response.status_code == 200:
            weather_data = response.json()
            current = weather_data.get("current_condition", [{}])[0]
            temp_c = current.get("temp_C", "N/A")
            temp_f = current.get("temp_F", "N/A")
            desc = current.get("weatherDesc", [{}])[0].get("value", "Unknown")
            humidity = current.get("humidity", "N/A")
            
            return f"Weather in {location}: {desc}, {temp_c}°C ({temp_f}°F), Humidity: {humidity}%"
        else:
            return f"Could not retrieve weather for {location}. Status code: {response.status_code}"
    except Exception as e:
        return f"Error getting weather: {str(e)}"

# Time tool
@mcp.tool()
def get_time(location: str) -> str:
    """Get the current time for a location"""
    print(f"[mcp_handler] get_time({location})")
    try:
        # Use timeapi.io to get time for location
        response = requests.get(f"https://timeapi.io/api/Time/current/zone?timeZone={location}", timeout=5)
        if response.status_code == 200:
            time_data = response.json()
            current_time = time_data.get("time", "Unknown")
            date = time_data.get("date", "Unknown")
            day_of_week = time_data.get("dayOfWeek", "Unknown")
            
            return f"Current time in {location}: {current_time} on {day_of_week}, {date}"
        else:
            return f"Could not retrieve time for {location}. Please try a valid timezone like 'America/New_York'."
    except Exception as e:
        return f"Error getting time: {str(e)}. Please try a valid timezone like 'America/New_York'."

def setup_mcp_routes(app: FastAPI):
    """Set up MCP routes on the FastAPI app"""
    # Create a router for MCP endpoints
    router = APIRouter()
    
    # Add MCP routes to the router
    mcp.setup_routes(router)
    
    # Include the router in the app with a prefix
    app.include_router(router, prefix="/mcp_http")
    
    print("MCP HTTP routes initialized at /mcp_http")
    return app

def start_mcp_server():
    """Start the MCP server in a separate process"""
    # This function can be used to start the MCP server in a separate process if needed
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    # For testing the MCP server standalone
    start_mcp_server()
