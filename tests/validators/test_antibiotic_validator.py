from validators.antibiotic_validator import AntHoja1Validator
import pandas as pd



class TestAntibioticValidator:

    @staticmethod
    def test_hoja_1():

        data = pd.DataFrame({
            "ORGANISM": ["ctr"],
            "FLU_NM": ">32"
        })

        errors = {}

        validator = AntHoja1Validator(errors, data)
        validator.validate()

        assert errors == {0: {'FLU_NM': 'Resistencia inusual a antif\xfangicos, enviar aislamiento al INS ,FLU_NM con este organismo ctr'}}