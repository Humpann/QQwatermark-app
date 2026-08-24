"""
Network utilities for discovering LAN IP addresses and generating QR codes.
"""
import socket
import io
import base64
from typing import List, Dict, Any
try:
    import qrcode
    from qrcode.main import QRCode
except ImportError:
    qrcode = None
    QRCode = None

def get_lan_ips() -> List[str]:
    """Retrieve all non-loopback IPv4 addresses on the host machine."""
    ips = []
    try:
        # Primary method: connect to an external UDP address (does not actually send data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            primary_ip = s.getsockname()[0]
            if primary_ip and primary_ip not in ips and not primary_ip.startswith("127."):
                ips.append(primary_ip)
    except Exception:
        pass

    # Secondary method: inspect all hostnames
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except Exception:
        pass

    # If all failed, return localhost
    if not ips:
        ips.append("127.0.0.1")
    return ips

def generate_qr_base64(data: str) -> str:
    """Generate a Base64-encoded PNG image data URI of a QR code."""
    if not qrcode or not QRCode:
        return ""
    try:
        qr = QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=3,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#4f46e5", back_color="#ffffff")
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"
    except Exception:
        return ""

def print_terminal_qr(data: str):
    """Print an ASCII QR code to the standard terminal output."""
    if not qrcode or not QRCode:
        return
    qr = QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
