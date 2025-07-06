from sqlalchemy import (
    String, Integer, ForeignKey, Text, Boolean,
    DateTime, SmallInteger, BigInteger, UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, DeclarativeBase
)
from datetime import datetime, timezone, timedelta

from db.base import Base
# Часовой пояс Москва (UTC+3)
MSK = timezone(timedelta(hours=3))


def msk_now():
    return datetime.now(MSK)



class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)

    users = relationship("User", back_populates="role")


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    zones = relationship("Zone", back_populates="branch")
    areas = relationship("Area", back_populates="branch")
    users = relationship("User", back_populates="branch")
    cities = relationship("City", back_populates="branch", cascade="all, delete")


class Zone(Base):
    __tablename__ = "zones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    branch_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("branches.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    city_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cities.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    area_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("areas.id", ondelete="CASCADE"), nullable=False
    )

    branch = relationship("Branch", back_populates="zones")
    city = relationship("City", back_populates="zones")
    area = relationship("Area", back_populates="zones")
    houses = relationship("House", back_populates="zone", cascade="all, delete")



class Area(Base):
    __tablename__ = "areas"
    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    branch_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("branches.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )

    branch = relationship("Branch", back_populates="areas")
    zones = relationship("Zone", back_populates="area", cascade="all, delete")
    users = relationship("User", back_populates="area", foreign_keys="[User.area_id]")
    temp_users = relationship("User", back_populates="temp_area", foreign_keys="[User.temp_area_id]")
    houses = relationship("House", back_populates="area")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram ID
    full_name: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20), nullable=True)

    area_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("areas.id"), nullable=True
    )
    temp_area_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("areas.id"), nullable=True
    )
    branch_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("branches.id"), nullable=True
    )

    role_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("roles.id"), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=msk_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=msk_now, onupdate=msk_now
    )
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    default_city_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("cities.id"), nullable=True)


    role = relationship("Role", back_populates="users")
    branch = relationship("Branch", back_populates="users")
    area = relationship("Area", back_populates="users", foreign_keys=[area_id])
    temp_area = relationship("Area", back_populates="temp_users", foreign_keys=[temp_area_id])


class House(Base):
    __tablename__ = "houses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    area_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("areas.id"), nullable=False
    )
    zone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("zones.id"), nullable=False
    )

    street: Mapped[str] = mapped_column(String(255), nullable=False)
    house_number: Mapped[str] = mapped_column(String(50), nullable=False)
    entrances: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    floors: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    is_in_gks: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    notes: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=msk_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=msk_now, onupdate=msk_now
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    updated_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("area_id", "street", "house_number", name="uk_house"),
    )

    area = relationship("Area", back_populates="houses")
    zone = relationship("Zone", back_populates="houses")

    entrances_rel = relationship("HouseEntrance", back_populates="house")
    housing_office_id: Mapped[int] = mapped_column(ForeignKey("housing_offices.id"), nullable=True)
    housing_office = relationship("HousingOffice")


class HouseEntrance(Base):
    __tablename__ = "house_entrances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    house_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("houses.id", ondelete="CASCADE"), nullable=False
    )
    entrance_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    floors: Mapped[int] = mapped_column(SmallInteger, nullable=True)

    flats_text: Mapped[str] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=msk_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=msk_now, onupdate=msk_now
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    updated_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("house_id", "entrance_number", name="uk_entrance"),
    )

    house = relationship("House", back_populates="entrances_rel")
    equipment = relationship("EntranceEquipment", back_populates="entrance")
    photos = relationship("EntrancePhoto", back_populates="entrance")
    flats_ranges = relationship("EntranceFlatsRange", back_populates="entrance", cascade="all, delete")


class EntranceFlatsRange(Base):
    __tablename__ = "entrance_flats_ranges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entrance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("house_entrances.id", ondelete="CASCADE"), nullable=False
    )
    start_flat: Mapped[int] = mapped_column(Integer, nullable=False)
    end_flat: Mapped[int] = mapped_column(Integer, nullable=False)

    entrance = relationship("HouseEntrance", back_populates="flats_ranges")


class EntranceEquipment(Base):
    __tablename__ = "entrance_equipment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entrance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("house_entrances.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100))
    serial_number: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="Работает")
    installed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=msk_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=msk_now, onupdate=msk_now
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    updated_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )

    entrance = relationship("HouseEntrance", back_populates="equipment")


class EntrancePhoto(Base):
    __tablename__ = "entrance_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entrance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("house_entrances.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(255))

    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=msk_now)
    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )

    entrance = relationship("HouseEntrance", back_populates="photos")


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    

    branch_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("branches.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False
    )

    branch = relationship("Branch", back_populates="cities")
    zones = relationship("Zone", back_populates="city")


class HousingOffice(Base):
    __tablename__ = "housing_offices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), nullable=False)
    comments: Mapped[str] = mapped_column(Text, default="")
    photo_url: Mapped[str] = mapped_column(String(500), default="")
    working_hours: Mapped[str] = mapped_column(String(100), default="")
    phone: Mapped[str] = mapped_column(String(50), default="")
    email: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=msk_now)

    city = relationship("City")
    zone = relationship("Zone")

    __table_args__ = (
        UniqueConstraint("name", "address", "city_id", "zone_id", name="uq_housing_office"),
    )


