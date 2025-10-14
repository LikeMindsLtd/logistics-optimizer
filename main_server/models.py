from datetime import date as dt_date, datetime
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, Field
from typing import Optional, List

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# ----------------- SQLALCHEMY MODELS (DB TABLES) -----------------

class PlantLog(db.Model):
    __tablename__ = "plant_log"
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
    __tablename__ = "train_log"
    id = db.Column(db.Integer, primary_key=True)
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
    __tablename__ = "port_tariffs"
    id = db.Column(db.Integer, primary_key=True)
    port_name = db.Column(db.String(50), index=True, nullable=False)
    material = db.Column(db.String(50), index=True, nullable=False)
    handling_cost_inr_tonne = db.Column(db.Float)
    storage_cost_inr_tonne_day = db.Column(db.Float)
    max_throughput_t_day = db.Column(db.Float)

class VesselCost(db.Model):
    __tablename__ = "vessel_costs"
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
    __tablename__ = "port_log"
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
    __tablename__ = "vessel_delay_history"
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
    
# ----------------- PYDANTIC BASE SCHEMAS (Used for POST/GET) -----------------

#All Optional fields are explicitly defaulted to None for Pydantic v2 to treat them as optional in the incoming JSON payload (POST/PUT).

class PlantLogSchema(BaseModel):
    id: Optional[int] = None
    date: dt_date # Required
    plant_id: str # Required
    plant_name: str # Required
    max_operating_capacity_mtpa: Optional[float] = None
    cumulative_capacity_utilization_percent: Optional[float] = None
    stock_utilization_percent: Optional[float] = None
    min_stock_target_tonnes: Optional[float] = None
    coal_bod_stock_tonnes: Optional[float] = None
    limestone_bod_stock_tonnes: Optional[float] = None
    coal_required_tonnes: Optional[float] = None
    limestone_required_tonnes: Optional[float] = None
    consumed_coal_tonnes: Optional[float] = None
    consumed_limestone_tonnes: Optional[float] = None
    coal_arrived_tonnes: Optional[float] = None
    limestone_arrived_tonnes: Optional[float] = None
    coal_eod_stock_tonnes: Optional[float] = None
    limestone_eod_stock_tonnes: Optional[float] = None
    steel_exported_tonnes: Optional[float] = None

    class Config:
        from_attributes = True

class TrainLogSchema(BaseModel):
    id: Optional[int] = None
    departure_time: datetime # Required
    arrival_time: Optional[datetime] = None
    trip_id: str # Required (due to unique=True in DB model, though schema just needs to ensure it's provided)
    rake_id: Optional[str] = None
    material_flow: Optional[str] = None
    material: Optional[str] = None
    source: Optional[str] = None
    destination: Optional[str] = None
    quantity_tonnes: float # Required
    distance_km: Optional[float] = None
    rake_availability_index: Optional[float] = None
    base_time_h: Optional[float] = None
    loading_time_h: Optional[float] = None
    unloading_time_h: Optional[float] = None
    delay_h: Optional[float] = None
    total_time_h: Optional[float] = None
    rail_freight_inr_tonne: Optional[float] = None
    port_handling_inr_tonne: Optional[float] = None
    total_trip_cost_inr: float # Required
    
    class Config:
        from_attributes = True

class PortTariffSchema(BaseModel):
    id: Optional[int] = None
    port_name: str # Required
    material: str # Required
    handling_cost_inr_tonne: float # Required
    storage_cost_inr_tonne_day: float # Required
    max_throughput_t_day: float # Required

    class Config:
        from_attributes = True

class VesselCostSchema(BaseModel):
    id: Optional[int] = None
    vessel_id: str # Required
    load_port: str # Required
    discharge_port: str # Required
    material: str # Required
    ocean_freight_inr_tonne: float # Required
    demurrage_rate_inr_hr: float # Required
    contract_quantity_tonnes: float # Required
    laydays_allowed_hours: float # Required

    class Config:
        from_attributes = True

class PortLogSchema(BaseModel):
    id: Optional[int] = None
    date: dt_date # Required
    port_name: str # Required
    coal_bod_storage_tonnes: Optional[float] = None
    limestone_bod_storage_tonnes: Optional[float] = None
    steel_bod_storage_tonnes: Optional[float] = None
    coal_arrived_tonnes: Optional[float] = None
    limestone_arrived_tonnes: Optional[float] = None
    coal_departed_tonnes: Optional[float] = None
    limestone_departed_tonnes: Optional[float] = None
    steel_arrived_tonnes: Optional[float] = None
    steel_shipped_tonnes: Optional[float] = None
    coal_eod_storage_tonnes: Optional[float] = None
    limestone_eod_storage_tonnes: Optional[float] = None
    steel_eod_storage_tonnes: Optional[float] = None

    class Config:
        from_attributes = True

class VesselDelayHistorySchema(BaseModel):
    id: Optional[int] = None
    vessel_name: str # Required
    port_name: str # Required
    eta_datetime: Optional[datetime] = None
    actual_berth_time: Optional[datetime] = None
    parcel_size_tonnes: Optional[float] = None
    laydays_start: Optional[datetime] = None
    laydays_end: Optional[datetime] = None
    queue_length: Optional[int] = None
    weather_score: Optional[int] = None
    crane_availability: Optional[int] = None
    past_delay_avg_hours: Optional[float] = None
    laydays_limit_hours: Optional[float] = None
    delay_hours: float # Required
    demurrage_cost_inr: float # Required

    class Config:
        from_attributes = True
        
        

# ----------------- PYDANTIC UPDATE SCHEMAS (Used for PUT/PATCH) -----------------

class PlantLogUpdateSchema(BaseModel):
    # ALL fields must be optional for PUT operations
    date: Optional[dt_date] = None
    plant_id: Optional[str] = None
    plant_name: Optional[str] = None
    max_operating_capacity_mtpa: Optional[float] = None
    cumulative_capacity_utilization_percent: Optional[float] = None
    stock_utilization_percent: Optional[float] = None
    min_stock_target_tonnes: Optional[float] = None
    coal_bod_stock_tonnes: Optional[float] = None
    limestone_bod_stock_tonnes: Optional[float] = None
    coal_required_tonnes: Optional[float] = None
    limestone_required_tonnes: Optional[float] = None
    consumed_coal_tonnes: Optional[float] = None
    consumed_limestone_tonnes: Optional[float] = None
    coal_arrived_tonnes: Optional[float] = None
    limestone_arrived_tonnes: Optional[float] = None
    coal_eod_stock_tonnes: Optional[float] = None
    limestone_eod_stock_tonnes: Optional[float] = None
    steel_exported_tonnes: Optional[float] = None
    class Config:
        from_attributes = True

class TrainLogUpdateSchema(BaseModel):
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    trip_id: Optional[str] = None
    rake_id: Optional[str] = None
    material_flow: Optional[str] = None
    material: Optional[str] = None
    source: Optional[str] = None
    destination: Optional[str] = None
    quantity_tonnes: Optional[float] = None
    distance_km: Optional[float] = None
    rake_availability_index: Optional[float] = None
    base_time_h: Optional[float] = None
    loading_time_h: Optional[float] = None
    unloading_time_h: Optional[float] = None
    delay_h: Optional[float] = None
    total_time_h: Optional[float] = None
    rail_freight_inr_tonne: Optional[float] = None
    port_handling_inr_tonne: Optional[float] = None
    total_trip_cost_inr: Optional[float] = None
    class Config:
        from_attributes = True

class PortTariffUpdateSchema(BaseModel):
    port_name: Optional[str] = None
    material: Optional[str] = None
    handling_cost_inr_tonne: Optional[float] = None
    storage_cost_inr_tonne_day: Optional[float] = None
    max_throughput_t_day: Optional[float] = None
    class Config:
        from_attributes = True

class VesselCostUpdateSchema(BaseModel):
    vessel_id: Optional[str] = None
    load_port: Optional[str] = None
    discharge_port: Optional[str] = None
    material: Optional[str] = None
    ocean_freight_inr_tonne: Optional[float] = None
    demurrage_rate_inr_hr: Optional[float] = None
    contract_quantity_tonnes: Optional[float] = None
    laydays_allowed_hours: Optional[float] = None
    class Config:
        from_attributes = True

class PortLogUpdateSchema(BaseModel):
    date: Optional[dt_date] = None
    port_name: Optional[str] = None
    coal_bod_storage_tonnes: Optional[float] = None
    limestone_bod_storage_tonnes: Optional[float] = None
    steel_bod_storage_tonnes: Optional[float] = None
    coal_arrived_tonnes: Optional[float] = None
    limestone_arrived_tonnes: Optional[float] = None
    coal_departed_tonnes: Optional[float] = None
    limestone_departed_tonnes: Optional[float] = None
    steel_arrived_tonnes: Optional[float] = None
    steel_shipped_tonnes: Optional[float] = None
    coal_eod_storage_tonnes: Optional[float] = None
    limestone_eod_storage_tonnes: Optional[float] = None
    steel_eod_storage_tonnes: Optional[float] = None
    class Config:
        from_attributes = True

class VesselDelayHistoryUpdateSchema(BaseModel):
    vessel_name: Optional[str] = None
    port_name: Optional[str] = None
    eta_datetime: Optional[datetime] = None
    actual_berth_time: Optional[datetime] = None
    parcel_size_tonnes: Optional[float] = None
    laydays_start: Optional[datetime] = None
    laydays_end: Optional[datetime] = None
    queue_length: Optional[int] = None
    weather_score: Optional[int] = None
    crane_availability: Optional[int] = None
    past_delay_avg_hours: Optional[float] = None
    laydays_limit_hours: Optional[float] = None
    delay_hours: Optional[float] = None
    demurrage_cost_inr: Optional[float] = None
    class Config:
        from_attributes = True

# ----------------- MODEL MAP (Used by services and routes) -----------------

# IMPORTANT: Ensure these keys match the keys used in your routes (e.g., /data/plants)
MODEL_MAP = {
    'plants': (PlantLog, PlantLogSchema, PlantLogUpdateSchema),
    'trains': (TrainLog, TrainLogSchema, TrainLogUpdateSchema),
    'tariffs': (PortTariff, PortTariffSchema, PortLogUpdateSchema),
    'vessel_costs': (VesselCost, VesselCostSchema, VesselCostUpdateSchema),
    'ports': (PortLog, PortLogSchema, PortLogUpdateSchema),
    'delay_history': (VesselDelayHistory, VesselDelayHistorySchema, VesselDelayHistoryUpdateSchema),
}
