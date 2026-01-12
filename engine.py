import time
from decimal import Decimal
from WhaleTracker import BlockchainService
import config
import db
from notifier import notify

def scan_once():
    providers = {
        chain: BlockchainService(url, chain) 
        for chain, url in config.SUPPORTED_CHAINS.items() if url
    }
    
    if not providers:
        return

    wallets = db.get_all_wallets()
    for w in wallets:
        svc = providers.get(w.chain)
        if not svc:
            continue

        try:
            eth_bal = svc.get_eth_balance(w.address)
            if eth_bal is not None:
                db.log_event(w.address, w.label, w.chain, "ETH", Decimal(eth_bal), Decimal(eth_bal))
                if eth_bal >= w.eth_threshold and w.last_eth_balance < w.eth_threshold:
                     notify(config.ALERT_CHANNELS, f"🚨 {w.label} [{w.chain}] Native Balance Alert: {eth_bal:.4f}", config)
        except Exception as e:
            print(f"Skipping {w.address}: {e}")
            eth_bal = None

        for sym, tsvc in svc.token_services.items():
            try:
                bal = tsvc.balance(w.address)
                if bal is None: continue
                
                db.log_event(w.address, w.label, w.chain, sym, Decimal(bal), Decimal(bal))
                if sym in ["USDT", "USDC", "DAI"] and bal >= w.usdt_threshold and w.last_usdt_balance < w.usdt_threshold:
                    notify(config.ALERT_CHANNELS, f"🚨 {w.label} [{w.chain}] {sym} High Balance: {bal:,.2f}", config)
            except Exception as e:
                print(f"Error reading token {sym}: {e}")

        if eth_bal is not None:
            usdt_service = svc.token_services.get("USDT")
            usdt_val = 0
            if usdt_service:
                try:
                    usdt_val = usdt_service.balance(w.address) or 0
                except: pass
            db.update_wallet_balances(w.address, eth_bal, usdt_val)

def run_loop():
    print("🚀 Scanner Engine Started...")
    while True:
        try:
            scan_once()
        except Exception as e:
            print(f"Critical Loop Error: {e}")
        time.sleep(config.SCAN_INTERVAL_SECONDS)