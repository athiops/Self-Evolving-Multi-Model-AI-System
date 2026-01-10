#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Self-Evolving AI Engine - Model 1
Tests all endpoints for the online learning anomaly detection system.
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

class Model1APITester:
    def __init__(self, base_url: str = "https://evolvai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"    Details: {details}")
        
        if success:
            self.tests_passed += 1
        else:
            self.failed_tests.append({
                "test": test_name,
                "details": details
            })
    
    def test_api_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                         data: Dict = None, files: Dict = None) -> tuple[bool, Dict]:
        """Generic API endpoint tester"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, files=files, timeout=10)
                else:
                    response = requests.post(url, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            return success, response_data
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}
    
    def test_welcome_endpoint(self):
        """Test GET /api/ returns welcome message"""
        success, data = self.test_api_endpoint("GET", "/")
        
        if success and "message" in data:
            self.log_test("Welcome Endpoint", True, f"Message: {data['message']}")
        else:
            self.log_test("Welcome Endpoint", False, f"Response: {data}")
    
    def test_health_endpoint(self):
        """Test GET /api/health returns system health status"""
        success, data = self.test_api_endpoint("GET", "/health")
        
        required_fields = ["health", "avg_score", "std_score", "confidence", 
                          "data_points_processed", "stream_mode"]
        
        if success:
            missing_fields = [field for field in required_fields if field not in data]
            if not missing_fields:
                self.log_test("Health Endpoint", True, 
                            f"Health: {data.get('health')}, Points: {data.get('data_points_processed')}")
            else:
                self.log_test("Health Endpoint", False, f"Missing fields: {missing_fields}")
        else:
            self.log_test("Health Endpoint", False, f"Response: {data}")
    
    def test_stream_next_endpoint(self):
        """Test GET /api/stream/next returns next data point"""
        success, data = self.test_api_endpoint("GET", "/stream/next")
        
        required_fields = ["anomaly_score", "is_anomaly", "system_status", 
                          "data_point", "timestamp"]
        
        if success:
            missing_fields = [field for field in required_fields if field not in data]
            if not missing_fields:
                self.log_test("Stream Next Endpoint", True, 
                            f"Score: {data.get('anomaly_score')}, Anomaly: {data.get('is_anomaly')}")
            else:
                self.log_test("Stream Next Endpoint", False, f"Missing fields: {missing_fields}")
        else:
            self.log_test("Stream Next Endpoint", False, f"Response: {data}")
    
    def test_stream_config_endpoint(self):
        """Test POST /api/stream/config allows changing mode"""
        # Test simulated mode
        success1, data1 = self.test_api_endpoint("POST", "/stream/config", 
                                                data={"mode": "simulated"})
        
        # Test csv mode
        success2, data2 = self.test_api_endpoint("POST", "/stream/config", 
                                                data={"mode": "csv"})
        
        # Test invalid mode
        success3, data3 = self.test_api_endpoint("POST", "/stream/config", 
                                                expected_status=400,
                                                data={"mode": "invalid"})
        
        if success1 and success2 and success3:
            self.log_test("Stream Config Endpoint", True, 
                        "All mode changes working correctly")
        else:
            self.log_test("Stream Config Endpoint", False, 
                        f"Simulated: {success1}, CSV: {success2}, Invalid: {success3}")
    
    def test_alerts_endpoint(self):
        """Test GET /api/alerts returns alerts array"""
        success, data = self.test_api_endpoint("GET", "/alerts")
        
        if success and "alerts" in data and isinstance(data["alerts"], list):
            self.log_test("Alerts Endpoint", True, f"Found {len(data['alerts'])} alerts")
        else:
            self.log_test("Alerts Endpoint", False, f"Response: {data}")
    
    def test_history_endpoint(self):
        """Test GET /api/history returns score history"""
        success, data = self.test_api_endpoint("GET", "/history")
        
        if success and "history" in data and isinstance(data["history"], list):
            self.log_test("History Endpoint", True, f"Found {len(data['history'])} history items")
        else:
            self.log_test("History Endpoint", False, f"Response: {data}")
    
    def test_model_stats_endpoint(self):
        """Test GET /api/model/stats returns model statistics"""
        success, data = self.test_api_endpoint("GET", "/model/stats")
        
        required_fields = ["data_points_processed", "created_at", "uptime_seconds"]
        
        if success:
            missing_fields = [field for field in required_fields if field not in data]
            if not missing_fields:
                self.log_test("Model Stats Endpoint", True, 
                            f"Processed: {data.get('data_points_processed')}, Uptime: {data.get('uptime_seconds'):.1f}s")
            else:
                self.log_test("Model Stats Endpoint", False, f"Missing fields: {missing_fields}")
        else:
            self.log_test("Model Stats Endpoint", False, f"Response: {data}")
    
    def test_model_reset_endpoint(self):
        """Test POST /api/model/reset resets the model"""
        success, data = self.test_api_endpoint("POST", "/model/reset")
        
        if success and "message" in data:
            self.log_test("Model Reset Endpoint", True, f"Message: {data['message']}")
        else:
            self.log_test("Model Reset Endpoint", False, f"Response: {data}")
    
    def test_export_json_endpoint(self):
        """Test GET /api/export/json exports data as JSON file"""
        url = f"{self.api_url}/export/json"
        
        try:
            response = requests.get(url, timeout=15)
            success = response.status_code == 200
            
            if success:
                # Check if it's a valid JSON response
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    try:
                        json_data = response.json()
                        self.log_test("Export JSON Endpoint", True, 
                                    f"JSON export successful, size: {len(response.content)} bytes")
                    except:
                        self.log_test("Export JSON Endpoint", False, "Invalid JSON response")
                else:
                    self.log_test("Export JSON Endpoint", False, f"Wrong content type: {content_type}")
            else:
                self.log_test("Export JSON Endpoint", False, f"Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Export JSON Endpoint", False, f"Request error: {str(e)}")
    
    def test_export_csv_endpoint(self):
        """Test GET /api/export/csv exports data as CSV file"""
        url = f"{self.api_url}/export/csv"
        
        try:
            response = requests.get(url, timeout=15)
            success = response.status_code == 200
            
            if success:
                content_type = response.headers.get('content-type', '')
                if 'text/csv' in content_type:
                    self.log_test("Export CSV Endpoint", True, 
                                f"CSV export successful, size: {len(response.content)} bytes")
                else:
                    self.log_test("Export CSV Endpoint", False, f"Wrong content type: {content_type}")
            else:
                self.log_test("Export CSV Endpoint", False, f"Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Export CSV Endpoint", False, f"Request error: {str(e)}")
    
    def test_csv_upload_endpoint(self):
        """Test CSV upload functionality"""
        # Create a simple test CSV
        csv_content = "1.0,2.0,3.0,4.0,5.0\n2.1,1.9,3.1,3.9,5.1\n"
        
        files = {
            'file': ('test_data.csv', csv_content, 'text/csv')
        }
        
        url = f"{self.api_url}/upload/csv"
        
        try:
            response = requests.post(url, files=files, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if "rows_loaded" in data and "features_per_row" in data:
                    self.log_test("CSV Upload Endpoint", True, 
                                f"Uploaded {data['rows_loaded']} rows with {data['features_per_row']} features")
                else:
                    self.log_test("CSV Upload Endpoint", False, f"Missing upload info: {data}")
            else:
                try:
                    error_data = response.json()
                    self.log_test("CSV Upload Endpoint", False, f"Status: {response.status_code}, Error: {error_data}")
                except:
                    self.log_test("CSV Upload Endpoint", False, f"Status: {response.status_code}")
                    
        except requests.exceptions.RequestException as e:
            self.log_test("CSV Upload Endpoint", False, f"Request error: {str(e)}")
    
    def test_integration_flow(self):
        """Test a complete integration flow"""
        print("\n🔄 Testing Integration Flow...")
        
        # 1. Reset model
        success1, _ = self.test_api_endpoint("POST", "/model/reset")
        
        # 2. Get initial health
        success2, health_data = self.test_api_endpoint("GET", "/health")
        
        # 3. Process some data points
        data_points_processed = 0
        for i in range(5):
            success, _ = self.test_api_endpoint("GET", "/stream/next")
            if success:
                data_points_processed += 1
            time.sleep(0.5)  # Small delay between requests
        
        # 4. Check updated health
        success3, updated_health = self.test_api_endpoint("GET", "/health")
        
        # 5. Get history
        success4, history_data = self.test_api_endpoint("GET", "/history")
        
        integration_success = all([success1, success2, success3, success4]) and data_points_processed > 0
        
        if integration_success:
            self.log_test("Integration Flow", True, 
                        f"Processed {data_points_processed} data points, history has {len(history_data.get('history', []))} items")
        else:
            self.log_test("Integration Flow", False, 
                        f"Flow failed at some step. Data points: {data_points_processed}")
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Model-1 Backend API Tests")
        print(f"🎯 Target: {self.base_url}")
        print("=" * 60)
        
        # Test all endpoints
        self.test_welcome_endpoint()
        self.test_health_endpoint()
        self.test_stream_next_endpoint()
        self.test_stream_config_endpoint()
        self.test_alerts_endpoint()
        self.test_history_endpoint()
        self.test_model_stats_endpoint()
        self.test_model_reset_endpoint()
        self.test_export_json_endpoint()
        self.test_export_csv_endpoint()
        self.test_csv_upload_endpoint()
        
        # Test integration flow
        self.test_integration_flow()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = Model1APITester()
    
    try:
        all_passed = tester.run_all_tests()
        return 0 if all_passed else 1
    except Exception as e:
        print(f"💥 Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())