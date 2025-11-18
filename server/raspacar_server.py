#!/usr/bin/env python3
"""
Raspberry Pi Car WiFi Server
Creates WiFi AP and serves video stream + control WebSocket
"""
from html_template import HTML_PAGE
from motor_controller import motor_controller
from cam_streamer import camera_streamer
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from websockets import ConnectionClosedError
import json
import threading
import time
import io
from PIL import Image
from fastapi.routing import APIRoute
from starlette.websockets import WebSocket as StarletteWebSocket
from starlette.responses import Response


def create_app(config = {}):
    """Create and configure the Flask app"""
    app = FastAPI()
    sock = WebSocketRoute(app)
    
    @app.get("/")
    async def root():
        """Serve web control interface"""
        return HTML_PAGE
    
    @app.get('/video_feed')
    def video_feed():
        """MJPEG video stream endpoint"""
        def generate():
            while True:
                frame = camera_streamer.get_frame()
                if frame:
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(0.033)
        
        return Response(generate(),
            mimetype='multipart/x-mixed-replace; boundary=frame')
    @sock.route('/ws')
    def websocket(ws):
        """WebSocket endpoint for control commands"""
        print("Client connected via WebSocket")
        try:
            while True:
                data = ws.receive()
                if data:
                    try:
                        command = json.loads(data)
                        x = float(command.get('x', 0))
                        y = float(command.get('y', 0))
                        motor_controller.move(x, y)
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Invalid command: {e}")
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            motor_controller.stop()
            print("Client disconnected")

    return app, sock

def main():
    """Main entry point"""
    print("\n" + "="*50)
    print("Raspberry Pi Car WiFi Server")
    print("="*50)
    
    try:
        app = create_app()
        
        # Start camera
        camera_streamer.start()
        
        print("\n✓ Server ready!")
        print(f"📱 Connect to WiFi: 'RPi-Car'")
        print(f"🌐 Open browser: http://192.168.4.1:5000")
        print(f"   (or http://raspberrypi.local:5000)")
        print("\nPress Ctrl+C to stop\n")
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        camera_streamer.stop()
        motor_controller.cleanup()
        print("✓ Cleanup complete")


if __name__ == "__main__":
    main()