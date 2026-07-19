from datetime import datetime, date, timedelta
from sqlalchemy import Column, Boolean, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32))
    token: Mapped[str] = mapped_column(String(32))
    
    locations: Mapped[list["DeviceLocation"]] = relationship(back_populates="device")

class AccessPoint(Base):
    __tablename__ = "access_points"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name = mapped_column(String(32))
    ssid = mapped_column(String(32))
    bssid = mapped_column(String(32))
    position_x = mapped_column(Float, nullable=True)
    position_y = mapped_column(Float, nullable=True)

class AccessPointSignal(Base):
    __tablename__ = "access_point_signals"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    access_point_id: Mapped[int] = mapped_column(ForeignKey("access_points.id"))
    device_location_id: Mapped[int] = mapped_column(ForeignKey("device_locations.id"))
    rssi: Mapped[float] = mapped_column(Float)

    access_point: Mapped["AccessPoint"] = relationship()
    device_location: Mapped["DeviceLocation"] = relationship(back_populates="access_point_signals")
    
class DeviceLocation(Base):
    __tablename__ = "device_locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    date_time: Mapped[datetime] = mapped_column(DateTime)
    position_x = mapped_column(Float, nullable=True)
    position_y = mapped_column(Float, nullable=True)

    device: Mapped["Device"] = relationship(back_populates="locations")
    access_point_signals: Mapped[list["AccessPointSignal"]] = relationship(back_populates="device_location")

class NamedLocation:
    __tablename__ = "named_locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    position_x = mapped_column(Float, nullable=True)
    position_y = mapped_column(Float, nullable=True)
    name = mapped_column(String(64))
