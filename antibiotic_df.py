import pandas as pd

# CZA_NM: >8
# ETP_NM: >=1
# IPM_NM: >=2
# MEM_NM: >=2
# CAZ_NM: >8
# CRO_NM: >=2
# CTX_NM: >=2
# FEP_NM: >=4

df = pd.DataFrame({
    "ANTIBIOTICO": ["CZA_NM", "ETP_NM", "IPM_NM", "MEM_NM", "CAZ_NM", "CRO_NM", "CTX_NM", "FEP_NM"],
    "SIMBOLO": [">8", ">=1", ">=2", ">=2", ">8", ">=2", ">=2", ">=4"],
})

