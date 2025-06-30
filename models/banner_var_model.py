from uuid import UUID, uuid4
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    Float,
    ForeignKey,
    UUID as UUID_TYPE,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class BannerVariant(Base):
    __tablename__ = "banner_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    variant_number = Column(Integer, nullable=False)  # 1, 2, 3, 4

    prompt_seed = Column(String(100))
    style_variation = Column(String(50))
    color_scheme = Column(String(50))

    s3_url = Column(String(500))
    s3_key = Column(String(300))
    s3_preview_url = Column(String(500))
    s3_preview_key = Column(String(300))
    file_size = Column(Integer)
    preview_size = Column(Integer)

    generation_time = Column(Float)
    status = Column(String(20), default="pending")
    error_message = Column(Text)

    view_count = Column(Integer, default=0)
    is_selected = Column(Boolean, default=False)
    is_downloaded = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", back_populates="variants")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    uuid: Mapped[UUID] = mapped_column(
        UUID_TYPE, unique=True, index=True, default=uuid4
    )
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Price information
    price = Column(Float)
    regular_price = Column(Float)
    currency = Column(String(10))
    offer = Column(String(100))

    # Product details
    brand = Column(String(100))
    category = Column(String(100))
    stock = Column(String(100))
    ratings = Column(Float)

    # URLs
    image_url = Column(String(500))
    product_url = Column(String(500))

    # Features
    feature_1 = Column(String(500))
    feature_2 = Column(String(500))
    feature_3 = Column(String(500))
    feature_4 = Column(String(500))
    feature_5 = Column(String(500))

    # Status
    is_live = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    variants = relationship("BannerVariant", back_populates="product")
