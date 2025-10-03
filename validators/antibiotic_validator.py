import pandas as pd
import re
import operator
from antibiotic_df import df as ant_df
from enum import Enum
from abc import abstractmethod, ABC

class AntValidator(ABC):
    df: pd.DataFrame
    columns: list
    data: pd.DataFrame
    ant: str
    errors: dict

    OPERATORS = {
        ">": operator.gt, 
        ">=": operator.ge, 
        "<": operator.lt, 
        "<=": operator.le
    }

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def check(self, row: pd.Series):
        pass

    def separate(self, value):
        match = re.search(r"(<|<=|>|>=)?(\.?\d+)", str(value))
        return (match.group(1) or "", match.group(2)) if match else ("", "")

class AntHoja1Validator(AntValidator):

    def __init__(self, errors: dict, data: pd.DataFrame):
        super().__init__()
        self.data = data
        self.errors = errors
        self.df = pd.read_excel("files/base-comparacion.xlsx", sheet_name=None)

    def check(self, row):
        org = row.get("ORGANISM")
        ant_list = self.df[self.df["ORGANISMO"] == org]
             
        if not ant_list.empty:
            for k, ant in ant_list.iterrows():
                sim, definition, ant_b = ant.get("SIMBOLO"), ant.get("DEFINICION"), ant.get("ANTIBIOTICO_B")
                value = row.get(ant_b)
                op, val = self.separate(value)
                limit_op, limit_val = self.separate(sim)

                if limit_val and val:
                    is_resistant = sim == value or self.OPERATORS[limit_op](float(val), float(limit_val))

                    if val and limit_val and op in limit_op and is_resistant:
                        self.errors.setdefault(row.name, {})[ant_b] = definition

    def validate(self):
        print("Validando hoja 1...")
        self.data.apply(self.check, axis=1)

class AntComparisonValidator(AntValidator):

    def __init__(
        self, 
        usecols: str, 
        ant: str, 
        errors: dict = {},
        data: pd.DataFrame = None,
        sheet_name=None
    ):
        super().__init__()
        self.data = data
        self.df = pd.read_excel(
            "files/base-comparacion.xlsx",
            sheet_name=sheet_name,
            usecols=usecols
        ).dropna(how="all")

        self.columns = [f"{col.split('.')[0]}_NM" for col in self.df.columns if "ORGANISMO" not in col]
        self.ant = ant

        self.df.columns = self.columns + ["ORGANISM"]
        self.errors = errors


    def check(self, row: pd.Series):
        antibiotics = row[self.columns[:-1]] # Todos los antibióticos menos la ultima columns
        org = row.get("ORGANISM") # Organismo de la fila
        orgs = self.df["ORGANISM"].values # Organismos del archivo de comparacion

        INT = {}
        for key, value in antibiotics.items():
            if not value:
                print("No hay valor.")
                continue

            op, val = self.separate(value)
            if val:
                limit_row = ant_df[ant_df["ANTIBIOTICO"] == key]
                limit = limit_row["SIMBOLO"].values[0] if not limit_row.empty else None

                limit_op, limit_val = self.separate(limit)

                if limit_val and val:
                    is_resistant = limit == value or self.OPERATORS[limit_op](float(val), float(limit_val))
                    if limit_val and op in limit_op and is_resistant:
                        INT[key] = "R"
                    else:
                        INT[key] = "S"

        int_str = "".join(INT.values())
        is_resistant = self.ant in INT and INT[self.ant] == "R"
        sensitive = [key for key, value in INT.items() if value == "S"]

        if (
            is_resistant
            and len(int_str) == len(self.columns[:-1])
            and int_str.count("R") == 1
            and self.ant in INT
            and org in orgs
        ):
            msg = f"El antibiótico {self.ant} es resistente, y los antibióticos {', '.join(sensitive)} son sensibles con el organismo {org}"
            if self.ant in self.errors.setdefault(row.name, {}):
                if self.errors.setdefault(row.name, {})[self.ant] != msg:
                    self.errors.setdefault(row.name, {})[self.ant] += f"; {msg}"
            else:
                self.errors.setdefault(row.name, {})[self.ant] = msg

    def validate(self):
        if all(col in self.data.columns for col in self.columns):
            self.columns.append("ORGANISM")
            self.data[self.columns].apply(self.check, axis=1)



# Validación
class AntEnum(Enum):
    ETP_NM = "ETP_NM"
    IPM_NM = "IPM_NM"
    MEM_NM = "MEM_NM"
    FEP_NM = "FEP_NM"
    CZA_NM = "CZA_NM"
    CAZ_NM = "CAZ_NM"

class Hoja(Enum):
    HOJA1 = "Hoja1"
    HOJA2 = "Hoja2"
    HOJA3 = "Hoja3"

class Ant:
    def __init__(self, rng: str, name: AntEnum, sheet: Hoja):
        self.name = name.value
        self.rng = rng
        self.sheet = sheet.value