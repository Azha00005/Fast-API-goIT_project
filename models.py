from typing import List
from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


from db import Base, engine



# === 2. Модель Користувача (User) ===
class Owner(Base):
    # Явно вказуємо назву таблиці в базі даних
    __tablename__ = "owner"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Стовпці таблиці, маповані на типи Python
    # Обратите внимание на "| None" и "nullable=True"
    username: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    
    # Стовпець зі значенням за замовчуванням (функція func.now() встановлює поточний час)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    
    # Связь с котами (чтобы можно было делать owner.cats)
    cats: Mapped[list["Cat"]] = relationship("Cat", back_populates="owner")

# === 3. Модель Товару (Item) ===
class Cat(Base):
    __tablename__ = "cat"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nickname: Mapped[str] = mapped_column(String(100), index=True)
    age: Mapped[int]
    vaccinated: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str | None] # Може бути None (nullable=True за замовчуванням)
    
    # Стовпець із зовнішнім ключем
    owner_id: Mapped[int] = mapped_column(ForeignKey("owner.id"), nullable=True)
    
    # Відношення Many-to-One: Товар належить одному користувачу, backref створює зворотне відношення і прописує автоматично сам в таблиці власника
    owner: Mapped["Owner"] = relationship("Owner", back_populates="cats")
    

Base.metadata.create_all(bind=engine)
    