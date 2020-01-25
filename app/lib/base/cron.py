class CronManager:
    def __init__(self, sessions):
        self.sessions = sessions

    def run(self):
        self.cron_check_running_sessions()
        self.cron_send_notifications()
        return True

    def cron_check_running_sessions(self):
        self.sessions.terminate_past_sessions()
        return True

    def cron_send_notifications(self):
        self.sessions.send_notifications()
        return True
