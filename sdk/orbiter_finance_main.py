import asyncio
from loguru import logger
import aiohttp
from sdk.excel import Excel


async def excel_write(address: str, quantity: int, number: int):
    Excel.sheet[f'A{number+1}'] = address
    Excel.sheet[f'B{number+1}'] = quantity


async def get_response(response):
    return await response.json()


async def request_(address: str, number: int, json_data):

    async with aiohttp.ClientSession() as session:
        try:

            response = await session.post('https://openapi.orbiter.finance/explore/v3/yj6toqvwh1177e1sexfy0u1pxx5j8o47', json=json_data)
            token_1 = await get_response(response)
            await excel_write(address=address, quantity=len(token_1['result']['list']), number=number)

        except Exception as e:
            logger.error(f'Ошибка: {e}')


async def get_eligible(wallets: list):

    tasks = []
    logger.info(f'Найдено {len(wallets)} кошельков')
    for address in wallets:

        json_data = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'orbiter_getTransactionByAddress',
            'params': [
                address,
                1000,
                1,
            ],
        }

        tasks.append(asyncio.create_task(request_(address, wallets.index(address)+1, json_data)))

    await asyncio.gather(*tasks)


def main_check(wallets: list):
    Excel()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_eligible(wallets))
        loop.close()

    except:
        logger.error('Проблема с указанием кошелька(ов)')


    Excel.workbook.save('results/result.xlsx')