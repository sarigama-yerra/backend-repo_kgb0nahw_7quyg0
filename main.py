import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from datetime import date

from database import db, create_document, get_documents
from schemas import Workout, ExerciseItem

app = FastAPI(title="Fitness Notes API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Fitness Notes API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# ------------------- Fitness Endpoints -------------------

class ExerciseIn(BaseModel):
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration: Optional[int] = None
    notes: Optional[str] = None

class WorkoutIn(BaseModel):
    title: str
    workout_date: Optional[date] = None
    notes: Optional[str] = None
    exercises: List[ExerciseIn] = []

@app.post("/api/workouts")
def create_workout(workout: WorkoutIn):
    try:
        workout_id = create_document("workout", workout.model_dump())
        return {"id": workout_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workouts")
def list_workouts():
    try:
        docs = get_documents("workout", {}, limit=100)
        # Convert ObjectId to string for JSON
        for d in docs:
            d["id"] = str(d.pop("_id", ""))
            # Convert nested dates if any
            if "workout_date" in d and isinstance(d["workout_date"], (date,)):
                d["workout_date"] = d["workout_date"].isoformat()
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workouts/{workout_id}")
def get_workout(workout_id: str):
    try:
        from pymongo import ReturnDocument
        doc = db["workout"].find_one({"_id": ObjectId(workout_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Workout not found")
        doc["id"] = str(doc.pop("_id", ""))
        if "workout_date" in doc and isinstance(doc["workout_date"], (date,)):
            doc["workout_date"] = doc["workout_date"].isoformat()
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/workouts/{workout_id}")
def delete_workout(workout_id: str):
    try:
        res = db["workout"].delete_one({"_id": ObjectId(workout_id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Workout not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/workouts/{workout_id}")
def update_workout(workout_id: str, workout: WorkoutIn):
    try:
        from datetime import datetime, timezone
        res = db["workout"].update_one(
            {"_id": ObjectId(workout_id)},
            {"$set": {**workout.model_dump(), "updated_at": datetime.now(timezone.utc)}}
        )
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Workout not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
