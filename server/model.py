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

class AccessPoint(Base):
    __tablename__ = "reference_devices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ssid = mapped_column(String(32))
    bssid = mapped_column(String(32))
    position_x = mapped_column(Float)
    position_y = mapped_column(Float)

class AccessPointSignal(Base):
    __tablename__ = "reference_signals"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    access_point_id: Mapped[int] = mapped_column(ForeignKey("reference_devices.id"))
    device_location_id: Mapped[int] = mapped_column(ForeignKey("device_locations.id"))
    rssi: Mapped[float] = mapped_column(Float)

    access_point: Mapped["AccessPoint"] = relationship()
    device_location: Mapped["DeviceLocation"] = relationship(back_populates="access_point_signals")
    
class DeviceLocation(Base):
    __tablename__ = "device_locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    date_time: Mapped[datetime] = mapped_column(DateTime)
    position_x = mapped_column(Float)
    position_y = mapped_column(Float)
    cell_x = mapped_column(Integer)
    cell_y = mapped_column(Integer)

    device: Mapped["Device"] = relationship()
    access_point_signals: Mapped[list["AccessPointSignal"]] = relationship(back_populates="device_location")
