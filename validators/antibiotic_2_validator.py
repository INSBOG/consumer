from validators.validator import Validator
from pandas import DataFrame
import pandas as pd

MSGS = {
    4: "Resistencia a LNZ, envio al INS según criterio",
    6: "Resistencia inusual a antifúngicos, envio al INS según criterios",
    7: "Envio al INS según criterios"
}

class Antibiotic2Validator(Validator):
    
    def __init__(self, df: DataFrame, errors: dict):
        self.df = df
        self.errors = errors
        self.comp_df = pd.read_excel("files/base-comparacion.xlsx", sheet_name=None)

    def check(self, row: pd.Series, ants: list, orgs: list, muestras: list, tipo_loc: list, sheet: int):
        org = row.get("ORGANISM")
        muestra = row.get("SPEC_TYPE")
        loc = row.get("WARD_TYPE")

        if ants and len(ants) > 0:

            for _ant, sym in ants:
                ant = row.get(_ant)

                limit_sim, limit_value = self.separate(sym)
                sim, val = self.separate(ant)


                if limit_value and val:
                    is_resistant = sym == ant or self.OPERATORS[limit_sim](float(val), float(limit_value))


                    if val and sim in limit_sim:
                        if (
                            is_resistant
                            and org in orgs
                            and muestra in muestras
                            and loc in tipo_loc
                        ):
                            self.errors.setdefault(row.name, {})[_ant] = MSGS.get(sheet, "Error desconocido")
        else:
            if (
                org in orgs
                and muestra in muestras
                and loc in tipo_loc
            ):
                self.errors.setdefault(row.name, {}).update({
                    "ORGANISM": MSGS.get(sheet, "Error desconocido"),
                })


    def validate(self):
        print("Validando Antibioticos parte 2...")
        sheets = [4, 6, 7]

        for sheet in sheets:
            print(f"Validando hoja{sheet}...")
            comp_data = self.comp_df[f"Hoja{sheet}"]

            ants = None
            if sheet != 7:
                ants = set(comp_data[["ANTIBIOTICO_B", "SIMBOLO"]].itertuples(index=False, name=None))

            
            orgs = comp_data["ORGANISMO"].dropna().unique().tolist()
            muestras = comp_data["SIGLA_DE_MUESTRA"].dropna().unique().tolist()
            tipo_loc = comp_data["TIPO_LOCALIZACION"].dropna().unique().tolist()

            self.df.apply(lambda row: self.check(
                    row=row, 
                    ants=ants, 
                    orgs=orgs, 
                    muestras=muestras, 
                    tipo_loc=tipo_loc,
                    sheet=sheet
                ), axis=1)

