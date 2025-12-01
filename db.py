from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# 1. Определение URL базы данных
# Указываем, что будем использовать SQLite и файл базы данных называется 'sql_app.db'
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. Создание движка (Engine) SQLAlchemy
# Движок отвечает за установление соединения с базой данных
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # Параметр connect_args нужен только для SQLite, когда используются несколько потоков.
    # Он разрешает одному и тому же соединению работать с разных потоков.
    # Для PostgreSQL или MySQL этот аргумент не нужен.
    connect_args={"check_same_thread": False} 
)

# 3. Создание класса сессии (SessionLocal)
# Используем sessionmaker для создания класса, который будет создавать объекты сессии.
SessionLocal = sessionmaker(
    autocommit=False,  # Отключаем автоматический коммит (нужно вызывать session.commit() вручную)
    autoflush=False,   # Отключаем автоматический сброс изменений в БД перед запросом
    bind=engine        # Связываем этот класс сессии с нашим движком (engine)
)

# Цей виклик створює всі таблиці
Base = declarative_base()


#Функція get_db виконує роль генератора сесій (session generator) і використовується у FastAPI як залежність.
#Основна мета цієї функції — створити нову сесію бази даних для кожного HTTP-запиту, гарантувати її коректне використання і закриття після завершення запиту, незалежно від того, чи була помилка, чи ні.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()