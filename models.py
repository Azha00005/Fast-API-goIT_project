from typing import List
from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

# === 1. Базовий клас декларативного мапування ===
# Він надає метадані для всіх ваших моделей
class Base(DeclarativeBase):
    # Усі моделі успадковують цей базовий клас
    # Він автоматично встановлює id як первинний ключ
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)


# === 2. Модель Користувача (User) ===
class Owner(Base):
    # Явно вказуємо назву таблиці в базі даних
    __tablename__ = "Owner"
    
    # Стовпці таблиці, маповані на типи Python
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    
    # Стовпець зі значенням за замовчуванням (функція func.now() встановлює поточний час)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    

# === 3. Модель Товару (Item) ===
class Cat(Base):
    __tablename__ = "cats"
    
    nickname: Mapped[str] = mapped_column(String(100), index=True)
    age: Mapped[int]
    vaccinated: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str | None] # Може бути None (nullable=True за замовчуванням)
    
    # Стовпець із зовнішнім ключем
    owner_id: Mapped[int] = mapped_column(ForeignKey("owner.id"), nullable=True)
    
    # Відношення Many-to-One: Товар належить одному користувачу, backref створює зворотне відношення і прописує автоматично сам в таблиці власника
    owner: Mapped["Owner"] = relationship("Owner", backref="cats")
    