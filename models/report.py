from adapters.mongo import MongoAdapter
from classes.validator import Validator

class Reporte(Validator):
    def __init__(self, mongo_adpter: MongoAdapter, data: dict = {}):
        super().__init__(mongo_adpter)

        for key, value in data.items():
            if key == "ORIGIN":
                setattr(self, key, value or "h")
            else:
                setattr(self, key, value)



