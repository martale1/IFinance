
import warnings
from GenerateScoringAndSignals import GenerateScoringAndSignals
from dbTickersData import dbTickersData
from dbValidTickers import dbValidTickers
from messaging import messaging
import pandas as pd
from datetime import datetime


def log_execution(nation, instrument_type):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{current_time}] Processed {nation} - {instrument_type}\n"

    # Append the log message to a file
    with open("/home/developer/PycharmProjects/learningProjects/IFinance/run_log.txt", "a") as log_file:
        log_file.write(log_message)

def run(nation,instrument_type,limit=0):
    db = dbValidTickers()
    listaTickerConPochiDati=[]
    nation = nation #IT, US
    instrument_type = instrument_type #ETC,ETF, #MIB30
    #Legge la lista ticker per lo strumento in oggetto
    tickers_df = db.get_tickers_by_nation_and_instrument(nation, instrument_type)
    total=len(tickers_df)
    print("Tickers ETC per la nazione IT:")
    if limit:
        tickers_df=tickers_df.head(limit)
    #Crea oggetto a db che contiene i dati sui Tickers
    dbT=dbTickersData()
    i=0
    actualAnalyzed=len(tickers_df)

    for index, row in tickers_df.iterrows():
        i=i+1

        ticker = row['ticker']  # Colonna del ticker
        ticker_name = row['name']  # Colonna del nome del ticker
        print(f"{i} out of {actualAnalyzed}. TotalDB: {total} - Ticker: {ticker} - {ticker_name}. ")
        ts = GenerateScoringAndSignals(ticker, ticker_name, ema_period=50, period='2y', candles=0)
        if len(ts.data)>10 and row['excluded']==0 :
            ts.run()
            json_data = ts.download_json()
            #print(json_data)
            #Aggiorna db che contiene il ticker con i dati aggiornati, anche con nation and instrument_type
            #print("Salvo")
            #print(json_data)
            dbT.save_json_data(json_data,nation, instrument_type)
        else:
            print("Ticker con meno di 10 campi:"+ticker)
            listaTickerConPochiDati.append(ticker)
            dbT.delete_json_data(ticker)

    num_entries = dbT.count_entries()
    print(f"Numero di voci nel database: {num_entries}")
    print("Titoli scartati:"+str(listaTickerConPochiDati))
    log_execution(nation, instrument_type)


def checkSignalsAndSendTelegram(instrument_type,limit=None):
    nation = "IT"
    myDb = dbTickersData()

    # Retrieve data from the database
    (df_count_1, df_count_neg_1, df_tickers_1, df_ticker_names_1,
     df_volume, df_percent_change_2, df_signal6, df_scoring) = myDb.get_signal_counts_and_ticker_lists(nation,
                                                                                                       instrument_type)

    # Number of tickers in S2
    numTickersS2 = df_count_1['S2']

    # Extract the tickers and names strings
    tickers_str = df_tickers_1['S2'].iloc[0]  # Assuming the first element contains the comma-separated string
    ticker_names_str = df_ticker_names_1['S2'].iloc[0]  # Same assumption for names

    # Split the strings into lists
    tickers_list = tickers_str.split(', ')
    ticker_names_list = ticker_names_str.split(', ')

    print(tickers_list)  # Debug: Check tickers list
    print(ticker_names_list)  # Debug: Check names list

    # Apply the limit to the lists
    if limit is not None:
        tickers_list = tickers_list[:limit]
        ticker_names_list = ticker_names_list[:limit]

    # Combine tickers, names, and links line by line
    if len(tickers_list) == len(ticker_names_list):
        scoring = 0
        signal6 = 0
        formatted_tickers = '\n'.join(
            f"<a href='http://theoiziruam.ddns.net:8503/?ticker={ticker}&scoring={scoring}&signal6={signal6}'>{ticker}</a>: {name}"
            for ticker, name in zip(tickers_list, ticker_names_list)
        )
    else:
        print("Error: Tickers and names lists have different lengths.")
        return

    # Print debug information
    print(f"Number of tickers in S2: {numTickersS2}")
    print(f"Formatted Tickers and Names in S2:\n{formatted_tickers}")

    # Send the list of tickers with names via Telegram
    ms = messaging(chatTarget=4)  # Specify the correct chatTarget
    message = f"Market:{instrument_type} \n\n Number of tickers in S2: {numTickersS2}\n\n{formatted_tickers}"
    print(message)  # Optional debug
    ms.sendURLs(message)




dbT=dbTickersData()
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
run("IT","ETF",0)
checkSignalsAndSendTelegram("ETF",20)

run("IT","ETC",0)
checkSignalsAndSendTelegram("ETC",20)

run("IT","MIB30",0)
checkSignalsAndSendTelegram("MIB30",20)












