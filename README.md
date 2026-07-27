# DashGuard: A 24/7 Dashboard Monitoring Agent

DashGuard is an AI-driven automated audit prototype built in Python to monitor Power BI dashboards 24/7. It is designed to intercept silent financial discrepancies and data pipeline failures that standard visual alerts often miss.

## Key Features

- **3-Layer Validation Engine**: Automates Data Collection, Rules Engine validation, and AI Anomaly Classification.
- **Power BI REST API Integration**: Autonomously executes diagnostic DAX queries via Service Principal to cross-validate semantic models.
- **AI Anomaly Classification**: Uses statistical Z-scores against historical baselines (with `numpy` and `scipy`) to dynamically classify the severity of data anomalies instead of relying on static thresholds.
- **Automated Alerting**: Routes alerts to specific channels (SMS, Email, Slack) based on severity context (e.g., weekends, month-end).

## Mock Implementation
This repository contains a mock implementation that simulates a real-world scenario where a $180K financial discrepancy occurs across 12 distributed databases. The `PowerBIMonitor` class is mocked to return simulated DAX query results that intentionally trigger the validation rules, demonstrating the AI classification engine.

## Setup and Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the monitoring agent:
   ```bash
   python main.py
   ```

## Output
When run, the agent will detect the simulated discrepancies, calculate their statistical severity, and output the classified alerts (e.g., HIGH, CRITICAL) along with recommended actions.
