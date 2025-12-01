from fastapi import FastAPI, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, select
from pydantic import BaseModel, EmailStr, Field
from typing import List

from db import get_db
from models import Owner, Cat


app = FastAPI()

@app.get("/")
def root():
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

class ResponseOwner(BaseModel):
    """Схема для вихідних даних (відповідь API)."""
    id : int
    email: EmailStr

    class Config:
        from_attributes = True
    


@app.get("/owners", response_model=List[ResponseOwner], tags=["owners"])
async def get_owners(db: Session = Depends(get_db)):
    owners = db.query(Owner).all()
    return owners


@app.post("/owners", response_model=ResponseOwner, tags=["owners"])
async def create_owner(
     body: OwnerModel, 
     db: Session = Depends(get_db)):
    # Створення об'єкта SQLAlchemy з Pydantic моделі
    owner = Owner(**body.dict())
    
    db.add(owner)
    db.commit()
    #для получения id после вставки
    db.refresh(owner)
    return owner


@app.get("/owners/{owner_id}", response_model=ResponseOwner, tags=["owners"])
async def get_owner(
     owner_id:int = Path(..., ge=1), 
     db: Session = Depends(get_db)
     ):
    owners = db.execute(select(Owner).filter_by(id=owner_id)).scalars().first()
    if owners is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Not found")
    return owners


@app.put("/owners/{owner_id}", response_model=ResponseOwner, tags=["owners"])
async def update_owners(
     body: OwnerModel, 
     owner_id:int = Path(..., ge=1), 
     db: Session = Depends(get_db)
     ):
    stmt = select(Owner).filter_by(id=owner_id)
    owner = db.execute(stmt).scalars().first()
    if owner is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Not found")
    owner.email = body.email
    db.commit()
    return owner


@app.delete("/owners/{owner_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["owners"])
async def delete_owner(
     owner_id:int = Path(..., ge=1), 
     db: Session = Depends(get_db)
     ):
    owners = db.execute(select(Owner).filter_by(id=owner_id)).scalars().first()
    if owners is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Not found")
    db.delete(owners)
    db.commit()
    return owners



#Модель для создания
class CatModel(BaseModel):
     nickname: str = Field('Barsil', min_length=3, max_length=10)
     age: int = Field(1, ge=1, le=20)
     vaccinated: bool=False
     description: str
     owner_id: int = Field(1, ge=1)

#модкль для ОТВЕТА
class ResponseCat(BaseModel):
     id: int =1 
     nickname: str
     age: int
     vaccinated: bool
     description: str
     owner: ResponseOwner

     class Config:
        from_attributes = True




@app.get("/cats", response_model=List[ResponseCat], tags=["cats"])
async def get_cats(limit: int=Query(10, le=1000), offset: int = 0, db: Session = Depends(get_db)):
    cats = db.query(Cat).limit(limit).offset(offset).all()
    return cats


@app.post("/cats", response_model=ResponseCat, tags=["cats"])
async def create_cats(
     body: CatModel, 
     db: Session = Depends(get_db)):
    # Створення об'єкта SQLAlchemy з Pydantic моделі
    cats = Cat(**body.dict())

    owner = db.query(Owner).filter(Owner.id == body.owner_id).first()
    if not owner:
         raise HTTPException(status_code=404, detail="Owner not found")
    
    db.add(cats)
    db.commit()
    #для получения id после вставки
    db.refresh(cats)
    return cats


@app.get("/cats/{cats_id}", response_model=ResponseCat, tags=["cats"])
async def get_cat(
     cats_id:int = Path(..., ge=1), 
     db: Session = Depends(get_db)
     ):
    cats = db.execute(select(Cat).filter_by(id=cats_id)).scalars().first()
    if cats is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Not found")
    return cats


@app.put("/cats/{cats_id}", response_model=ResponseCat, tags=["cats"])
async def update_cats(
     body: CatModel, 
     cats_id:int = Path(..., ge=1), 
     db: Session = Depends(get_db)
     ):
    stmt = select(Cat).filter_by(id=cats_id)
    cats = db.execute(stmt).scalars().first()
    if cats is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Not found")
    cats.nickname = body.nickname
    cats.age = body.age
    cats.vaccinated = body.vaccinated
    cats.description = body.description
    cats.owner_id = body.owner_id
    db.commit()
    return cats


@app.delete("/cats/{cats_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["cats"])
async def delete_cats(
     cats_id:int = Path(..., ge=1), 
     db: Session = Depends(get_db)
     ):
    cats = db.execute(select(Owner).filter_by(id=cats_id)).scalars().first()
    if cats is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Not found")
    db.delete(cats)
    db.commit()
    return cats 

