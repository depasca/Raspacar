import time
import io
import threading

# Try to import the real Picamera2; if unavailable provide a minimal stub
try:
    from picamera2 import Picamera2
    from libcamera import Transform
except Exception:
    class Picamera2:
        def __init__(self):
            pass
        def create_preview_configuration(self, main=None):
            # return a minimal config object compatible with configure(...)
            return {}
        def configure(self, config):
            pass
        def start(self):
            # indicate at runtime that the real camera is not available
            raise RuntimeError("picamera2 is not available on this system")
        def capture_array(self):
            raise RuntimeError("picamera2 is not available on this system")
        def stop(self):
            pass
        def close(self):
            pass
    class Transform:
        def __init__(self, hflip=0, vflip=0):
            pass    

# Import PIL.Image if available, otherwise provide a clearer runtime error if used
try:
    from PIL import Image
except Exception:
    class Image:
        @staticmethod
        def fromarray(array):
            raise RuntimeError("Pillow (PIL) is not available on this system")


class CameraStreamer:
    """Handles MJPEG camera streaming"""
    
    def __init__(self):
        self.init_camera()

    def init_camera(self):
        self.camera = Picamera2()
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        
        # Configure camera
        config = self.camera.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}, 
            transform=Transform(hflip=1, vflip=1)
        )
        self.camera.configure(config)
        print("✓ Camera configured")
    
    def start(self):
        """Start camera capture"""
        if not self.camera:
            self.init_camera()
            
        self.running = True
        self.camera.rotate = 180
        self.camera.start()
        time.sleep(2)  # Camera warm-up
        
        thread = threading.Thread(target=self._capture_loop)
        thread.daemon = True
        thread.start()
        print("✓ Camera streaming started")
    
    def _capture_loop(self):
        """Capture frames continuously"""
        while self.running:
            try:
                # Capture frame
                array = self.camera.capture_array()
                img = Image.fromarray(array)
                
                # Convert to JPEG
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                
                with self.lock:
                    self.frame = buffer.getvalue()
                
                time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                print(f"Camera error: {e}")
                time.sleep(0.1)
    
    def get_frame(self):
        """Get latest frame"""
        with self.lock:
            return self.frame
    
    def stop(self):
        """Stop camera"""
        self.running = False
        self.camera.stop()
        self.camera.close()
        self.camera = None
# Global camera streamer instance
camera_streamer = CameraStreamer()
