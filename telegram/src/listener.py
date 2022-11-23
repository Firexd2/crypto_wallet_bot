from web3_ import Web3
import asyncio


def handle_event(event):
    print(Web3.toJSON(event))
    # and whatever


async def log_loop(event_filter, poll_interval):
    while True:
        for PairCreated in event_filter.get_new_entries():
            handle_event(PairCreated)
        await asyncio.sleep(poll_interval)
