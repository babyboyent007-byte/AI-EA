import pandas as pd

class TimeSeriesSplitter:
    """
    Ensures Train/Val/Test splits respect the arrow of time.
    """
    def __init__(self, train_pct=0.7, val_pct=0.15):
        self.train_pct = train_pct
        self.val_pct = val_pct

    def split(self, df: pd.DataFrame):
        df = df.sort_values('timestamp')
        n = len(df)
        
        train_end = int(n * self.train_pct)
        val_end = int(n * (self.train_pct + self.val_pct))
        
        train = df.iloc[:train_end]
        val = df.iloc[train_end:val_end]
        test = df.iloc[val_end:]
        
        print(f'[Splitter] Split complete: Train({len(train)}), Val({len(val)}), Test({len(test)})')
        return train, val, test