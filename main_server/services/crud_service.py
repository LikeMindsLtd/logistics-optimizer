from sqlalchemy.exc import IntegrityError
from ..models import db, MODEL_MAP

# --- Utility Functions ---

def get_model_and_schema(table_name):
    """Retrieve SQLAlchemy model and Pydantic schema from MODEL_MAP"""
    if table_name not in MODEL_MAP:
        # Consistent return of 3 values (Model, ReadSchema, UpdateSchema)
        return None, None, None

    model_tuple = MODEL_MAP[table_name]
    
    # Ensure 3 values are always returned, padding with None if only 2 are in MODEL_MAP
    if len(model_tuple) == 2:
        Model, Schema = model_tuple
        return Model, Schema, None

    return model_tuple

# --- Core CRUD Operations ---

def fetch_one_record(table_name, item_id):
    Model, Schema, _ = get_model_and_schema(table_name)
    if not Model:
        return None, None
    
    item = db.get_or_404(Model, item_id)
    return item, Schema


def fetch_all_records(table_name):
    Model, Schema, UpdateSchema = get_model_and_schema(table_name)
    if not Model:
        return None, None, None
    
    try:
        items = db.session.execute(db.select(Model)).scalars().all()
        # Return 3 values: the items, the Read Schema, and the Update Schema
        return items, Schema, UpdateSchema
    except Exception as e:
        print(f"Database Error: Could not fetch records for table '{table_name}'. {e}")
        # Return 3 values on fetch error
        return [], Schema, UpdateSchema


def insert_record(Model, validated_data):
    try:
        validated_data.pop('id', None) 
        obj = Model(**validated_data)
        db.session.add(obj)
        db.session.commit()
        return obj, None
    except IntegrityError:
        db.session.rollback()
        return None, "Integrity Error"
    except Exception as e:
        db.session.rollback()
        return None, str(e)
    

def update_record(item, validated_data):
    try:
        for k, v in validated_data.items():
            if hasattr(item, k):
                setattr(item, k, v)
        
        db.session.commit()
        return item, None
    except IntegrityError:
        db.session.rollback()
        return None, "Integrity Error"
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def delete_record(Model, item_id):
    try:
        item = db.get_or_404(Model, item_id)
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False
