This is a light telegram bot of a crypto wallet
There are two main components:
- a smart contract (blockchain/contracts/wallet.sol)
- a telegram bot (telegram/src/bot.py)

**Shortly, it can do:**

*To create new wallet, let's type:*

/new_wallet :name: :external_key: :private_key:

*To get your wallets:*

/my_wallets

*To make a deposit link:*

/make_link :wallet_name: :amount: :buyer_id:

*To withdraw from wallet, let's go:*

/withdrawal :name: :amount: :address:

**To run locally, you need to do:**
- to run network locally, for example Ganache
- to change telegram/src/constants.py
- to run: truffle migrate --reset --network development
- to install poetry and everything from poetry.lock
- to run bot: python src/bot.py