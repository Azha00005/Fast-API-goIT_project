from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, EmailStr
from models import Owner

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
    

class OwnerModel(BaseModel):
    email:EmailStr

@app.get("/owners")
async def get_owners(db: Session = Depends(get_db)):
    owners = db.query(Owner).all()
    return owners

@app.post("/owners")
async def get_owners(body: OwnerModel, db: Session = Depends(get_db)):
    owner = Owner(**body.dict())
    db.add(owner)
    db.commit()
    #для получения id после вставки
    db.refresh(owner)
    return owner