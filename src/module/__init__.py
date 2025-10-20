# This file makes the component directory a Python package.

from src.module.speech_recognition.vad_processor import VADProcessor
from src.module.speech_recognition.asr_processor import ASRProcessor

__all__ = ["VADProcessor", "ASRProcessor"]
