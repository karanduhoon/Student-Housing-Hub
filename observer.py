class NotificationSystem:
    def __init__(self):
        self.notifications = []

    def notify(self, message):
        self.notifications.append(message)

    def get_notifications(self):
        current_notifications = self.notifications[:]
        self.notifications.clear()
        return current_notifications
