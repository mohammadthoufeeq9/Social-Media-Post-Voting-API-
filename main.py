from fastapi import FastAPI
from pydantic import BaseModel
from random import randrange


app=FastAPI()
posts_DB=[
    {
        "title": "hello",
        "content": "api",
        "id": 4604
    }
]


class create_post(BaseModel):
    title:str
    content:str



@app.get("/posts")
def home():
    return posts_DB



@app.get("/post/{post_id}")
def get_post_by_id(post_id:int):

    for post in posts_DB:
        if post["id"]==post_id:
            return post
    return {"Message":"Post not found"}



@app.post("/posts")
def createPost(post:create_post):
    new_post={
        "title":post.title,
        "content":post.content,
        "id":randrange(2,10000)
    }
    posts_DB.append(new_post)
    return {"message":"post created"}



@app.put("/posts")
def put_update():
    return {"Message":"Entire post is been updated"}



@app.patch("/posts/{post_id}")
def patch_update(post_id:int,updated_post:create_post):

    for post in posts_DB:
            if post["id"]==post_id:
                post['title']=updated_post.title
                post['content']=updated_post.content
                return post
            posts_DB.append(post)
    return {"Message":"Specific field is been updated"}
    

@app.delete("/posts")
def post_delete():
    return {"Message":"post is been deleted successfully"}


@app.delete("/post/{post_id}")
def postdelets(post_id:int,delete_post=create_post):
    for post in posts_DB:
        if post["id"]==post_id:
            posts_DB.remove(post)
    return {"Message":"post is been deleted successfully"}