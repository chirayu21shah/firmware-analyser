import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_analyse_no_file(client):
    responce = client.post('/analyse')
    assert responce.status_code == 400
    assert responce.get_json() == {'error': 'No firmware file provided'}


def test_analyse_with_zip_file(client):
    with open('app\\tests\\fixtures\\test_firmware.zip', 'rb') as f:
        responce = client.post('/analyse',
                               data = {'firmware' : (f, 'test_firmware.zip')},
                               content_type='multipart/form-data')
    assert responce.status_code == 202
    json_data = responce.get_json()
    assert 'job_id' in json_data
    assert json_data['message'] == 'Firmware analysis started'

    job_id = json_data['job_id']
    # Poll for result
    for _ in range(20):
        responce = client.get(f'/analyse/{job_id}')
        assert responce.status_code == 200
        json_data = responce.get_json()

        if json_data['status'] == 'completed':
            assert 'result' in json_data
            break
        elif json_data['status'] == 'failed':
            assert 'error' in json_data
            break

def test_analyse_with_tar_file(client):
    with open('app\\tests\\fixtures\\test_firmware.tar', 'rb') as f:
        responce = client.post('/analyse',
                               data = {'firmware' : (f, 'test_firmware.tar')},
                               content_type='multipart/form-data')
    assert responce.status_code == 202
    json_data = responce.get_json()
    assert 'job_id' in json_data
    assert json_data['message'] == 'Firmware analysis started'

    job_id = json_data['job_id']
    # Poll for result
    for _ in range(20):
        responce = client.get(f'/analyse/{job_id}')
        assert responce.status_code == 200
        json_data = responce.get_json()

        if json_data['status'] == 'completed':
            assert 'result' in json_data
            break
        elif json_data['status'] == 'failed':
            assert 'error' in json_data
            break


def test_analyse_job_not_found(client):
    responce = client.get('/analyse/non_existent_job_id')

    assert responce.status_code == 404
    assert responce.get_json() == {'error': 'Job not found'}