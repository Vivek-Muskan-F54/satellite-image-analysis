import pytest
import os
import io
from app.storage.local import LocalStorageService
from app.storage.cloud import S3StorageService
from fastapi import HTTPException

# --- Local Storage Tests ---
def test_local_storage_save_and_get(tmp_path):
    storage = LocalStorageService(base_dir=str(tmp_path))
    file_data = b"test file content"
    file_obj = io.BytesIO(file_data)
    
    storage_key = "users/user123/images/img1.jpg"
    returned_key = storage.save(file_obj, storage_key, "image/jpeg")
    assert returned_key == storage_key
    assert storage.exists(storage_key)
    
    # Check physical file
    assert os.path.exists(os.path.join(tmp_path, "users/user123/images/img1.jpg"))
    
    # Get
    retrieved_obj = storage.get(storage_key)
    assert retrieved_obj.read() == file_data

def test_local_storage_path_traversal(tmp_path):
    storage = LocalStorageService(base_dir=str(tmp_path))
    file_obj = io.BytesIO(b"test")
    
    with pytest.raises(HTTPException):
        storage.save(file_obj, "../../../outside.jpg", "image/jpeg")
        
def test_local_storage_delete(tmp_path):
    storage = LocalStorageService(base_dir=str(tmp_path))
    storage_key = "test_delete.jpg"
    storage.save(io.BytesIO(b"test"), storage_key, "image/jpeg")
    
    assert storage.exists(storage_key)
    assert storage.delete(storage_key) is True
    assert not storage.exists(storage_key)

# --- S3 Storage Tests (Mocked) ---
def test_s3_storage_save(mocker):
    # Mock settings
    mocker.patch('app.storage.cloud.settings.S3_BUCKET', 'test-bucket')
    mocker.patch('app.storage.cloud.settings.S3_ENDPOINT_URL', None)
    mocker.patch('app.storage.cloud.settings.S3_REGION', 'us-east-1')
    mocker.patch('app.storage.cloud.settings.S3_ACCESS_KEY_ID', 'test')
    mocker.patch('app.storage.cloud.settings.S3_SECRET_ACCESS_KEY', 'test')
    
    mock_boto_client = mocker.patch('boto3.client')
    s3_client_instance = mock_boto_client.return_value
    
    storage = S3StorageService()
    
    file_obj = io.BytesIO(b"s3 content")
    object_key = "users/123/img.png"
    
    returned_key = storage.save(file_obj, object_key, "image/png")
    assert returned_key == object_key
    
    # Verify boto3 was called correctly
    s3_client_instance.upload_fileobj.assert_called_once_with(
        file_obj,
        'test-bucket',
        object_key,
        ExtraArgs={'ContentType': 'image/png'}
    )

def test_s3_storage_delete(mocker):
    mocker.patch('app.storage.cloud.settings.S3_BUCKET', 'test-bucket')
    mock_boto_client = mocker.patch('boto3.client')
    s3_client_instance = mock_boto_client.return_value
    
    storage = S3StorageService()
    
    result = storage.delete("test.jpg")
    assert result is True
    
    s3_client_instance.delete_object.assert_called_once_with(Bucket='test-bucket', Key="test.jpg")
