import asyncio
import time
from datetime import timedelta
import random

from fastapi import WebSocket, APIRouter, Depends

from db import redis, db
from service_api import get_candles
from . import models


router = APIRouter()


@router.websocket("/price/wss")
async def get_last_price(websocket: WebSocket):
    keys = await redis.keys()
    await websocket.accept()
    while True:
        data = {}
        for figi in keys:
            item = await redis.hgetall(figi)
            try:
                item["color"] = (
                    "green"
                    if float(item["price"]) > float(item["old_price"])
                    else "red"
                )
            except:
                item["color"] = "grey"
            item["free_float"] = round((random.random() * 100), 2)
            data[figi] = item
        await asyncio.sleep(0.5)
        await websocket.send_json(data)


@router.get("/{figi}", response_model=models.ShareInfo)
async def get_share_by_figi(figi: str):
    share = await db["shares"].find_one({"figi": figi}, {"_id": 0})
    print(share)
    return share


@router.get("/{figi}/candles")
async def get_int(figi: str, period: int, interval: str):
    periods = {
        1: timedelta(hours=6),
        2: timedelta(hours=12),
        3: timedelta(days=10),
        4: timedelta(days=90),
    }

    candles = await get_candles(figi, periods[period], interval)
    for candle in candles:
        candle.open = round(float(f"{candle.open.units}.{candle.open.nano}"), 10)
        candle.high = round(float(f"{candle.high.units}.{candle.high.nano}"), 10)
        candle.low = round(float(f"{candle.low.units}.{candle.low.nano}"), 10)
        candle.close = round(float(f"{candle.close.units}.{candle.close.nano}"), 10)
        candle.time = str(candle.time)

    return candles
