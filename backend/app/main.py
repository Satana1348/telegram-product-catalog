import os
from io import BytesIO
from uuid import uuid4
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from minio import Minio
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
class S(BaseSettings):
 database_url:str; minio_endpoint:str="localhost:9000"; minio_root_user:str="minioadmin"; minio_root_password:str; minio_secure:bool=False; minio_public_url:str="http://localhost:9000"; internal_api_token:str
s=S()
class Base(DeclarativeBase): pass
class Product(Base):
 __tablename__="products"; id:Mapped[str]=mapped_column(String(36),primary_key=True); name:Mapped[str]=mapped_column(String(200)); object_key:Mapped[str]=mapped_column(String(300),unique=True)
engine=create_engine(s.database_url,pool_pre_ping=True)
def storage(): return Minio(s.minio_endpoint,access_key=s.minio_root_user,secret_key=s.minio_root_password,secure=s.minio_secure)
app=FastAPI(title="Product Catalog API"); app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["GET","POST"],allow_headers=["*"])
@app.on_event("startup")
def boot():
 Base.metadata.create_all(engine); c=storage()
 if not c.bucket_exists("catalog"): c.make_bucket("catalog")
 c.set_bucket_policy("catalog",'{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":["*"]},"Action":["s3:GetObject"],"Resource":["arn:aws:s3:::catalog/*"]}]}')
@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/api/products")
def products():
 with Session(engine) as db: return [{"id":x.id,"name":x.name,"image_url":f"{s.minio_public_url}/catalog/{x.object_key}"} for x in db.scalars(select(Product).limit(100))]
@app.post("/api/internal/products",status_code=201)
def create(name:str,image:UploadFile=File(...),x_internal_token:str|None=Header(None)):
 if x_internal_token!=s.internal_api_token: raise HTTPException(401,"Invalid internal token")
 name=name.strip()
 if not 1<=len(name)<=200 or image.content_type not in {"image/jpeg","image/png","image/webp"}: raise HTTPException(422,"Invalid name or image")
 data=image.file.read()
 if not data or len(data)>10*1024*1024: raise HTTPException(413,"Image must be up to 10 MB")
 key=f"products/{uuid4()}.{image.content_type.split('/')[-1]}"; storage().put_object("catalog",key,BytesIO(data),len(data),content_type=image.content_type)
 item=Product(id=str(uuid4()),name=name,object_key=key)
 with Session(engine) as db: db.add(item); db.commit()
 return {"id":item.id,"name":item.name}
