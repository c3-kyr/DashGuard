class AlertDistributor:
    def __init__(self, config):
        self.config = config

    def send_alert(self, alert):
        severity = alert["severity"]
        
        # Mock printing out what it would do instead of actually sending SMS/Email/Slack
        print(f"\n[{severity} ALERT Triggered]")
        print("-" * 40)
        print(f"Rule: {alert['rule_name']}")
        print(f"Deviation: {alert['deviation_pct']}% (Z-Score: {alert['z_score']})")
        print(f"Recommendation: {alert['recommendation']}")
        print(f"Context: {alert['contextual_factors']}")
        print("Actions Taken:")

        if severity == "CRITICAL":
            print(f" -> [SMS] sent to: {self.config.get('critical_contacts', [])}")
            print(f" -> [Email] sent to: {self.config.get('critical_email_list', [])}")
            print(f" -> [Slack] message sent to: {self.config.get('slack_channel_critical', '')}")

        elif severity == "HIGH":
            print(f" -> [Email] sent to: {self.config.get('standard_email_list', [])}")
            print(f" -> [Slack] message sent to: {self.config.get('slack_channel_alerts', '')}")

        elif severity == "MEDIUM":
            print(f" -> [Slack] message sent to: {self.config.get('slack_channel_alerts', '')}")
            
        elif severity == "WARNING":
            print(f" -> [Slack] message sent to: {self.config.get('slack_channel_alerts', '')} (Downgraded due to context)")

        else:
            print(" -> [Log] Logged for tracking. No notifications sent.")
        print("-" * 40 + "\n")
