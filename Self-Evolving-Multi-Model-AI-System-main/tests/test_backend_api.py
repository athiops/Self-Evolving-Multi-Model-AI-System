"""
Backend API Tests for Self-Evolving AI Engine
Tests all 6 models: Core AI, Federated Learning, Drift Detection, Digital Twin, XAI, JARVIS
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndCore:
    """MODEL-1: Core Self-Evolving AI Engine tests"""
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ Root endpoint: {data['message']}")
    
    def test_health_endpoint(self):
        """Test health endpoint returns all required fields"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        required_fields = ["health", "avg_score", "confidence", "samples_in_window", 
                          "data_points_processed", "stream_mode", "drift_injection_active"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        assert data["health"] in ["STABLE", "WARNING", "UNSTABLE"]
        print(f"✓ Health: {data['health']}, Score: {data['avg_score']}")
    
    def test_stream_next(self):
        """Test streaming next data point"""
        response = requests.get(f"{BASE_URL}/api/stream/next")
        assert response.status_code == 200
        data = response.json()
        
        assert "anomaly_score" in data
        assert "is_anomaly" in data
        assert "data_point" in data
        assert "system_status" in data
        assert "drift_status" in data
        assert "federated_round" in data
        
        assert isinstance(data["data_point"], list)
        assert len(data["data_point"]) == 5
        print(f"✓ Stream next: score={data['anomaly_score']:.4f}, anomaly={data['is_anomaly']}")
    
    def test_model_stats(self):
        """Test model statistics endpoint"""
        response = requests.get(f"{BASE_URL}/api/model/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "data_points_processed" in data
        assert "created_at" in data
        assert "uptime_seconds" in data
        print(f"✓ Model stats: {data['data_points_processed']} points processed")
    
    def test_alerts_endpoint(self):
        """Test alerts endpoint"""
        response = requests.get(f"{BASE_URL}/api/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert isinstance(data["alerts"], list)
        print(f"✓ Alerts: {len(data['alerts'])} alerts")
    
    def test_history_endpoint(self):
        """Test history endpoint"""
        response = requests.get(f"{BASE_URL}/api/history?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)
        print(f"✓ History: {len(data['history'])} records")


class TestFederatedLearning:
    """MODEL-2: Federated Learning tests"""
    
    def test_federated_status(self):
        """Test federated learning status - shows all 5 nodes"""
        response = requests.get(f"{BASE_URL}/api/federated/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "global_health" in data
        assert "total_nodes" in data
        assert "online_nodes" in data
        assert "aggregation_rounds" in data
        assert "nodes" in data
        
        # Verify 5 nodes exist
        assert data["total_nodes"] == 5
        assert len(data["nodes"]) == 5
        
        # Verify each node has required fields
        for node_id, node in data["nodes"].items():
            assert "name" in node
            assert "location" in node
            assert "status" in node
            assert "health" in node
            assert "data_points_processed" in node
            assert "drift_status" in node
        
        print(f"✓ Federated: {data['online_nodes']}/{data['total_nodes']} nodes online, health={data['global_health']}")
    
    def test_federated_nodes_list(self):
        """Test federated nodes list endpoint"""
        response = requests.get(f"{BASE_URL}/api/federated/nodes")
        assert response.status_code == 200
        data = response.json()
        
        assert "nodes" in data
        assert len(data["nodes"]) == 5
        
        node_names = [n["name"] for n in data["nodes"]]
        expected_names = ["Edge Node Alpha", "Edge Node Beta", "Edge Node Gamma", 
                         "Edge Node Delta", "Edge Node Epsilon"]
        for name in expected_names:
            assert name in node_names, f"Missing node: {name}"
        
        print(f"✓ Federated nodes: {', '.join(node_names)}")
    
    def test_federated_aggregation(self):
        """Test manual aggregation trigger"""
        response = requests.post(f"{BASE_URL}/api/federated/aggregate")
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "round" in data
        assert "weight_norm" in data
        print(f"✓ Aggregation: round={data['round']}, weight_norm={data['weight_norm']:.4f}")


class TestDriftDetection:
    """MODEL-2: Drift Detection tests"""
    
    def test_drift_status(self):
        """Test drift detection status"""
        response = requests.get(f"{BASE_URL}/api/drift/status")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["total_samples", "drift_count", "adwin_drifts", 
                          "ph_drifts", "in_drift", "last_drift_time"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"✓ Drift status: {data['drift_count']} drifts, in_drift={data['in_drift']}")
    
    def test_drift_events(self):
        """Test drift events endpoint"""
        response = requests.get(f"{BASE_URL}/api/drift/events?limit=20")
        assert response.status_code == 200
        data = response.json()
        
        assert "events" in data
        assert isinstance(data["events"], list)
        print(f"✓ Drift events: {len(data['events'])} events")
    
    def test_drift_injection(self):
        """Test drift injection toggle"""
        # Activate drift
        response = requests.post(f"{BASE_URL}/api/drift/inject", 
                                json={"active": True})
        assert response.status_code == 200
        data = response.json()
        assert data["active"] == True
        print(f"✓ Drift injection activated")
        
        # Deactivate drift
        response = requests.post(f"{BASE_URL}/api/drift/inject", 
                                json={"active": False})
        assert response.status_code == 200
        data = response.json()
        assert data["active"] == False
        print(f"✓ Drift injection deactivated")


class TestDigitalTwin:
    """MODEL-3: Digital Twin Simulator tests"""
    
    def test_risk_score(self):
        """Test risk score calculation"""
        response = requests.get(f"{BASE_URL}/api/twin/risk-score")
        assert response.status_code == 200
        data = response.json()
        
        assert "global_risk" in data
        assert "node_risks" in data
        assert "timestamp" in data
        
        # Verify global risk structure
        global_risk = data["global_risk"]
        assert "risk_score" in global_risk
        assert "risk_category" in global_risk
        assert "factors" in global_risk
        assert global_risk["risk_category"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        
        # Verify node risks
        assert len(data["node_risks"]) == 5
        
        print(f"✓ Risk score: {global_risk['risk_score']:.1f} ({global_risk['risk_category']})")
    
    def test_predict_health(self):
        """Test future health predictions"""
        response = requests.get(f"{BASE_URL}/api/twin/predict-health?steps=10")
        assert response.status_code == 200
        data = response.json()
        
        assert "current_health" in data
        assert "predictions" in data
        assert "generated_at" in data
        
        # Verify predictions structure
        predictions = data["predictions"]
        assert len(predictions) == 10
        
        for pred in predictions:
            assert "step" in pred
            assert "predicted_score" in pred
            assert "predicted_health" in pred
            assert "confidence" in pred
        
        print(f"✓ Health predictions: {len(predictions)} steps ahead")
    
    def test_simulation_sustained_drift(self):
        """Test what-if simulation - sustained drift"""
        response = requests.post(f"{BASE_URL}/api/twin/simulate", 
                                json={"scenario_type": "sustained_drift", 
                                      "params": {"duration_minutes": 5, "intensity": 0.7}})
        assert response.status_code == 200
        data = response.json()
        
        assert "scenario" in data
        assert "outcome" in data
        assert data["scenario"] == "sustained_drift"
        assert "expected_health" in data["outcome"]
        assert "recommendation" in data["outcome"]
        
        print(f"✓ Simulation (sustained_drift): {data['outcome']['expected_health']}")
    
    def test_simulation_node_failure(self):
        """Test what-if simulation - node failure"""
        response = requests.post(f"{BASE_URL}/api/twin/simulate", 
                                json={"scenario_type": "node_failure", 
                                      "params": {"node_count": 2, "total_nodes": 5}})
        assert response.status_code == 200
        data = response.json()
        
        assert data["scenario"] == "node_failure"
        assert "remaining_capacity" in data["outcome"]
        assert "system_stability" in data["outcome"]
        
        print(f"✓ Simulation (node_failure): {data['outcome']['system_stability']}")
    
    def test_live_vs_predicted(self):
        """Test live vs predicted comparison"""
        response = requests.get(f"{BASE_URL}/api/twin/comparison")
        assert response.status_code == 200
        data = response.json()
        
        assert "live_state" in data
        assert "predicted_state" in data
        assert "accuracy" in data
        
        print(f"✓ Live vs Predicted: accuracy={data['accuracy']:.3f}")


class TestExplainableAI:
    """MODEL-4: Explainable AI Layer tests"""
    
    def test_explain_health(self):
        """Test health explanation"""
        response = requests.get(f"{BASE_URL}/api/explain/health")
        assert response.status_code == 200
        data = response.json()
        
        assert "explanation" in data
        assert "health" in data
        assert "metrics" in data
        
        # Explanation should be a meaningful string
        assert len(data["explanation"]) > 20
        
        print(f"✓ Health explanation: {data['health']} - {data['explanation'][:50]}...")
    
    def test_explain_anomaly(self):
        """Test anomaly explanation - requires streaming data first"""
        # First stream some data to have a latest prediction
        requests.get(f"{BASE_URL}/api/stream/next")
        
        response = requests.get(f"{BASE_URL}/api/explain/anomaly")
        assert response.status_code == 200
        data = response.json()
        
        assert "explanation" in data
        assert "anomaly_score" in data
        
        print(f"✓ Anomaly explanation: score={data.get('anomaly_score', 0)}")
    
    def test_explain_drift(self):
        """Test drift explanation - recent drift events"""
        response = requests.get(f"{BASE_URL}/api/explain/drift/recent")
        assert response.status_code == 200
        data = response.json()
        
        assert "explanation" in data
        
        print(f"✓ Drift explanation: {data['explanation'][:50]}...")


class TestJARVIS:
    """MODEL-5: JARVIS Cognitive Interface tests"""
    
    def test_jarvis_system_health_query(self):
        """Test JARVIS query - system health"""
        response = requests.post(f"{BASE_URL}/api/jarvis/query", 
                                json={"query": "What is the system health?"})
        assert response.status_code == 200
        data = response.json()
        
        assert "query" in data
        assert "intent" in data
        assert "response" in data
        assert "timestamp" in data
        
        # Response should be meaningful
        assert len(data["response"]) > 10
        
        print(f"✓ JARVIS (health): {data['response'][:60]}...")
    
    def test_jarvis_prediction_query(self):
        """Test JARVIS query - future prediction"""
        response = requests.post(f"{BASE_URL}/api/jarvis/query", 
                                json={"query": "Predict the future"})
        assert response.status_code == 200
        data = response.json()
        
        assert data["intent"] in ["prediction", "predict_future"]
        assert "response" in data
        
        print(f"✓ JARVIS (prediction): {data['response'][:60]}...")
    
    def test_jarvis_risk_query(self):
        """Test JARVIS query - risk assessment"""
        response = requests.post(f"{BASE_URL}/api/jarvis/query", 
                                json={"query": "What is the risk level?"})
        assert response.status_code == 200
        data = response.json()
        
        assert data["intent"] in ["risk", "risk_assessment"]
        assert "response" in data
        
        print(f"✓ JARVIS (risk): {data['response'][:60]}...")
    
    def test_jarvis_federated_query(self):
        """Test JARVIS query - federated status"""
        response = requests.post(f"{BASE_URL}/api/jarvis/query", 
                                json={"query": "How are the nodes doing?"})
        assert response.status_code == 200
        data = response.json()
        
        assert data["intent"] in ["federated", "node_status"]
        assert "response" in data
        
        print(f"✓ JARVIS (federated): {data['response'][:60]}...")


class TestUserPreferences:
    """MODEL-6: Personalization, Report & Research Packaging tests"""
    
    def test_get_preferences(self):
        """Test getting user preferences"""
        response = requests.get(f"{BASE_URL}/api/user/preferences")
        assert response.status_code == 200
        data = response.json()
        
        expected_fields = ["alert_threshold", "explanation_depth", "auto_aggregation", 
                          "notification_level", "dashboard_refresh_rate"]
        for field in expected_fields:
            assert field in data, f"Missing preference: {field}"
        
        print(f"✓ Preferences: threshold={data['alert_threshold']}, depth={data['explanation_depth']}")
    
    def test_update_preferences(self):
        """Test updating user preferences"""
        new_prefs = {
            "preferences": {
                "alert_threshold": 0.8,
                "explanation_depth": "simple",
                "auto_aggregation": False
            }
        }
        response = requests.post(f"{BASE_URL}/api/user/preferences", json=new_prefs)
        assert response.status_code == 200
        data = response.json()
        
        assert "preferences" in data
        assert data["preferences"]["alert_threshold"] == 0.8
        
        # Reset to defaults
        requests.post(f"{BASE_URL}/api/user/preferences", json={
            "preferences": {
                "alert_threshold": 0.7,
                "explanation_depth": "detailed",
                "auto_aggregation": True
            }
        })
        
        print(f"✓ Preferences updated and reset")
    
    def test_run_experiment(self):
        """Test running an experiment"""
        response = requests.post(f"{BASE_URL}/api/experiments/run", 
                                json={"experiment_type": "drift_detection", "duration_seconds": 10})
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "type" in data
        assert "status" in data
        assert data["type"] == "drift_detection"
        assert data["status"] == "running"
        
        print(f"✓ Experiment started: {data['id'][:8]}...")
    
    def test_list_experiments(self):
        """Test listing experiments"""
        response = requests.get(f"{BASE_URL}/api/experiments/list")
        assert response.status_code == 200
        data = response.json()
        
        assert "experiments" in data
        assert isinstance(data["experiments"], list)
        
        print(f"✓ Experiments list: {len(data['experiments'])} experiments")
    
    def test_generate_report(self):
        """Test report generation"""
        response = requests.get(f"{BASE_URL}/api/reports/generate?format=json")
        assert response.status_code == 200
        data = response.json()
        
        assert "generated_at" in data
        assert "system_overview" in data
        assert "model_performance" in data
        assert "key_findings" in data
        
        print(f"✓ Report generated at: {data['generated_at']}")


class TestExportFunctionality:
    """Test export functionality"""
    
    def test_export_json(self):
        """Test JSON export"""
        response = requests.get(f"{BASE_URL}/api/export/json?limit=10")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        
        data = response.json()
        assert "exported_at" in data
        assert "model_stats" in data
        assert "predictions" in data
        
        print(f"✓ JSON export: {len(data['predictions'])} predictions")
    
    def test_export_csv(self):
        """Test CSV export"""
        response = requests.get(f"{BASE_URL}/api/export/csv?limit=10")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        
        print(f"✓ CSV export: {len(response.content)} bytes")


class TestIntegrationFlow:
    """End-to-end integration tests"""
    
    def test_full_streaming_flow(self):
        """Test complete streaming flow with all models"""
        # 1. Reset model
        response = requests.post(f"{BASE_URL}/api/model/reset")
        assert response.status_code == 200
        print("  1. Model reset")
        
        # 2. Stream several data points
        for i in range(5):
            response = requests.get(f"{BASE_URL}/api/stream/next")
            assert response.status_code == 200
        print("  2. Streamed 5 data points")
        
        # 3. Check health
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        health = response.json()
        assert health["data_points_processed"] >= 5
        print(f"  3. Health check: {health['health']}")
        
        # 4. Check federated status
        response = requests.get(f"{BASE_URL}/api/federated/status")
        assert response.status_code == 200
        fed = response.json()
        assert fed["total_data_points"] >= 5
        print(f"  4. Federated: {fed['total_data_points']} total points")
        
        # 5. Get risk score
        response = requests.get(f"{BASE_URL}/api/twin/risk-score")
        assert response.status_code == 200
        risk = response.json()
        print(f"  5. Risk: {risk['global_risk']['risk_category']}")
        
        # 6. Get explanation
        response = requests.get(f"{BASE_URL}/api/explain/health")
        assert response.status_code == 200
        explain = response.json()
        print(f"  6. Explanation: {explain['health']}")
        
        # 7. Query JARVIS
        response = requests.post(f"{BASE_URL}/api/jarvis/query", 
                                json={"query": "System status"})
        assert response.status_code == 200
        jarvis = response.json()
        print(f"  7. JARVIS: {jarvis['intent']}")
        
        print("✓ Full integration flow completed")
    
    def test_drift_injection_flow(self):
        """Test drift injection and detection flow"""
        # 1. Inject drift
        response = requests.post(f"{BASE_URL}/api/drift/inject", 
                                json={"active": True})
        assert response.status_code == 200
        print("  1. Drift injection activated")
        
        # 2. Stream data with drift
        for i in range(10):
            response = requests.get(f"{BASE_URL}/api/stream/next")
            assert response.status_code == 200
        print("  2. Streamed 10 data points with drift")
        
        # 3. Check drift status
        response = requests.get(f"{BASE_URL}/api/drift/status")
        assert response.status_code == 200
        drift = response.json()
        print(f"  3. Drift status: {drift['drift_count']} drifts detected")
        
        # 4. Deactivate drift
        response = requests.post(f"{BASE_URL}/api/drift/inject", 
                                json={"active": False})
        assert response.status_code == 200
        print("  4. Drift injection deactivated")
        
        print("✓ Drift injection flow completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
