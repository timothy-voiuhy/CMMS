class InventoryOps:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.console_logger = self.db_manager.console_logger

    def connect(self):
        return self.db_manager.connect()

    def close(self):
        return self.db_manager.close()

