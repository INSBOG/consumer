from adapters.mongo import MongoAdapter
from validators.validator import Validator
from datetime import datetime
import pandas as pd

class SpecValidator(Validator):

    def __init__(self, df, month, errors: dict = {}):
        super().__init__(df)
        self.errors = errors
        self.month = month
        self.db = MongoAdapter()

    def validate(self):
        self.__validate_spec_date()
        self.__validate_spec_type()
        self.__validate_spec_code()

    def __validate_spec_type(self):
        invalid_specs = self.df["SPEC_TYPE"].apply(lambda x: not self.__get_spec_type(x))

        for index in invalid_specs[invalid_specs].index:
            self.errors.setdefault(index, {}).update(
                {"SPEC_TYPE": "La sigla no esta estandarizada en el diccionario WHONET."})

    def __validate_spec_date(self):

        self.df["SPEC_DATE"] = pd.to_datetime(self.df["SPEC_DATE"], errors='coerce', dayfirst=True)

        self.df["SPEC_DATE"] = self.df["SPEC_DATE"].apply(lambda x: x.strftime("%Y-%m-%d"))
        invalid_dates = self.df["SPEC_DATE"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").strftime("%Y-%m") != self.month)

        for index in invalid_dates[invalid_dates].index:
            self.errors.setdefault(index, {}).update(
                {"SPEC_DATE": "El fecha no coincide con el mes de notificación."})
            
    def __get_spec_type(self, spec_type: str):
        sample = self.db.get_collection("samples").find_one({"acron": spec_type})
        return sample.get("num_value", False) if sample else False

    def __validate_spec_code(self):

        def check_spec_code(row):
            spec_code = row.get("SPEC_CODE", 0)
            spec_type = row.get("SPEC_TYPE")

            sample = self.db.get_collection("samples").find_one({"acron": spec_type})
            if not sample:
                self.errors.setdefault(row.name, {}).update(
                    {"SPEC_TYPE": "La sigla no esta estandarizada en el diccionario WHONET."})
                return

            if spec_code != sample.get("num_value", ""):
                self.errors.setdefault(row.name, {}).update(
                    {"SPEC_CODE": "la sigla no concuerda con el codigo numérico de muestra."})

        self.df.apply(lambda x: check_spec_code(x), axis=1)
