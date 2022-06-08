import pandas as pd


class Excel_Processing:
    def __init__(self, fname):
        self.fname = fname
        self.df = pd.read_excel(fname)

        self.shops = self.df.columns[6:].to_list()
        self.months = list(self.df['Month'].unique())
        self.items = list(self.df['Item'].unique())
        self.brands = list(self.df['BRAND'].unique())

        self.data = self._data()
        
    def _data(self):
        clean_data  = self.df
        clean_data = clean_data.set_index(['Month', 'Item', 'BRAND'], append=True, drop=True)
        clean_data = clean_data.drop(columns = ['PGBRAND', 'MonthBRAND'])
        return clean_data