import aiohttp
import asyncio

BASE_URL = "https://api.quppyaml.com/v1/basic/tokens"
API_KEY = "NzNkZjk1OWRhNWRhYjBlODM0ZDQzMzVkYjdkMmFjZDQ1OWQ0YzRhMGIxYjFmNjdlYjQzNmQwZWExNDk3Yjg2Zg"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

async def fetch_all_tokens():
    """
    Асинхронно получает все токены из API.
    """
    page = 1
    network = 'ETH'
    all_tokens = []

    async with aiohttp.ClientSession() as session:
        while True:
            params = {"page": page, "network": network}
            async with session.get(BASE_URL, headers=headers, params=params) as response:
                if response.status != 200:
                    print(f"Ошибка {response.status}: {await response.text()}")
                    break

                data = await response.json()
                tokens = data.get("tokens", [])  # Получаем список токенов
                all_tokens.extend(tokens)  # Добавляем токены в общий список

                print(f"Страница {page}: {len(tokens)} токенов")

                # Проверяем, есть ли еще страницы
                if page >= data.get("total_pages", 1):
                    break

                page += 1  # Переходим к следующей странице

    return all_tokens

async def check_transaction(network: str, token_id: str, tx_hash: str, output_address: str, direction: str, stop_event: asyncio.Event):
    """
    Асинхронно проверяет транзакцию на соответствие AML-регламентам.
    """
    url = "https://api.quppyaml.com/v1/checks/transfers"
    payload = {
        "network": network,
        "token_id": token_id,
        "tx_hash": tx_hash,
        "output_address": output_address,
        "direction": direction
    }

    async with aiohttp.ClientSession() as session:
        while not stop_event.is_set():  # Проверяем, не нужно ли остановиться
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    print(f"Ошибка: {response.status}, {await response.text()}")
                    return None

                result = await response.json()
                check_status = result.get("check_status")

                if check_status == "checked":
                    print(f"Транзакция проверена для токена {token_id}: {result}")
                    return result
                elif check_status == "checking":
                    print(f"Транзакция проверяется для токена {token_id}. Останавливаем другие задачи...")
                    stop_event.set()  # Останавливаем все задачи
                    return result
                else:
                    print(f"Неизвестный статус проверки для токена {token_id}: {result}")
                    return result

            # Уменьшаем время ожидания между запросами
            await asyncio.sleep(1)  # Ждем 1 секунду вместо 5

async def process_tokens(tokens, tx_hash, output_address, direction):
    """
    Асинхронно обрабатывает список токенов и проверяет транзакции.
    """
    stop_event = asyncio.Event()  # Событие для остановки задач
    tasks = []

    # Ограничиваем количество токенов для проверки (например, первые 50)

    for token in tokens:
        network = token.get("network", "N/A")
        token_id = token.get("tokenId", "N/A")
        symbol = token.get("symbol", "N/A")
        name = token.get("name", "N/A")

        print(f"\nПроверка транзакции для токена: {symbol} ({name}, ID: {token_id})")

        # Создаем задачу для проверки транзакции
        task = asyncio.create_task(
            check_transaction(network, token_id, tx_hash, output_address, direction, stop_event)
        )
        tasks.append(task)

    # Ожидаем завершения всех задач с таймаутом 20 секунд
    try:
        await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=120)
    except asyncio.TimeoutError:
        print("Время выполнения превысило 20 секунд. Останавливаем задачи...")
        stop_event.set()  # Останавливаем все задачи

async def main():
    # Получаем все токены
    tokens = await fetch_all_tokens()
    print(f"\nВсего токенов получено: {len(tokens)}")

    # Пример данных для проверки транзакции
    tx_hash = "0x79101405fe8799629ea264d12aae64300401aa717922c9d0ee4683b359e4fb26"
    output_address = "0x391E7C679d29bD940d63be94AD22A25d25b5A604"
    direction = "outgoing"  # или "incoming"

    # Проверяем транзакцию для каждого токена
    await process_tokens(tokens, tx_hash, output_address, direction)

# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())