from typing import Optional

from fastapi import Depends, Query, Path, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement

import models
import schemas
from database import get_db
from config import SRID

router = APIRouter(prefix="/address", tags=["Address"])

# NOTE: SQLAlchemy doesn't have compatibility for using `await` directly.
# https://fastapi.tiangolo.com/tutorial/sql-databases/#about-def-vs-async-def
# `encode/databases` is needed to support asyncio.
# https://fastapi.tiangolo.com/advanced/async-sql-databases


@router.post(
    "/",
    response_model=schemas.Address,
    status_code=status.HTTP_201_CREATED,
    summary="Create an address",
)
def create_address(
    address: schemas.AddressCreate, db: Session = Depends(get_db)
):
    return models.Address.create_address(db, address)


@router.get("/", response_model=list[schemas.Address], summary="Get addresses")
def get_addresses(
    skip: Optional[int] = Query(0, description="Number of items to skip"),
    limit: Optional[int] = Query(
        10, description="Max number of items to return"
    ),
    query: Optional[schemas.AddressFind] = None,
    db: Session = Depends(get_db),
):
    if query:
        return models.Address.find_address_within_distance(
            db,
            query.distance,
            WKTElement(
                f"POINT({query.longitude} {query.latitude})", srid=SRID
            ),
            skip,
            limit,
        )
    return models.Address.get_addresses(db, skip, limit)


@router.get(
    "/{id}", response_model=schemas.Address, summary="Get an address by ID"
)
def get_address(
    id: int = Path(..., description="The ID of the address"),
    db: Session = Depends(get_db),
):
    db_address = models.Address.find_address_by_id(db, id)
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    return db_address


@router.patch(
    "/{id}", response_model=schemas.Address, summary="Update an address by ID"
)
def update_address(
    address: schemas.AddressUpdate,
    id: int = Path(..., description="The ID of the address"),
    db: Session = Depends(get_db),
):
    result = models.Address.update_address_by_id(db, id, address)
    if not result:
        raise HTTPException(status_code=404, detail="Address not found")
    return result


@router.delete(
    "/{id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an address by ID",
)
def delete_address(
    id: int = Path(..., description="The ID of the address"),
    db: Session = Depends(get_db),
):
    result = models.Address.delete_address_by_id(db, id)
    if not result:
        raise HTTPException(status_code=404, detail="Address not found")
