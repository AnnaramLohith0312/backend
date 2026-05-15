from backend.database import SessionLocal
from backend import models

def update_incident_status(incident_id: str, status: str):
    if not incident_id:
        return
    try:
        db = SessionLocal()
        incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
        if incident and incident.status != "failed":
            incident.status = status
            db.commit()
    except Exception as e:
        print(f"Failed to update incident {incident_id} status to {status}: {e}")
    finally:
        db.close()
