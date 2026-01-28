import pandas as pd

class TransformData:
    
    # 엑셀을 통해 추출한 데이터 컬럼 중 EPS, PER, 선행 EPS, 선행 PER, BPS, PBR는 nullable(null값이 '-'로 표현)되어 object형이므로 변환 필요.
    def to_numerical_cols(table):
        to_numeric_columns = ['EPS', 'PER', '선행 EPS', '선행 PER', 'BPS', 'PBR']

        for col in to_numeric_columns:
            table[col] = pd.to_numeric(table[col], errors='coerce') # Null값은 NaN으로 처리
        
        return table