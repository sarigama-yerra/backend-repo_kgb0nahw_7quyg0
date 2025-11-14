"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Fitness App Schemas
# --------------------------------------------------
class ExerciseItem(BaseModel):
    name: str = Field(..., description="Exercise name, e.g., Bench Press")
    sets: Optional[int] = Field(None, ge=0, description="Number of sets")
    reps: Optional[int] = Field(None, ge=0, description="Reps per set")
    weight: Optional[float] = Field(None, ge=0, description="Weight in kg or lbs")
    duration: Optional[int] = Field(None, ge=0, description="Duration in minutes for cardio")
    notes: Optional[str] = Field(None, description="Any notes for this exercise")

class Workout(BaseModel):
    """
    Workouts collection schema
    Collection name: "workout"
    """
    title: str = Field(..., description="Workout plan title")
    workout_date: Optional[date] = Field(None, description="Date of the workout")
    notes: Optional[str] = Field(None, description="General notes for the workout")
    exercises: List[ExerciseItem] = Field(default_factory=list, description="List of exercises in this workout")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
