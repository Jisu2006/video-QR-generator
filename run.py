import os
import argparse
from app import create_app
from app.utils.network_helper import get_local_ip

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Video QR Generator Server")
    parser.add_argument('--host', default='0.0.0.0', help="Host interface to bind (default: 0.0.0.0)")
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5000)), help="Port number (default: 5000)")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    args = parser.parse_args()

    local_ip = get_local_ip()
    port = args.port

    print("\n" + "=" * 65)
    print("  [VIDEO QR GENERATOR] - SERVER READY")
    print("=" * 65)
    print(f"  Local Access       : http://127.0.0.1:{port}")
    print(f"  Network (Mobile)   : http://{local_ip}:{port}")
    print(f"  Admin Login        : http://127.0.0.1:{port}/admin/login")
    print(f"  Default Credentials: admin / admin123")
    print("=" * 65)
    print("  * Tip: Connect your mobile phone to the same Wi-Fi network and")
    print(f"    scan generated QR codes to stream videos directly!\n")

    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug or app.config.get('DEBUG', True)
    )
