import pandas

class PrintData:
    def to_table(table):
        return table.style.hide(axis='index').format({
            'BPS': '{:.0f}',
            'PBR': '{:.2f}',
            'T_Price': '{:.2f}',
            'D_Support': '{:.0f}',
            'U_Potential': '{:.2f}',
            'RR_Ratio': '{:.2f}',
        })

    def to_selected_row(table, selected_cols):
        table[table['종목명'].isin(selected_cols)].style.hide(axis='index').format({
            'BPS': '{:.0f}',
            'PBR': '{:.2f}',
            'T_Price': '{:.2f}',
            'D_Support': '{:.0f}',
            'U_Potential': '{:.2f}',
            'RR_Ratio': '{:.2f}',
        })