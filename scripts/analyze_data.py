import pandas as pd

class AnalyzeData:

    def filter_stock(table):
        # 2025 상장폐지 사유 발생 기업 필터링
        delisting_stock = ['국보', '웰바이오텍', '세원이엔씨', '아이에이치큐', '이아이디', 'KH 필룩스', '금양', 
                   'KC코트렐', 'KC그린홀딩스', '범양건설', '효성화학', '한국패러랠', '한창']
        table.drop(table[table['종목명'].isin(delisting_stock)].index, inplace=True)

        return table

    def stock_suppression_prevention_raw_impact(table):
        table['T_Price'] = table['BPS'] * 0.8
        table['D_Support'] = table['BPS'] * 0.35
        table['U_Potential'] = (table['T_Price'] / table['종가'] - 1) * 100
        table['RR_Ratio'] = (table['T_Price'] - table['종가']) / (table['종가'] - table['D_Support'])

        result = table.sort_values(by=['U_Potential'], ascending=False)
        result.reset_index(drop=True, inplace=True)

        return result