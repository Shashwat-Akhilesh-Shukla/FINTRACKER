import asyncio
from pprint import pprint
from market_data_service import market_data_service


async def main():
    print("\n=== Testing search_symbols ===")
    symbols = await market_data_service.search_symbols("RELIANCE", exchange="NSE")

    test_symbol = "RELIANCE"

    print("\n=== Testing get_quote ===")
    quote = await market_data_service.get_quote(test_symbol, exchange="NSE")
    pprint(quote)

    print("\n=== Testing get_multiple_quotes ===")
    quotes = await market_data_service.get_multiple_quotes([test_symbol, "INFY", "RELIANCE"], exchange="NSE")
    pprint(quotes)

    print("\n=== Testing get_historical_data ===")
    hist = await market_data_service.get_historical_data(test_symbol, period="1y", exchange="NSE")
    pprint(hist[:5])  # show first 5 rows

    print("\n=== Closing service ===")
    await market_data_service.close()


if __name__ == "__main__":
    asyncio.run(main())
