
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
   