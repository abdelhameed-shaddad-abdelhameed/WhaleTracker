from datetime import datetime
from decimal import Decimal
from typing import List, Tuple

from sqlalchemy import (
    Column, String, Integer, Numeric, DateTime, create_engine, select, delete, update
)
from sqlalchemy.orm import declarative_base, Session

import config

Base = declarative_base()
engine = create_engine(config.POSTGRES_DSN, future=True)

class Wallet(Base):
    __tablename__ = "wallets"
    address = Column(String, primary_key=True)
    label = Column(String)
    chain = Column(String, default="ethereum")
    eth_threshold = Column(Numeric, default=config.DEFAULT_ETH_THRESHOLD)
    usdt_threshold = Column(Numeric, default=config.DEFAULT_USDT_THRESHOLD)
    last_eth_balance = Column(Numeric, default=0)
    last_usdt_balance = Column(Numeric, default=0)

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    address = Column(String, nullable=False)
    label = Column(String)
    chain = Column(String, nullable=False)
    asset = Column(String, nullable=False)
    amount_change = Column(Numeric, nullable=False)
    new_balance = Column(Numeric, nullable=False)

def init_db() -> None:
    Base.metadata.create_all(engine)

def add_wallet(address: str, label: str, chain: str, eth_th: Decimal, usdt_th: Decimal) -> None:
    with Session(engine) as s:
        if s.get(Wallet, address) is None:
            s.add(Wallet(address=address, label=label, chain=chain, eth_threshold=eth_th, usdt_threshold=usdt_th))
            s.commit()

def remove_wallet(address: str) -> None:
    with Session(engine) as s:
        s.execute(delete(Wallet).where(Wallet.address == address))
        s.commit()

def get_all_wallets() -> List[Wallet]:
    with Session(engine) as s:
        return list(s.scalars(select(Wallet)).all())

def update_wallet_balances(address: str, eth_balance: Decimal, usdt_balance: Decimal) -> None:
    with Session(engine) as s:
        s.execute(
            update(Wallet)
            .where(Wallet.address == address)
            .values(last_eth_balance=eth_balance, last_usdt_balance=usdt_balance)
        )
        s.commit()

def log_event(address: str, label: str, chain: str, asset: str, amount_change: Decimal, new_balance: Decimal) -> None:
    with Session(engine) as s:
        s.add(Log(address=address, label=label, chain=chain, asset=asset,
                  amount_change=amount_change, new_balance=new_balance))
        s.commit()

def get_logs(limit: int = 500) -> List[Tuple]:
    with Session(engine) as s:
        stmt = select(Log).order_by(Log.id.desc()).limit(limit)
        return [(l.timestamp, l.address, l.label, l.chain, l.asset, l.amount_change, l.new_balance)
                for l in s.scalars(stmt).all()]