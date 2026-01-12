import streamlit as st
import time
from decimal import Decimal
import pandas as pd
from web3 import Web3

# استدعاء الملفات الأخرى
import config
import db as db
from notifier import notify
from engine import run_loop, scan_once

# --- 1. تعريف الأنماط (Styles) ---
DARK_CSS = """
<style>
:root { --primary: #4f46e5; --bg: #0f172a; --sidebar-bg: #1e293b; --card: #111827; --text: #e5e7eb; }
body, .stApp { background-color: var(--bg); color: var(--text); }
[data-testid="stSidebar"] { background-color: var(--sidebar-bg) !important; border-right: 1px solid #334155; }
[data-testid="stSidebar"] * { color: var(--text) !important; }
.stMetric, .stDataFrame, .stTable { background-color: var(--card) !important; color: var(--text) !important; border-radius: 8px; padding: 10px; }
div[data-testid="stDataFrame"] { background-color: var(--card); }
</style>
"""

LIGHT_CSS = """
<style>
:root { --primary: #4f46e5; --bg: #ffffff; --card: #f1f5f9; --text: #0f172a; }
body, .stApp { background: var(--bg); color: var(--text); }
.stMetric, .stDataFrame, .stTable { background: var(--card) !important; color: var(--text) !important; }
</style>
"""

def main():
    st.set_page_config(page_title="WhaleHunter Pro", layout="wide")
    
    # تهيئة قاعدة البيانات
    try:
        db.init_db()
    except Exception as e:
        st.error(f"Database Error: {e}")

    # --- 2. الشريط الجانبي ---
    with st.sidebar:
        st.header("🎨 المظهر")
        is_dark = st.toggle("🌙 Dark Mode", value=True)
        if is_dark:
            st.markdown(DARK_CSS, unsafe_allow_html=True)
        else:
            st.markdown(LIGHT_CSS, unsafe_allow_html=True)
            
        st.divider()
        st.header("🎯 إدارة الأهداف")
        
        # نموذج إضافة المحفظة
        with st.form("add_wallet"):
            addr = st.text_input("Wallet Address")
            lbl = st.text_input("Label (e.g. BlackRock)")
            chain = st.selectbox("Network", list(config.SUPPORTED_CHAINS.keys()))
            eth_th = st.number_input("ETH Threshold", value=float(config.DEFAULT_ETH_THRESHOLD), min_value=0.0, step=0.001)
            usdt_th = st.number_input("USDT Threshold", value=float(config.DEFAULT_USDT_THRESHOLD), min_value=0.0, step=10.0)
            
            if st.form_submit_button("Track Target"):
                if Web3.is_address(addr):
                    db.add_wallet(Web3.to_checksum_address(addr), lbl, chain, Decimal(str(eth_th)), Decimal(str(usdt_th)))
                    st.success("Added!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid Address")

        # حذف المحافظ
        wallets = db.get_all_wallets()
        st.caption(f"Tracking {len(wallets)} wallets")
        if wallets:
            del_addr = st.selectbox("Remove Wallet", [w.address for w in wallets],
                                    format_func=lambda x: f"{x[:6]}...{x[-4:]}")
            if st.button("🗑️ Delete Selected"):
                db.remove_wallet(del_addr)
                st.rerun()

        st.divider()
        
        if st.button("🔔 Test Telegram"):
            notify(config.ALERT_CHANNELS, "👋 Test from WhaleHunter Pro", config)
            st.success("Sent!")

        if st.button("▶️ Start Scanner (Bg Thread)"):
            import threading
            t = threading.Thread(target=run_loop, daemon=True)
            t.start()
            st.info("Scanner started in background.")

        # --- Footer ---
        st.markdown("---")
        st.caption("Developed by **Abdelhameed Shaddad** © 2026")
        st.markdown(
            """
            <a href="https://www.linkedin.com/in/abdelhameed-mansour-911034151/" target="_blank" style="text-decoration: none;">
                <div style="background-color: #0e76a8; color: white; padding: 8px; border-radius: 5px; text-align: center; font-weight: bold;">
                    👔 Connect on LinkedIn
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )
        st.caption("🔒 All Rights Reserved")

    # --- 3. المحتوى الرئيسي ---
    st.title("🐋 WhaleHunter Pro - Live Market Intelligence")

    if st.button("⚡ Force Scan Now", type="primary"):
        with st.spinner("Scanning Blockchain..."):
            try:
                scan_once()
                st.success("Scan Complete!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Scan failed: {e}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Active Targets", len(wallets))
    col2.metric("System Status", "🟢 Online")
    col3.metric("Last Update", time.strftime("%H:%M:%S UTC"))

    st.markdown("### 📈 Asset Performance")
    logs = db.get_logs(2000)
    
    if logs:
        df = pd.DataFrame(logs, columns=["ts", "addr", "label", "chain", "asset", "change", "balance"])
        df["ts"] = pd.to_datetime(df["ts"])
        
        # ترتيب زمني للرسم البياني
        df_chart = df.sort_values("ts")

        tab1, tab2, tab3 = st.tabs(["📊 ETH Chart", "💰 Stablecoins", "📋 Raw Data"])
        
        with tab1:
            st.caption("تحركات رصيد الإيثيريوم (ETH)")
            eth_data = df_chart[df_chart["asset"] == "ETH"]
            if not eth_data.empty:
                st.line_chart(eth_data, x="ts", y="balance", color="#00ff00")
            else:
                st.info("No ETH history yet.")

        with tab2:
            st.caption("تحركات العملات المستقرة (USDT/USDC/DAI)")
            stable_data = df_chart[df_chart["asset"].isin(["USDT", "USDC", "DAI"])]
            if not stable_data.empty:
                st.line_chart(stable_data, x="ts", y="balance")
            else:
                st.info("No Stablecoin history yet.")

        with tab3:
            # عرض الجدول مرتباً من الأحدث للأقدم
            st.dataframe(df.sort_values("ts", ascending=False), use_container_width=True)
            
        st.markdown("### 📥 Export Data")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "whale_logs.csv", "text/csv")
    else:
        st.info("No data yet. Add a wallet and click 'Force Scan'.")

if __name__ == "__main__":
    main()