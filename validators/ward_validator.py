
from bson import ObjectId
import pandas as pd

from adapters.mongo import MongoAdapter
from validators.validator import Validator


class WardValidator(Validator):

    def __init__(self, df: pd.DataFrame, report: dict = None, errors = {}):
        super().__init__(df)
        self.report = report
        self.errors = errors
        self.db = MongoAdapter()

    def validate(self):
        self.__validate_ward_with_age()
        self.__validate_ward_and_ward_type()

    def __validate_ward_with_age(self):
        col = self.db.get_collection("services")
        svcs = list(col.find({}))
        self.df["VALIDATION_ERRORS"] += self.df.apply(
            lambda x: self.__check_exists(x, svcs), axis=1)

    def __check_exists(self, row, services):

        ward = row.get("WARD")
        svcs = list(filter(lambda s: ward in s.get("WARDS"), services))
        pat_types = [row["PAT_TYPE"] for row in svcs]

        if len(pat_types) == 0:
            self.errors.setdefault(row.name, {}).update({"WARD": "La sigla no esta estandarizada en el diccionario nacional"})
            return

        age = self.parse_age(row.get("AGE", 0))


        if "todas las edades" in pat_types:
            return

        if age == self.one_month and set(pat_types) & {"new", "ped"}:
            return

        err_str = "La edad del paciente no concuerda con la localizacion"

        if age < self.one_month and "new" not in pat_types:
            self.errors.setdefault(row.name, {}).update({"WARD": err_str})
        elif self.one_month <= age < 18 and "ped" not in pat_types:
            self.errors.setdefault(row.name, {}).update({"WARD": err_str})
        elif age >= 18 and "adu" not in pat_types:
            self.errors.setdefault(row.name, {}).update({"WARD": err_str})
        else:
            return

    def __validate_ward_and_ward_type(self):
        department = self.report.get("department")
        col = self.db.get_collection("locations")
        location = col.find_one({"_id": ObjectId(department)})

        if not location:
            raise ValueError(f"Location with id '{department}' not found.")

        values = location.get("values", [])

        invalid_wards = self.df.apply(lambda x: f"{x['WARD']}-{x['WARD_TYPE']}" not in values, axis=1)

        for index in invalid_wards[invalid_wards].index:
            self.errors.setdefault(index, {}).update({
                "WARD": "La localizacion no concuerda con el  tipo de localizacion",
                "WARD_TYPE": "El tipo localizacion no concuerda con la localizacion"
            }) 
