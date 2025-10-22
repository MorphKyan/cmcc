# This file makes the component directory a Python package.

from src.module.vad.vad_processor import VADProcessor
from src.module.asr.asr_processor import ASRProcessor

__all__ = ["VADProcessor", "ASRProcessor"]
