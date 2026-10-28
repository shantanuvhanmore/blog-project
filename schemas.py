from pydantic import BaseModel

# Input 
class BlogCreate(BaseModel):
    title: str 
    content: str


#Output
class BlogResponse(BaseModel):
    id: int
    title : str
    content: str
    class Config:
        from_attributes = True

