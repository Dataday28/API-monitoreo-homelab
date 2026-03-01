from __future__ import annotations

import asyncio
from pydantic import ValidationError
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from app.services.hardware import HardwareReader
from app.schemas.metrics import SystemMetricsSnapshot

router = APIRouter()

hw = HardwareReader(cpu_interval=0.2)

@router.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket) -> None:
    await websocket.accept()
    
    try:
        while True:
            raw = hw.snapshot()
            
            try:
                payload = SystemMetricsSnapshot.model_validate(raw)
                data = payload.model_dump()
                
                await websocket.send_json(data)
                
            except ValidationError as e:
                logging.error(f"Error de validación en los datos de hardware: {e}")
            
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        logging.warning("Cliente desconectado")
        return
    except asyncio.CancelledError:
        raise
    except Exception:
        logging.error(f"Error inesperado en WebSocket: {e}")
        try:
            await websocket.close(code=1011)
        except Exception:
            pass