import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from app.models import db, Video, Admin, AppSetting
from app.routes.auth import login_required
from app.utils.file_handler import delete_video_and_qr_files
from app.utils.qr_generator import generate_video_qr_code
from app.utils.network_helper import get_local_ip, get_effective_base_url

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def index():
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Main admin dashboard displaying video listings, metrics, and quick actions."""
    search_query = request.args.get('q', '').strip()
    
    query = Video.query.order_by(Video.created_at.desc())
    if search_query:
        query = query.filter(
            (Video.title.ilike(f'%{search_query}%')) |
            (Video.unique_id.ilike(f'%{search_query}%')) |
            (Video.original_filename.ilike(f'%{search_query}%'))
        )
        
    videos = query.all()

    # Calculate statistics
    total_videos = Video.query.count()
    total_views = db.session.query(db.func.sum(Video.views_count)).scalar() or 0
    total_bytes = db.session.query(db.func.sum(Video.file_size)).scalar() or 0

    # Format storage size
    storage_str = "0 MB"
    if total_bytes > 0:
        bytes_val = total_bytes
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                storage_str = f"{bytes_val:.1f} {unit}"
                break
            bytes_val /= 1024.0
        else:
            storage_str = f"{bytes_val:.1f} TB"

    local_ip = get_local_ip()
    configured_base = AppSetting.get('base_url', current_app.config.get('BASE_URL', ''))

    return render_template(
        'admin/dashboard.html',
        videos=videos,
        total_videos=total_videos,
        total_views=total_views,
        storage_str=storage_str,
        search_query=search_query,
        local_ip=local_ip,
        configured_base=configured_base
    )


@admin_bp.route('/edit/<unique_id>', methods=['POST'])
@login_required
def edit_video(unique_id):
    """Edit video title and description."""
    video = Video.query.filter_by(unique_id=unique_id).first_or_404()
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Video title cannot be empty.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    video.title = title
    video.description = description
    db.session.commit()
    
    flash(f'Updated "{video.title}" successfully!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/delete/<unique_id>', methods=['POST'])
@login_required
def delete_video(unique_id):
    """Delete video from database and remove associated video and QR files from disk."""
    video = Video.query.filter_by(unique_id=unique_id).first_or_404()
    
    video_title = video.title
    file_path = video.file_path
    qr_code_path = video.qr_code_path
    
    try:
        # Delete from DB
        db.session.delete(video)
        db.session.commit()
        
        # Safely remove physical files from server disk
        delete_video_and_qr_files(file_path, qr_code_path)
        
        flash(f'Video "{video_title}" and its QR code were permanently deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting video: {str(e)}', 'danger')
        
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/regenerate-qr/<unique_id>', methods=['POST'])
@login_required
def regenerate_qr(unique_id):
    """Regenerate the QR code for a video (useful after changing Base URL or Domain)."""
    video = Video.query.filter_by(unique_id=unique_id).first_or_404()
    
    try:
        custom_base = AppSetting.get('base_url', '').strip()
        base_url = custom_base if custom_base else get_effective_base_url()
        new_video_url = f"{base_url.rstrip('/')}/video/{unique_id}"
        
        qr_rel_path, _ = generate_video_qr_code(
            video_url=new_video_url,
            unique_id=unique_id,
            qr_folder=current_app.config['QR_FOLDER'],
            style='modern'
        )
        
        video.video_url = new_video_url
        video.qr_code_path = qr_rel_path
        db.session.commit()
        
        flash(f'Regenerated QR code for "{video.title}" with URL: {new_video_url}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error regenerating QR code: {str(e)}', 'danger')
        
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Application settings page (Base URL / Domain, Password change)."""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_domain':
            new_base_url = request.form.get('base_url', '').strip().rstrip('/')
            AppSetting.set('base_url', new_base_url)
            flash('Base URL updated successfully. Newly generated QR codes will use this URL.', 'success')
            
        elif action == 'change_password':
            current_pass = request.form.get('current_password', '')
            new_pass = request.form.get('new_password', '')
            confirm_pass = request.form.get('confirm_password', '')
            
            admin = Admin.query.get(session.get('admin_id'))
            if not admin or not admin.check_password(current_pass):
                flash('Current password is incorrect.', 'danger')
            elif len(new_pass) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
            elif new_pass != confirm_pass:
                flash('New password and confirmation do not match.', 'danger')
            else:
                admin.set_password(new_pass)
                db.session.commit()
                flash('Admin password changed successfully!', 'success')
                
        return redirect(url_for('admin.settings'))

    current_base = AppSetting.get('base_url', current_app.config.get('BASE_URL', ''))
    local_ip = get_local_ip()
    port = request.environ.get('SERVER_PORT', '5000')
    suggested_lan_url = f"http://{local_ip}:{port}"
    
    return render_template(
        'admin/settings.html',
        current_base=current_base,
        local_ip=local_ip,
        suggested_lan_url=suggested_lan_url
    )
