import asyncio
import os
from figi import L
import time
from datetime import datetime, timedelta
from tinkoff.invest.utils import now
from db import redis


from tinkoff.invest import AsyncClient, LastPriceInstrument, CandleInterval
from tinkoff.invest.async_services import AsyncMarketDataStreamManager


TOKEN = os.environ.get("TINKOFF_TOKEN")


async def get_candles(figi, from_, interval):
    async with AsyncClient(TOKEN) as client:
        generator = client.get_all_candles(
            figi=figi,
            from_=now() - from_,  # datetime.utcnow()
            interval=CandleInterval[interval],
        )
        candles = [candle async for candle in generator]
        return candles


async def redis_init(redis):
    keys = await redis.keys()

    for item in L:
        if item["figi"] not in keys:
            await redis.hset(item["figi"], mapping=item)


# Функция предназначена для обновления данных о ценнах закрытия последних торгов
async def last_close_price(redis):
    await redis_init(redis)
    keys = await redis.keys()

    for key in keys:
        try:
            candles = await get_candles(key, timedelta(days=5), "CANDLE_INTERVAL_DAY")
            close = round(
                float(f"{candles[-1].open.units}.{candles[-1].open.nano}"), 10
            )
            share = await redis.hgetall(key)
            share["old_price"] = close
            await redis.hset(key, mapping=share)
            print(f"{key} set open day price {close}")
        except:
            print(f"Ошибка обновления {key}")


if __name__ == "__main__":
    asyncio.run(last_close_price(redis))
