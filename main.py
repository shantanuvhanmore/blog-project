from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models,schemas
from auth import create_token, verify_token


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# DB dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()

# login API 
@app.post("/login")
def login():
    
    return {"access_token": create_token({"user": "admin"}), "token_type": "bearer"}

#home
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


# Create Blog (protected)
@app.post("/blogs", response_model= schemas.BlogResponse)
def create_blog(blog: schemas.BlogCreate, db: Session = Depends(get_db), user = Depends(verify_token)):
    new = models.Blog(
        title= blog.title,
        content= blog.content 
    )
    db.add(new)
    db.commit()
    db.refresh(new)

    return new

# Read ALL Blogs 
@app.get("/blogs")
def get_all_blog(db : Session = Depends(get_db), page : int =1, limit : int = 5, search: str = Query(default="")):
    query = db.query(models.Blog)
    if search:
        query = query.filter(models.Blog.title.ilike(f"%{search}%")) 

    total = query.count()
    start = (page - 1) * limit
    blogs = query.offset(start).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": blogs
    }

# Read Blog by ID 
@app.get("/blogs/{id}", response_model= schemas.BlogResponse)
def get_blogs(id : int, db : Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
            raise HTTPException(status_code=404, detail="Not Found")
    return  blog

# Update Blog by ID (protected)
@app.put("/blogs/{id}", response_model= schemas.BlogResponse)
def update(id: int,new: schemas.BlogCreate, db :Session = Depends(get_db),user = Depends(verify_token)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Not Found")
    blog.title = new.title
    blog.content = new.content

    db.commit()
    return blog

# Delete Blog by ID (protected)
@app.delete("/blogs/{id}")
def delete_blog(id: int, db :Session =Depends(get_db),user = Depends(verify_token)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Not Found")
    db.delete(blog)
    db.commit()
    return {"message": "Blog Has Been Deleted Successfully" }

