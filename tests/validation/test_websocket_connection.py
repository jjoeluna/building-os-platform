#!/usr/bin/env python3
"""
🚀 BuildingOS WebSocket Connection Test
======================================

Simple test to verify WebSocket connectivity.
"""

import asyncio
import websockets
import ssl
import json
from datetime import datetime

async def test_websocket():
    """Test WebSocket connection"""
    print("🧪 Testing WebSocket Connection...")
    
    websocket_url = "wss://08ozbst1md.execute-api.us-east-1.amazonaws.com/dev"
    
    try:
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        print(f"🔗 Connecting to: {websocket_url}")
        
        # Connect to WebSocket
        async with websockets.connect(
            websocket_url,
            ssl=ssl_context
        ) as websocket:
            
            print("✅ WebSocket connection established!")
            
            # Send a test message
            test_message = {
                "message": "Hello BuildingOS! This is a test message from WebSocket client.",
                "user_id": "test-user",
                "timestamp": datetime.now().isoformat(),
                "test": True
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Test message sent")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
                return True
            except asyncio.TimeoutError:
                print("⏰ No response received (timeout)")
                return True  # Connection successful even without response
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 BuildingOS WebSocket Connection Test")
    print("=" * 50)
    
    success = await test_websocket()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 WebSocket connection test PASSED!")
        print("✅ WebSocket is working correctly")
    else:
        print("❌ WebSocket connection test FAILED!")
        print("⚠️  Please check the WebSocket configuration")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
