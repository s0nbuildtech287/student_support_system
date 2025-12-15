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

def get_top_exercises(limit=9):
    df = pd.read_csv(DATA_PATH)

    # tìm cột name
    name_col = None
    for c in df.columns:
        if c.lower() in ["name", "title", "exercise_name"]:
            name_col = c
            break
    if not name_col:
        name_col = df.columns[0]

    items = []
    for _, row in df.iterrows():
        name = str(row[name_col]).strip()
        uses = int(FAKE_USES.get(name, 200))

        items.append({
            "name": name,
            "muscle_group": row.get("target", row.get("muscle", "")),
            "body_part": row.get("bodyPart", row.get("body_part", "")),
            "equipment": row.get("equipment", ""),
            "difficulty": row.get("difficulty", "Intermediate"),
            "image": row.get("image", row.get("gifUrl", "")),
            "uses": uses
        })

    items.sort(key=lambda x: x["uses"], reverse=True)
    top = items[:limit]
    for i, it in enumerate(top, start=1):
        it["rank"] = i
    return top
