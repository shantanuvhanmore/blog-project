from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models,schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# DB dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()


#home
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


# Create Blog
@app.post("/blogs", response_model= schemas.BlogResponse)
def create_blog(blog: schemas.BlogCreate, db: Session = Depends(get_db)):
    new = models.Blog(
        title= blog.title,
        content= blog.content 
    )
    db.add(new)
    db.commit()
    db.refresh(new)

    return new

# Read ALL Blogs
@app.get("/blogs", response_model= list[schemas.BlogResponse])
def get_all_blog(db : Session = Depends(get_db)):
    return db.query(models.Blog).all()

# Read Blog by ID 
@app.get("/blogs/{id}", response_model= schemas.BlogResponse)
def get_blogs(id : int, db : Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
            raise HTTPException(status_code=404, detail="Not Found")
    return  blog

@app.put("/blogs/{id}", response_model= schemas.BlogResponse)
def update(id: int,new: schemas.BlogCreate, db :Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Not Found")
    blog.title = new.title
    blog.content = new.content

    db.commit()
    return blog


@app.delete("/blogs/{id}")
def delete_blog(id: int, db :Session =Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Not Found")
    db.delete(blog)
    db.commit()
    return {"message": "Blog Has Been Deleted Successfully" }

