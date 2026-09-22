import socket
from flask import request, current_app

def get_local_ip():
    """
    Detect the local network IP of the server machine (e.g., 192.168.1.15).
    This allows mobile devices connected to the same Wi-Fi network to access the server.
    """
    try:
        # Create a dummy socket connection to detect outgoing network interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Using a public DNS server address (does not actually send packets)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return '127.0.0.1'


def get_effective_base_url(preferred_mode='auto'):
    """
    Determine the most appropriate base URL to encode into the QR code.
    Modes:
      - 'auto': Uses configured BASE_URL if set, else request.host_url (or local IP if localhost)
      - 'local_ip': Explicitly uses http://<LOCAL_IP>:<PORT> (ideal for Wi-Fi mobile testing)
      - 'request': Uses request.host_url
    """
    configured_url = current_app.config.get('BASE_URL', '').strip()
    
    if configured_url:
        return configured_url.rstrip('/')

    # Check request context
    if request:
        host = request.host
        scheme = request.scheme
        
        # If accessing from localhost/127.0.0.1, provide LAN IP alternative for mobile scanning
        if 'localhost' in host or '127.0.0.1' in host:
            local_ip = get_local_ip()
            port = request.environ.get('SERVER_PORT', '5000')
            if port and port not in ('80', '443'):
                return f"{scheme}://{local_ip}:{port}"
            return f"{scheme}://{local_ip}"
        
        return request.host_url.rstrip('/')
        
    local_ip = get_local_ip()
    return f"http://{local_ip}:5000"
