from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Product
from src.schema import ProductSchema


product_router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

@product_router.get("/", response_model=List[ProductSchema])
def get_products(db: Session = Depends(get_db)) ->List[ProductSchema]:
    return db.query(Product).all()

@product_router.get("/{id}", response_model=ProductSchema)
def get_product(id: int, db: Session = Depends(get_db)) -> ProductSchema:
    return db.query(Product).get(id)

@product_router.post("/")
def create_product(
    product: ProductSchema,
    db: Session = Depends(get_db)
) -> ProductSchema:
    new_product = Product(**product.model_dump(exclude_unset=True))
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@product_router.put("/{id}", response_model=ProductSchema)
def update_product(
    id: int,
    product: ProductSchema,
    db: Session = Depends(get_db)
) -> ProductSchema:
    existing_product = db.query(Product).get(id)
    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(existing_product, key, value)
    db.commit()
    db.refresh(existing_product)
    return existing_product

@product_router.delete("/{id}")
def delete_product(id: int, db: Session = Depends(get_db)) -> dict:
    product = db.query(Product).get(id)
    db.delete(product)
    db.commit()
    return {
        "message": "product has been deleted"
    }
