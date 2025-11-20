# 🚗 Raspberry Pi Remote Control Car Server

A WiFi-controlled RC car server for Raspberry Pi with live video streaming and real-time motor control. Built with FastAPI and Websockets for low-latency remote operation.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🎥 **Real-time MJPEG Video Streaming** - Smooth 30 FPS camera feed at 640x480
- 🎮 **WebSocket Control** - Low-latency bidirectional communication
- 🔌 **Adafruit Motor HAT Support** - Professional-grade motor control with PWM
- 📱 **Web Interface** - Built-in test interface accessible from any browser
- 🌐 **WiFi Access Point Mode** - Create standalone network or use existing WiFi
- ⚡ **Async Architecture** - Built on FastAPI for maximum performance
- 🛡️ **Differential Steering** - Smooth turning with independent left/right control

## 📸 Demo

TBD

## 🔧 Hardware Requirements

### Required Components

- **Raspberry Pi 3 A+** (or any Raspberry Pi with WiFi)
- **Raspberry Pi Camera Module** (v1, v2, or HQ camera)
- **Adafruit DC & Stepper Motor HAT** for Raspberry Pi
- **4x DC Motors** (6-12V)
- **Power Supply** for motors (6-12V, 3A+ recommended)
- **Chassis** with wheels
- **Battery Pack** (for mobile operation)

### Wiring Diagram

```
Motor HAT Connections:
├─ M1: Front Right Motor
├─ M2: Rear Right Motor
├─ M3: Front Left Motor
├─ M4: Rear Right Motor
└─ Power: 6-12V Battery (3A+)

Camera: Connect to CSI port on Raspberry Pi
```

## 🚀 Quick Start

### 1. System Setup

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Enable I2C for Motor HAT
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable

# Enable Camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable

# Reboot
sudo reboot
```

### 2. Install Dependencies

```bash
# Install Python packages
pip3 install fastapi uvicorn websockets
pip3 install adafruit-circuitpython-motorkit
pip3 install picamera2 pillow

# Install I2C tools (optional, for debugging)
sudo apt-get install -y i2c-tools
```

### 3. Verify Hardware

```bash
# Check Motor HAT is detected (should show 0x60)
sudo i2cdetect -y 1

# Test camera
libcamera-hello
```

### 4. Clone and Run

```bash
# Clone repository
git clone https://github.com/depasca/raspacar.git
cd raspacar/server

# Run server
sudo python3 raspacar_server.py
```

The server will start on `http://0.0.0.0:5000`

### 5. Connect and Control

**On your local network:**
1. Find your Raspberry Pi's IP address: `hostname -I`
2. Connect your phone/computer to the same WiFi network
3. Open browser: `http://RASPBERRY_PI_IP:5000`
4. Use the virtual joystick to control the car!

## 📁 Project Structure

```
server/
├── raspacar_server.py                      # FastAPI server with video streaming and WebSocket control
├── motor_controller.py # Motor control using Adafruit Motor HAT
├── cam_streamer.py              # Camera capture and MJPEG streaming
├── html_template.py             # Web interface template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🌐 WiFi Access Point Setup (Optional)

To make your car completely standalone, configure it as a WiFi Access Point:

```bash
# Install required packages
sudo apt-get install -y hostapd dnsmasq

# Configure static IP for wlan0
sudo nano /etc/dhcpcd.conf
# Add at the end:
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant

# Configure dnsmasq
sudo nano /etc/dnsmasq.conf
# Add:
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h

# Configure hostapd
sudo nano /etc/hostapd/hostapd.conf
# Add:
interface=wlan0
ssid=Raspacar
wpa_passphrase=rpicar123
hw_mode=g
channel=7
wpa=2
wpa_key_mgmt=WPA-PSK

# Enable services
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

# Reboot
sudo reboot
```

After reboot, your Raspberry Pi will broadcast **"RPi-Car"** WiFi network (password: `rpicar123`).

Connect to it and access the interface at: `http://192.168.4.1:5000`

## 🎮 API Endpoints

### Video Stream
```
GET /video_feed
Returns: MJPEG stream (multipart/x-mixed-replace)
```

### Control WebSocket
```
WS /ws
Send: {"x": 0.5, "y": 1.0}
  x: -1.0 (left) to 1.0 (right)
  y: -1.0 (backward) to 1.0 (forward)
```

### Web Interface
```
GET /
Returns: HTML control interface
```

## 🔧 Configuration

### Motor Speed Adjustment

Edit `adafruit_motor_controller.py`:

```python
def move(self, x, y):
    # Adjust these multipliers for speed control
    forward_speed = y * 100  # 0-100% motor power
    turn_speed = x * 100     # 0-100% turning intensity
```

### Camera Settings

Edit `cam_streamer.py`:

```python
config = self.camera.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"},  # Change resolution
            transform=Transform(hflip=1, vflip=1)   # if you need to rotate the image
)

# Adjust frame rate
time.sleep(0.033)  # ~30 FPS (decrease for higher FPS)
```

### Server Port

Edit `raspacar_server.py` or run with custom port:

```bash
uvicorn raspacar_server:app --host 0.0.0.0 --port 8000
```

## 🐛 Troubleshooting

### Motor HAT Not Detected

```bash
# Check I2C is enabled
sudo raspi-config

# Verify device at 0x60
sudo i2cdetect -y 1

# Check connections - HAT should be firmly seated
```

## 🔋 Power Considerations

- **Raspberry Pi:** 5V 2.5A USB power supply
- **Motors:** Separate 6-12V 3-4A power supply
- **Never power motors from Raspberry Pi's GPIO**
- For mobile operation, use:
  - USB power bank (10,000mAh+) for Raspberry Pi
  - Separate battery pack for motors

## 📊 Performance

- **Video Latency:** ~100-200ms on local network
- **Control Latency:** ~50ms via WebSocket
- **Frame Rate:** 30 FPS @ 640x480
- **Range:** ~30-50 meters (WiFi dependent)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Motor control via [Adafruit CircuitPython](https://github.com/adafruit/Adafruit_CircuitPython_MotorKit)
- Camera support using [Picamera2](https://github.com/raspberrypi/picamera2)

## 📧 Contact

Paolo De Pascalis 
Project Link: [https://github.com/depasca/raspacar](https://github.com/depasca/raspacar)

---

⭐ **If you found this project helpful, please give it a star!** ⭐
