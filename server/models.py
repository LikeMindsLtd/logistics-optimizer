from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel
from typing import Optional, List

db = SQLAlchemy()

# ----------------- SQLALCHEMY MODELS (DB TABLES) -----------------

class PlantLog(db.Model):
    _tablename_ = "plant_log"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, nullable=False)
    plant_id = db.Column(db.String(50), index=True, nullable=False)
    plant_name = db.Column(db.String(100))
    max_operating_capacity_mtpa = db.Column(db.Float)
    cumulative_capacity_utilization_percent = db.Column(db.Float)
    stock_utilization_percent = db.Column(db.Float)
    min_stock_target_tonnes = db.Column(db.Float)
    coal_bod_stock_tonnes = db.Column(db.Float)
    limestone_bod_stock_tonnes = db.Column(db.Float)
    coal_required_tonnes = db.Column(db.Float)
    limestone_required_tonnes = db.Column(db.Float)
    consumed_coal_tonnes = db.Column(db.Float)
    consumed_limestone_tonnes = db.Column(db.Float)
    coal_arrived_tonnes = db.Column(db.Float)
    limestone_arrived_tonnes = db.Column(db.Float)
    coal_eod_stock_tonnes = db.Column(db.Float)
    limestone_eod_stock_tonnes = db.Column(db.Float)
    steel_exported_tonnes = db.Column(db.Float)

class TrainLog(db.Model):
    _tablename_ = "train_log"
    id = db.Column(db.Integer, primary_key=True)
    # Using DateTime for precise time-based metrics
    departure_time = db.Column(db.DateTime, index=True, nullable=False)
    arrival_time = db.Column(db.DateTime)
    trip_id = db.Column(db.String(100), unique=True)
    rake_id = db.Column(db.String(100), index=True)
    material_flow = db.Column(db.String(50))
    material = db.Column(db.String(50))
    source = db.Column(db.String(50))
    destination = db.Column(db.String(50))
    quantity_tonnes = db.Column(db.Float)
    distance_km = db.Column(db.Float)
    rake_availability_index = db.Column(db.Float)
    base_time_h = db.Column(db.Float)
    loading_time_h = db.Column(db.Float)
    unloading_time_h = db.Column(db.Float)
    delay_h = db.Column(db.Float)
    total_time_h = db.Column(db.Float)
    rail_freight_inr_tonne = db.Column(db.Float)
    port_handling_inr_tonne = db.Column(db.Float)
    total_trip_cost_inr = db.Column(db.Float)

class PortTariff(db.Model):
    _tablename_ = "port_tariffs"
    id = db.Column(db.Integer, primary_key=True)
    port_name = db.Column(db.String(50), index=True, nullable=False)
    material = db.Column(db.String(50), index=True, nullable=False)
    handling_cost_inr_tonne = db.Column(db.Float)
    storage_cost_inr_tonne_day = db.Column(db.Float)
    max_throughput_t_day = db.Column(db.Float)

class VesselCost(db.Model):
    _tablename_ = "vessel_costs"
    id = db.Column(db.Integer, primary_key=True)
    vessel_id = db.Column(db.String(100), index=True, nullable=False)
    load_port = db.Column(db.String(50))
    discharge_port = db.Column(db.String(50))
    material = db.Column(db.String(50))
    ocean_freight_inr_tonne = db.Column(db.Float)
    demurrage_rate_inr_hr = db.Column(db.Float)
    contract_quantity_tonnes = db.Column(db.Float)
    laydays_allowed_hours = db.Column(db.Float)

class PortLog(db.Model):
    _tablename_ = "port_log"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, nullable=False)
    port_name = db.Column(db.String(50), index=True, nullable=False)
    coal_bod_storage_tonnes = db.Column(db.Float)
    limestone_bod_storage_tonnes = db.Column(db.Float)
    steel_bod_storage_tonnes = db.Column(db.Float)
    coal_arrived_tonnes = db.Column(db.Float)
    limestone_arrived_tonnes = db.Column(db.Float)
    coal_departed_tonnes = db.Column(db.Float)
    limestone_departed_tonnes = db.Column(db.Float)
    steel_arrived_tonnes = db.Column(db.Float)
    steel_shipped_tonnes = db.Column(db.Float)
    coal_eod_storage_tonnes = db.Column(db.Float)
    limestone_eod_storage_tonnes = db.Column(db.Float)
    steel_eod_storage_tonnes = db.Column(db.Float)

class VesselDelayHistory(db.Model):
    _tablename_ = "vessel_delay_history"
    id = db.Column(db.Integer, primary_key=True)
    vessel_name = db.Column(db.String(100), index=True, nullable=False)
    port_name = db.Column(db.String(50))
    eta_datetime = db.Column(db.DateTime)
    actual_berth_time = db.Column(db.DateTime)
    parcel_size_tonnes = db.Column(db.Float)
    laydays_start = db.Column(db.DateTime)
    laydays_end = db.Column(db.DateTime)
    queue_length = db.Column(db.Integer)
    weather_score = db.Column(db.Integer)
    crane_availability = db.Column(db.Integer)
    past_delay_avg_hours = db.Column(db.Float)
    laydays_limit_hours = db.Column(db.Float)
    delay_hours = db.Column(db.Float)
    demurrage_cost_inr = db.Column(db.Float)
    
    # --- 1. Plant Log Schema ---
class PlantLogSchema(BaseModel):
    id: int
    date: date
    plant_id: str
    plant_name: str
    max_operating_capacity_mtpa: Optional[float]
    cumulative_capacity_utilization_percent: Optional[float]
    stock_utilization_percent: Optional[float]
    min_stock_target_tonnes: Optional[float]
    coal_bod_stock_tonnes: Optional[float]
    limestone_bod_stock_tonnes: Optional[float]
    coal_required_tonnes: Optional[float]
    limestone_required_tonnes: Optional[float]
    consumed_coal_tonnes: Optional[float]
    consumed_limestone_tonnes: Optional[float]
    coal_arrived_tonnes: Optional[float]
    limestone_arrived_tonnes: Optional[float]
    coal_eod_stock_tonnes: Optional[float]
    limestone_eod_stock_tonnes: Optional[float]
    steel_exported_tonnes: Optional[float]
    class Config:
        from_attributes = True

# --- 2. Train Log Schema ---
class TrainLogSchema(BaseModel):
    id: int
    departure_time: datetime
    arrival_time: Optional[datetime]
    trip_id: str
    rake_id: Optional[str]
    material_flow: Optional[str]
    material: Optional[str]
    source: Optional[str]
    destination: Optional[str]
    quantity_tonnes: float
    distance_km: Optional[float]
    rake_availability_index: Optional[float]
    base_time_h: Optional[float]
    loading_time_h: Optional[float]
    unloading_time_h: Optional[float]
    delay_h: Optional[float]
    total_time_h: Optional[float]
    rail_freight_inr_tonne: Optional[float]
    port_handling_inr_tonne: Optional[float]
    total_trip_cost_inr: float
    class Config:
        from_attributes = True

# --- 3. Port Tariff Schema ---
class PortTariffSchema(BaseModel):
    id: int
    port_name: str
    material: str
    handling_cost_inr_tonne: float
    storage_cost_inr_tonne_day: float
    max_throughput_t_day: float
    class Config:
        from_attributes = True

# --- 4. Vessel Cost Schema ---
class VesselCostSchema(BaseModel):
    id: int
    vessel_id: str
    load_port: str
    discharge_port: str
    material: str
    ocean_freight_inr_tonne: float
    demurrage_rate_inr_hr: float
    contract_quantity_tonnes: float
    laydays_allowed_hours: float
    class Config:
        from_attributes = True

# --- 5. Port Log Schema ---
class PortLogSchema(BaseModel):
    id: int
    date: date
    port_name: str
    coal_bod_storage_tonnes: Optional[float]
    limestone_bod_storage_tonnes: Optional[float]
    steel_bod_storage_tonnes: Optional[float]
    coal_arrived_tonnes: Optional[float]
    limestone_arrived_tonnes: Optional[float]
    coal_departed_tonnes: Optional[float]
    limestone_departed_tonnes: Optional[float]
    steel_arrived_tonnes: Optional[float]
    steel_shipped_tonnes: Optional[float]
    coal_eod_storage_tonnes: Optional[float]
    limestone_eod_storage_tonnes: Optional[float]
    steel_eod_storage_tonnes: Optional[float]
    class Config:
        from_attributes = True

# --- 6. Vessel Delay History Schema ---
class VesselDelayHistorySchema(BaseModel):
    id: int
    vessel_name: str
    port_name: str
    eta_datetime: Optional[datetime]
    actual_berth_time: Optional[datetime]
    parcel_size_tonnes: Optional[float]
    laydays_start: Optional[datetime]
    laydays_end: Optional[datetime]
    queue_length: Optional[int]
    weather_score: Optional[int]
    crane_availability: Optional[int]
    past_delay_avg_hours: Optional[float]
    laydays_limit_hours: Optional[float]
    delay_hours: float
    demurrage_cost_inr: float
    class Config:
        from_attributes = True

# --- UPDATE MODEL_MAP ---
# Update the MODEL_MAP in models.py to use these new schemas:
MODEL_MAP = {
    'plants': (PlantLog, PlantLogSchema),
    'trains': (TrainLog, TrainLogSchema),
    'tariffs': (PortTariff, PortTariffSchema),
    'vessel_costs': (VesselCost, VesselCostSchema),
    'ports': (PortLog, PortLogSchema),
    'delay_history': (VesselDelayHistory, VesselDelayHistorySchema),
}