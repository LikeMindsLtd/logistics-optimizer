from ..models import db, MODEL_MAP
from sqlalchemy import desc

from ..models import TrainLog, PlantLog, PortLog, VesselDelayHistory

# --- Utility Functions ---

def get_model_and_schema(table_name):
    
    model_tuple = MODEL_MAP.get(table_name)
    if not model_tuple:
        return None, None, None
    
    # Handle both (Model, Schema) and (Model, Schema, UpdateSchema)
    if len(model_tuple) == 2:
        Model, Schema = model_tuple
        UpdateSchema = None
    elif len(model_tuple) >= 3:
        Model, Schema, UpdateSchema = model_tuple[:3]
    else:
        return None, None, None

    return Model, Schema, UpdateSchema

def _get_schema_for_model(Model):

    for _, (M, S, *_) in MODEL_MAP.values():
        if M is Model:
            return S
    return None

# --- Specialized Read Operations ---

def fetch_records_by_range(table_name, start_date, end_date):
    Model, Schema, _ = get_model_and_schema(table_name)
    if not Model:
        return None, "Invalid Table Name"

    if not hasattr(Model, 'date'):
        return None, "Model lacks a 'date' attribute for range filtering"

    items = db.session.query(Model).filter(
        Model.date >= start_date, 
        Model.date <= end_date
    ).all()
    return items, Schema, None

def fetch_last_n_records(table_name, n):
    Model, Schema, _ = get_model_and_schema(table_name)
    if not Model:
        return None, "Invalid Table Name"
    
    items = db.session.query(Model).order_by(desc(Model.id)).limit(n).all()
    return items, Schema, None

# --- Specialized Analytics/Reporting Queries ---

def get_active_rakes():
    return db.session.query(TrainLog).filter(TrainLog.end_time.is_(None)).all()

def get_plant_last_logs():
    last_logs = []
    for pid in range(1,6):
        log = db.session.query(PlantLog).filter(PlantLog.plant_id==pid).order_by(desc(PlantLog.date)).first()
        if log:
            last_logs.append(log)
    return last_logs


def get_port_last_logs():
    last_logs = []
    for pid in range(1,5):
        log = db.session.query(PortLog).filter(PortLog.port_id==pid).order_by(desc(PortLog.date)).first()
        if log:
            last_logs.append(log)
    return last_logs

def get_vessels_docked():
    return db.session.query(VesselDelayHistory).filter(VesselDelayHistory.departure_time.is_(None)).all()