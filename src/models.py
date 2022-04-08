from http.client import HTTPException
from typing import Optional

from geoalchemy2 import Geometry, WKTElement
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

import schemas
from config import SRID

# Base for ORM model
Base = declarative_base()


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    # 4326 = WGS84 - Lat Long - POINT(Long Lat)
    geo = Column(Geometry(geometry_type="POINT", srid=SRID, management=True))

    @classmethod
    def create_address(
        cls, db: Session, address: schemas.AddressCreate
    ) -> schemas.Address:
        """Creates an address."""
        # Create geometry point from the given coordinates.
        geo = WKTElement(
            f"POINT({address.longitude} {address.latitude})", srid=SRID
        )

        db_address = cls(
            address=address.address,
            latitude=address.latitude,
            longitude=address.longitude,
            geo=geo,
        )

        db.add(db_address)
        db.commit()
        db.refresh(db_address)

        return db_address

    @classmethod
    def get_addresses(
        cls,
        db: Session,
        skip: Optional[int] = 0,
        limit: Optional[int] = 10,
    ) -> list[schemas.Address]:
        """Returns a list of addresses."""
        return db.query(cls).offset(skip).limit(limit).all()

    @classmethod
    def find_address_within_distance(
        cls,
        db: Session,
        distance: float,
        geo: Geometry,
        skip: Optional[int] = 0,
        limit: Optional[int] = 10,
    ) -> list[schemas.Address]:
        """Returns a list of addresses whose coordinates fall inside
        the given distance from the given coordinates.
        """
        # `ST_Distance` returns the distance between two geometries in meters.
        # `use_ellipsoid` computes on ellipsoid, more precise but slower.
        # http://www.gaia-gis.it/gaia-sins/spatialite-sql-5.0.1.html#p13
        # `ST_DWithin` would've been a more fitting spatial function
        # but is not supported by SpatiaLite.
        # NOTE: Distance is in degrees. May be better if in meters?
        #       However, Geography data is not supported by SpatiaLite.
        filter = func.ST_Distance(cls.geo, geo, use_ellipsoid=True) <= distance
        return db.query(cls).filter(filter).offset(skip).limit(limit).all()

    @classmethod
    def find_address_by_id(
        cls, db: Session, id: int
    ) -> Optional[schemas.Address]:
        """Returns an address found by ID."""
        return db.query(cls).filter_by(id=id).first()

    @classmethod
    def update_address_by_id(
        cls, db: Session, id: int, address: schemas.AddressUpdate
    ) -> Optional[schemas.Address]:
        """Partially updates an address found by ID."""
        result = (
            db.query(cls)
            .filter_by(id=id)
            .update(address.dict(exclude_none=True))
        )

        if result:
            db.commit()
            return cls.find_address_by_id(db, id)

    @classmethod
    def delete_address_by_id(cls, db: Session, id: int) -> int:
        """Deletes an address found by ID."""
        result = db.query(cls).filter_by(id=id).delete()
        if result:
            db.commit()
        return result
