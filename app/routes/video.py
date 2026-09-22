import os
from flask import Blueprint, render_template, abort, send_file, request, current_app, redirect, url_for
from app.models import db, Video
from app.utils.file_handler import stream_video_partial
from app.utils.qr_generator import generate_high_res_qr_stream

video_bp = Blueprint('video', __name__)

@video_bp.route('/video/<unique_id>')
def watch_video(unique_id):
    """
    Public video viewing page.
    Opened when scanning the QR code or visiting the unique video URL directly.
    """
    video = Video.query.filter_by(unique_id=unique_id).first_or_404()

    # Increment view count (simple count tracking)
    try:
        video.views_count += 1
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Check if stream source is playable
    stream_url = url_for('video.stream_video', unique_id=unique_id)
    qr_url = url_for('static', filename=video.qr_code_path)
    download_qr_url = url_for('video.download_qr', unique_id=unique_id)

    return render_template(
        'video/watch.html',
        video=video,
        stream_url=stream_url,
        qr_url=qr_url,
        download_qr_url=download_qr_url
    )


@video_bp.route('/stream/<unique_id>')
def stream_video(unique_id):
    """
    Stream video file using HTTP 206 Partial Content range requests.
    Crucial for mobile phones (iOS Safari / Android Chrome) to scrub and play smoothly.
    """
    video = Video.query.filter_by(unique_id=unique_id).first_or_404()
    
    if not os.path.exists(video.file_path):
        abort(404, description="Video file not found on server disk.")

    return stream_video_partial(video.file_path, video.mime_type)


@video_bp.route('/qr/<unique_id>')
def get_qr_image(unique_id):
    """Serve the static QR code image for a given video."""
    video = Video.query.filter_by(unique_id=unique_id).first_or_404()
    qr_abs_path = os.path.join(current_app.root_path, 'static', video.qr_code_path)
    
    if not os.path.exists(qr_abs_path):
        abort(404, description="QR code image not found.")
        
    return send_file(qr_abs_path, mimetype='image/png')


@video_bp.route('/qr/<unique_id>/download')
def download_qr(unique_id):
    """
    Download a crystal-clear, high-resolution QR code (300 DPI) for printing.
    """
    video = Video.query.filter_by(unique_id=unique_id).first_or_404()
    
    # Generate high resolution stream on the fly or send stored file
    qr_stream = generate_high_res_qr_stream(video.video_url, box_size=30)
    download_name = f"QR_{video.unique_id}_{video.title[:20].replace(' ', '_')}.png"
    
    return send_file(
        qr_stream,
        mimetype='image/png',
        as_attachment=True,
        download_name=download_name
    )
