from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[str] = mapped_column(String(20))
    servings: Mapped[int] = mapped_column(Integer)
    ingredients: Mapped[list] = mapped_column(JSON)
    instructions: Mapped[list] = mapped_column(JSON)
    tags: Mapped[list] = mapped_column(JSON)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(Integer)
    rating: Mapped[str] = mapped_column(String(20))
    note: Mapped[str] = mapped_column(Text, default="")
