import asyncio
import time
from datetime import timedelta
import random
from fastapi import WebSocket, APIRouter
from fastapi.encoders import jsonable_encoder
from db import redis, db
from service_api import get_candles
from . import models


router = APIRouter()


@router.websocket("/price/wss")
async def get_last_price(websocket: WebSocket):
    '''Непрерывное получение информации о текущих ценах
    на список торговых инструментов'''
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

@router.get("/")
async def get_shares_from_redis():
    '''Возвращает список торговых инстументов 
    доступных в redis '''
    shares_keys = await redis.keys()
    result = []
    for figi in shares_keys:
        item = await redis.hgetall(figi)
        result.append(item)
    return result

@router.post("/")
async def add_share(share: models.Share):
    '''Добавит новый торговый инструмент в redis
    обязательные поля figi, ticker, name'''
    shares_keys = await redis.keys()
    if share.figi not in shares_keys:
        added_share = await redis.hset(share.figi, mapping=share.dict())
        return share


@router.put("/{figi}/edit", response_model=models.Share)
async def edit_share(figi:str, share: models.Share):
    ''' Обновить поля торгового инструмента'''
    update_share_encoded = jsonable_encoder(share)
    await redis.hset(figi, mapping=update_share_encoded)
    return update_share_encoded

@router.delete("/{figi}", status_code=204)
async def delete_share(figi:str):
    ''' Удалить торговый интсрумент из redis'''
    await redis.delete(figi)
    return {'ok': True}

@router.get("/{figi}", response_model=models.ShareInfo)
async def get_share_by_figi(figi: str):
    '''Вернет справочую информацию о торговом 
    инструментк из mongoDB'''
    share = await db["shares"].find_one({"figi": figi}, {"_id": 0})
    return share


@router.get("/{figi}/candles")
async def get_int(figi: str, period: int, interval: str):
    '''Возращает информацию о ценах на торговый инструмент
    за выбранный переод времени в виде свечей(O,H,L,C)'''
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
