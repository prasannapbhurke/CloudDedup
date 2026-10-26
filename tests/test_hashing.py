import io
import pytest
import hashlib
from app.services.hashing_service import HashingService


def test_sha256_hash_calculation():
    """Test standard SHA-256 chunked calculation against known standard hash."""
    test_content = b"Cloud computing microproject deduplication test content."
    expected_hash = hashlib.sha256(test_content).hexdigest()

    stream = io.BytesIO(test_content)
    calculated_hash, size = HashingService.calculate_sha256(stream)

    assert calculated_hash == expected_hash
    assert size == len(test_content)


def test_identical_content_different_filenames():
    """Test that identical content produces identical hashes regardless of filename."""
    content = b"Identical binary bytes for assignment 10MB test"

    stream1 = io.BytesIO(content)
    hash1, _ = HashingService.calculate_sha256(stream1)

    stream2 = io.BytesIO(content)
    hash2, _ = HashingService.calculate_sha256(stream2)

    assert hash1 == hash2


def test_different_content_produces_different_hashes():
    """Test that modifying content changes the fingerprint."""
    stream1 = io.BytesIO(b"Original file contents v1.0")
    hash1, _ = HashingService.calculate_sha256(stream1)

    stream2 = io.BytesIO(b"Modified file contents v1.1")
    hash2, _ = HashingService.calculate_sha256(stream2)

    assert hash1 != hash2


def test_empty_file_handling():
    """Test that empty 0-byte streams raise ValueError."""
    empty_stream = io.BytesIO(b"")
    with pytest.raises(ValueError):
        HashingService.calculate_sha256(empty_stream)
