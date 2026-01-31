import asyncio
from fastapi import APIRouter
from loguru import logger
from src.core import dependencies

router = APIRouter(
    prefix="/asr",
    tags=["ASR"]
)

@router.post("/restart")
async def restart_asr():
    """Restart ASR processor with latest hotwords."""
    logger.info("Received request to restart ASR")
    try:
        # Get hotwords from DataService
        hotwords = dependencies.data_service.get_all_hotwords()
        logger.info(f"Loaded {len(hotwords)} hotwords from data service")
        
        if dependencies.asr_processor:
             # Update settings
            dependencies.asr_processor.settings.hotwords = hotwords
            
            # Re-initialize
            await dependencies.asr_processor.initialize()
            
            return {
                "success": True, 
                "message": f"ASR restarted successfully with {len(hotwords)} hotwords",
                "hotwords_count": len(hotwords)
            }
        else:
            return {"success": False, "message": "ASR processor not initialized"}
            
    except Exception as e:
        logger.exception("Failed to restart ASR")
        return {"success": False, "message": f"Failed to restart ASR: {str(e)}"}
