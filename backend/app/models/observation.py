import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
import enum


class WaterClarity(str, enum.Enum):
    clear = "clear"
    slightly_cloudy = "slightly_cloudy"
    cloudy = "cloudy"
    opaque = "opaque"


class Odor(str, enum.Enum):
    none = "none"
    earthy = "earthy"
    chemical = "chemical"
    sewage = "sewage"


class Observation(Base):
    __tablename__ = "observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    photo_url = Column(String, nullable=True)
    water_clarity = Column(SQLEnum(WaterClarity), nullable=True)
    visible_waste = Column(Boolean, nullable=True)
    algae = Column(Boolean, nullable=True)
    odor = Column(SQLEnum(Odor), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
