import os
import io
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
import tempfile

import torch
import soundfile as sf
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Security
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from whosper import WhosperTranscriber
from transformers import VitsModel, AutoTokenizer as VitsTokenizer
from huggingface_hub import login

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set. Please ensure it is injected via Secret Manager.")

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify the API key provided in the request header."""
    if api_key != API_KEY:
        logger.warning("Failed authentication attempt with invalid API key.")
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

ml_models: Dict[str, Any] = {}
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Diagnostic logging for GPU detection
logger.info(f"PyTorch version: {torch.__version__}")
logger.info(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    logger.info(f"CUDA version: {torch.version.cuda}")
    logger.info(f"GPU count: {torch.cuda.device_count()}")
    logger.info(f"Current GPU: {torch.cuda.get_device_name(0)}")
else:
    logger.warning("CUDA not available - checking for common issues...")
    try:
        logger.info(f"CUDA version (if available): {torch.version.cuda}")
    except:
        logger.info("CUDA version not available in PyTorch build")
    logger.warning("No GPU detected, falling back to CPU. Performance will be degraded.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        try:
            logger.info("Logging into Hugging Face Hub...")
            login(token=hf_token)
        except Exception as e:
            logger.error(f"HF Login failed: {e}")
    else:
        logger.warning("HF_TOKEN environment variable not set. Some models may be inaccessible.")

    logger.info("Loading ASR model (sudoping01/bambara-asr-v2)...")
    try:
        ml_models["asr"] = WhosperTranscriber(model_id="sudoping01/bambara-asr-v2")
    except Exception as e:
        logger.error(f"Failed to load ASR model: {e}. Transcription will be unavailable.")
        ml_models["asr"] = None

    if DEVICE == "cuda":
        logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
    else:
        logger.warning("No GPU detected, falling back to CPU. Performance will be degraded.")
        
    logger.info(f"Loading TTS model (facebook/mms-tts-bam) on {DEVICE}...")
    try:
        ml_models["tts"] = VitsModel.from_pretrained("facebook/mms-tts-bam").to(DEVICE)
        ml_models["tts_tokenizer"] = VitsTokenizer.from_pretrained("facebook/mms-tts-bam")
    except Exception as e:
        logger.error(f"Failed to load TTS model: {e}")
        raise

    logger.info("All models loaded successfully.")
    
    yield  
    
    logger.info("Shutting down and cleaning up models...")
    ml_models.clear()

app = FastAPI(
    title="Bambara TTS & ASR API",
    description="API for Bambara Speech-to-Text and Text-to-Speech",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize into speech", examples=["I ni ce"])

class TranscriptionResponse(BaseModel):
    transcription: str
    processing_time: float

@app.post("/transcribe", response_model=TranscriptionResponse, dependencies=[Depends(verify_api_key)])
async def transcribe(audio: UploadFile = File(...)):
    """
    Transcribe audio in Bambara to text.
    """
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        logger.warning(f"Invalid content type received: {audio.content_type}")
        raise HTTPException(status_code=400, detail="File provided is not an audio file")

    logger.info(f"Received audio file for transcription: {audio.filename}")
    
    try:
        start_time = time.time()
        audio_content = await audio.read()
        
        transcriber: WhosperTranscriber = ml_models["asr"]
        if transcriber is None:
            raise HTTPException(status_code=503, detail="ASR model is not loaded. Transcription is unavailable.")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_content)
            tmp_path = tmp_file.name

        try:
            transcription_result = transcriber.transcribe_audio(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        text: str
        if isinstance(transcription_result, str):
            text = transcription_result
        elif isinstance(transcription_result, dict) and "text" in transcription_result:
            text = transcription_result["text"]
        else:
            logger.error(f"ASR model returned unexpected type or format: {type(transcription_result)} - {transcription_result}")
            raise HTTPException(status_code=500, detail="ASR model returned an unexpected format for transcription.")
        
        duration = round(time.time() - start_time, 2)
        logger.info(f"Successfully transcribed audio in {duration}s.")
        
        return TranscriptionResponse(transcription=text, processing_time=duration)
    
    except Exception as e:
        logger.error(f"Error during transcription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during transcription")

@app.post("/synthesize", dependencies=[Depends(verify_api_key)])
async def synthesize(request: TTSRequest):
    """
    Synthesize Bambara text to speech.
    """
    logger.info(f"Received text for synthesis: {request.text}")
    
    try:
        tokenizer = ml_models["tts_tokenizer"]
        model = ml_models["tts"]
        
        inputs = tokenizer(request.text, return_tensors="pt").to(DEVICE)
        
        with torch.no_grad():
            output = model(**inputs).waveform
        
        waveform = output.squeeze().cpu().numpy()
        
        buffer = io.BytesIO()
        sf.write(buffer, waveform, model.config.sampling_rate, format='WAV')
        buffer.seek(0)
        
        logger.info(f"Successfully synthesized speech for text: {request.text[:30]}...")
        return StreamingResponse(buffer, media_type="audio/wav")
        
    except Exception as e:
        logger.error(f"Error during synthesis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during synthesis")

@app.get("/health")
def health():
    """
    Health check endpoint.
    """
    return {
        "status": "ready",
        "device": DEVICE,
        "asr_loaded": ml_models.get("asr") is not None,
        "tts_loaded": ml_models.get("tts") is not None
    }