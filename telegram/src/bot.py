import asyncio
import http.server
import json
import logging
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from jinja2 import Template
from motor.motor_asyncio import AsyncIOMotorClient
from web3 import Web3

from listener import log_loop
from constants import BOT_API_TOKEN, MONGODB_HOST, WEB3_PROVIDER_URL, CONTRACT_ADDRESS
from web3_ import register_wallet, get_balance, contract_json, contract, withdrawal

logging.basicConfig(level=logging.INFO)


bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher(bot)
db_client = AsyncIOMotorClient(host=MONGODB_HOST)["crypto_wallet_bot"]


async def _send_text(message, text, markup=None):
    await bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )


@dp.message_handler(commands="make_link")
async def make_link_handler(message: types.Message):
    *_, name, amount, buyer_id = message.text.split(" ")

    wallet = await db_client.wallet.find_one({"tg_id": message.chat.id, "name": name})
    await _send_text(
        message,
        f"http://127.0.0.1:8080/?external_key={wallet['external_key']}&"
        f"amount={amount}&buyer_id={buyer_id}",
    )


@dp.message_handler(commands="withdrawal")
async def withdrawal_handler(message: types.Message):
    *_, name, amount, address = message.text.split(" ")

    wallet = await db_client.wallet.find_one({"tg_id": message.chat.id, "name": name})
    th = withdrawal(wallet["private_key"], Web3.toWei(float(amount), "ether"), address)
    await _send_text(message, f"Ok, it has already done: <code>{th.hex()}</code>")


@dp.message_handler(commands="new_wallet")
async def new_wallet_handler(message: types.Message):
    *_, name, external_key, private_key = message.text.split(" ")

    await db_client.wallet.update_one({"tg_id": message.chat.id, "name": name}, {"$set" :{
        "external_key": external_key,
        "private_key": private_key,
    }}, upsert=True)
    th = register_wallet(external_key, private_key)

    await _send_text(
        message,
        f"Ok, it seems to me that everything is alright! I did a request to a "
        f"blockchain network and it told me: \n<code>{th.hex()}<code>",
    )


@dp.message_handler(commands="my_wallets")
async def my_wallets_handler(message: types.Message):
    cursor = db_client.wallet.find({"tg_id": message.chat.id})
    wallets = []
    async for data in cursor:
        data["balance"] = get_balance(data["external_key"])
        wallets.append(data)

    await _send_text(
        message,
        "Your wallets and their balances:\n\n" + "\n".join(
            [f"Name: {w['name']}\nBalance: <b>{w['balance']}</b> ETH" for w in wallets]
        ),
    )


@dp.message_handler()
async def base_handler(message: types.Message):
    await _send_text(
        message,
        "Hi there! I'm a crypto bot wallet. I can receive eth from any metamask wallet and then to call your webhook.\n\n"
        "to create new wallet, let's type:\n"
        " <code>/new_wallet :name: :external_key: :private_key:</code>\n\n"
        "to get your wallets:\n"
        "/my_wallets\n\n"
        "to make a deposit link:\n"
        "<code>/make_link :wallet_name: :amount: :buyer_id:</code>\n\n"
        "to withdraw from wallet, let's go:\n"
        "<code>/withdrawal :name: :amount: :address:</code>",
    )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # start a webserver for serving of deposit.html
    class Server(http.server.SimpleHTTPRequestHandler) :
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            query = urlparse(self.path).query
            query = {qc.split("=")[0]: qc.split("=")[1] for qc in query.split("&") if qc}
            if not query:
                return
            with open("deposit.html", "r") as template:
                self.wfile.write(bytes(
                    Template(template.read()).render(
                        web3_provider_url=WEB3_PROVIDER_URL,
                        contract_address=CONTRACT_ADDRESS,
                        abi_json=json.dumps(contract_json["abi"]),
                        value=Web3.toWei(float(query["amount"]), "ether"),
                        buyer_id=query["buyer_id"],
                        external_key=query["external_key"]
                    ), "UTF-8"
                ))
    server = http.server.HTTPServer(('', 8080), Server)
    loop.run_in_executor(None, server.serve_forever)

    # start a listener for getting information about new deposits
    event_filter = contract.events.Deposit.createFilter(fromBlock='latest')
    loop = asyncio.get_event_loop()
    loop.create_task(log_loop(event_filter, 2))

    # start a telegram bot
    executor.start_polling(dp, skip_updates=True)
