import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw, ImageFont
from flask import current_app

def generate_video_qr_code(video_url, unique_id, qr_folder=None, style='modern'):
    """
    Generate a high-resolution, print-ready QR Code for the unique video URL.
    
    Args:
        video_url (str): The full public URL (e.g., https://domain.com/video/8f72a91c)
        unique_id (str): The unique identifier for the video
        qr_folder (str, optional): Directory to save the QR code image
        style (str): 'modern' (rounded modules, premium palette) or 'classic'
        
    Returns:
        tuple: (relative_web_path, absolute_file_path)
    """
    if qr_folder is None:
        qr_folder = current_app.config['QR_FOLDER']
        
    os.makedirs(qr_folder, exist_ok=True)
    filename = f"qr_{unique_id}.png"
    filepath = os.path.join(qr_folder, filename)
    relative_path = f"qr_codes/{filename}"

    # Setup QR Code parameters
    # Error correction level H (High: 30% recovery) ensures easy camera scanning
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=16,   # Yields high-resolution image (~600-1200px)
        border=3
    )
    qr.add_data(video_url)
    qr.make(fit=True)

    try:
        if style == 'modern':
            # Modern styling: Deep Slate/Indigo dark modules with crisp white background
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=SolidFillColorMask(
                    back_color=(255, 255, 255),
                    front_color=(15, 23, 42)  # Slate-900
                )
            )
        else:
            # Classic styling
            img = qr.make_image(
                fill_color="black",
                back_color="white"
            )
        
        # Save as PNG
        img.save(filepath, format="PNG", optimize=True)
        
    except Exception as e:
        # Fallback to standard QR image if styled image encounters issues
        basic_img = qr.make_image(fill_color="black", back_color="white")
        basic_img.save(filepath, format="PNG")

    return relative_path, filepath


def generate_high_res_qr_stream(video_url, box_size=25):
    """
    Generate an ultra high-resolution QR code in-memory for download / printing.
    """
    import io
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=4
    )
    qr.add_data(video_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#0f172a", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", dpi=(300, 300))
    buffer.seek(0)
    return buffer
