#!/usr/bin/env python3
"""
Desktop Test Client for Raspberry Pi Car
Connects via Bluetooth, displays video feed, and allows keyboard control
"""

import bluetooth
import threading
import time
import io
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
import queue


class BluetoothCarClient:
    """Desktop client for testing RPi car"""
    
    def __init__(self):
        self.socket = None
        self.connected = False
        self.running = False
        
        # Data queues
        self.frame_queue = queue.Queue(maxsize=5)
        self.command_queue = queue.Queue()
        
        # Threads
        self.receive_thread = None
        self.send_thread = None
        
        # Current movement state
        self.current_x = 0.0
        self.current_y = 0.0
    
    def scan_devices(self):
        """Scan for nearby Bluetooth devices"""
        print("Scanning for Bluetooth devices...")
        devices = bluetooth.discover_devices(duration=8, lookup_names=True)
        return devices
    
    def connect(self, address):
        """Connect to Raspberry Pi car"""
        try:
            print(f"Connecting to {address}...")
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((address, 1))  # RFCOMM channel 1
            self.connected = True
            self.running = True
            print("Connected!")
            
            # Start threads
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            self.send_thread = threading.Thread(target=self._send_loop)
            self.send_thread.daemon = True
            self.send_thread.start()
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            messagebox.showerror("Connection Error", str(e))
            return False
    
    def disconnect(self):
        """Disconnect from car"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        print("Disconnected")
    
    def _receive_loop(self):
        """Receive and process video frames"""
        buffer = bytearray()
        
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                buffer.extend(data)
                
                # Look for JPEG markers
                while len(buffer) > 2:
                    # Find JPEG start (0xFF 0xD8)
                    start_idx = -1
                    for i in range(len(buffer) - 1):
                        if buffer[i] == 0xFF and buffer[i + 1] == 0xD8:
                            start_idx = i
                            break
                    
                    if start_idx == -1:
                        buffer.clear()
                        break
                    
                    if start_idx > 0:
                        buffer = buffer[start_idx:]
                    
                    # Find JPEG end (0xFF 0xD9)
                    end_idx = -1
                    for i in range(2, len(buffer) - 1):
                        if buffer[i] == 0xFF and buffer[i + 1] == 0xD9:
                            end_idx = i
                            break
                    
                    if end_idx == -1:
                        break
                    
                    # Extract frame
                    frame_data = bytes(buffer[:end_idx + 2])
                    buffer = buffer[end_idx + 2:]
                    
                    # Try to add to queue (drop if full)
                    try:
                        self.frame_queue.put_nowait(frame_data)
                    except queue.Full:
                        # Drop old frame
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put_nowait(frame_data)
                        except:
                            pass
                            
            except Exception as e:
                print(f"Receive error: {e}")
                break
        
        self.connected = False
        print("Receive loop stopped")
    
    def _send_loop(self):
        """Send commands to car"""
        while self.running:
            try:
                # Send current movement state every 100ms
                command = f"M:{self.current_x:.2f},{self.current_y:.2f}\n"
                self.socket.send(command.encode('utf-8'))
                time.sleep(0.1)
            except Exception as e:
                print(f"Send error: {e}")
                break
        
        print("Send loop stopped")
    
    def set_movement(self, x, y):
        """Update movement command"""
        self.current_x = max(-1.0, min(1.0, x))
        self.current_y = max(-1.0, min(1.0, y))
    
    def stop(self):
        """Stop movement"""
        self.set_movement(0, 0)


class CarControlGUI:
    """GUI for controlling the car"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RPi Car Test Client")
        self.root.geometry("800x700")
        
        self.client = BluetoothCarClient()
        self.devices = []
        
        # Key states for smooth movement
        self.keys_pressed = set()
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Bind keyboard events
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        
        # Start video update loop
        self.update_video()
        self.update_movement()
    
    def setup_ui(self):
        """Setup GUI components"""
        
        # Connection frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(conn_frame, text="Scan Devices", command=self.scan_devices).pack(side=tk.LEFT, padx=5)
        
        self.device_combo = ttk.Combobox(conn_frame, width=40, state='readonly')
        self.device_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_btn = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect, state='disabled')
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = ttk.Label(conn_frame, text="Not connected", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Video frame
        video_frame = ttk.LabelFrame(self.root, text="Camera Feed", padding=10)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.video_label = ttk.Label(video_frame, text="No video feed", background="black", foreground="white")
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Control frame
        ctrl_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Instructions
        instructions = """
        Keyboard Controls:
        W/↑ - Forward    S/↓ - Backward    A/← - Left    D/→ - Right
        Space - Stop
        """
        ttk.Label(ctrl_frame, text=instructions, justify=tk.LEFT).pack()
        
        # Movement indicators
        indicator_frame = ttk.Frame(ctrl_frame)
        indicator_frame.pack(pady=10)
        
        ttk.Label(indicator_frame, text="X (Left/Right):").grid(row=0, column=0, padx=5)
        self.x_label = ttk.Label(indicator_frame, text="0.00", width=8, background="lightgray")
        self.x_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(indicator_frame, text="Y (Fwd/Back):").grid(row=1, column=0, padx=5)
        self.y_label = ttk.Label(indicator_frame, text="0.00", width=8, background="lightgray")
        self.y_label.grid(row=1, column=1, padx=5)
    
    def scan_devices(self):
        """Scan for Bluetooth devices"""
        self.status_label.config(text="Scanning...", foreground="orange")
        self.root.update()
        
        try:
            self.devices = self.client.scan_devices()
            
            if self.devices:
                device_list = [f"{name} ({addr})" for addr, name in self.devices]
                self.device_combo['values'] = device_list
                self.device_combo.current(0)
                self.status_label.config(text=f"Found {len(self.devices)} device(s)", foreground="blue")
            else:
                messagebox.showinfo("Scan Complete", "No devices found")
                self.status_label.config(text="No devices found", foreground="red")
        except Exception as e:
            messagebox.showerror("Scan Error", str(e))
            self.status_label.config(text="Scan failed", foreground="red")
    
    def connect(self):
        """Connect to selected device"""
        if not self.device_combo.get():
            messagebox.showwarning("No Device", "Please scan and select a device first")
            return
        
        # Get selected device address
        idx = self.device_combo.current()
        address = self.devices[idx][0]
        
        if self.client.connect(address):
            self.status_label.config(text="Connected", foreground="green")
            self.connect_btn.config(state='disabled')
            self.disconnect_btn.config(state='normal')
            self.device_combo.config(state='disabled')
    
    def disconnect(self):
        """Disconnect from device"""
        self.client.disconnect()
        self.status_label.config(text="Disconnected", foreground="red")
        self.connect_btn.config(state='normal')
        self.disconnect_btn.config(state='disabled')
        self.device_combo.config(state='readonly')
    
    def on_key_press(self, event):
        """Handle key press"""
        key = event.keysym.lower()
        self.keys_pressed.add(key)
    
    def on_key_release(self, event):
        """Handle key release"""
        key = event.keysym.lower()
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def update_movement(self):
        """Update movement based on pressed keys"""
        x = 0.0
        y = 0.0
        
        # Forward/Backward
        if 'w' in self.keys_pressed or 'up' in self.keys_pressed:
            y += 1.0
        if 's' in self.keys_pressed or 'down' in self.keys_pressed:
            y -= 1.0
        
        # Left/Right
        if 'a' in self.keys_pressed or 'left' in self.keys_pressed:
            x -= 1.0
        if 'd' in self.keys_pressed or 'right' in self.keys_pressed:
            x += 1.0
        
        # Stop
        if 'space' in self.keys_pressed:
            x = 0.0
            y = 0.0
            self.keys_pressed.clear()
        
        # Update client
        if self.client.connected:
            self.client.set_movement(x, y)
            
            # Update UI
            self.x_label.config(text=f"{x:.2f}")
            self.y_label.config(text=f"{y:.2f}")
        
        # Schedule next update
        self.root.after(50, self.update_movement)
    
    def update_video(self):
        """Update video feed"""
        try:
            if not self.client.frame_queue.empty():
                frame_data = self.client.frame_queue.get_nowait()
                
                # Convert JPEG to image
                image = Image.open(io.BytesIO(frame_data))
                
                # Resize to fit window while maintaining aspect ratio
                display_width = self.video_label.winfo_width()
                display_height = self.video_label.winfo_height()
                
                if display_width > 1 and display_height > 1:
                    image.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                self.video_label.config(image=photo, text="")
                self.video_label.image = photo  # Keep reference
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Video update error: {e}")
        
        # Schedule next update
        self.root.after(33, self.update_video)  # ~30 FPS
    
    def on_close(self):
        """Handle window close"""
        if self.client.connected:
            self.client.disconnect()
        self.root.destroy()
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    print("RPi Car Desktop Test Client")
    print("=" * 40)
    
    app = CarControlGUI()
    app.run()