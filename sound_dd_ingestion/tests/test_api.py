from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sound_dd_ingestion.app.main import app
from sound_dd_ingestion.app.services.storage_service import StorageService

client = TestClient(app)

# Mock S3 Upload to avoid actual AWS calls
@patch.object(StorageService, 'upload_file')
def test_audio_upload(mock_upload):
    mock_upload.return_value = "test/path.wav"
    
    # Create dummy WAV file (header only)
    # RIFF header + generic bytes
    dummy_wav = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00'
    
    response = client.post(
        "/api/v1/upload/audio",
        data={
            "device_id": "TEST_DEVICE_01",
            "latitude": 13.0,
            "longitude": 80.0
        },
        files={"file": ("test.wav", dummy_wav, "audio/wav")}
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "id" in json_data

def test_invalid_file_type():
    response = client.post(
        "/api/v1/upload/audio",
        data={"device_id": "dev", "latitude": 0, "longitude": 0},
        files={"file": ("test.txt", b"text data", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]