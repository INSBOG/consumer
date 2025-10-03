import pandas as pd
from validators.general_validator import GeneralValidator

class TestGeneralValidator:
    @staticmethod
    def test_validate_empty():
        with open("tests/data.json") as f:
            df = pd.read_json(f)

        errors = {index: {} for index in range(len(df))}
        validator = GeneralValidator(df, errors)
        validator.validate()

        assert validator.errors == {
            0: {
                'VAN_NM': 'VAN_NM no puede ser vacío', 
                'AMP_NM': 'AMP_NM no puede ser vacío', 
                'LNZ_NM': 'LNZ_NM no puede ser vacío', 
                'FIRST_NAME': 'FIRST_NAME y LAST_NAME no pueden ser vacíos', 
                'LAST_NAME': 'FIRST_NAME y LAST_NAME no pueden ser vacíos'
            }, 
            1: {}, 
            2: {
                'VAN_NM': 'VAN_NM no puede ser vacío', 
                'AMP_NM': 'AMP_NM no puede ser vacío', 
                'LNZ_NM': 'LNZ_NM no puede ser vacío'
            }, 
            3: {
                'VAN_NM': 'VAN_NM no puede ser vacío', 
                'AMP_NM': 'AMP_NM no puede ser vacío', 
                'LNZ_NM': 'LNZ_NM no puede ser vacío'
            }, 
            4: {
                'VAN_NM': 'VAN_NM no puede ser vacío', 
                'AMP_NM': 'AMP_NM no puede ser vacío', 
                'LNZ_NM': 'LNZ_NM no puede ser vacío'
            }
        }
