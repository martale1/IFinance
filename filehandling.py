import pandas as pd

class fileHandling:
  def __init__(self, path='/home/developer/PycharmProjects/finance/'):
    self.path=path
    self.valid_name=None
    self.valid_ticker=None
    self.US_ETFTickers=None
    self.US_ETFNames=None
    self.US_OthersTickers=None
    self.US_OthersNames=None
    self.MIB30Names=None
    self.MIB30Tickers=None
    self.ETCTickers = None
    self.ETCNames = None
    self.getValidETC(0)
    self.getValidMIB30(0)
    self.getValidUS_ETF(0)
    self.getValidUS_Others(0)
    self.getValidTicker(0)
    # Define the path to the Excel file




  def getValidUS_Others(self,nTicker=10):
    # Mount Google Drive
    # Define the path to the Excel file
    filename = 'validtickers_US_Others.xlsx'
    file_path = self.path + filename
    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Assuming 'ticker' is the name of the column containing tickers
    if nTicker==0:
      ne=len(df)
    else:
      ne=nTicker
    self.US_OthersTickers = df['Ticker'].head(ne).tolist()
    self.US_OthersNames = df['Name'].head(ne).tolist()

  def getValidUS_ETF(self,nTicker=10):
    # Mount Google Drive
    # Define the path to the Excel file

    filename = 'validtickers_US_ETF.xlsx'
    file_path = self.path + filename
    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Assuming 'ticker' is the name of the column containing tickers
    if nTicker==0:
      ne=len(df)
    else:
      ne=nTicker
    self.US_ETFTickers = df['Ticker'].head(ne).tolist()
    self.US_ETFNames = df['Name'].head(ne).tolist()

  def getValidTicker(self,nTicker=10):
    # Mount Google Drive
    # Define the path to the Excel file
    filename = 'validtickers_IT_Others.xlsx'
    file_path = self.path + filename
    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Assuming 'ticker' is the name of the column containing tickers
    if nTicker==0:
      ne=len(df)
    else:
      ne=nTicker
    self.valid_ticker = df['Ticker'].head(ne).tolist()
    self.valid_name = df['Name'].head(ne).tolist()

  def getValidETC(self,nTicker=10):
    # Mount Google Drive
    # Define the path to the Excel file
    filename = 'validtickers_IT_ETC.xlsx'
    file_path = self.path + filename
    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Assuming 'ticker' is the name of the column containing tickers
    if nTicker==0:
      ne=len(df)
    else:
      ne=nTicker
    self.ETCTickers = df['Ticker'].head(ne).tolist()
    self.ETCNames = df['Name'].head(ne).tolist()

  def getValidMIB30(self,nTicker=10):
    # Mount Google Drive
    # Define the path to the Excel file
    filename = 'MIB30_infoproviders.xlsx' #validation not needed
    file_path = self.path + filename
    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Assuming 'ticker' is the name of the column containing tickers
    if nTicker==0:
      ne=len(df)
    else:
      ne=nTicker
    self.MIB30Tickers = df['Ticker'].head(ne).tolist()
    self.MIB30Names = df['Name'].head(ne).tolist()

  def dfToCSV(self, df, output_file):
    # Save DataFrame to a CSV file
    output_path = self.path + output_file
    df.to_csv(output_path, index=False)
    print(f"Output saved to: {output_path}")

  def fromCSVToDF(self, input_file):
        # Define the path to the CSV file
        input_path = self.path + input_file
        # Read the CSV file into a DataFrame
        df = pd.read_csv(input_path)
        return df

  def dfToXLSX(self, df, output_file):
    # Save DataFrame to a CSV file
    output_path = self.path + output_file
    df.to_excel(output_path, index=False)
    print(f"Output saved to: {output_path}")

  def fromXLSXToDF(self, input_file):
        # Define the path to the CSV file
        input_path = self.path + input_file
        # Read the CSV file into a DataFrame
        df = pd.read_excel(input_path)
        return df

  def getTickerList(self,market):
    if market=='ETC':
      return self.ETCTickers,self.ETCNames
    elif market=='MIB30':
      return self.MIB30Tickers,self.MIB30Names
    elif market=='ETF':
      return self.valid_ticker,self.valid_name
    elif market=='US_ETF':
      return self.US_ETFTickers,self.US_ETFNames
    elif market=='US_Others':

      return self.US_OthersTickers,self.US_OthersNames
    else:
      return None, None




