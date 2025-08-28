import os
from dotenv import load_dotenv
import aiohttp
import requests
import asyncio
import json
from decimal import Decimal, getcontext





load_dotenv()
api_key = os.getenv('aml_api_key')
blockchair_api = os.getenv('blockchair_api')
eth_api = os.getenv('eth_api')



# Асинхронная функция для проверки адреса
async def check_address(address: str, network: str):
    """
    Проверяет адрес на соответствие AML-регламентам.

    :param address: Блокчейн-адрес для проверки.
    :param network: Сеть (например, "mainnet").
    :return: Ответ от API в формате JSON.
    """
    url = "https://api.quppyaml.com/v1/checks/addresses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "address": address,
        "network": network
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Ошибка: {response.status}, {await response.text()}")
                return None


# Асинхронная функция для получения информации о проверке по ID
async def get_check_by_id(check_id: str):
    """
    Получает информацию о проверке по её ID.

    :param check_id: ID проверки.
    :return: Ответ от API в формате JSON.
    """
    if not isinstance(check_id, str):
        raise ValueError("check_id должен быть строкой")

    url = f"https://api.quppyaml.com/v1/checks/{check_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Ошибка: {response.status}, {await response.text()}")
                return {"error": f"Ошибка API: {await response.text()}"}


# Асинхронная функция для проверки транзакции
async def check_transaction(network: str, token_id: str, tx_hash: str, output_address: str, direction: str):
    """
    Проверяет транзакцию на соответствие AML-регламентам.

    :param network: Сеть (например, "mainnet").
    :param token_id: ID токена (например, "NATIVE" для нативных токенов).
    :param tx_hash: Хэш транзакции.
    :param output_address: Адрес получателя.
    :param direction: Направление транзакции ("incoming" или "outgoing").
    :return: Ответ от API в формате JSON.
    """
    url = "https://api.quppyaml.com/v1/checks/transfers"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "network": network,
        "token_id": token_id,
        "tx_hash": tx_hash,
        "output_address": output_address,
        "direction": direction
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Ошибка: {response.status}, {await response.text()}")
                return None


# Асинхронная функция для получения списка сетей
async def get_networks(action: str):
    """
    Возвращает список всех поддерживаемых сетей.

    :return: Список сетей.
    """
    # url = "https://api.quppyaml.com/v1/basic/networks"
    # headers = {
    #     "Authorization": f"Bearer {api_key}",
    #     "Content-Type": "application/json"
    # }

    # async with aiohttp.ClientSession() as session:
    #     async with session.get(url, headers=headers) as response:
    #         if response.status == 200:
    #             data = await response.json()
    #             return [network["code"] for network in data]
    #         else:
    #             print(f"Ошибка: {response.status} - {await response.text()}")
    #             return []

    if action == 'address':
        networks = [
            ("Tron", "TRX"),          # TRX
            ("Ethereum", "ETH"),      # ETH
            ("Bitcoin", "BTC"),       # BTC
            ("Litecoin", "LTC"),      # LTC
            ("Bitcoin Cash", "BCH"),  # BCH
            ("Avalanche", "AVAX"),    # AVAX
            ("NEAR Protocol", "NEAR"),# NEAR
            ("Polygon", "MATIC"),     # MATIC
            ("Solana", "SOL"),        # SOL
            ("Arbitrum", "ARB"),      # ARB
            ("Optimism", "OP"),       # OP
            ("The Open Network", "TON"),  # TON
            ("Binance Smart Chain", "BSC")  # BSC
        ]
    else:
        networks = [
            ("Tron", "TRX"),          # TRX
            ("Ethereum", "ETH"),      # ETH
            ("Bitcoin", "BTC"),       # BTC
            ("Litecoin", "LTC"),      # LTC
        ]

    return networks


# Асинхронная функция для получения токенов
async def get_tokens(network: str):
    """
    Возвращает список токенов для указанной сети в формате кортежей (tokenId, symbol, name).

    :param network: Сеть (например, "mainnet").
    :return: Список кортежей (tokenId, symbol, name).
    """
    url = f"https://api.quppyaml.com/v1/basic/tokens?network={network}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                # print(data)
                tokens = data.get("tokens", [])
                return [
                    (token.get("tokenId"), token.get("symbol"), token.get("name"))
                    for token in tokens
                ]
            else:
                print(f"Ошибка: {response.status} - {await response.text()}")
                return []


# Асинхронная функция для получения токенов
async def get_token_by_symbol(symbol: str, network: str):
    """
    Возвращает информацию о токене по его символу в указанной сети.

    :param symbol: Символ токена (например, "BTC").
    :param network: Сеть (например, "mainnet").
    :param api_key: API-ключ для авторизации.
    :return: Словарь с информацией о токене или None, если токен не найден.
    """
    url = f"https://api.quppyaml.com/v1/basic/tokens"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "network": network,
        "symbol": f'${symbol}'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                tokens = data.get("tokens", [])

                # Поиск токена по символу
                for token in tokens:
                    # print(token.get("symbol"))
                    if token.get("symbol") == f"${symbol}":
                        # Возвращаем словарь с информацией о токене
                        return {
                            "tokenId": token.get("tokenId"),
                            "symbol": token.get("symbol"),
                            "name": token.get("name"),
                            "network": network,
                            # Добавьте другие поля, если они есть в ответе
                        }

                # Если токен не найден
                print(f"Токен с символом '{symbol}' не найден.")
                return None
            else:
                print(f"Ошибка: {response.status} - {await response.text()}")
                return None



async def get_token_symbol(hash: str, network: str):
    """
    Возвращает symbol токена для указанной транзакции.

    :param hash: Хеш транзакции.
    :param network: Сеть (например, "TRON", "ETH", "BSC", "POLYGON").
    :return: Symbol токена или None, если не удалось извлечь.
    """
    # Словарь с URL и параметрами для каждой сети

    network_config = {
        "TRX": {
            "url": f"https://apilist.tronscanapi.com/api/transaction-info?hash={hash}",
            "params": {}  # Дополнительные параметры, если нужны
        },
        "ETH": {
            "url": f"https://api.blockchair.com/ethereum/dashboards/transaction/{hash}?erc_20=true",
            "params": {}  # Дополнительные параметры, если нужны
        },
        "LTC": {
            "url": f"https://api.bscscan.com/api?module=proxy&action=eth_getTransactionByHash&txhash={hash}&apikey=YourApiKeyToken",
            "params": {}  # Дополнительные параметры, если нужны
        },
        "POLYGON": {
            "url": f"https://api.polygonscan.com/api?module=proxy&action=eth_getTransactionByHash&txhash={hash}&apikey=YourApiKeyToken",
            "params": {}  # Дополнительные параметры, если нужны
        }
    }

    # Проверяем, поддерживается ли сеть
    if network not in network_config:
        print(f"Сеть '{network}' не поддерживается.")
        return None

    # Получаем конфигурацию для сети
    config = network_config[network]
    url = config["url"]
    params = config.get("params", {})

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:

                if network == "LTC":
                    return "LTC"

                data = await response.json()

                # Запись данных в файл с отступами (для отладки)
                with open(f"transaction_info_{network}.json", "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)

                # Обработка данных в зависимости от сети
                if network == "TRX":
                    # Извлекаем symbol из trc20TransferInfo или transfersAllList
                    trc20_transfers = data.get("trc20TransferInfo", [])
                    transfers_all = data.get("transfersAllList", [])

                    # Ищем symbol в trc20TransferInfo
                    if trc20_transfers:
                        return trc20_transfers[0].get("symbol")

                    # Ищем symbol в transfersAllList
                    if transfers_all:
                        return transfers_all[0].get("symbol")

                    # Если symbol не найден
                    print("Symbol токена не найден в данных транзакции.")
                    return None
                
                elif network == "ETH":

                    print(data)
                    # address_info = f'https://api.etherscan.io/v2/api?chainid=1&module=token&action=tokeninfo&contractaddress={address}&apikey={api_key}'

                    # Извлекаем symbol из trc20TransferInfo или transfersAllList

                    # Если symbol не найден
                    print("Symbol токена не найден в данных транзакции.")
                    return None

                # Для других сетей пока возвращаем None (можно добавить логику позже)
                else:
                    print(f"Логика для сети '{network}' пока не реализована.")
                    return None

            else:
                print(f"Ошибка: {response.status} - {await response.text()}")
                return None




# Пример использования асинхронных функций
# async def main():
#     network = 'ETH'
#     # hash = 'ddfea581f0f9d228cc6eb0bbf01279318e9b2e094ab9c89e1a863b7c53c95635'
#     hash = '0x9ac51754d5ec64ef95bf17ae5a0a82fea76cdb20ea151310c022b0374a22fe33'
#     symbol = await get_token_symbol(hash=hash, network=network)

#     # result = await get_token(hash=hash, network=network)
#     result = await get_token_by_symbol(symbol=symbol, network=network)
#     print(result)


# # Запуск асинхронного кода
# if __name__ == "__main__":
#     asyncio.run(main())