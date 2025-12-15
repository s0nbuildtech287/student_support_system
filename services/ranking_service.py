import os
import pandas as pd

DATA_PATH = os.path.join("data", "workout_list_exercise.csv")

FAKE_USES = {
    "Barbell Squat": 1280,
    "Dumbbell Bench Press": 1120,
    "Barbell Deadlift": 980,
    "Pull Up": 860,
    "Push Up": 820,
    "Dumbbell Shoulder Press": 790,
    "Plank": 760,
    "Lat Pulldown": 720,
    "Leg Press": 690,
    "Bicep Curl": 650,
}

def get_top_exercises(limit=9, mode="all"):
    df = pd.read_csv(DATA_PATH)

    items = []
    for _, row in df.iterrows():
        name = str(row.get("name", "")).strip()
        if not name:
            continue

        equipment_raw = row.get("equipment", "")
        equipment = str(equipment_raw).strip()
        equipment_l = equipment.lower()

        # ✅ HOME nếu equipment có chứa "bodyweight"
        is_home = "bodyweight" in equipment_l

        if mode == "home" and not is_home:
            continue
        if mode == "gym" and is_home:
            continue

        uid = int(row.get("id"))

        uses = int(FAKE_USES.get(name, 200))

        items.append({
            "uid": uid,
            "name": name,
            "muscle_group": row.get("target", ""),
            "body_part": row.get("bodyPart", ""),
            "equipment": equipment,
            "difficulty": row.get("difficulty", "Intermediate"),
            "image": row.get("image", ""),
            "uses": uses,
        })

    items.sort(key=lambda x: x["uses"], reverse=True)
    top = items[:limit]

    for i, it in enumerate(top, start=1):
        it["rank"] = i

    return top
