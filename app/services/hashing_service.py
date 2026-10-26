import hashlib
import os


class HashingService:
    """
    Cryptographic Hashing Service.
    Generates SHA-256 fingerprints of file byte content using streaming chunks.
    Guarantees consistent content-based identification regardless of filenames.
    """

    CHUNK_SIZE = 64 * 1024  # 64 KB chunk size for memory efficiency

    @classmethod
    def calculate_sha256(cls, file_stream):
        """
        Calculates the SHA-256 hash and size of a file-like object in binary mode.
        Streams in chunks so memory consumption remains O(1) regardless of file size.
        Resets the stream pointer to 0 upon completion.

        Args:
            file_stream: A binary file stream (e.g., FileStorage.stream or open file handle).

        Returns:
            tuple: (sha256_hex: str, total_bytes: int)

        Raises:
            ValueError: If file is empty or cannot be read.
        """
        if file_stream is None:
            raise ValueError("File stream cannot be None.")

        # Ensure we start from the beginning
        file_stream.seek(0)
        hasher = hashlib.sha256()
        total_bytes = 0

        while True:
            chunk = file_stream.read(cls.CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
            total_bytes += len(chunk)

        # Reset stream position to beginning so downstream uploaders can read it
        file_stream.seek(0)

        if total_bytes == 0:
            raise ValueError("Cannot calculate hash for an empty (0 bytes) file.")

        return hasher.hexdigest().lower(), total_bytes

    @classmethod
    def calculate_file_path_sha256(cls, file_path):
        """
        Calculates SHA-256 hash directly from a filesystem path.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            return cls.calculate_sha256(f)
