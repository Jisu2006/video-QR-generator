from flask import Blueprint, jsonify, request, current_app
from app.models import Video, AppSetting
from app.utils.network_helper import get_local_ip

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/videos', methods=['GET'])
def get_videos():
    """Retrieve list of videos as JSON with optional search."""
    search_query = request.args.get('q', '').strip()
    query = Video.query.order_by(Video.created_at.desc())
    
    if search_query:
        query = query.filter(
            (Video.title.ilike(f'%{search_query}%')) |
            (Video.unique_id.ilike(f'%{search_query}%'))
        )
        
    videos = query.all()
    return jsonify({
        'status': 'success',
        'count': len(videos),
        'videos': [v.to_dict() for v in videos]
    })


@api_bp.route('/videos/<unique_id>', methods=['GET'])
def get_video_detail(unique_id):
    """Get metadata for a specific video."""
    video = Video.query.filter_by(unique_id=unique_id).first()
    if not video:
        return jsonify({'status': 'error', 'message': 'Video not found'}), 404
        
    return jsonify({
        'status': 'success',
        'video': video.to_dict()
    })


@api_bp.route('/system-info', methods=['GET'])
def system_info():
    """Get server network & configuration status."""
    local_ip = get_local_ip()
    base_url = AppSetting.get('base_url', current_app.config.get('BASE_URL', ''))
    
    return jsonify({
        'status': 'success',
        'local_ip': local_ip,
        'configured_base_url': base_url,
        'allowed_formats': list(current_app.config['ALLOWED_EXTENSIONS']),
        'max_upload_size_mb': current_app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
    })
