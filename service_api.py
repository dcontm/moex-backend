import asyncio
import os
import time
from tinkoff.invest.utils import now
from tinkoff.invest import AsyncClient, LastPriceInstrument, CandleInterval
from tinkoff.invest.async_services import AsyncMarketDataStreamManager
from db import redis
from figi import L



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


async def stream_last_price(redis):
    await redis_init(redis)
    keys = await redis.keys()

    async with AsyncClient(TOKEN) as client:
        market_data_stream: AsyncMarketDataStreamManager = (
            client.create_market_data_stream()
        )
        market_data_stream.last_price.subscribe(
            [LastPriceInstrument(figi) for figi in keys]
        )
        async for marketdata in market_data_stream:
            try:
                key = marketdata.last_price.figi
                data = await redis.hgetall(key)
                data["time"] = time.mktime(marketdata.last_price.time.timetuple())
                data["price"] = round(
                    float(
                        f"{marketdata.last_price.price.units}.{marketdata.last_price.price.nano}"
                    ),
                    10,
                )
                await redis.hset(key, mapping=data)
            except AttributeError:
                pass


if __name__ == "__main__":
    asyncio.run(stream_last_price(redis))
