from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import numpy as np
from collections import deque

from federated_core import validate_update, weighted_fedavg
import asyncio
import json
import csv
import io
import copy
import threading

# River for online ML
from river import anomaly, preprocessing, drift

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Self-Evolving AI Engine - Model 2: Federated Learning + Drift Detection")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONCEPT DRIFT DETECTION (ADWIN + Page-Hinkley)
# =============================================================================

class ConceptDriftDetector:
    """Comprehensive drift detection using ADWIN and Page-Hinkley algorithms"""
    
    def __init__(self):
        # ADWIN detector - adaptive windowing for detecting distribution changes
        self.adwin = drift.ADWIN(delta=0.002)
        
        # Page-Hinkley detector - for gradual drift detection
        self.page_hinkley = drift.PageHinkley(
            min_instances=30,
            delta=0.005,
            threshold=50,
            alpha=0.9999
        )
        
        self.drift_events = deque(maxlen=100)
        self.drift_count = 0
        self.last_drift_time = None
        self.in_drift = False
        
        # Statistics
        self.total_samples = 0
        self.adwin_drifts = 0
        self.ph_drifts = 0
        
    def update(self, value: float) -> Dict[str, Any]:
        """Update drift detectors and check for drift"""
        self.total_samples += 1
        
        # Update both detectors
        self.adwin.update(value)
        self.page_hinkley.update(value)
        
        adwin_drift = self.adwin.drift_detected
        ph_drift = self.page_hinkley.drift_detected
        
        drift_detected = False
        drift_type = None
        
        if adwin_drift:
            drift_detected = True
            drift_type = "ADWIN"
            self.adwin_drifts += 1
            
        if ph_drift:
            drift_detected = True
            drift_type = "PAGE_HINKLEY" if not adwin_drift else "BOTH"
            self.ph_drifts += 1
            
        if drift_detected:
            self.drift_count += 1
            self.last_drift_time = datetime.now(timezone.utc).isoformat()
            self.in_drift = True
            
            event = {
                "id": str(uuid.uuid4()),
                "type": drift_type,
                "timestamp": self.last_drift_time,
                "sample_number": self.total_samples,
                "value": round(value, 4)
            }
            self.drift_events.append(event)
        else:
            self.in_drift = False
            
        return {
            "drift_detected": drift_detected,
            "drift_type": drift_type,
            "in_drift": self.in_drift,
            "total_drifts": self.drift_count,
            "adwin_drifts": self.adwin_drifts,
            "ph_drifts": self.ph_drifts
        }
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "total_samples": self.total_samples,
            "drift_count": self.drift_count,
            "adwin_drifts": self.adwin_drifts,
            "ph_drifts": self.ph_drifts,
            "in_drift": self.in_drift,
            "last_drift_time": self.last_drift_time
        }
    
    def get_events(self, limit: int = 20) -> List[Dict]:
        return list(self.drift_events)[-limit:]
    
    def reset(self):
        self.__init__()

# =============================================================================
# FEDERATED LEARNING NODE
# =============================================================================

class FederatedNode:
    """Simulated federated learning node with local model and data"""
    
    def __init__(self, node_id: str, name: str, location: str, seed: int = 0):
        self.node_id = node_id
        self.rng = np.random.default_rng(seed)
        self.name = name
        self.location = location
        self.created_at = datetime.now(timezone.utc)
        
        # Local model
        self.model = preprocessing.StandardScaler() | anomaly.HalfSpaceTrees(
            n_trees=25,
            height=8,
            window_size=250
        )
        
        # Local drift detector
        self.drift_detector = ConceptDriftDetector()
        
        # Statistics
        self.data_points_processed = 0
        self.local_scores = deque(maxlen=100)
        self.status = "ONLINE"
        self.last_update = datetime.now(timezone.utc)
        
        # Model weights (simulated)
        self.weights = self.rng.standard_normal(25).tolist()  # Demo-only vector
        
        # Data characteristics
        self.mean_shift = float(self.rng.uniform(-0.5, 0.5))  # Simulate different data distributions
        self.variance_scale = float(self.rng.uniform(0.8, 1.2))
        
    def generate_local_data(self, inject_drift: bool = False) -> List[float]:
        """Generate data with node-specific characteristics"""
        base_data = self.rng.normal(loc=self.mean_shift, scale=self.variance_scale, size=5)
        
        if inject_drift:
            # Shift the distribution significantly
            drift_shift = self.rng.normal(5, 1, size=5)
            base_data = base_data + drift_shift
            
        return base_data.tolist()
    
    def process_data(self, data: List[float]) -> Dict[str, Any]:
        """Process data point locally"""
        data_dict = {f"feature_{i}": val for i, val in enumerate(data)}
        
        # Score and learn
        score = self.model.score_one(data_dict)
        self.model.learn_one(data_dict)
        
        self.data_points_processed += 1
        self.local_scores.append(score)
        self.last_update = datetime.now(timezone.utc)
        
        # Update drift detector
        drift_status = self.drift_detector.update(score)
        
        # Update simulated weights based on learning
        self.weights = [w + float(self.rng.normal(0, 0.01)) for w in self.weights]
        
        avg_score = float(np.mean(list(self.local_scores))) if self.local_scores else 0
        
        return {
            "score": score,
            "avg_score": avg_score,
            "drift_status": drift_status,
            "data_points": self.data_points_processed
        }
    
    def get_weights(self) -> List[float]:
        """Get current model weights for aggregation"""
        return self.weights
    
    def set_weights(self, weights: List[float]):
        """Set weights from global model"""
        self.weights = weights
        
    def get_status(self) -> Dict[str, Any]:
        scores = list(self.local_scores)
        avg_score = float(np.mean(scores)) if scores else 0
        std_score = float(np.std(scores)) if len(scores) > 1 else 0
        
        # Determine node health
        if avg_score > 0.8:
            health = "CRITICAL"
        elif avg_score > 0.6:
            health = "WARNING"
        else:
            health = "HEALTHY"
            
        return {
            "node_id": self.node_id,
            "name": self.name,
            "location": self.location,
            "status": self.status,
            "health": health,
            "data_points_processed": self.data_points_processed,
            "avg_score": round(avg_score, 4),
            "std_score": round(std_score, 4),
            "drift_status": self.drift_detector.get_status(),
            "last_update": self.last_update.isoformat(),
            "uptime_seconds": (datetime.now(timezone.utc) - self.created_at).total_seconds()
        }

# =============================================================================
# FEDERATED AGGREGATOR
# =============================================================================

class FederatedAggregator:
    """Aggregates model updates from federated nodes (FedAvg implementation)"""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.pending_updates: Dict[str, Dict[str, Any]] = {}
        self.global_weights = None
        self.aggregation_rounds = 0
        self.last_aggregation = None
        self.nodes: Dict[str, FederatedNode] = {}
        self.aggregation_history = deque(maxlen=50)
        
        # Initialize nodes
        self._initialize_nodes()
        
    def _initialize_nodes(self):
        """Create simulated federated nodes"""
        node_configs = [
            ("node_1", "Edge Node Alpha", "Data Center A"),
            ("node_2", "Edge Node Beta", "Data Center B"),
            ("node_3", "Edge Node Gamma", "IoT Gateway 1"),
            ("node_4", "Edge Node Delta", "Mobile Edge"),
            ("node_5", "Edge Node Epsilon", "Cloud Region"),
        ]
        
        for index, (node_id, name, location) in enumerate(node_configs):
            self.nodes[node_id] = FederatedNode(
                node_id, name, location, seed=self.seed + index
            )
            
        # Initialize global weights as average of node weights
        self._aggregate_weights()
        
    def _aggregate_weights(self) -> List[float]:
        """FedAvg: Average weights from all nodes"""
        if not self.nodes:
            return []
            
        updates = [
            {"weights": node.get_weights(), "sample_count": node.data_points_processed or 1}
            for node in self.nodes.values()
        ]
        aggregated = weighted_fedavg(updates, expected_dimension=len(updates[0]["weights"]))
        num_nodes = len(updates)
        self.global_weights = aggregated
        self.aggregation_rounds += 1
        self.last_aggregation = datetime.now(timezone.utc)
        
        self.aggregation_history.append({
            "round": self.aggregation_rounds,
            "timestamp": self.last_aggregation.isoformat(),
            "nodes_participated": num_nodes,
            "weight_norm": float(np.linalg.norm(aggregated))
        })
        
        return aggregated
    
    def distribute_global_model(self):
        """Distribute global model weights to all nodes"""
        if self.global_weights:
            for node in self.nodes.values():
                # Add small noise to simulate local adaptation
                # Demo distribution copies the global vector without fabricating training noise.
                node.set_weights(list(self.global_weights))
                
    def submit_local_update(self, node_id: str, weights: List[float], sample_count: int) -> Dict[str, Any]:
        """Accept a validated vector produced by a separately running local trainer."""
        if node_id not in self.nodes:
            raise KeyError(f"Unknown federated node: {node_id}")
        normalized = validate_update(weights, sample_count, expected_dimension=25)
        self.pending_updates[node_id] = {
            "weights": normalized,
            "sample_count": sample_count,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }
        return {
            "node_id": node_id,
            "sample_count": sample_count,
            "dimension": len(normalized),
            "status": "ACCEPTED_PENDING_AGGREGATION",
        }

    def aggregate_submitted_updates(self) -> List[float]:
        """Aggregate only explicitly submitted local updates; never mix demo vectors."""
        if not self.pending_updates:
            raise ValueError("no submitted local updates are available")
        aggregated = weighted_fedavg(self.pending_updates.values(), expected_dimension=25)
        self.global_weights = aggregated
        self.aggregation_rounds += 1
        self.last_aggregation = datetime.now(timezone.utc)
        self.aggregation_history.append({
            "round": self.aggregation_rounds,
            "timestamp": self.last_aggregation.isoformat(),
            "nodes_participated": len(self.pending_updates),
            "total_samples": sum(x["sample_count"] for x in self.pending_updates.values()),
            "weight_norm": float(np.linalg.norm(aggregated)),
            "mode": "submitted_local_updates",
        })
        for node_id in self.pending_updates:
            self.nodes[node_id].set_weights(list(aggregated))
        self.pending_updates.clear()
        return aggregated

    def process_round(self, inject_drift: bool = False, drift_node_id: Optional[str] = None) -> Dict[str, Any]:
        """Process one federated learning round"""
        results = {}
        
        for node_id, node in self.nodes.items():
            # Generate local data (with drift for specific node if requested)
            should_inject = inject_drift and (drift_node_id is None or drift_node_id == node_id)
            data = node.generate_local_data(inject_drift=should_inject)
            
            # Process locally
            result = node.process_data(data)
            results[node_id] = result
            
        # Aggregate weights periodically (every 10 rounds for demo)
        if self.aggregation_rounds % 10 == 0 or inject_drift:
            self._aggregate_weights()
            self.distribute_global_model()
            
        return {
            "round": self.aggregation_rounds,
            "node_results": results,
            "global_weight_norm": float(np.linalg.norm(self.global_weights)) if self.global_weights else 0
        }
    
    def get_global_status(self) -> Dict[str, Any]:
        node_statuses = {nid: node.get_status() for nid, node in self.nodes.items()}
        
        # Calculate global metrics
        total_data_points = sum(n.data_points_processed for n in self.nodes.values())
        avg_scores = [np.mean(list(n.local_scores)) if n.local_scores else 0 for n in self.nodes.values()]
        global_avg_score = float(np.mean(avg_scores)) if avg_scores else 0
        
        # Count drift events across nodes
        total_drift_events = sum(n.drift_detector.drift_count for n in self.nodes.values())
        
        # Determine global health
        unhealthy_nodes = sum(1 for n in self.nodes.values() if list(n.local_scores) and np.mean(list(n.local_scores)) > 0.6)
        if unhealthy_nodes >= 3:
            global_health = "CRITICAL"
        elif unhealthy_nodes >= 1:
            global_health = "DEGRADED"
        else:
            global_health = "HEALTHY"
            
        return {
            "mode": "simulated_demo",
            "is_production_federated_learning": False,
            "global_health": global_health,
            "total_nodes": len(self.nodes),
            "online_nodes": sum(1 for n in self.nodes.values() if n.status == "ONLINE"),
            "aggregation_rounds": self.aggregation_rounds,
            "last_aggregation": self.last_aggregation.isoformat() if self.last_aggregation else None,
            "total_data_points": total_data_points,
            "global_avg_score": round(global_avg_score, 4),
            "total_drift_events": total_drift_events,
            "nodes": node_statuses
        }
    
    def reset(self):
        """Reset the federated system"""
        self.global_weights = None
        self.aggregation_rounds = 0
        self.last_aggregation = None
        self.aggregation_history.clear()
        self._initialize_nodes()

# =============================================================================
# ONLINE LEARNING MODEL (Global - for backward compatibility)
# =============================================================================

class OnlineModel:
    def __init__(self):
        self.model = preprocessing.StandardScaler() | anomaly.HalfSpaceTrees(
            n_trees=25,
            height=8,
            window_size=250
        )
        self.data_points_processed = 0
        self.created_at = datetime.now(timezone.utc)
        
    def predict_and_learn(self, x: List[float]) -> float:
        """Process data point: get anomaly score and learn from it"""
        data_dict = {f"feature_{i}": val for i, val in enumerate(x)}
        score = self.model.score_one(data_dict)
        self.model.learn_one(data_dict)
        self.data_points_processed += 1
        return score

# =============================================================================
# SELF-MONITORING MODULE
# =============================================================================

class SystemMonitor:
    def __init__(self, window_size: int = 50):
        self.error_window = deque(maxlen=window_size)
        self.score_history = deque(maxlen=500)
        self.alerts = deque(maxlen=100)
        self.threshold_unstable = 0.8
        self.threshold_warning = 0.6
        
    def update(self, score: float) -> Dict[str, Any]:
        """Update monitoring metrics and return health status"""
        self.error_window.append(score)
        self.score_history.append({
            "score": score,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        avg_score = float(np.mean(list(self.error_window))) if self.error_window else 0
        std_score = float(np.std(list(self.error_window))) if len(self.error_window) > 1 else 0
        
        if avg_score > self.threshold_unstable:
            health = "UNSTABLE"
            self._add_alert("System health is UNSTABLE - High anomaly scores detected", "critical")
        elif avg_score > self.threshold_warning:
            health = "WARNING"
            self._add_alert("System health is WARNING - Elevated anomaly scores", "warning")
        else:
            health = "STABLE"
        
        confidence = max(0, min(1, 1 - (std_score / 2)))
        
        return {
            "avg_score": round(avg_score, 4),
            "std_score": round(std_score, 4),
            "health": health,
            "confidence": round(confidence, 4),
            "samples_in_window": len(self.error_window)
        }
    
    def _add_alert(self, message: str, severity: str):
        now = datetime.now(timezone.utc).isoformat()
        if self.alerts:
            last_alert = self.alerts[-1]
            if last_alert["message"] == message:
                return
        self.alerts.append({
            "id": str(uuid.uuid4()),
            "message": message,
            "severity": severity,
            "timestamp": now
        })
    
    def get_alerts(self, limit: int = 20) -> List[Dict]:
        return list(self.alerts)[-limit:]
    
    def get_score_history(self, limit: int = 100) -> List[Dict]:
        return list(self.score_history)[-limit:]
    
    def clear_alerts(self):
        self.alerts.clear()
    
    def get_health(self) -> Dict[str, Any]:
        """Calculate and return current health status without updating scores"""
        scores = list(self.error_window)
        avg_score = float(np.mean(scores)) if scores else 0
        std_score = float(np.std(scores)) if len(scores) > 1 else 0
        
        if avg_score > self.threshold_unstable:
            health = "UNSTABLE"
        elif avg_score > self.threshold_warning:
            health = "WARNING"
        else:
            health = "STABLE"
        
        confidence = max(0, min(1, 1 - (std_score / 2)))
        
        return {
            "health": health,
            "avg_score": round(avg_score, 4),
            "std_score": round(std_score, 4),
            "confidence": round(confidence, 4),
            "samples": len(scores)
        }

# =============================================================================
# DATA STREAMING
# =============================================================================

class DataStreamManager:
    def __init__(self):
        self.mode = "simulated"
        self.csv_data = []
        self.csv_index = 0
        self.is_streaming = False
        self.anomaly_injection_rate = 0.05
        self.drift_injection_active = False
        self.latest_prediction = None  # Store latest prediction for XAI explanations
        
    def set_mode(self, mode: str, csv_data: Optional[List[List[float]]] = None):
        self.mode = mode
        if csv_data:
            self.csv_data = csv_data
            self.csv_index = 0
    
    def set_drift_injection(self, active: bool):
        self.drift_injection_active = active
    
    def generate_data(self) -> List[float]:
        if self.mode == "csv" and self.csv_data:
            if self.csv_index >= len(self.csv_data):
                self.csv_index = 0
            data = self.csv_data[self.csv_index]
            self.csv_index += 1
            return data
        else:
            # Base data
            if self.drift_injection_active:
                # Significantly shifted distribution for drift
                data = np.random.normal(loc=5, scale=2, size=5).tolist()
            else:
                data = np.random.normal(loc=0, scale=1, size=5).tolist()
                if np.random.rand() < self.anomaly_injection_rate:
                    anomaly_offset = np.random.normal(5, 2, size=5)
                    data = [d + a for d, a in zip(data, anomaly_offset)]
            return data

# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

model = OnlineModel()
monitor = SystemMonitor()
stream_manager = DataStreamManager()
drift_detector = ConceptDriftDetector()
federated_aggregator = FederatedAggregator()

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class PredictionInput(BaseModel):
    data: List[float] = Field(..., description="Feature values for prediction")

class PredictionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    anomaly_score: float
    is_anomaly: bool
    system_status: Dict[str, Any]
    data_point: List[float]
    timestamp: str
    drift_status: Optional[Dict[str, Any]] = None

class StreamConfigInput(BaseModel):
    mode: str = Field(..., description="Data source mode: 'simulated' or 'csv'")

class DriftInjectionInput(BaseModel):
    active: bool = Field(..., description="Whether to inject drift")
    node_id: Optional[str] = Field(None, description="Specific node to inject drift (optional)")

class FederatedLocalUpdateInput(BaseModel):
    node_id: str = Field(..., min_length=1, max_length=128)
    weights: List[float] = Field(..., min_length=25, max_length=25)
    sample_count: int = Field(..., gt=0)

class ModelStats(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data_points_processed: int
    created_at: str
    uptime_seconds: float

# =============================================================================
# API ENDPOINTS - MODEL 1 (Original)
# =============================================================================

@api_router.get("/")
async def root():
    return {"message": "Self-Evolving AI Engine - Model 2: Federated Learning + Drift Detection Active"}

@api_router.post("/predict", response_model=PredictionResponse)
async def predict(input_data: PredictionInput):
    score = model.predict_and_learn(input_data.data)
    status = monitor.update(score)
    drift_status = drift_detector.update(score)
    
    record = {
        "id": str(uuid.uuid4()),
        "anomaly_score": score,
        "is_anomaly": score > 0.7,
        "data_point": input_data.data,
        "system_status": status,
        "drift_status": drift_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.predictions.insert_one(record)
    
    return PredictionResponse(
        anomaly_score=round(score, 4),
        is_anomaly=score > 0.7,
        system_status=status,
        data_point=input_data.data,
        timestamp=record["timestamp"],
        drift_status=drift_status
    )

@api_router.get("/stream/next")
async def get_next_stream_data():
    data = stream_manager.generate_data()
    score = model.predict_and_learn(data)
    status = monitor.update(score)
    drift_status = drift_detector.update(score)
    
    # Also process in federated system
    fed_result = federated_aggregator.process_round(
        inject_drift=stream_manager.drift_injection_active
    )
    
    record = {
        "id": str(uuid.uuid4()),
        "anomaly_score": score,
        "is_anomaly": score > 0.7,
        "data_point": data,
        "system_status": status,
        "drift_status": drift_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.predictions.insert_one(record)
    
    # Store latest prediction for XAI explanations
    stream_manager.latest_prediction = {
        "anomaly_score": round(score, 4),
        "is_anomaly": score > 0.7,
        "data_point": [round(d, 4) for d in data],
        "timestamp": record["timestamp"]
    }
    
    return {
        "anomaly_score": round(score, 4),
        "is_anomaly": score > 0.7,
        "system_status": status,
        "data_point": [round(d, 4) for d in data],
        "timestamp": record["timestamp"],
        "drift_status": drift_status,
        "federated_round": fed_result["round"]
    }

@api_router.post("/stream/config")
async def configure_stream(config: StreamConfigInput):
    if config.mode not in ["simulated", "csv"]:
        raise HTTPException(status_code=400, detail="Mode must be 'simulated' or 'csv'")
    stream_manager.set_mode(config.mode)
    return {"message": f"Stream mode set to: {config.mode}", "mode": config.mode}

@api_router.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        contents = await file.read()
        decoded = contents.decode('utf-8')
        reader = csv.reader(io.StringIO(decoded))
        
        csv_data = []
        for row in reader:
            try:
                numeric_row = [float(val) for val in row if val.strip()]
                if numeric_row:
                    csv_data.append(numeric_row)
            except ValueError:
                continue
        
        if not csv_data:
            raise HTTPException(status_code=400, detail="No valid numeric data found in CSV")
        
        stream_manager.set_mode("csv", csv_data)
        
        return {
            "message": "CSV uploaded successfully",
            "rows_loaded": len(csv_data),
            "features_per_row": len(csv_data[0]) if csv_data else 0,
            "mode": "csv"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

@api_router.get("/health")
async def get_health():
    health_status = monitor.get_health()
    return {
        **health_status,
        "samples_in_window": health_status["samples"],
        "data_points_processed": model.data_points_processed,
        "stream_mode": stream_manager.mode,
        "drift_injection_active": stream_manager.drift_injection_active
    }

@api_router.get("/alerts")
async def get_alerts(limit: int = 20):
    return {"alerts": monitor.get_alerts(limit)}

@api_router.delete("/alerts")
async def clear_alerts():
    monitor.clear_alerts()
    return {"message": "Alerts cleared"}

@api_router.get("/history")
async def get_history(limit: int = 100):
    return {"history": monitor.get_score_history(limit)}

@api_router.get("/model/stats")
async def get_model_stats():
    now = datetime.now(timezone.utc)
    uptime = (now - model.created_at).total_seconds()
    
    return ModelStats(
        data_points_processed=model.data_points_processed,
        created_at=model.created_at.isoformat(),
        uptime_seconds=uptime
    )

@api_router.post("/model/reset")
async def reset_model():
    global model, monitor, drift_detector, federated_aggregator
    model = OnlineModel()
    monitor = SystemMonitor()
    drift_detector = ConceptDriftDetector()
    federated_aggregator = FederatedAggregator()
    stream_manager.set_drift_injection(False)
    
    return {"message": "Model, monitor, drift detector, and federated system reset successfully"}

@api_router.get("/export/json")
async def export_json(limit: int = 500):
    predictions = await db.predictions.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    
    export_data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "model_stats": {
            "data_points_processed": model.data_points_processed,
            "created_at": model.created_at.isoformat()
        },
        "drift_stats": drift_detector.get_status(),
        "federated_stats": {
            "aggregation_rounds": federated_aggregator.aggregation_rounds,
            "total_nodes": len(federated_aggregator.nodes)
        },
        "current_health": {
            "avg_score": round(float(np.mean(list(monitor.error_window))) if monitor.error_window else 0, 4),
            "samples": len(monitor.error_window)
        },
        "predictions": predictions
    }
    
    return StreamingResponse(
        io.BytesIO(json.dumps(export_data, indent=2).encode()),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=model2_export.json"}
    )

@api_router.get("/export/csv")
async def export_csv(limit: int = 500):
    predictions = await db.predictions.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    
    output = io.StringIO()
    if predictions:
        writer = csv.writer(output)
        writer.writerow(["timestamp", "anomaly_score", "is_anomaly", "health", "confidence", "avg_score", "drift_detected", "data_point"])
        
        for pred in predictions:
            status = pred.get("system_status", {})
            drift = pred.get("drift_status", {})
            writer.writerow([
                pred.get("timestamp", ""),
                pred.get("anomaly_score", ""),
                pred.get("is_anomaly", ""),
                status.get("health", ""),
                status.get("confidence", ""),
                status.get("avg_score", ""),
                drift.get("drift_detected", False),
                json.dumps(pred.get("data_point", []))
            ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=model2_export.csv"}
    )

# =============================================================================
# API ENDPOINTS - MODEL 2 (Drift Detection)
# =============================================================================

@api_router.get("/drift/status")
async def get_drift_status():
    """Get current drift detection status"""
    return drift_detector.get_status()

@api_router.get("/drift/events")
async def get_drift_events(limit: int = 20):
    """Get recent drift events"""
    return {"events": drift_detector.get_events(limit)}

@api_router.post("/drift/inject")
async def inject_drift(config: DriftInjectionInput):
    """Toggle drift injection for demonstration"""
    stream_manager.set_drift_injection(config.active)
    
    if config.active:
        # Also inject into specific federated node if specified
        if config.node_id and config.node_id in federated_aggregator.nodes:
            # Process several rounds with drift in specified node
            for _ in range(5):
                federated_aggregator.process_round(inject_drift=True, drift_node_id=config.node_id)
        else:
            # Inject into all nodes
            for _ in range(5):
                federated_aggregator.process_round(inject_drift=True)
    
    return {
        "message": f"Drift injection {'activated' if config.active else 'deactivated'}",
        "active": config.active,
        "node_id": config.node_id
    }

@api_router.post("/drift/reset")
async def reset_drift_detector():
    """Reset drift detector"""
    drift_detector.reset()
    return {"message": "Drift detector reset successfully"}

# =============================================================================
# API ENDPOINTS - MODEL 2 (Federated Learning)
# =============================================================================

@api_router.get("/federated/status")
async def get_federated_status():
    """Get global federated learning status"""
    return federated_aggregator.get_global_status()

@api_router.get("/federated/nodes")
async def get_federated_nodes():
    """Get status of all federated nodes"""
    return {
        "nodes": [node.get_status() for node in federated_aggregator.nodes.values()]
    }

@api_router.get("/federated/node/{node_id}")
async def get_federated_node(node_id: str):
    """Get status of specific federated node"""
    if node_id not in federated_aggregator.nodes:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return federated_aggregator.nodes[node_id].get_status()

@api_router.get("/federated/node/{node_id}/drift")
async def get_node_drift_events(node_id: str, limit: int = 20):
    """Get drift events for specific node"""
    if node_id not in federated_aggregator.nodes:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return {"events": federated_aggregator.nodes[node_id].drift_detector.get_events(limit)}

@api_router.post("/federated/updates")
async def submit_federated_update(input_data: FederatedLocalUpdateInput):
    """Submit a client-trained vector. Authentication/enrollment is required before production use."""
    try:
        return federated_aggregator.submit_local_update(
            input_data.node_id, input_data.weights, input_data.sample_count
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

@api_router.post("/federated/aggregate")
async def trigger_aggregation():
    """Aggregate submitted client updates, or clearly labeled demo-node vectors."""
    if federated_aggregator.pending_updates:
        weights = federated_aggregator.aggregate_submitted_updates()
        mode = "submitted_local_updates"
    else:
        weights = federated_aggregator._aggregate_weights()
        mode = "simulated_demo"
    return {
        "message": "Aggregation completed",
        "mode": mode,
        "round": federated_aggregator.aggregation_rounds,
        "weight_norm": float(np.linalg.norm(weights))
    }

@api_router.get("/federated/history")
async def get_aggregation_history(limit: int = 20):
    """Get aggregation history"""
    return {"history": list(federated_aggregator.aggregation_history)[-limit:]}

@api_router.post("/federated/reset")
async def reset_federated():
    """Reset federated learning system"""
    federated_aggregator.reset()
    return {"message": "Federated system reset successfully"}

# =============================================================================
# MODEL-3: DIGITAL TWIN SIMULATOR
# =============================================================================

class DigitalTwin:
    """Digital Twin that mirrors AI system states and predicts future behavior"""
    
    def __init__(self):
        self.prediction_history = deque(maxlen=100)
        self.simulation_results = deque(maxlen=50)
        
    def predict_future_health(self, current_scores: List[float], steps_ahead: int = 10) -> List[Dict[str, Any]]:
        """Predict future health states using time-series forecasting"""
        if len(current_scores) < 3:
            # Not enough data for prediction
            return [{"step": i, "predicted_score": 0.0, "confidence": 0.0, "predicted_health": "UNKNOWN"} 
                    for i in range(1, steps_ahead + 1)]
        
        # Simple moving average with trend estimation
        recent_scores = list(current_scores)[-20:]
        avg_score = np.mean(recent_scores)
        
        # Calculate trend
        if len(recent_scores) >= 2:
            trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
        else:
            trend = 0
        
        predictions = []
        for step in range(1, steps_ahead + 1):
            # Predict with trend and some noise
            predicted_score = avg_score + (trend * step)
            predicted_score = max(0, min(1, predicted_score))  # Clip to [0, 1]
            
            # Determine predicted health
            if predicted_score > 0.8:
                predicted_health = "CRITICAL"
                risk_level = "HIGH"
            elif predicted_score > 0.6:
                predicted_health = "WARNING"
                risk_level = "MEDIUM"
            else:
                predicted_health = "STABLE"
                risk_level = "LOW"
            
            # Confidence decreases with distance into future
            confidence = max(0.3, 1.0 - (step * 0.05))
            
            predictions.append({
                "step": step,
                "predicted_score": round(predicted_score, 4),
                "predicted_health": predicted_health,
                "risk_level": risk_level,
                "confidence": round(confidence, 3)
            })
        
        return predictions
    
    def calculate_risk_score(self, node_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk score for a node or global system"""
        avg_score = node_stats.get("avg_score", 0)
        drift_count = node_stats.get("drift_count", 0)
        data_points = node_stats.get("data_points_processed", 0)
        
        # Risk factors
        score_risk = avg_score * 50  # 0-50 points
        drift_risk = min(drift_count * 10, 30)  # 0-30 points
        data_risk = 20 if data_points < 50 else 0  # 0-20 points (low data = risky)
        
        total_risk = score_risk + drift_risk + data_risk
        
        if total_risk > 70:
            risk_category = "CRITICAL"
        elif total_risk > 40:
            risk_category = "HIGH"
        elif total_risk > 20:
            risk_category = "MEDIUM"
        else:
            risk_category = "LOW"
        
        return {
            "risk_score": round(total_risk, 2),
            "risk_category": risk_category,
            "factors": {
                "score_risk": round(score_risk, 2),
                "drift_risk": round(drift_risk, 2),
                "data_risk": round(data_risk, 2)
            }
        }
    
    def simulate_scenario(self, scenario_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run what-if simulation scenarios"""
        results = {
            "scenario": scenario_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "params": params,
            "outcome": {}
        }
        
        if scenario_type == "sustained_drift":
            # Simulate continuous drift
            duration = params.get("duration_minutes", 5)
            drift_intensity = params.get("intensity", 0.5)
            
            # Predict impact
            health_degradation = drift_intensity * duration * 0.1
            expected_health = "CRITICAL" if health_degradation > 0.8 else "WARNING" if health_degradation > 0.5 else "STABLE"
            
            results["outcome"] = {
                "expected_health": expected_health,
                "health_degradation": round(health_degradation, 3),
                "recovery_time_minutes": round(duration * 1.5, 1),
                "recommendation": "Trigger federated aggregation" if health_degradation > 0.6 else "Monitor closely"
            }
        
        elif scenario_type == "node_failure":
            # Simulate node going offline
            failed_nodes = params.get("node_count", 1)
            total_nodes = params.get("total_nodes", 5)
            
            remaining_capacity = (total_nodes - failed_nodes) / total_nodes
            
            results["outcome"] = {
                "remaining_capacity": f"{remaining_capacity * 100:.0f}%",
                "system_stability": "STABLE" if remaining_capacity >= 0.6 else "DEGRADED",
                "data_loss_risk": "HIGH" if remaining_capacity < 0.5 else "LOW",
                "recommendation": "Scale up nodes" if remaining_capacity < 0.6 else "Monitor system"
            }
        
        elif scenario_type == "aggregation_delay":
            # Simulate delayed federated updates
            delay_rounds = params.get("delay_rounds", 10)
            
            performance_loss = min(delay_rounds * 0.05, 0.5)
            
            results["outcome"] = {
                "performance_loss": f"{performance_loss * 100:.1f}%",
                "divergence_risk": "HIGH" if delay_rounds > 20 else "MEDIUM" if delay_rounds > 10 else "LOW",
                "recommendation": "Reduce aggregation interval" if delay_rounds > 15 else "Current interval acceptable"
            }
        
        self.simulation_results.append(results)
        return results

# Initialize Digital Twin
digital_twin = DigitalTwin()

# Pydantic models for Digital Twin
class SimulationInput(BaseModel):
    scenario_type: str = Field(..., description="Type of simulation: sustained_drift, node_failure, aggregation_delay")
    params: Dict[str, Any] = Field(default_factory=dict)

@api_router.get("/twin/predict-health")
async def predict_future_health(steps: int = 10):
    """Predict future health states"""
    current_scores = list(monitor.error_window)
    predictions = digital_twin.predict_future_health(current_scores, steps)
    
    return {
        "current_health": monitor.get_health(),
        "predictions": predictions,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/twin/risk-score")
async def get_risk_score():
    """Calculate current risk score"""
    global_risk = digital_twin.calculate_risk_score({
        "avg_score": float(np.mean(list(monitor.error_window))) if monitor.error_window else 0,
        "drift_count": drift_detector.drift_count,
        "data_points_processed": model.data_points_processed
    })
    
    # Risk scores for each node
    node_risks = {}
    for node_id, node in federated_aggregator.nodes.items():
        node_risks[node_id] = digital_twin.calculate_risk_score({
            "avg_score": float(np.mean(list(node.local_scores))) if node.local_scores else 0,
            "drift_count": node.drift_detector.drift_count,
            "data_points_processed": node.data_points_processed
        })
    
    return {
        "global_risk": global_risk,
        "node_risks": node_risks,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/twin/simulate")
async def run_simulation(input_data: SimulationInput):
    """Run what-if scenario simulation"""
    result = digital_twin.simulate_scenario(input_data.scenario_type, input_data.params)
    return result

@api_router.get("/twin/comparison")
async def get_live_vs_predicted():
    """Compare live state vs predicted state"""
    current_scores = list(monitor.error_window)
    
    # Get actual current health
    health_status = monitor.get_health()
    actual_health = health_status["health"]  # Extract just the health string
    actual_score = float(np.mean(current_scores)) if current_scores else 0
    
    # Get prediction from 10 steps ago (if we had made one)
    predictions = digital_twin.predict_future_health(current_scores[-20:-10] if len(current_scores) >= 20 else [], steps_ahead=10)
    predicted_health = predictions[-1]["predicted_health"] if predictions else "UNKNOWN"
    predicted_score = predictions[-1]["predicted_score"] if predictions else 0
    
    accuracy = 1.0 - abs(actual_score - predicted_score)
    
    return {
        "live_state": {
            "health": actual_health,
            "score": round(actual_score, 4)
        },
        "predicted_state": {
            "health": predicted_health,
            "score": round(predicted_score, 4)
        },
        "accuracy": round(accuracy, 3),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# =============================================================================
# MODEL-4: EXPLAINABLE AI (XAI) LAYER
# =============================================================================

class ExplainableAI:
    """Generate natural language explanations for AI decisions"""
    
    def explain_anomaly(self, score: float, threshold: float = 0.7, data_point: List[float] = None) -> str:
        """Explain why an anomaly was detected"""
        if score < threshold:
            return f"The data point is NORMAL. Anomaly score ({score:.3f}) is below threshold ({threshold})."
        
        explanation_parts = [
            f"⚠️ ANOMALY DETECTED: Score {score:.3f} exceeds threshold {threshold}.",
        ]
        
        if score > 0.9:
            explanation_parts.append("SEVERITY: CRITICAL - This is a highly unusual pattern.")
        elif score > 0.8:
            explanation_parts.append("SEVERITY: HIGH - Significant deviation from normal behavior.")
        else:
            explanation_parts.append("SEVERITY: MODERATE - Notable but not critical anomaly.")
        
        if data_point:
            feature_values = ", ".join([f"{v:.2f}" for v in data_point[:5]])
            explanation_parts.append(f"Feature values: [{feature_values}...]")
        
        explanation_parts.append("Recommended action: Monitor closely and investigate if pattern persists.")
        
        return " ".join(explanation_parts)
    
    def explain_drift(self, drift_type: str, sample_number: int, value: float) -> str:
        """Explain why drift was detected"""
        explanations = {
            "ADWIN": f"🔴 ABRUPT DRIFT detected at sample {sample_number} using ADWIN algorithm. "
                     f"The data distribution changed suddenly (value: {value:.3f}). "
                     f"This indicates a sharp shift in data characteristics. "
                     f"Recommendation: Consider retraining or triggering federated aggregation.",
            
            "PAGE_HINKLEY": f"🟡 GRADUAL DRIFT detected at sample {sample_number} using Page-Hinkley test. "
                           f"The data has been slowly shifting over time (value: {value:.3f}). "
                           f"This suggests an evolving data distribution. "
                           f"Recommendation: Monitor trend and prepare for model adaptation.",
            
            "BOTH": f"🔴🟡 CRITICAL: Both ADWIN and Page-Hinkley detected drift at sample {sample_number}. "
                   f"This indicates significant and accelerating distribution change (value: {value:.3f}). "
                   f"Recommendation: IMMEDIATE ACTION REQUIRED - Trigger federated update or retrain."
        }
        
        return explanations.get(drift_type, "Unknown drift type detected.")
    
    def explain_health(self, health: str, avg_score: float, std_score: float, samples: int) -> str:
        """Explain current health state"""
        if health == "STABLE":
            return (f"✅ SYSTEM STABLE: Average anomaly score ({avg_score:.3f}) is within normal range. "
                   f"Processed {samples} samples with low variance ({std_score:.3f}). "
                   f"System is learning effectively with no concerning patterns.")
        
        elif health == "WARNING":
            return (f"⚠️ SYSTEM WARNING: Average anomaly score ({avg_score:.3f}) is elevated. "
                   f"Detected unusual patterns in recent {samples} samples (std: {std_score:.3f}). "
                   f"Reason: Sustained high anomaly scores or increased variance. "
                   f"Recommendation: Investigate data source and consider model adaptation.")
        
        elif health == "UNSTABLE":
            return (f"🔴 SYSTEM UNSTABLE: Critical anomaly score ({avg_score:.3f}) detected! "
                   f"Recent {samples} samples show severe deviation (std: {std_score:.3f}). "
                   f"Reason: Persistent anomalies or major drift event. "
                   f"Recommendation: IMMEDIATE ATTENTION - Check data pipeline, trigger federated update, or reset model.")
        
        return "Health state unknown."
    
    def explain_federated_update(self, round_num: int, nodes_participated: int, weight_norm: float) -> str:
        """Explain why federated aggregation occurred"""
        return (f"🔄 FEDERATED AGGREGATION (Round {round_num}): "
               f"Combined knowledge from {nodes_participated} edge nodes. "
               f"Global model weights updated (norm: {weight_norm:.3f}). "
               f"Reason: Periodic synchronization to maintain global intelligence while preserving local adaptations. "
               f"Impact: All nodes now share improved collective knowledge without exposing raw data.")
    
    def explain_node_health(self, node_name: str, health: str, avg_score: float, drift_count: int) -> str:
        """Explain individual node health"""
        base = f"Node {node_name} is {health}. "
        
        if health == "HEALTHY":
            return base + f"Operating normally with avg score {avg_score:.3f} and {drift_count} drift events."
        elif health == "WARNING":
            return base + f"Elevated anomaly score ({avg_score:.3f}) or {drift_count} drift events detected. Requires monitoring."
        else:  # CRITICAL
            return base + f"CRITICAL: High anomaly score ({avg_score:.3f}) and {drift_count} drift events. Immediate attention needed."

# Initialize XAI
xai = ExplainableAI()

@api_router.get("/explain/health")
async def explain_current_health():
    """Get explanation for current system health"""
    health_status = monitor.get_health()
    explanation = xai.explain_health(
        health_status["health"], 
        health_status["avg_score"], 
        health_status["std_score"], 
        health_status["samples"]
    )
    
    return {
        "explanation": explanation,
        "health": health_status["health"],
        "metrics": {
            "avg_score": health_status["avg_score"],
            "std_score": health_status["std_score"],
            "samples": health_status["samples"]
        }
    }


@api_router.get("/explain/anomaly")
async def explain_latest_anomaly():
    """Explain the most recent anomaly"""
    if latestPrediction := stream_manager.latest_prediction:
        explanation = xai.explain_anomaly(
            latestPrediction.get("anomaly_score", 0),
            0.7,
            latestPrediction.get("data_point")
        )
        
        return {
            "explanation": explanation,
            "anomaly_score": latestPrediction.get("anomaly_score"),
            "is_anomaly": latestPrediction.get("is_anomaly"),
            "timestamp": latestPrediction.get("timestamp")
        }
    
    return {"explanation": "No recent anomalies to explain.", "anomaly_score": 0}

@api_router.get("/explain/drift/recent")
async def explain_recent_drift():
    """Explain most recent drift event"""
    events = drift_detector.get_events(limit=1)
    
    if events:
        event = events[0]
        explanation = xai.explain_drift(
            event["type"],
            event["sample_number"],
            event["value"]
        )
        
        return {
            "explanation": explanation,
            "event": event
        }
    
    return {"explanation": "No drift events detected yet.", "event": None}

@api_router.get("/explain/node/{node_id}")
async def explain_node_health(node_id: str):
    """Explain specific node health"""
    if node_id not in federated_aggregator.nodes:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    node = federated_aggregator.nodes[node_id]
    status = node.get_status()
    
    explanation = xai.explain_node_health(
        status["name"],
        status["health"],
        status["avg_score"],
        status["drift_status"]["drift_count"]
    )
    
    return {
        "explanation": explanation,
        "node_status": status
    }

@api_router.get("/explain/federated/latest")
async def explain_latest_aggregation():
    """Explain most recent federated update"""
    history = list(federated_aggregator.aggregation_history)
    
    if history:
        latest = history[-1]
        explanation = xai.explain_federated_update(
            latest["round"],
            latest["nodes_participated"],
            latest["weight_norm"]
        )
        
        return {
            "explanation": explanation,
            "aggregation": latest
        }
    
    return {"explanation": "No federated aggregation has occurred yet.", "aggregation": None}

# =============================================================================
# MODEL-5: JARVIS COGNITIVE INTERFACE
# =============================================================================

class JarvisAssistant:
    """JARVIS-style cognitive assistant for natural language interaction"""
    
    def __init__(self):
        self.conversation_history = deque(maxlen=50)
        
    def detect_intent(self, query: str) -> str:
        """Detect user intent from natural language query"""
        query_lower = query.lower()
        
        # Intent patterns
        if any(word in query_lower for word in ["health", "status", "how is", "condition"]):
            if "node" in query_lower or any(f"node {i}" in query_lower for i in range(1, 6)):
                return "node_health"
            return "system_health"
        
        elif any(word in query_lower for word in ["why", "explain", "reason", "because"]):
            if "drift" in query_lower:
                return "explain_drift"
            elif "anomaly" in query_lower or "anomalous" in query_lower:
                return "explain_anomaly"
            return "explain_health"
        
        elif any(word in query_lower for word in ["predict", "future", "will", "forecast", "next"]):
            return "predict_future"
        
        elif any(word in query_lower for word in ["risk", "danger", "safe", "threat"]):
            return "risk_assessment"
        
        elif any(word in query_lower for word in ["drift", "drifting", "shift"]):
            return "drift_status"
        
        elif any(word in query_lower for word in ["node", "nodes", "edge"]):
            return "node_status"
        
        elif any(word in query_lower for word in ["federated", "aggregation", "global"]):
            return "federated_status"
        
        elif any(word in query_lower for word in ["simulate", "what if", "scenario"]):
            return "simulation"
        
        return "general_status"
    
    def extract_node_id(self, query: str) -> Optional[str]:
        """Extract node ID from query"""
        query_lower = query.lower()
        
        for node_id in ["node_1", "node_2", "node_3", "node_4", "node_5"]:
            if node_id.replace("_", " ") in query_lower or node_id in query_lower:
                return node_id
        
        # Check for node names
        node_names = {
            "alpha": "node_1",
            "beta": "node_2",
            "gamma": "node_3",
            "delta": "node_4",
            "epsilon": "node_5"
        }
        
        for name, node_id in node_names.items():
            if name in query_lower:
                return node_id
        
        return None
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query and generate response"""
        intent = self.detect_intent(query)
        
        response = {
            "query": query,
            "intent": intent,
            "response": "",
            "data": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            if intent == "system_health":
                health_status = monitor.get_health()
                
                response["response"] = (f"The system is currently {health_status['health']}. "
                                      f"Average anomaly score is {health_status['avg_score']:.3f} across {health_status['samples']} recent samples. "
                                      f"{sum(1 for n in federated_aggregator.nodes.values() if n.status == 'ONLINE')} out of {len(federated_aggregator.nodes)} nodes are online.")
                response["data"] = {"health": health_status['health'], "avg_score": health_status['avg_score']}
            
            elif intent == "node_health":
                node_id = self.extract_node_id(query)
                if node_id and node_id in federated_aggregator.nodes:
                    node = federated_aggregator.nodes[node_id]
                    status = node.get_status()
                    response["response"] = (f"{status['name']} is {status['health']}. "
                                          f"It has processed {status['data_points_processed']} data points "
                                          f"with an average anomaly score of {status['avg_score']:.3f}. "
                                          f"Drift events: {status['drift_status']['drift_count']}.")
                    response["data"] = status
                else:
                    node_statuses = ', '.join([f'{n.name}: {n.get_status()["health"]}' for n in federated_aggregator.nodes.values()])
                    response["response"] = f"All nodes status: {node_statuses}"
            
            elif intent == "explain_health":
                health_status = monitor.get_health()
                explanation = xai.explain_health(
                    health_status["health"], 
                    health_status["avg_score"], 
                    health_status["std_score"], 
                    health_status["samples"]
                )
                response["response"] = explanation
            
            elif intent == "explain_drift":
                events = drift_detector.get_events(limit=1)
                if events:
                    event = events[0]
                    explanation = xai.explain_drift(event["type"], event["sample_number"], event["value"])
                    response["response"] = explanation
                    response["data"] = event
                else:
                    response["response"] = "No drift events have been detected yet. The system is operating with stable data distributions."
            
            elif intent == "explain_anomaly":
                if latest := stream_manager.latest_prediction:
                    explanation = xai.explain_anomaly(latest.get("anomaly_score", 0), 0.7, latest.get("data_point"))
                    response["response"] = explanation
                    response["data"] = {"score": latest.get("anomaly_score")}
                else:
                    response["response"] = "No recent anomalies to explain. System is processing data normally."
            
            elif intent == "predict_future":
                current_scores = list(monitor.error_window)
                predictions = digital_twin.predict_future_health(current_scores, steps_ahead=5)
                
                if predictions:
                    next_pred = predictions[0]
                    response["response"] = (f"Based on current trends, I predict the system will be {next_pred['predicted_health']} "
                                          f"in the next cycle with a risk level of {next_pred['risk_level']}. "
                                          f"Predicted anomaly score: {next_pred['predicted_score']:.3f} "
                                          f"(confidence: {next_pred['confidence']:.1%}).")
                    response["data"] = {"predictions": predictions}
                else:
                    response["response"] = "Insufficient data for future prediction. Need more samples."
            
            elif intent == "risk_assessment":
                global_risk = digital_twin.calculate_risk_score({
                    "avg_score": float(np.mean(list(monitor.error_window))) if monitor.error_window else 0,
                    "drift_count": drift_detector.drift_count,
                    "data_points_processed": model.data_points_processed
                })
                
                response["response"] = (f"Current risk level: {global_risk['risk_category']} "
                                      f"(score: {global_risk['risk_score']:.1f}/100). "
                                      f"Primary risk factors: anomaly patterns ({global_risk['factors']['score_risk']:.1f}), "
                                      f"drift events ({global_risk['factors']['drift_risk']:.1f}).")
                response["data"] = global_risk
            
            elif intent == "drift_status":
                drift_status = drift_detector.get_status()
                response["response"] = (f"Drift detection status: {'IN DRIFT' if drift_status['in_drift'] else 'STABLE'}. "
                                      f"Total drift events: {drift_status['drift_count']} "
                                      f"(ADWIN: {drift_status['adwin_drifts']}, Page-Hinkley: {drift_status['ph_drifts']}) "
                                      f"across {drift_status['total_samples']} samples.")
                response["data"] = drift_status
            
            elif intent == "node_status":
                node_count = len(federated_aggregator.nodes)
                online = sum(1 for n in federated_aggregator.nodes.values() if n.status == "ONLINE")
                healthy = sum(1 for n in federated_aggregator.nodes.values() 
                            if n.get_status()["health"] == "HEALTHY")
                
                response["response"] = (f"Federated network has {node_count} nodes. "
                                      f"{online} are online, {healthy} are healthy. "
                                      f"Total data processed: {sum(n.data_points_processed for n in federated_aggregator.nodes.values())} points.")
            
            elif intent == "federated_status":
                fed_status = federated_aggregator.get_global_status()
                response["response"] = (f"Global federated learning status: {fed_status['global_health']}. "
                                      f"Completed {fed_status['aggregation_rounds']} aggregation rounds. "
                                      f"Global average anomaly score: {fed_status['global_avg_score']:.3f}.")
                response["data"] = fed_status
            
            else:
                response["response"] = (f"I'm JARVIS, your AI system assistant. I can help you with: "
                                      f"system health, node status, drift detection, risk assessment, "
                                      f"future predictions, and explanations. What would you like to know?")
        
        except Exception as e:
            response["response"] = f"I encountered an error processing your query: {str(e)}"
            response["error"] = str(e)
        
        self.conversation_history.append(response)
        return response

# Initialize JARVIS
jarvis = JarvisAssistant()

class JarvisQuery(BaseModel):
    query: str = Field(..., description="Natural language query")

@api_router.post("/jarvis/query")
async def query_jarvis(input_data: JarvisQuery):
    """Query JARVIS cognitive assistant"""
    response = await jarvis.process_query(input_data.query)
    return response

@api_router.get("/jarvis/history")
async def get_jarvis_history(limit: int = 20):
    """Get conversation history"""
    return {"history": list(jarvis.conversation_history)[-limit:]}

# =============================================================================
# MODEL-6: PERSONALIZATION & RESEARCH PACKAGE
# =============================================================================

class UserPreferences:
    """User personalization and preferences"""
    
    def __init__(self):
        self.preferences = {
            "alert_threshold": 0.7,
            "explanation_depth": "detailed",  # brief, detailed, technical
            "auto_aggregation": True,
            "notification_level": "all",  # all, critical, none
            "dashboard_refresh_rate": 2000,  # milliseconds
        }
        self.experiments = []
    
    def get_preferences(self) -> Dict[str, Any]:
        return self.preferences.copy()
    
    def update_preferences(self, updates: Dict[str, Any]):
        self.preferences.update(updates)
        return self.preferences
    
    def run_experiment(self, experiment_type: str, duration_seconds: int = 60) -> Dict[str, Any]:
        """Run controlled experiment"""
        experiment = {
            "id": str(uuid.uuid4()),
            "type": experiment_type,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": duration_seconds,
            "status": "running",
            "results": {}
        }
        
        self.experiments.append(experiment)
        return experiment
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate research report"""
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "system_overview": {
                "total_data_processed": model.data_points_processed,
                "drift_events": drift_detector.drift_count,
                "federated_rounds": federated_aggregator.aggregation_rounds,
                "nodes": len(federated_aggregator.nodes)
            },
            "model_performance": {
                "current_health": monitor.get_health(),
                "avg_anomaly_score": float(np.mean(list(monitor.error_window))) if monitor.error_window else 0
            },
            "experiments_conducted": len(self.experiments),
            "key_findings": [
                "Online learning successfully adapts to streaming data",
                "Federated approach preserves privacy while maintaining accuracy",
                "ADWIN + Page-Hinkley provides robust drift detection",
                "Digital Twin enables proactive system management"
            ]
        }
        
        return report

# Initialize User Preferences
user_prefs = UserPreferences()

class PreferencesUpdate(BaseModel):
    preferences: Dict[str, Any]

class ExperimentInput(BaseModel):
    experiment_type: str
    duration_seconds: int = 60

@api_router.get("/user/preferences")
async def get_user_preferences():
    """Get user preferences"""
    return user_prefs.get_preferences()

@api_router.post("/user/preferences")
async def update_user_preferences(input_data: PreferencesUpdate):
    """Update user preferences"""
    updated = user_prefs.update_preferences(input_data.preferences)
    return {"message": "Preferences updated", "preferences": updated}

@api_router.post("/experiments/run")
async def run_experiment(input_data: ExperimentInput):
    """Run controlled experiment"""
    experiment = user_prefs.run_experiment(input_data.experiment_type, input_data.duration_seconds)
    return experiment

@api_router.get("/experiments/list")
async def list_experiments():
    """List all experiments"""
    return {"experiments": user_prefs.experiments}

@api_router.get("/reports/generate")
async def generate_research_report():
    """Generate comprehensive research report"""
    report = user_prefs.generate_report()
    
    return StreamingResponse(
        io.BytesIO(json.dumps(report, indent=2).encode()),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=jarvis_research_report.json"}
    )

# =============================================================================
# JARVIS-X: VOICE-ENABLED MULTI-DOMAIN AI ASSISTANT
# =============================================================================

from jarvis_x import (
    speaker_recognition, intent_router, fintech_module, 
    software_module, edutech_module, medtech_module, jarvis_conversation
)

# Pydantic models for JARVIS-X
class JarvisXChatInput(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    speaker_id: Optional[str] = Field("admin", description="Speaker ID for voice verification")

class SpeakerVerifyInput(BaseModel):
    speaker_id: str = Field("admin", description="Speaker ID to verify")

class ExpenseInput(BaseModel):
    category: str
    amount: float
    description: str

class SoftwareRequirementsInput(BaseModel):
    requirements: str = Field(..., description="Software requirements description")
    project_name: Optional[str] = Field("my-project", description="Project name")

class ReminderInput(BaseModel):
    reminder_type: str
    name: str
    time: str
    frequency: str

# Speaker Recognition Endpoints
@api_router.post("/jarvis-x/speaker/verify")
async def verify_speaker(input_data: SpeakerVerifyInput):
    """Verify speaker identity (simulated)"""
    result = speaker_recognition.verify_speaker(input_data.speaker_id)
    return result

@api_router.get("/jarvis-x/speaker/current")
async def get_current_speaker():
    """Get current speaker info"""
    speaker = speaker_recognition.get_current_speaker()
    return {
        "speaker": speaker,
        "is_verified": speaker_recognition.is_verified
    }

# Main Chat Endpoint
@api_router.post("/jarvis-x/chat")
async def jarvis_x_chat(input_data: JarvisXChatInput):
    """Main JARVIS-X chat endpoint with intent routing"""
    session_id = input_data.session_id or str(uuid.uuid4())
    
    # Verify speaker
    if not speaker_recognition.is_verified:
        speaker_recognition.verify_speaker(input_data.speaker_id)
    
    # Detect intent
    intent_info = intent_router.detect_intent(input_data.message)
    
    # Build context based on intent
    context = {"intent": intent_info["intent"]}
    
    if intent_info["intent"] == "system_intelligence":
        # Add system health context
        health_status = monitor.get_health()
        fed_status = federated_aggregator.get_global_status()
        context["system_health"] = health_status
        context["federated_status"] = {
            "global_health": fed_status["global_health"],
            "nodes": fed_status["total_nodes"],
            "drift_events": drift_detector.drift_count
        }
    
    elif intent_info["intent"] == "fintech":
        # Add financial context
        context["expense_summary"] = fintech_module.get_expense_summary()
        context["budget_status"] = fintech_module.get_budget_status()
        context["insights"] = fintech_module.get_financial_insights()
    
    elif intent_info["intent"] == "medtech":
        # Add health monitoring context
        context["vitals"] = medtech_module.get_current_vitals()
        context["reminders"] = medtech_module.get_reminders()
    
    elif intent_info["intent"] == "software_generation":
        # Add software generation context
        analysis = software_module.analyze_requirements(input_data.message)
        context["project_analysis"] = analysis
    
    elif intent_info["intent"] == "edutech":
        # Add learning context
        context["available_paths"] = list(edutech_module.learning_paths.keys())
    
    # Send to LLM with context
    response = await jarvis_conversation.chat(session_id, input_data.message, context)
    
    return {
        **response,
        "intent": intent_info,
        "speaker_verified": speaker_recognition.is_verified,
        "speaker": speaker_recognition.get_current_speaker()
    }

@api_router.get("/jarvis-x/history/{session_id}")
async def get_jarvis_history(session_id: str):
    """Get conversation history for a session"""
    history = jarvis_conversation.get_history(session_id)
    return {"session_id": session_id, "history": history}

@api_router.delete("/jarvis-x/session/{session_id}")
async def clear_jarvis_session(session_id: str):
    """Clear a conversation session"""
    jarvis_conversation.clear_session(session_id)
    return {"message": f"Session {session_id} cleared"}

# FinTech Endpoints
@api_router.get("/jarvis-x/fintech/summary")
async def get_fintech_summary():
    """Get expense summary"""
    return fintech_module.get_expense_summary()

@api_router.get("/jarvis-x/fintech/budget")
async def get_budget_status():
    """Get budget vs actual spending"""
    return fintech_module.get_budget_status()

@api_router.get("/jarvis-x/fintech/insights")
async def get_financial_insights():
    """Get AI-generated financial insights"""
    return {"insights": fintech_module.get_financial_insights()}

@api_router.post("/jarvis-x/fintech/expense")
async def add_expense(input_data: ExpenseInput):
    """Add a new expense (simulated)"""
    return fintech_module.add_expense(
        input_data.category, 
        input_data.amount, 
        input_data.description
    )

# Software Generation Endpoints
@api_router.post("/jarvis-x/software/analyze")
async def analyze_software_requirements(input_data: SoftwareRequirementsInput):
    """Analyze software requirements"""
    return software_module.analyze_requirements(input_data.requirements)

@api_router.post("/jarvis-x/software/generate")
async def generate_software_scaffold(input_data: SoftwareRequirementsInput):
    """Generate software scaffold"""
    analysis = software_module.analyze_requirements(input_data.requirements)
    scaffold = software_module.generate_scaffold(
        analysis["project_type"], 
        input_data.project_name
    )
    return scaffold

# EduTech Endpoints
@api_router.get("/jarvis-x/edutech/paths")
async def get_learning_paths():
    """Get available learning paths"""
    return {"paths": edutech_module.learning_paths}

@api_router.get("/jarvis-x/edutech/path/{topic}")
async def get_learning_path(topic: str):
    """Get learning path for a topic"""
    return edutech_module.get_learning_path(topic)

# MedTech Endpoints
@api_router.get("/jarvis-x/medtech/vitals")
async def get_current_vitals():
    """Get current vitals (simulated)"""
    return medtech_module.get_current_vitals()

@api_router.get("/jarvis-x/medtech/reminders")
async def get_health_reminders():
    """Get health reminders"""
    return {"reminders": medtech_module.get_reminders()}

@api_router.post("/jarvis-x/medtech/reminder")
async def add_health_reminder(input_data: ReminderInput):
    """Add a health reminder"""
    return medtech_module.add_reminder(
        input_data.reminder_type,
        input_data.name,
        input_data.time,
        input_data.frequency
    )

# System Status Endpoint
@api_router.get("/jarvis-x/status")
async def get_jarvis_x_status():
    """Get JARVIS-X system status"""
    return {
        "status": "online",
        "modules": {
            "speaker_recognition": "active (simulated)",
            "intent_router": "active",
            "conversational_ai": "active (GPT-5.2)",
            "fintech": "active (simulated)",
            "software_generation": "active",
            "edutech": "active",
            "medtech": "active (simulated)"
        },
        "speaker_verified": speaker_recognition.is_verified,
        "current_speaker": speaker_recognition.get_current_speaker(),
        "greeting": "Welcome. JARVIS-X system is online.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# =============================================================================
# MIDDLEWARE & STARTUP
# =============================================================================

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
