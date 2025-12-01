from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from db import get_db



app = FastAPI()

@app.get("/")
async def root():
    return {}

#Перевірка працездатності застосунку та бази даних
@app.get('/api/healthchecker')
def healthchecker(db: Session = Depends(get_db)):
    """
    Виконує просту перевірку з'єднання з базою даних. 
    Повертає 200 OK, якщо застосунок та БД працюють, і 500 Internal Server Error у разі помилки.
    """
    try:
        # Виконання найпростішого синхронного запиту для перевірки з'єднання
        # Це підійде, якщо ваша get_db повертає синхронну сесію (як у вашому прикладі)
        result = db.execute(text("SELECT 1")).fetchone()
        
        # Якщо запит успішний, повертаємо статус OK
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")
        return {
            "message": "Service is fully operational"
        }
    except Exception:
        # Якщо будь-яка помилка (наприклад, БД не відповідає), повертаємо 500
        return {
            "status": "unhealthy",
            "db_connection": "Failed"
        }, status.HTTP_500_INTERNAL_SERVER_ERROR