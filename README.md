# 🐋 WhaleHunter Pro - Live Market Intelligence

**WhaleHunter Pro** is a powerful, real-time blockchain monitoring dashboard built with Python and Streamlit. It tracks "Whale" wallets across multiple chains (Ethereum, BSC, Polygon) and sends instant alerts when large movements occur.

![System Status](https://img.shields.io/badge/System-Online-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Key Features

* **Multi-Chain Tracking:** Monitor wallets on Ethereum, BSC, and Polygon simultaneously.
* **Real-Time Alerts:** Integration with Telegram, Discord, Slack, and Email.
* **Visual Analytics:** Interactive charts for ETH holdings and Stablecoin (USDT/USDC/DAI) movements.
* **Secure Architecture:** Uses Streamlit Secrets management and Environment variables protection.
* **Resilient Engine:** Auto-retry logic with exponential backoff for RPC connection stability.
* **Persistent Data:** SQLite database to store wallet history and transaction logs.

## 🚀 Installation & Local Setup

### Prerequisites
* Python 3.9+
* Git

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/WhaleHunter-Pro.git](https://github.com/yourusername/WhaleHunter-Pro.git)
cd WhaleHunter-Pro
