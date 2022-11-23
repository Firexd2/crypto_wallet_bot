import json

from web3 import Web3

from constants import WEB3_PROVIDER_URL, CONTRACT_ADDRESS, MAIN_ACCOUNT_ADDRESS

web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

with open("../blockchain/build/contracts/Wallet.json", "r") as file:
    contract_json = json.loads(file.read())

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_json["abi"]) # noqa


def register_wallet(external_key, private_key):
    return contract.functions.registerWallet(external_key, private_key).transact({"from": MAIN_ACCOUNT_ADDRESS})


def withdrawal(private_key, value, address):
    return contract.functions.withdrawal(private_key, value, address).transact({"from": MAIN_ACCOUNT_ADDRESS})


def get_balance(external_key):
    return Web3.fromWei(contract.functions.getBalance(external_key).call(), "ether")
