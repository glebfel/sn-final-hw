from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./todo.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()


class TodoItem(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False


@app.post("/items")
def create_item(item: TodoCreate):
    db = SessionLocal()
    todo = TodoItem(**item.dict())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    db.close()
    return todo


@app.get("/items")
def read_items():
    db = SessionLocal()
    todos = db.query(TodoItem).all()
    db.close()
    return todos


@app.get("/items/{item_id}")
def read_item(item_id: int):
    db = SessionLocal()
    todo = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    db.close()
    if not todo:
        raise HTTPException(status_code=404, detail="Item not found")
    return todo


@app.put("/items/{item_id}")
def update_item(item_id: int, item: TodoCreate):
    db = SessionLocal()
    todo = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not todo:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    db.close()
    return todo


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    db = SessionLocal()
    todo = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if not todo:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(todo)
    db.commit()
    db.close()
    return {"message": "Item deleted"}
