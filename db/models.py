from typing import List
from typing import Optional
import datetime
from sqlalchemy import Text, Float
from sqlalchemy import DateTime, func
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass

class Job(Base):
     __tablename__ = "jobs"

     id: Mapped[int] = mapped_column(primary_key=True)
     status : Mapped[str] = mapped_column(String(20), nullable=False)
     video_url : Mapped[str] = mapped_column(String(500), nullable=False)
     created_at : Mapped[datetime.datetime] = mapped_column(
          DateTime(timezone=True),
          server_default=func.now()
     )
     updated_at : Mapped[datetime.datetime] = mapped_column(
          DateTime(timezone=True),
          server_default=func.now(),
          onupdate=func.now()
     )
     error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
     clips = Mapped[list["Clip"]] = relationship("Clip", back_populates="job")


class Clip(Base):
     __tablename__ = "clips"

     clip_id: Mapped[int] = mapped_column(primary_key=True)
     job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
     file_path: Mapped[str] = mapped_column(String(500), nullable=False)
     start_time : Mapped[float] = mapped_column(Float, nullable=False)
     end_time : Mapped[float] = mapped_column(Float, nullable=False)
     duration : Mapped[float] = mapped_column(Float, nullable=False)
     score : Mapped[float] = mapped_column(Float, nullable=False)
     topic : Mapped[str] = mapped_column(Text, nullable=False)
     speaker : Mapped[str] = mapped_column(String(20), nullable=False)
     energy_level : Mapped[str] = mapped_column(String(10), nullable=False)
     created_at : Mapped[datetime.datetime] = mapped_column(
          DateTime(timezone=True),
          server_default=func.now()
     )
     job : Mapped["Job"] = relationship("Job", back_populates="clips")



