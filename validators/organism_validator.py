from validators.validator import Validator
import pandas as pd

#"VAN_NM",
#"AMP_NM",
#"LNZ_NM"

class OrganismValidator(Validator):

    def __init__(self, df: pd.DataFrame, errors = {}):
        super().__init__(df)
        self.errors = errors

    def validate(self):
        comp_df = pd.read_excel("files/base-comparacion.xlsx")

        empty_ant = self.df[self.df["VAN_NM"].isna() | self.df["AMP_NM"].isna() | self.df["LNZ_NM"].isna()] #

        empty_ant.sort_values(by=["ORGANISM"]).apply(lambda item: self.__check_ant_with_org(item, comp_df), axis=1)

    def __check_ant_with_org(self, item, comp_df: pd.DataFrame):
        org = item.get("ORGANISM")

        ants = comp_df.loc[
           (comp_df["ORGANISMO"] == org) &
           (comp_df["ANTIBIOTICO_B"].isin(["VAN_NM", "AMP_NM", "LNZ_NM"]))
        ]

        if ants.empty:
            return

        for index, row in ants.iterrows():
            antibiotic = row.get("ANTIBIOTICO_B")
            value = item.get(antibiotic)

            if pd.isna(value):
                self.errors[item.name].update({
                    antibiotic: f"{antibiotic} - Registro vacío"
                })



