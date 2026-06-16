from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import time
from uuid import uuid4
import os
import shutil

from app.services.analyser import analyze_firmware, extract_archive

TEMP_DIR = 'temp_firmware'

class JobManager:
    def __init__(self, max_workers=4):
        self.jobs = {}
        self.lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def create_job(self, firmware):
        job_id = str(uuid4())
        job_dir = os.path.join(TEMP_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)

        upload_path = os.path.join(job_dir, firmware.filename)
        csv_path = os.path.join(job_dir, 'output.csv')
        firmware.save(upload_path)


        job = {
            'id' : job_id,
            'status': 'pending',
            'upload_path': upload_path,
            'csv_path': csv_path,
            'filename': firmware.filename,
            'result': None,
            'created_at': time.time(),
            'updated_at': time.time(),
            'error': None
        }

        with self.lock:
            self.jobs[job_id] = job
        
        self.executor.submit(self.run_job, job_id)
        return job_id
    
    def run_job(self, job_id):
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return
            job['status'] = 'running'
        try:
            # Extract the firmware
            extracted_path = extract_archive(job['upload_path'], os.path.dirname(job['upload_path']))

            json_output = analyze_firmware(extracted_path, job['csv_path'])
            with self.lock:
                job['status'] = 'completed'
                job['result'] = json_output
                job['updated_at'] = time.time()
            self.clean_up_directory(job['upload_path'], job['csv_path'])
        except Exception as e:
            with self.lock:
                job['status'] = 'failed'
                job['error'] = str(e)
                job['updated_at'] = time.time()
            self.clean_up_directory(job['upload_path'], job['csv_path'], keep_csv=False)
    
    def get_job(self, job_id):
        with self.lock:
            return self.jobs.get(job_id)

    def clean_up_directory(self, upload_path, csv_path, keep_csv=True):
        job_dir = os.path.dirname(upload_path)

        for entry in os.listdir(job_dir):
            entry_path = os.path.join(job_dir, entry)

            if keep_csv and entry_path == csv_path:
                continue

            if os.path.isdir(entry_path):
                shutil.rmtree(entry_path, ignore_errors=True)
            else:
                try:
                    os.remove(entry_path)
                except FileNotFoundError:
                    pass
