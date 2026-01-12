import asyncio
import time
from decimal import Decimal

if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.set_event_loop(asyncio.new_event_loop())

from WhaleTracker import BlockchainService
import config
import db
from notifier import notify

def scan_once():
    # Pass 'chain' name to BlockchainService so it loads correct tokens
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

        # 1. Native Balance (ETH/BNB/MATIC)
        try:
            eth_bal = svc.get_eth_balance(w.address)
            if eth_bal is not None:
                # Log balance occasionally or on change (logic simplified here)
                db.log_event(w.address, w.label, w.chain, "ETH", Decimal(eth_bal), Decimal(eth_bal))
                
                # Check ETH Threshold
                if eth_bal >= w.eth_threshold and w.last_eth_balance < w.eth_threshold:
                     notify(config.ALERT_CHANNELS, f"🚨 {w.label} [{w.chain}] Native Balance Alert: {eth_bal:.4f}", config)

        except Exception as e:
            print(f"Skipping {w.address} due to error: {e}")
            eth_bal = None

        # 2. Token Balances (USDT, USDC, etc per chain)
        for sym, tsvc in svc.token_services.items():
            try:
                bal = tsvc.balance(w.address)
                if bal is None: continue
                
                db.log_event(w.address, w.label, w.chain, sym, Decimal(bal), Decimal(bal))

                # Check USDT/Token Threshold (using generic usdt_threshold for all stables for now)
                if sym in ["USDT", "USDC", "DAI"] and bal >= w.usdt_threshold and w.last_usdt_balance < w.usdt_threshold:
                    notify(config.ALERT_CHANNELS, f"🚨 {w.label} [{w.chain}] {sym} High Balance: {bal:,.2f}", config)
                    
            except Exception as e:
                print(f"Error reading token {sym} for {w.address}: {e}")

        # Update last known balances in DB (simplified)
        if eth_bal is not None:
            # Note: We are updating just ETH/USDT columns for legacy compatibility
            # Ideally, expand DB schema to store all token balances
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