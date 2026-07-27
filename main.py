import os
import json
from datetime import datetime

from monitor import PowerBIMonitor
from validation import ValidationEngine
from history import HistoryStore
from classifier import AnomalyClassifier
from alert import AlertDistributor

def load_config():
    config_path = "config.json"
    if not os.path.exists(config_path):
        default_config = {
            "tenant_id": "placeholder_tenant",
            "client_id": "placeholder_client",
            "client_secret": "placeholder_secret",
            "critical_contacts": ["+1234567890"],
            "critical_email_list": ["cfo@example.com", "data-oncall@example.com"],
            "standard_email_list": ["data-team@example.com"],
            "slack_channel_critical": "#data-incidents",
            "slack_channel_alerts": "#data-alerts"
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config
    
    with open(config_path, "r") as f:
        return json.load(f)

def main():
    print("Starting DashGuard Agent...")
    config = load_config()

    # Initialize layers
    monitor = PowerBIMonitor(
        config.get("tenant_id"), 
        config.get("client_id"), 
        config.get("client_secret")
    )
    
    engine = ValidationEngine(monitor)
    
    history_store = HistoryStore()
    classifier = AnomalyClassifier(history_store)
    
    alerter = AlertDistributor(config)

    # Setup Rules 
    MANUFACTURING_DATASET = "dummy_dataset_id"
    
    engine.add_cross_source_rule(
        name="Revenue: Dashboard vs ERP Total",
        dataset_id=MANUFACTURING_DATASET,
        dax_query_a='EVALUATE ROW("Revenue", [Total Revenue])',
        dax_query_b='EVALUATE ROW("ERP", [ERP Revenue Total])',
        tolerance_pct=1.0
    )

    engine.add_completeness_rule(
        name="All 12 Plants Reporting",
        dataset_id=MANUFACTURING_DATASET,
        dax_query='''
            EVALUATE ROW("PlantCount",
                DISTINCTCOUNT(Plants[PlantID]))
        ''',
        expected_min=12
    )

    engine.add_freshness_rule(
        name="Latest Transaction Within 24h",
        dataset_id=MANUFACTURING_DATASET,
        dax_query='''
            EVALUATE ROW("LatestDate",
                MAX(Transactions[TransactionDate]))
        ''',
        max_age_hours=24
    )

    engine.add_trend_rule(
        name="Daily Revenue Anomaly Check",
        dataset_id=MANUFACTURING_DATASET,
        dax_query='''
            EVALUATE ROW("TodayRev",
                CALCULATE([Total Revenue],
                    'Date'[Date] = TODAY()))
        ''',
        lookback_days=30,
        z_threshold=2.5
    )

    # Generate current context
    now = datetime.now()
    context = {
        "day_of_month": now.day,
        "is_weekend": now.weekday() >= 5,
        "is_holiday": False
    }

    # Run Checks
    print("\n[DashGuard] Running Validation Checks...")
    deviations = engine.run_checks()
    
    if not deviations:
        print("\n[DashGuard] All checks passed. Dashboard is healthy.")
    else:
        print(f"\n[DashGuard] Found {len(deviations)} deviations. Classifying severity...")
        for dev in deviations:
            # Add rule name to the dictionary before passing to classifier
            dev["rule_name"] = dev["rule_name"]
            
            classified_alert = classifier.classify_severity(
                rule_name=dev["rule_name"],
                current_value=dev["current_value"],
                expected_value=dev["expected_value"],
                context=context,
                deviation_pct=dev.get("deviation_pct")
            )
            
            # Merge information
            classified_alert["rule_name"] = dev["rule_name"]
            
            # Send alert
            alerter.send_alert(classified_alert)

if __name__ == "__main__":
    main()
