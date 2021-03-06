from fastapi import Depends, FastAPI, Response, status, HTTPException, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import  List, Optional
from .. import models, schemas, oauth2
from ..database import  get_db


router = APIRouter(
  prefix="/posts",
  tags= ['Posts']
)


# Get list of posts
#@router.get("/", response_model=List[schemas.Post])
@router.get("/", response_model=List[schemas.PostVotes])
def get_posts(db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
  print(current_user.email)
  print(limit)
  # cursor.execute("""SELECT * FROM posts""")
  # posts= cursor.fetchall()
  #posts = db.query(models.Post).all()
  #posts = db.query(models.Post).limit(limit).all() # limit some posts
  #posts = db.query(models.Post).limit(limit).offset(skip).all() # skip some post

  # Add search post by title
  #posts = db.query(models.Post)\
  #  .filter(models.Post.title.contains(search))\
  #  .limit(limit)\
  #  .offset(skip)\
  #  .all()

  """
  Performing LEFT JOIN on SQLAlchemy
  By default SQLAlchemy performs INNER JOIN, to control it use isouter=True or isinner=True
  """
  result = db.query(models.Post,func.count(models.Vote.post_id).label("total_votes")).join(models.Vote,models.Vote.post_id == models.Post.id, isouter=True)\
    .group_by(models.Post.id)\
    .filter(models.Post.title.contains(search))\
    .limit(limit).offset(skip).all()
  print(result)
  # return {"data": posts}
  return result


# Create a post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.CreatePost, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
  print(current_user.id)
  # cursor.execute(""" INSERT INTO posts (title,content,published) VALUES (%s, %s, %s) RETURNING * """,(
  #                post.title, post.content, post.published),)
  #
  # # Commit changes to the database
  # conn.commit()
  #
  # # Fetch the current created post
  # new_post = cursor.fetchone()

  # Orm create post
  # new_post = models.Post(title=post.title, content=post.content, published=post.published)
  """ If we have too many fields we need to automatically unpack the fields using **post.dict()"""
  new_post = models.Post(owner_id=current_user.id,**post.dict())
  db.add(new_post)
  db.commit()

  db.refresh(new_post)

  # return {"data": new_post}
  return new_post

# Get single post
@router.get("/{id}", response_model=schemas.PostVotes)
def get_post(id: int, db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):
  print(current_user.email)
  # cursor.execute(""" SELECT * FROM posts WHERE id=%s """,(str(id)))
  # post = cursor.fetchone()
  #post = db.query(models.Post).filter(models.Post.id==id).first()
  post = db.query(models.Post,func.count(models.Vote.post_id).label("total_votes"))\
    .join(models.Vote,models.Vote.post_id == models.Post.id, isouter=True)\
    .group_by(models.Post.id).filter(models.Post.id==id).first()

  if not post:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Post with id: {id} was not found")

  # return {"data": post}
  return post



# Delete a post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
  print(current_user)
  # delete a post
  # cursor.execute(""" DELETE FROM posts WHERE id=%s RETURNING *""",(str(id),))
  # deleted_post = cursor.fetchone()
  # conn.commit()

  post = db.query(models.Post).filter(models.Post.id == id)

  if post.first() == None:
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=f"The post with id: {id} does not exists")

  if post.first().owner_id != current_user.id:
    raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
  post.delete(synchronize_session=False)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)



# Update a post
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.CreatePost, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
  print(current_user)
  # cursor.execute(""" UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""", (
  #   post.title,
  #   post.content, post.published,str(id)),)
  #
  # updated_post = cursor.fetchone()
  # conn.commit()
  updated_post = db.query(models.Post).filter(models.Post.id == id)

  # Raise an exception if does not exist
  if updated_post.first() == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id: {id} does not exists")

  # Check if the user updating the post is the owner of the post
  if updated_post.first().owner_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
  updated_post.update(post.dict(), synchronize_session=False)
  db.commit()

  # return {"data": updated_post.first()}
  return updated_post.first()


