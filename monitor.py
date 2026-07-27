from datetime import datetime, timedelta
import random

class PowerBIMonitor:
    """Mock version of PowerBIMonitor for demonstration purposes."""
    def __init__(self, tenant_id=None, client_id=None, client_secret=None):
        self.token = "mock_token"
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        print(f"[Monitor] Initialized Mock PowerBIMonitor")

    def execute_dax_query(self, dataset_id, dax_query):
        """Mock execute a DAX query returning a simulated response."""
        print(f"[Monitor] Executing mock DAX query on dataset {dataset_id}:\n  {dax_query.strip()}")
        
        # Simulate different scenarios based on the query contents
        if "Total Revenue" in dax_query:
            return {"results": [{"rows": [{"[Value]": 4020000}]}]}  # Simulated dashboard revenue (Missing $180k)
        elif "ERP Revenue Total" in dax_query:
            return {"results": [{"rows": [{"[Value]": 4200000}]}]}  # Simulated ERP revenue (Actual $4.2M)
        elif "DISTINCTCOUNT(Plants[PlantID])" in dax_query:
            return {"results": [{"rows": [{"[Value]": 9}]}]}  # Simulated missing plants (9 instead of 12)
        elif "MAX(Transactions[TransactionDate])" in dax_query:
            # Simulate freshness
            return {"results": [{"rows": [{"[Value]": (datetime.now() - timedelta(hours=2)).isoformat()}]}]}
        elif "TODAY()" in dax_query:
            # Simulate daily revenue drop for trend anomaly
            return {"results": [{"rows": [{"[Value]": 150000}]}]} # Lower than expected
        else:
            return {"results": [{"rows": [{"[Value]": 0}]}]}

    def get_refresh_history(self, dataset_id):
        """Mock refresh history"""
        return {
            "value": [
                {"status": "Completed", "startTime": (datetime.now() - timedelta(hours=1)).isoformat()}
            ]
        }
