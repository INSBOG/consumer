

from adapters.mongo import MongoAdapter
from validators.validator import Validator
from constants import not_empty_columns
import pandas as pd


class GeneralValidator(Validator):
    def __init__(self, df, errors: dict = {}):
        super().__init__(df)
        self.df = df
        self.errors = errors
        self.db = MongoAdapter()
        self

    def validate(self):
        self.__validate_empty()
        self.__validate_name_lastname()
        self.__validate_institut_laboratory()
        self.__validate_sex()
        self.__validate_birthdate()
        self.__validate_country()
        self.__validate_orgs()
        self.__validate_datebirth_specdate()
        self.__validate_age()

    def __validate_empty(self):
        if "ORIGIN" not in self.df.columns:
            return
        
        self.df["ORIGIN"] = self.df["ORIGIN"].replace("", "h").fillna("h")
        for column in self.df.columns.to_list():
            
            if column not in not_empty_columns:
                continue

            null_values = self.df[column].isnull()
            for index in null_values[null_values].index:
                self.errors.setdefault(index, {}).update(
                    {column: f"{column} - Registro vacío"})
                
    def __validate_name_lastname(self):
        if "FIRST_NAME" not in self.df.columns or "LAST_NAME" not in self.df.columns:
            return
        empty_name = self.df["FIRST_NAME"].isna() & self.df["LAST_NAME"].isna()

        for index in empty_name[empty_name].index:
            self.errors.setdefault(index, {}).update({
                "FIRST_NAME": "Nombre y apellido no pueden estar vacíos",
                "LAST_NAME": "Nombre y apellido no pueden estar vacíos"
            })

    def __validate_institut_laboratory(self):
        if "INSTITUT" not in self.df.columns or "LABORATORY" not in self.df.columns:
            return
        # Identificar filas donde las columnas no coinciden
        mismatched_rows = self.df[self.df["INSTITUT"].str.lower() != self.df["LABORATORY"].str.lower()]

        # Registrar errores específicos para cada fila
        for index in mismatched_rows.index:
            self.errors.setdefault(index, {}).update({
                    "INSTITUT": "Sigla de la columna LABORATORY vs INSTITUT no coincide",
                    "LABORATORY": "Sigla de la columna LABORATORY vs INSTITUT no coincide"
                })
    
    def __validate_sex(self):
        if "SEX" not in self.df.columns:
            return
        # Verifica si los valores no están en ["m", "f"]
        invalid_sex = ~self.df["SEX"].str.lower().isin(["m", "f"])
        for index in invalid_sex[invalid_sex].index:
            self.errors.setdefault(index, {}).update({"SEX": "No corresponde a la sigla M y F"})

    def __validate_birthdate(self):
        if "DATE_BIRTH" not in self.df.columns:
            return
        # Convertir la columna a datetime, manteniéndola como datetime
        self.df["DATE_BIRTH"] = pd.to_datetime(
            self.df["DATE_BIRTH"], format="%d/%m/%Y", errors="coerce", dayfirst=True
        )

        # Identificar fechas inválidas (convertidas a NaT)
        invalid_birthdates = self.df[self.df["DATE_BIRTH"].isna()]

        # Rellenar NaT con fecha base si necesitas evitar errores más adelante
        self.df["DATE_BIRTH"] = self.df["DATE_BIRTH"].fillna(pd.Timestamp("1900-01-01"))

        # Registrar errores
        for index in invalid_birthdates.index:
            self.errors.setdefault(index, {}).update({
                "DATE_BIRTH": "DATE_BIRTH debe ser una fecha válida"
            })


    def __validate_age(self):
        if "AGE" not in self.df.columns:
            return
        more_than_100 = self.df["AGE"].fillna(0).apply(lambda x: self.parse_age(x) > 100)
        invalid_ages = self.df["AGE"].fillna(0).apply(lambda x: not(0 <= self.parse_age(x) < 105))

        for index in invalid_ages[invalid_ages].index:
            self.errors.setdefault(index, {}).update(
                {"AGE": "AGE debe ser un número entre 0 y 105"})

        for index in more_than_100[more_than_100].index:
            self.errors.setdefault(index, {}).update(
                {"AGE": "Confirmar edad"})


    def __validate_country(self):
        if "COUNTRY_A" not in self.df.columns:
            return
        invalid_countries = self.df["COUNTRY_A"].apply(lambda x: x != "COL")

        for index in invalid_countries[invalid_countries].index:
            self.errors.setdefault(index, {}).update(
                {"COUNTRY_A": "COUNTRY_A debe ser 'COL'"})
            

    def __validate_orgs(self):
        if "ORGANISM" not in self.df.columns or "LOCAL_ORG" not in self.df.columns:
            return
        col = self.db.get_collection("organisms")
        def check_orgs(row):
            org = row.get("ORGANISM")
            local_org = row.get("LOCAL_ORG")
            item = col.find_one({"org": org})

            if not item:
                self.errors.setdefault(row.name, {}).update(
                    {"ORGANISM": "La sigla de organismo no esta estandarizada en el diccionario WHONET"})
                return
            
            if local_org not in item.get("organisms", []):
                self.errors.setdefault(row.name, {}).update(
                    {"LOCAL_ORG": "La sigla del orgarnismo no concuerda con el codigo local del organismos"})
            

        self.df.apply(check_orgs, axis=1)

    def __validate_datebirth_specdate(self):
        if "DATE_BIRTH" not in self.df.columns or "SPEC_DATE" not in self.df.columns:
            return
        self.df.apply(lambda x: self.__check_datebirth_specdate(x), axis=1)

    def __check_datebirth_specdate(self, row):
        if pd.isna(row.get("DATE_BIRTH")) or pd.isna(row.get("SPEC_DATE")):
            return
        date_birth = pd.to_datetime(row.get("DATE_BIRTH"), errors="coerce", dayfirst=True)
        spec_date = pd.to_datetime(row.get("SPEC_DATE"), errors="coerce", dayfirst=True)

        if pd.isna(date_birth) or pd.isna(spec_date):
            return  # o manejar el error de fechas inválidas si quieres

        if date_birth >= spec_date:
            self.errors.setdefault(row.name, {}).update(
                {
                    "SPEC_DATE": "Fecha de toma de muestra no puede ser anterior a la fecha nacimiento",
                    "DATE_BIRTH": "Fecha de nacimiento mayor a la toma de muestra"
                }
            )

