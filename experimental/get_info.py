import os
from datetime import datetime, timedelta
from tinkoff.invest import Client, CandleInterval
from figi import L

TOKEN = os.environ.get("TINKOFF_TOKEN")

def main():
    with Client(TOKEN) as client:
        info = (
            client.instruments.currencies()
        )  # currencies() - валюта, futures() - фьючерсы
        for i in info.instruments:
            if i.currency == "rub":
                print(i.ticker, i.figi, i.name)
                for every in L:
                    if every["figi"] == i.figi:
                        every["name"] = i.name
        print(L)

def main01():
    ''' Выводит доступный список валют'''
    with Client(TOKEN) as client:
        info = (
            client.instruments.currencies()
        )  # currencies() - валюта, futures() - фьючерсы
        for i in info.instruments:
                print(i.ticker, i.figi, i.name)



def main1():
    with Client(TOKEN) as client:
        gen_candles = client.get_all_candles(
            figi="BBG004730N88",
            from_=datetime.utcnow() - timedelta(days=2),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR,
        )
        candles = [i for i in gen_candles]
        print(candles)
        return candles


def main2():
    with Client(TOKEN) as client:
        response = client.users.get_accounts()
        accounts = [account.id for account in response.accounts]
        res = client.operations.get_portfolio(account_id=accounts[0])
        print(res)


if __name__ == "__main__":
    main()
