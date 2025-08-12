from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    register_time: Mapped[datetime] = mapped_column(nullable=False, unique=False)
    city_id: Mapped[int] = mapped_column(ForeignKey('cities.id', ondelete='SET NULL', onupdate='CASCADE'),
                                         unique=False, nullable=False)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    newsletter: Mapped[bool] = mapped_column(unique=False, nullable=False)

class Cities(Base):
    __tablename__ = 'cities'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    city_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    timezone: Mapped[int] = mapped_column(nullable=False, unique=False)