from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from .services import crud_service
from .services import reporting_service
from .services.crud_service import get_model_and_schema
import requests
from .models import db, MODEL_MAP
import pandas as pd
from .models import (
    PlantLogSchema,
    PortLogSchema,
    TrainLogSchema,
    VesselCostSchema,
    PortTariffSchema,
    VesselDelayHistorySchema
)



bp = Blueprint('api', __name__, url_prefix='/api/main/v1')

# Map table names to existing schemas
TABLE_SCHEMAS = {
    'plants': PlantLogSchema,
    'ports': PortLogSchema,
    'trains': TrainLogSchema,
    'vessels': VesselCostSchema,
    'port_tariffs': PortTariffSchema,
    'vessel_delay_history': VesselDelayHistorySchema
}

# --- Utility: Standardize response output ---

def serialize_item(item, Schema):
    """Converts a SQLAlchemy model instance to a dictionary using Pydantic schema."""
    if item is None:
        return None
    return Schema.from_orm(item).dict()

# --- 1. Generic CRUD API Endpoints ---

@bp.route('/data/<string:table_name>', methods=['GET'])
def get_all_records(table_name):
    """Fetches all records for a given table."""
    items, Schema, _ = crud_service.fetch_all_records(table_name)
    
    if items is None:
        return jsonify({"message": f"Table '{table_name}' not supported or does not exist."}), 404
    
    serialized_items = [serialize_item(item, Schema) for item in items]
    return jsonify({"data": serialized_items}), 200


@bp.route('/data/<string:table_name>/<int:item_id>', methods=['GET'])
def get_one_record(table_name, item_id):
    """Fetches a single record by ID for a given table."""
    try:
        item, Schema = crud_service.fetch_one_record(table_name, item_id)
    except Exception:
        # db.get_or_404 handles the 404 internally if not found
        return jsonify({"message": f"Record with ID {item_id} not found in {table_name}."}), 404

    if item is None:
        # Should be caught by db.get_or_404, but acts as a safeguard
        return jsonify({"message": f"Table '{table_name}' not supported."}), 404
    
    return jsonify({"data": serialize_item(item, Schema)}), 200


@bp.route('/data/<string:table_name>', methods=['POST'])
def create_record(table_name):
    """Creates a single record after Pydantic validation."""
    data = request.get_json()
    Model, Schema, _ = get_model_and_schema(table_name)
    
    if not Model:
        return jsonify({"message": f"Table '{table_name}' not supported."}), 404
        
    try:
        # 1. Validation happens here in the Controller
        validated_data = Schema(**data).dict()
    except ValidationError as e:
        return jsonify({"message": "Validation Error", "errors": e.errors()}), 400

    # 2. Persistence delegated to the Service Layer
    obj, error = crud_service.insert_record(Model, validated_data)

    if error:
        status_code = 409 if "Integrity Error" in error else 500
        return jsonify({"message": f"Database Error: {error}"}), status_code
        
    return jsonify({"data": serialize_item(obj, Schema)}), 201


@bp.route('/data/<string:table_name>/bulk', methods=['POST'])
def create_bulk_records(table_name):
    """Creates multiple records, skipping invalid items (Controller decision)."""
    data_list = request.get_json()
    if not isinstance(data_list, list):
        return jsonify({"message": "Bulk upload requires a list of records."}), 400

    Model, Schema, _ = get_model_and_schema(table_name)
    if not Model:
        return jsonify({"message": f"Table '{table_name}' not supported."}), 404

    inserted_items = []
    failed_items = []

    # 1. Loop and validation is handled in the Controller
    for index, data in enumerate(data_list):
        try:
            validated_data = Schema(**data).dict(exclude_unset=True)
            
            # 2. Persistence delegated to the Service Layer (single insert per loop)
            obj, error = crud_service.insert_record(Model, validated_data)

            if obj:
                inserted_items.append(serialize_item(obj, Schema))
            else:
                failed_items.append({"index": index, "reason": error, "data": data})

        except ValidationError as e:
            failed_items.append({"index": index, "reason": "Validation Error", "errors": e.errors()})
        except Exception as e:
            failed_items.append({"index": index, "reason": f"Unknown Error: {str(e)}", "data": data})

    # Return structured response summarizing successes and failures
    if inserted_items or failed_items:
        return jsonify({
            "message": "Bulk insert process completed.",
            "success_count": len(inserted_items),
            "failure_count": len(failed_items),
            "inserted": inserted_items,
            "failed": failed_items
        }), 207 if failed_items else 201 # 207 Multi-Status for partial success
    else:
        return jsonify({"message": "No valid records were provided."}), 400


@bp.route('/data/<string:table_name>/<int:item_id>', methods=['PUT'])
def update_record_route(table_name, item_id):
    """Updates a single record by ID after Pydantic validation."""
    data = request.get_json()
    Model, Schema, updateSchema = get_model_and_schema(table_name)

    if not Model:
        return jsonify({"message": f"Table '{table_name}' not supported."}), 404

    try:
        # 1. Validation happens here in the Controller (partial update schema)
        validated_data = updateSchema(**data).dict(exclude_unset=True)
    except ValidationError as e:
        return jsonify({"message": "Validation Error", "errors": e.errors()}), 400
    
    # 2. Fetch the existing item using the Service's logic (or db.get_or_404)
    try:
        item, _ = crud_service.fetch_one_record(table_name, item_id)
    except Exception:
        return jsonify({"message": f"Record with ID {item_id} not found."}), 404
        
    # 3. Persistence delegated to the Service Layer
    updated_obj, error = crud_service.update_record(item, validated_data)

    if error:
        return jsonify({"message": f"Database Error: {error}"}), 500
        
    return jsonify({"data": serialize_item(updated_obj, Schema)}), 200


@bp.route('/data/<string:table_name>/<int:item_id>', methods=['DELETE'])
def delete_record_route(table_name, item_id):
    """Deletes a single record by ID."""
    Model, _, _= get_model_and_schema(table_name)
    
    if not Model:
        return jsonify({"message": f"Table '{table_name}' not supported."}), 404

    # The service handles fetching and deleting, raising 404 if necessary
    try:
        success = crud_service.delete_record(Model, item_id)
    except Exception:
        return jsonify({"message": f"Record with ID {item_id} not found in {table_name}."}), 404
        
    if success:
        return jsonify({"message": "Record deleted successfully"}), 204
    else:
        # Fallback for other deletion failures
        return jsonify({"message": "Failed to delete record due to database error."}), 500


# --- 2. Specialized Reporting/Analytics API Endpoints ---

@bp.route('/reports/last-n/<string:table_name>/<int:n>', methods=['GET'])
def get_last_n_records(table_name, n):
    """Fetches the last N records inserted for a given table."""
    items, Schema = reporting_service.fetch_last_n_records(table_name, n)
    
    if items is None:
        return jsonify({"message": f"Table '{table_name}' not supported."}), 404

    serialized_items = [serialize_item(item, Schema) for item in items]
    return jsonify({"data": serialized_items}), 200


@bp.route('/reports/range/<string:table_name>', methods=['GET'])
def get_records_by_range(table_name):
    """Fetches records between a specified start_date and end_date."""
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    if not start_date or not end_date:
        return jsonify({"message": "Missing 'start' and 'end' query parameters."}), 400

    items, Schema_or_Error = reporting_service.fetch_records_by_range(table_name, start_date, end_date)
    
    if items is None:
        # Schema_or_Error contains the error message if the model is unsupported or lacks a 'date' column
        return jsonify({"message": Schema_or_Error}), 404 if "Table" in Schema_or_Error else 400

    serialized_items = [serialize_item(item, Schema_or_Error) for item in items]
    return jsonify({"data": serialized_items}), 200


@bp.route('/reports/active-rakes', methods=['GET'])
def get_active_rakes_route():
    """Returns all train rakes that have started but not ended."""
    items = reporting_service.get_active_rakes()
    
    # We must retrieve the Schema for serialization dynamically
    _, Schema, _ = get_model_and_schema('train_log') 
    
    serialized_items = [serialize_item(item, Schema) for item in items]
    return jsonify({"data": serialized_items}), 200


@bp.route('/reports/plant-last-logs', methods=['GET'])
def get_plant_last_logs_route():
    """Returns the last log entry for each plant."""
    items = reporting_service.get_plant_last_logs()
    
    _, Schema, _ = get_model_and_schema('plant_log')
    
    serialized_items = [serialize_item(item, Schema) for item in items]
    return jsonify({"data": serialized_items}), 200


@bp.route('/reports/port-last-logs', methods=['GET'])
def get_port_last_logs_route():
    """Returns the last log entry for each port."""
    items = reporting_service.get_port_last_logs()
    
    _, Schema, _ = get_model_and_schema('port_log')
    
    serialized_items = [serialize_item(item, Schema) for item in items]
    return jsonify({"data": serialized_items}), 200


@bp.route('/reports/vessels-docked', methods=['GET'])
def get_vessels_docked_route():
    """Returns all vessels currently docked (no departure time)."""
    items = reporting_service.get_vessels_docked()
    _, Schema, _ = get_model_and_schema('vessel_delay_history')
    
    serialized_items = [serialize_item(item, Schema) for item in items]
    return jsonify({"data": serialized_items}), 200



# ---------------- Proxy Route for AI Training ----------------

AI_SERVER_URL = "http://127.0.0.1:6000/api/ai/v1"

# Trigger training via main server
@bp.route("/trigger-training", methods=["POST"])
def trigger_training_proxy():
    try:
        resp = requests.post(f"{AI_SERVER_URL}/trigger-training", json={}, timeout=5)
        try:
            return jsonify(resp.json())
        except ValueError:
            return jsonify({
                "message": "AI server returned invalid JSON",
                "status_code": resp.status_code,
                "response_text": resp.text
            }), 502
    except requests.RequestException as e:
        return jsonify({"message": "Failed to reach AI server", "error": str(e)}), 500

# Get training status via main server
@bp.route("/training-status", methods=["GET"])
def training_status_proxy():
    try:
        resp = requests.get(f"{AI_SERVER_URL}/training-status", timeout=5)
        try:
            return jsonify(resp.json())
        except ValueError:
            return jsonify({
                "message": "AI server returned invalid JSON",
                "status_code": resp.status_code,
                "response_text": resp.text
            }), 502
    except requests.RequestException as e:
        return jsonify({"message": "Failed to reach AI server", "error": str(e)}), 500


# ------------------- Excel Upload Endpoint -------------------

@bp.route('/data/upload-excel', methods=['POST'])
def upload_excel():
    table = request.form.get('table')
    file = request.files.get('file')

    if not table or not file:
        return jsonify({"error": "Table and file are required"}), 400

    # Get the corresponding schema and model
    Schema = TABLE_SCHEMAS.get(table)
    if not Schema:
        return jsonify({"error": f"No schema found for table '{table}'"}), 400

    Model, _, _ = crud_service.get_model_and_schema(table)
    if not Model:
        return jsonify({"error": f"No model found for table '{table}'"}), 400

    # Read Excel file
    try:
        df = pd.read_excel(file)
    except Exception as e:
        return jsonify({"error": f"Failed to read Excel: {str(e)}"}), 400

    inserted_count = 0
    failed_rows = []

    for i, row in df.iterrows():
        data = row.to_dict()

        # Convert columns if needed
        if 'rake_id' in data:
            data['rake_id'] = str(data['rake_id'])

        try:
            # Pydantic validation
            validated_data = Schema(**data).dict(exclude_unset=True)

            # Insert into DB
            obj, error = crud_service.insert_record(Model, validated_data)
            if obj:
                inserted_count += 1
            else:
                failed_rows.append({"row": i + 2, "error": error, "data": data})

        except Exception as e:
            failed_rows.append({"row": i + 2, "error": str(e), "data": data})

    status_code = 201 if not failed_rows else 207  # 207 = partial success
    return jsonify({
        "message": f"Excel file uploaded for table '{table}'",
        "rows_uploaded": inserted_count,
        "rows_failed": failed_rows
    }), status_code
