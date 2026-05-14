import models
import database
from crud import create_feedback
from schemas import FeedbackCreate

models.Base.metadata.create_all(bind=database.engine)
db = database.SessionLocal()

samples = [
    FeedbackCreate(participant_name="Alice Johnson", program_name="React Workshop 2025", rating=5, comments="Excellent workshop! Hands-on sessions were very helpful."),
    FeedbackCreate(participant_name="Bob Smith", program_name="Python for Data Engineers", rating=4, comments="Great content. Could use more real-world examples."),
    FeedbackCreate(participant_name="Carol Williams", program_name="FastAPI Masterclass", rating=5, comments="Loved the live coding sessions and clear explanations."),
    FeedbackCreate(participant_name="David Brown", program_name="React Workshop 2025", rating=3, comments="Good but felt rushed towards the end."),
    FeedbackCreate(participant_name="Eva Martinez", program_name="Docker and Kubernetes", rating=4, comments="Very informative. Labs were well structured."),
]

for s in samples:
    create_feedback(db, s)

db.close()
print("Database seeded with 5 sample feedback entries.")
