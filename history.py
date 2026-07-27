import json
import os

class HistoryStore:
    def __init__(self, filename="history.json"):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_deviation(self, rule_name, deviation_pct):
        if rule_name not in self.data:
            self.data[rule_name] = []
        self.data[rule_name].append(deviation_pct)
        # Keep last 90 entries for mock
        self.data[rule_name] = self.data[rule_name][-90:]
        self.save()

    def get_deviations(self, rule_name, days=90):
        """Mock return of historical deviations to test z-score logic."""
        if rule_name in self.data and len(self.data[rule_name]) >= 10:
             return self.data[rule_name][-days:]
        
        # If no history, simulate a baseline of small fluctuations
        return [0.5, 1.2, 0.3, 0.8, 1.5, 0.2, 0.7, 1.1, 0.9, 0.4, 0.6, 1.3]
