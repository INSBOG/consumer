from tests.test_data import get_temp_row
from validators.organism_validator import OrganismValidator
import pandas as pd

class TestOrganismValidator:

    @staticmethod
    def test_validate():
        data = get_temp_row()

        data["ORGANISM"] = ["efa"]
        data["AMP_NM"] = [None]

        df = pd.DataFrame(data)

        errors = {index: {} for index in range(len(df))}

        validator = OrganismValidator(df, errors)

        validator.validate()

        assert errors == {0: {
            'AMP_NM': 'Registro vacío',
            'LNZ_NM': 'Registro vacío',
        }}

