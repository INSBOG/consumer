
from validators.validator import Validator


class PatTypeValidator(Validator):

    def __init__(self, df, errors):
        self.df = df
        self.errors = errors

    def validate(self):
        self.df["VALIDATION_ERRORS"] += self.df.apply(lambda x: self.__check_pat_type(x), axis=1)

    def __check_pat_type(self, row):
        age = row.get("AGE")
        pat_type = row.get("PAT_TYPE")

        parsed_age = self.parse_age(age)

        if pat_type == "neo":
            self.errors.setdefault(row.name, {}).update({"PAT_TYPE": "Sigla correcta new"})
            return

        if parsed_age == self.one_month and pat_type in ("new", "ped"):
            return None

        msg = "El tipo de paciente con coincide con la edad"

        if parsed_age < self.one_month and pat_type != "new":
            self.errors.setdefault(row.name, {}).update({"PAT_TYPE": msg})
        elif self.one_month <= parsed_age <= 18 and pat_type == "new":
            self.errors.setdefault(row.name, {}).update({"PAT_TYPE": msg})
        elif parsed_age > 18 and pat_type != "adu":
            self.errors.setdefault(row.name, {}).update({"PAT_TYPE": msg})

