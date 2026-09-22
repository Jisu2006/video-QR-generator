import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from app.models import db, Video, AppSetting
from app.routes.auth import login_required
from app.utils.file_handler import (
    generate_unique_id,
    validate_video_file,
    save_video_file
)
from app.utils.qr_generator import generate_video_qr_code
from app.utils.network_helper import get_local_ip, get_effective_base_url

upload_bp = Blueprint('upload', __name__, url_prefix='/admin')

@upload_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_video():
    """Handle video file upload and automatic QR code generation."""
    if request.method == 'POST':
        # Check if file part exists in request
        if 'video_file' not in request.files:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                return jsonify({'success': False, 'message': 'No video file provided in the request.'}), 400
            flash('No video file selected.', 'danger')
            return redirect(request.url)

        file = request.files['video_file']
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        preferred_base_mode = request.form.get('base_url_mode', 'auto')

        # Validate file
        is_valid, error_msg = validate_video_file(file)
        if not is_valid:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': error_msg}), 400
            flash(error_msg, 'danger')
            return redirect(request.url)

        try:
            # Generate unique video identifier
            unique_id = generate_unique_id(length=8)
            while Video.query.filter_by(unique_id=unique_id).first():
                unique_id = generate_unique_id(length=8)

            # Auto-fill title from filename if not provided
            if not title:
                original_base = os.path.splitext(file.filename)[0]
                title = original_base.replace('_', ' ').replace('-', ' ').title()

            # Save physical video file safely
            original_filename, stored_filename, abs_file_path, file_size, mime_type = save_video_file(file, unique_id)

            # Determine public base URL for video & QR code
            # Priority: Saved AppSetting > Config.BASE_URL > Dynamic LAN IP / Request
            custom_base = AppSetting.get('base_url', '').strip()
            if custom_base:
                base_url = custom_base.rstrip('/')
            elif preferred_base_mode == 'local_ip':
                local_ip = get_local_ip()
                port = request.environ.get('SERVER_PORT', '5000')
                scheme = request.scheme
                base_url = f"{scheme}://{local_ip}:{port}" if port not in ('80', '443') else f"{scheme}://{local_ip}"
            else:
                base_url = get_effective_base_url()

            video_public_url = f"{base_url}/video/{unique_id}"

            # Generate high-resolution QR code pointing to unique video URL
            qr_rel_path, qr_abs_path = generate_video_qr_code(
                video_url=video_public_url,
                unique_id=unique_id,
                qr_folder=current_app.config['QR_FOLDER'],
                style='modern'
            )

            # Save video record to database
            video_record = Video(
                unique_id=unique_id,
                title=title,
                description=description,
                original_filename=original_filename,
                stored_filename=stored_filename,
                file_path=abs_file_path,
                file_size=file_size,
                mime_type=mime_type,
                video_url=video_public_url,
                qr_code_path=qr_rel_path
            )
            db.session.add(video_record)
            db.session.commit()

            # Respond to AJAX or redirect standard form
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('is_ajax') == '1':
                return jsonify({
                    'success': True,
                    'message': 'Video uploaded and QR code generated successfully!',
                    'unique_id': unique_id,
                    'video_url': video_public_url,
                    'redirect_url': url_for('upload.upload_result', unique_id=unique_id)
                })

            flash('Video uploaded and QR Code generated successfully!', 'success')
            return redirect(url_for('upload.upload_result', unique_id=unique_id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during video upload: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
            flash(f'An error occurred during upload: {str(e)}', 'danger')
            return redirect(request.url)

    # GET Request: render upload form
    local_ip = get_local_ip()
    configured_base = AppSetting.get('base_url', current_app.config.get('BASE_URL', ''))
    max_mb = current_app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
    
    return render_template(
        'admin/upload.html',
        local_ip=local_ip,
        configured_base=configured_base,
        max_mb=max_mb
    )


@upload_bp.route('/result/<unique_id>')
@login_required
def upload_result(unique_id):
    """Display generated QR code and sharing options for uploaded video."""
    video = Video.query.filter_by(unique_id=unique_id).first_or_404()
    local_ip = get_local_ip()
    
    return render_template(
        'admin/result.html',
        video=video,
        local_ip=local_ip
    )
