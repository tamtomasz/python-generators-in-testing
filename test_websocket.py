"""
WebSocket Connection Test Script

Simple test to verify WebSocket connectivity to the FastAPI server.
"""

import asyncio
import websockets
import json


async def test_websocket_connection():
    """Test WebSocket connection to the FastAPI server."""
    uri = "ws://127.0.0.1:8000/ws"
    
    try:
        print(f"Attempting to connect to {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection successful!")
            
            # Send a test message
            test_message = {
                "command": "generate_batch",
                "count": 1
            }
            
            print(f"Sending test message: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            print("Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"✅ Received response: {response}")
            
    except ConnectionRefusedError:
        print("❌ Connection refused - server not running on port 8000")
    except asyncio.TimeoutError:
        print("❌ Connection timeout - server not responding")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
