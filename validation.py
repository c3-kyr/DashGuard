from datetime import datetime

class ValidationEngine:
    def __init__(self, monitor):
        self.monitor = monitor
        self.rules = []

    def add_cross_source_rule(self, name, dataset_id, dax_query_a, dax_query_b, tolerance_pct=2.0):
        """Compare two values that should match"""
        self.rules.append({
            "type": "cross_source",
            "name": name,
            "dataset_id": dataset_id,
            "query_a": dax_query_a,
            "query_b": dax_query_b,
            "tolerance": tolerance_pct
        })

    def add_completeness_rule(self, name, dataset_id, dax_query, expected_min):
        """Ensure row counts meet minimums"""
        self.rules.append({
            "type": "completeness",
            "name": name,
            "dataset_id": dataset_id,
            "query": dax_query,
            "expected_min": expected_min
        })

    def add_freshness_rule(self, name, dataset_id, dax_query, max_age_hours=24):
        """Ensure data isn't stale"""
        self.rules.append({
            "type": "freshness",
            "name": name,
            "dataset_id": dataset_id,
            "query": dax_query,
            "max_age_hours": max_age_hours
        })

    def add_trend_rule(self, name, dataset_id, dax_query, lookback_days=30, z_threshold=2.5):
        """Detect statistical anomalies in trends"""
        self.rules.append({
            "type": "trend_anomaly",
            "name": name,
            "dataset_id": dataset_id,
            "query": dax_query,
            "lookback": lookback_days,
            "z_threshold": z_threshold
        })

    def run_checks(self):
        """Run all configured validation rules and yield deviations."""
        deviations = []
        for rule in self.rules:
            try:
                if rule["type"] == "cross_source":
                    res_a = self.monitor.execute_dax_query(rule["dataset_id"], rule["query_a"])
                    res_b = self.monitor.execute_dax_query(rule["dataset_id"], rule["query_b"])
                    val_a = res_a["results"][0]["rows"][0]["[Value]"]
                    val_b = res_b["results"][0]["rows"][0]["[Value]"]
                    
                    diff = abs(val_a - val_b)
                    if diff > 0:
                        pct_diff = (diff / max(val_a, val_b)) * 100
                        if pct_diff > rule["tolerance"]:
                            deviations.append({
                                "rule_name": rule["name"],
                                "current_value": val_a,
                                "expected_value": val_b,
                                "deviation_pct": pct_diff
                            })

                elif rule["type"] == "completeness":
                    res = self.monitor.execute_dax_query(rule["dataset_id"], rule["query"])
                    val = res["results"][0]["rows"][0]["[Value]"]
                    if val < rule["expected_min"]:
                        deviations.append({
                            "rule_name": rule["name"],
                            "current_value": val,
                            "expected_value": rule["expected_min"],
                            "deviation_pct": ((rule["expected_min"] - val) / rule["expected_min"]) * 100
                        })

                elif rule["type"] == "freshness":
                    res = self.monitor.execute_dax_query(rule["dataset_id"], rule["query"])
                    latest_date_str = res["results"][0]["rows"][0]["[Value]"]
                    # Simplified parsing for the mock ISO format
                    latest_date = datetime.fromisoformat(latest_date_str)
                    age_hours = (datetime.now() - latest_date).total_seconds() / 3600
                    if age_hours > rule["max_age_hours"]:
                        deviations.append({
                            "rule_name": rule["name"],
                            "current_value": age_hours,
                            "expected_value": rule["max_age_hours"],
                            "deviation_pct": ((age_hours - rule["max_age_hours"]) / rule["max_age_hours"]) * 100
                        })

                elif rule["type"] == "trend_anomaly":
                    res = self.monitor.execute_dax_query(rule["dataset_id"], rule["query"])
                    val = res["results"][0]["rows"][0]["[Value]"]
                    # For a real implementation, we would compare this against a 30-day average from the history store.
                    # Here we simulate an anomaly where the value is lower than a simulated expected moving average of 200k.
                    expected_avg = 200000
                    diff = abs(expected_avg - val)
                    pct_diff = (diff / expected_avg) * 100
                    if pct_diff > 10: # Mock simple threshold
                         deviations.append({
                             "rule_name": rule["name"],
                             "current_value": val,
                             "expected_value": expected_avg,
                             "deviation_pct": pct_diff
                         })

            except Exception as e:
                print(f"[Engine] Error running rule '{rule['name']}': {e}")
                
        return deviations
