import MetaTrader5 as mt5

if not mt5.initialize():
    print("Initialization failed")
    print(mt5.last_error())
    quit()

tick = mt5.symbol_info_tick("EURUSD")

print(tick)

mt5.shutdown()
