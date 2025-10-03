from abc import ABC, abstractmethod

import pandas as pd
import re
import operator


class Validator(ABC):
    df: pd.DataFrame = None
    one_month = 1/12

    OPERATORS = {">": operator.gt, ">=": operator.ge, "<": operator.lt, "<=": operator.le}

    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def validate(self):
        pass
    

    def parse_age(self, age):
        if isinstance(age, str):
            age_str = age.lower()
            if "d" in age_str:
                return int(age_str.replace("d", "")) / 365
            elif "m" in age_str:
                return int(age_str.replace("m", "")) / 12
            return int(age_str or 0)
        return age
    
    def separate(self, value):
        match = re.search(r"(<|<=|>|>=)?(\.?\d+)", str(value))
        return (match.group(1) or "", match.group(2)) if match else ("", "")