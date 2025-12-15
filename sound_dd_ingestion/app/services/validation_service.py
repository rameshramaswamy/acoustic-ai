from fastapi import UploadFile, HTTPException

class ValidationService:
    ALLOWED_MIME_TYPES = ["audio/wav", "audio/x-wav", "audio/flac"]
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    @staticmethod
    async def validate_audio_file(file: UploadFile):
        # 1. Check Content Type Header
        if file.content_type not in ValidationService.ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file type. Only WAV/FLAC allowed.")

        # 2. Check Magic Bytes (Sanitization)
        # Read first 4 bytes to ensure it's actually a RIFF file
        header = await file.read(4)
        await file.seek(0)  # Reset cursor
        
        if header != b'RIFF' and file.content_type != "audio/flac":
            raise HTTPException(status_code=400, detail="Malicious file detected. Header mismatch.")
        
        return True