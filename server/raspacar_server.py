#!/usr/bin/env python3
"""
Raspberry Pi Car WiFi Server
Creates WiFi AP and serves video stream + control WebSocket
"""
from html_template import HTML_PAGE
from motor_controller import motor_controller
from cam_streamer import camera_streamer

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse

import json
import asyncio


def create_app(config = {}):
    """Create and configure the FastAPI app"""
    app = FastAPI()
    
    @app.get("/")
    async def root():
        """Serve web control interface"""
        return HTMLResponse(HTML_PAGE)
    
    @app.get('/video_feed')
    async def video_feed():
        """MJPEG video stream endpoint"""
        async def generate():
            while True:
                frame = camera_streamer.get_frame()
                if frame:
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                await asyncio.sleep(0.033)  # ~30 FPS
        
        return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for control commands"""
        await websocket.accept()
        print("Client connected via WebSocket")
        try:
            while True:
                data = await websocket.receive_text()
                if data:
                    try:
                        command = json.loads(data)
                        x = float(command.get('x', 0))
                        y = float(command.get('y', 0))
                        motor_controller.move(x, y)
                        print(f"Command: x={x:.2f}, y={y:.2f}")
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Invalid command: {e}")
        except WebSocketDisconnect:
            print("Client disconnected normally")
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            motor_controller.stop()
            print("Client disconnected")

    return app


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*50)
    print("Raspberry Pi Car WiFi Server")
    print("="*50)
    
    app = create_app()
    
    # Start camera
    camera_streamer.start()
    
    print("\n✓ Server ready!")
    print(f"📱 Connect to WiFi: 'RPi-Car'")
    print(f"🌐 Open browser: http://192.168.4.1:5000")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        camera_streamer.stop()
        #motor_controller.cleanup()
        print("✓ Cleanup complete")