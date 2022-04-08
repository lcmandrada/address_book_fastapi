from typing import Optional

from pydantic import BaseModel


class AddressCreate(BaseModel):
    address: str
    latitude: float
    longitude: float


class AddressUpdate(BaseModel):
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


class AddressFind(BaseModel):
    distance: float
    latitude: float
    longitude: float


class Address(AddressCreate):
    id: int

    class Config:
        orm_mode = True
