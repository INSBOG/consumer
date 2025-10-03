import pandas as pd

from tests.test_data import get_temp_row
from validators.ward_validator import WardValidator

class TestWardValidator:

    def test_ward_validator(self):
        data = get_temp_row()
        data["AGE"] = "23d"
        data["PAT_TYPE"] = "new"
        data["WARD"] = "ucine"

        df = pd.DataFrame(data)

        df["VALIDATION_ERRORS"] = ""

        errors = {index: {} for index in range(len(df))}

        validator = WardValidator(df, errors)

        validator.validate()

        assert errors[0] == {}