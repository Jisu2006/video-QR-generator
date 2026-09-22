import os
import re
import secrets
import mimetypes
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app, request, Response, abort

def generate_unique_id(length=8):
    """
    Generate a clean, URL-safe unique identifier (e.g. '8f72a91c').
    Uses secrets module for cryptographic randomness.
    """
    return secrets.token_hex(length // 2)


def allowed_file(filename):
    """Check if the filename extension is in the allowed video extensions list."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def get_mime_type(filename, default='video/mp4'):
    """Get the MIME type of a file based on its extension."""
    mime, _ = mimetypes.guess_type(filename)
    if mime:
        return mime
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    mapping = {
        'mp4': 'video/mp4',
        'webm': 'video/webm',
        'mov': 'video/quicktime',
        'mkv': 'video/x-matroska',
        'avi': 'video/x-msvideo',
        'm4v': 'video/x-m4v'
    }
    return mapping.get(ext, default)


def validate_video_file(file_storage):
    """
    Validate uploaded file:
    - Check presence
    - Check filename and extension
    - Check MIME type
    - Check non-zero size
    """
    if not file_storage or file_storage.filename == '':
        return False, "No file was selected."

    filename = file_storage.filename
    if not allowed_file(filename):
        allowed_list = ", ".join(sorted(current_app.config['ALLOWED_EXTENSIONS']))
        return False, f"Invalid video format. Supported formats: {allowed_list}"

    content_type = file_storage.content_type
    if content_type and content_type not in current_app.config['ALLOWED_MIME_TYPES']:
        # Sometimes browsers send application/octet-stream for MKV or MOV; allow if extension matches
        ext = filename.rsplit('.', 1)[-1].lower()
        if ext not in current_app.config['ALLOWED_EXTENSIONS']:
            return False, f"Unsupported video content type: {content_type}"

    return True, "Valid file"


def save_video_file(file_storage, unique_id):
    """
    Save the uploaded video file securely with a sanitized name prefixed by unique_id.
    
    Returns:
        tuple: (original_filename, stored_filename, absolute_path, file_size, mime_type)
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    original_filename = secure_filename(file_storage.filename)
    if not original_filename:
        original_filename = f"video_{unique_id}.mp4"
        
    ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'mp4'
    stored_filename = f"{unique_id}_{secrets.token_hex(4)}.{ext}"
    absolute_path = os.path.join(upload_folder, stored_filename)
    
    # Save the file stream to disk
    file_storage.save(absolute_path)
    
    file_size = os.path.getsize(absolute_path)
    mime_type = get_mime_type(stored_filename)
    
    return original_filename, stored_filename, absolute_path, file_size, mime_type


def delete_video_and_qr_files(video_file_path, qr_code_path):
    """
    Safely delete the stored video file and its associated QR code file from disk.
    """
    # Delete video file
    if video_file_path and os.path.exists(video_file_path):
        try:
            os.remove(video_file_path)
        except OSError:
            pass

    # Delete QR code file
    if qr_code_path:
        full_qr_path = os.path.join(current_app.root_path, 'static', qr_code_path) if not os.path.isabs(qr_code_path) else qr_code_path
        if os.path.exists(full_qr_path):
            try:
                os.remove(full_qr_path)
            except OSError:
                pass


def stream_video_partial(file_path, mime_type='video/mp4'):
    """
    Stream video file using HTTP 206 Partial Content range requests.
    Enables instant seeking, smooth buffering, and full compatibility with
    mobile browsers (iOS Safari, Android Chrome).
    """
    if not os.path.exists(file_path):
        abort(404)

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get('Range', None)

    if not range_header:
        # Standard HTTP 200 response when no Range header is present
        def full_stream():
            with open(file_path, 'rb') as f:
                while chunk := f.read(1024 * 1024):  # 1MB chunks
                    yield chunk

        rv = Response(full_stream(), 200, mimetype=mime_type, direct_passthrough=True)
        rv.headers.add('Content-Length', str(file_size))
        rv.headers.add('Accept-Ranges', 'bytes')
        return rv

    # Parse Range header (e.g., 'bytes=0-1048575' or 'bytes=1048576-')
    range_match = re.search(r'bytes=(\d+)-(\d*)', range_header)
    if not range_match:
        abort(416)  # Range Not Satisfiable

    start_byte = int(range_match.group(1))
    end_byte = range_match.group(2)
    end_byte = int(end_byte) if end_byte else file_size - 1

    if start_byte >= file_size or end_byte >= file_size or start_byte > end_byte:
        abort(416)

    content_length = end_byte - start_byte + 1

    def partial_stream():
        with open(file_path, 'rb') as f:
            f.seek(start_byte)
            bytes_left = content_length
            while bytes_left > 0:
                chunk_size = min(1024 * 1024, bytes_left)  # Up to 1MB chunks
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                bytes_left -= len(chunk)
                yield chunk

    response = Response(partial_stream(), 206, mimetype=mime_type, direct_passthrough=True)
    response.headers.add('Content-Range', f'bytes {start_byte}-{end_byte}/{file_size}')
    response.headers.add('Accept-Ranges', 'bytes')
    response.headers.add('Content-Length', str(content_length))
    response.headers.add('Cache-Control', 'public, max-age=3600')
    return response
