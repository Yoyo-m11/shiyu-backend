from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PostCreate(BaseModel):
    title: str
    type: str
    category: str
    time: str
    location: str
    description: str
    images: List[str]
    contact: str

class PostResponse(BaseModel):
    id: int
    title: str
    type: str
    category: str
    time: str
    location: str
    description: str
    images: List[str]
    contact: str
    status: str
    similarity: float
    match_reason: List[str]
    created_at: str
    updated_at: str

class PostMatchResponse(BaseModel):
    id: int
    title: str
    type: str
    category: str
    time: str
    location: str
    description: str
    images: List[str]
    contact: str
    status: str
    similarity: float
    match_reason: List[str]
    created_at: str
    updated_at: str
class ClaimCreate(BaseModel):
    post_id: int
    claimer_contact: str
    message: str