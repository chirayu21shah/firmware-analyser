import os

from flask import current_app, jsonify, Blueprint, request

from app.services.analyser import analyze_firmware, extract_archive


analyse_bp = Blueprint('analyse_bp', __name__)

TEMP_DIR = 'temp_firmware'
@analyse_bp.route('/analyse', methods=['POST'])
def analyse():
    firmware = request.files.get('firmware')

    if not firmware:
        return jsonify({'error': 'No firmware file provided'}), 400
    
    job_manager = current_app.extensions['job_manager']
    job_id = job_manager.create_job(firmware)

    return jsonify({
        'job_id': str(job_id),
        'message': 'Firmware analysis started'
    }), 202


@analyse_bp.route('/analyse/<job_id>', methods= ['GET'])
def get_analysis_result(job_id):
    job_manager = current_app.extensions['job_manager']

    job = job_manager.get_job(job_id)


    if not job:
        return jsonify({'error': 'Job not found'}), 404 
    
    if job['status'] == 'completed':
        return jsonify({
            'job_id' : str(job_id),
            'status': job['status'],
            'result': job['result']
        }), 200
    
    if job['status'] == 'failed':
        return jsonify({
            'job_id': str(job_id),
            'status': job['status'],
            'error': job['error']
        }), 500
    
    return jsonify({
        'job_id': str(job_id),
        'status': job['status'],
        'message': 'Analysis in progress'}), 200