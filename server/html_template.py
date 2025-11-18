# HTML page for web interface (for testing)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>RPi Car Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            width: 100%;
            height: 100%;
            overflow: hidden;
            position: fixed;
        }
        
        body {
            background: #000;
            font-family: Arial, sans-serif;
        }
        
        #video {
            position: absolute;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
        }
        
        #joystick {
            position: fixed;
            bottom: 40px;
            right: 40px;
            width: 150px;
            height: 150px;
            background: rgba(0,0,0,0.3);
            border: 2px solid rgba(255,255,255,0.5);
            border-radius: 50%;
            touch-action: none;
            z-index: 100;
        }
        
        #stick {
            position: absolute;
            width: 50px;
            height: 50px;
            background: rgba(33,150,243,0.8);
            border: 2px solid white;
            border-radius: 50%;
            left: 50px;
            top: 50px;
            pointer-events: none;
        }
        
        #info {
            position: fixed;
            top: 10px;
            left: 10px;
            color: white;
            background: rgba(0,0,0,0.5);
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
            z-index: 100;
        }
    </style>
</head>
<body>
    <img id="video" src="/video_feed" alt="Camera Feed">
    <div id="info">
        <div>Status: <span id="status">Connecting...</span></div>
        <div>X: <span id="x">0.00</span> | Y: <span id="y">0.00</span></div>
    </div>
    <div id="joystick">
        <div id="stick"></div>
    </div>
    
    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const joystick = document.getElementById('joystick');
        const stick = document.getElementById('stick');
        const statusEl = document.getElementById('status');
        const xEl = document.getElementById('x');
        const yEl = document.getElementById('y');
        
        let isDragging = false;
        const maxRadius = 50;
        
        ws.onopen = () => {
            statusEl.textContent = 'Connected';
            statusEl.style.color = '#4CAF50';
        };
        
        ws.onclose = () => {
            statusEl.textContent = 'Disconnected';
            statusEl.style.color = '#f44336';
        };
        
        function sendCommand(x, y) {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({x, y}));
                xEl.textContent = x.toFixed(2);
                yEl.textContent = y.toFixed(2);
            }
        }
        
        function updateStick(clientX, clientY) {
            const rect = joystick.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            let dx = clientX - centerX;
            let dy = clientY - centerY;
            const distance = Math.sqrt(dx*dx + dy*dy);
            
            if (distance > maxRadius) {
                dx = (dx / distance) * maxRadius;
                dy = (dy / distance) * maxRadius;
            }
            
            stick.style.left = (50 + dx) + 'px';
            stick.style.top = (50 + dy) + 'px';
            
            const x = dx / maxRadius;
            const y = -dy / maxRadius;
            sendCommand(x, y);
        }
        
        function resetStick() {
            stick.style.left = '50px';
            stick.style.top = '50px';
            sendCommand(0, 0);
        }
        
        // Touch events
        joystick.addEventListener('touchstart', (e) => {
            e.preventDefault();
            isDragging = true;
            updateStick(e.touches[0].clientX, e.touches[0].clientY);
        });
        
        joystick.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (isDragging) {
                updateStick(e.touches[0].clientX, e.touches[0].clientY);
            }
        });
        
        joystick.addEventListener('touchend', (e) => {
            e.preventDefault();
            isDragging = false;
            resetStick();
        });
        
        // Mouse events
        joystick.addEventListener('mousedown', (e) => {
            isDragging = true;
            updateStick(e.clientX, e.clientY);
        });
        
        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                updateStick(e.clientX, e.clientY);
            }
        });
        
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                resetStick();
            }
        });
        
        // Prevent pinch zoom and other gestures
        document.addEventListener('gesturestart', (e) => e.preventDefault());
        document.addEventListener('gesturechange', (e) => e.preventDefault());
        document.addEventListener('gestureend', (e) => e.preventDefault());
    </script>
</body>
</html>
"""