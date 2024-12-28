import telepot
import pandas as pd

from filehandling import  fileHandling
class messaging:
    def __init__(self, chatTarget=0):
        if chatTarget==1:
            token = '6648986015:AAGlh0ql3p_IPy0X7ezt1aeHlD_hMymBC8Y' #Best IT_ETC, MIB30
        elif (chatTarget==0):
            token='7174330107:AAFl_0U_6uzYnhIsjcW9uRYS8UnX82-eAC0'   #Best of Watchlist
        elif (chatTarget==2):
            token='7121436038:AAFP4mL96ue27NEXMx2z1qL-vNleUSdWg6g'   #Best of IT_ETF
        elif (chatTarget==3):                                        #US
            token='7005549386:AAELFQjgq8mZzo1qooW0nx9MtNAgv3O8iP0'
        elif (chatTarget==4):                                       #Signals uptrend
            token='6981065640:AAHuWWVOJd9NIk8zfvCDLu7Lg34cRZAGeo8'
        elif(chatTarget==5):
            token='7010267167:AAGHq4lEFSO7THA22WUoOHORX7YuJBqIXJE'#Not used it could be for signals downtrend

        self.token= token

        self.receiver_id = '5872825403'

    #https://api.telegram.org /bot6545897515:AAE6hz2p8vbaypT96kUVKHzotfs0wcjOhc4/getUpdates

    def send(self,testo):
        #Maurizio
        print(self.token)
        bot=telepot.Bot(self.token)
        bot.sendMessage(self.receiver_id,testo)

    def sendURLs(self,testo):
        #Maurizio

        bot=telepot.Bot(self.token)
        bot.sendMessage(self.receiver_id,testo+ "\u200B",parse_mode='HTML')

    def sort_within_group(self,group, sort_column='Volume'):
        return group.sort_values(by=sort_column, ascending=True)

    def ordina(self,d, sort_column='Volume'):
        d_sorted = d.sort_values(by='Scoring', ascending=False)
        grouped = d.groupby(pd.cut(d['Scoring'], bins=range(-5, 5), labels=False))
        sorted_groups = grouped.apply(lambda x: self.sort_within_group(x, sort_column))
        # sorted_groups = grouped.apply(sort_within_group)
        sorted_groups = sorted_groups.iloc[::-1]
        sorted_dataframe = sorted_groups.reset_index(drop=True)
        return sorted_dataframe

    def sendSignals(self,market, volumeThreshold=1500, telegramChannel=4):
        print("Signals for market " + market)
        # Apre il file con i segnali
        fh = fileHandling()
        df = fh.fromXLSXToDF("Best_" + market + ".xlsx")

        #############################################################
        #    Signal reverse uptrend with Alligator #
        #    Signal3: Price crossing the teeth
        #############################################################
        print("**************************************************************************")
        priceCrossingTeeth = df[((df['Signal3'] == 1)) & (df['Volume'] > volumeThreshold)]
        priceCrossingTeeth_sorted = priceCrossingTeeth.sort_values(by='Percent_Change_2', ascending=False)
        # Stampa le voci ordinate
        print("s3 Alligator signals price crossing the teeth:")
        print(priceCrossingTeeth.head(20).to_string())
        # Invia telegram
        self.sendTickerList(market + ": S3 Price crossing the teeth:", priceCrossingTeeth_sorted.head(20), 0,
                       telegramChannel)

        #############################################################
        #    Signal reverse uptren with Alligator #
        #    Signal4:Lips(Green) > Teeth(Red) and Lips(Green) < Jaw (Blu)
        #############################################################
        print("**************************************************************************")
        # | (df['Signal5'] == 1)
        LipsBetweenTeethAndJaw = df[((df['Signal4'] == 1)) & (df['Volume'] > volumeThreshold)]
        LipsBetweenTeethAndJaw_sorted = LipsBetweenTeethAndJaw.sort_values(by='Percent_Change_2', ascending=False)
        # Stampa le voci ordinate
        print("s4 Alligator signals:")
        print(LipsBetweenTeethAndJaw_sorted.head(20).to_string())
        # Invia telegram
        self.sendTickerList(market + ": S4 lips>teeth :", LipsBetweenTeethAndJaw_sorted.head(20), 0, telegramChannel)

        #############################################################
        #    Signal reverse boolinger #
        #    Signal5: Close>Upper Boolinger and previous 3 closes below upper Boolinger
        #############################################################
        print("**************************************************************************")
        priceAboveBoolingerUpper = df[((df['Signal5'] == 1)) & (df['Volume'] > volumeThreshold)]
        priceAboveBoolingerUpper_sorted = (priceAboveBoolingerUpper.sort_values(by='Percent_Change_2', ascending=False))
        # Stampa le voci ordinate
        print("s5 Boolinger signals:")
        print(priceAboveBoolingerUpper_sorted.head(20).to_string())
        # Invia telegram

        self.sendTickerList(market + ": S5 Close above Boolinger:", priceAboveBoolingerUpper_sorted.head(20), 0,
                       telegramChannel)



    def sendTickerList(self,market, df, executionTime, telegramChannel):
        filtered_df = df
        if len(df):
            sorted_df = df
            telegram_message = market + "\nStocks: " + str(len(filtered_df)) + "\n\n"
            telegram_message_simplified = market + " Trending stocks: " + str(len(filtered_df)) + "\n\n"
            for index, entry in sorted_df.iterrows():
                tname = entry['Ticker Name']
                ticker = entry['Ticker']
                volume = entry['Volume']
                pct2 = entry['Percent_Change_2']
                close = entry['Close']
                scoring = entry['Scoring']
                sl = entry['ATR_Trailing_Stop_Loss']
                atr = entry['ATR']
                AI = entry['AI']
                ADX = entry['ADX']
                RSI = entry['RSI']
                MACD = entry['MACD']
                MACDS = entry['MACD_Signal']
                MACD_Histogram = entry['MACD_Histogram']
                K = entry['Stochastic_K']
                D = entry['Stochastic_D']
                cplus = entry['cdlplus']
                cminus = entry['cdlminus']
                ticker = ticker.strip()
                candlespattern = entry['candlespattern']
                signal6=entry['Signal6']
                if (
                        'pippo' in market):  # Here you should put MylList, MIB, ETC, etc to trigger the candlestick pattern in the telegram message
                    # print("################## MIA LISTA ###########")
                    patternName = 'P:'

                else:
                    # print("%%%%%%%%%%%% Non e` la mia lista:"+market)
                    patternName = ''
                    candlespattern = ''
                # Genera il link HTML
                #url = f"<a href='https://it.finance.yahoo.com/quote/{ticker}/'>{ticker}</a>"
                url = f"<a href='http://theoiziruam.ddns.net:8503/?ticker={ticker}&scoring={scoring}&signal6={signal6}'>{ticker}</a>"
                #url=  f"<a http://theoiziruam.ddns.net:8503/?ticker={ticker}</a>"

                # print(url)
                # url = f"<a href='https://it.finance.yahoo.com/quote/{ticker}/'>{ticker}</a>"
                asterisk = ''
                if scoring == 4:
                    asterisk = '$$$$ '
                elif scoring == 3:
                    asterisk = '$$$ '
                elif scoring == 2:
                    asterisk = '$$ '
                elif scoring == 1:
                    asterisk = '$ '
                elif scoring == -4:
                    asterisk = '@@@@ '
                elif scoring == -3:
                    asterisk = '@@@ '
                elif scoring == -2:
                    asterisk = '@@ '
                elif scoring == -1:
                    asterisk = '@ '
                # print(f"Telegram channel {telegramChannel}")
                if (AI == None):
                    if (telegramChannel == 4):
                        entry_message = f"{asterisk}{tname} {url} c+:{cplus} c-:{cminus} Histogram:{MACD_Histogram} S_K:{K} V:{volume} p%:{pct2}%  S_D:{D} C:{close}  score:{scoring} SL:{sl}  MACD:{MACD} MACD_S:{MACDS}  RSI:{RSI}  ADX:{ADX}  {patternName} {candlespattern}\n\n"
                    else:
                        entry_message = f"{asterisk}{tname} {url} c+:{cplus} c-:{cminus} C:{close} V:{volume} p%:{pct2}%  score:{scoring} SL:{sl}  MACD:{MACD} MACD_S:{MACDS} S_K:{K} S_D:{D} RSI:{RSI}  ADX:{ADX} {patternName} {candlespattern} \n\n"
                else:
                    if (telegramChannel == 4):
                        entry_message = f"{asterisk}{tname} {url} c+:{cplus} c-:{cminus} Histogram:{MACD_Histogram} S_K:{K}  p%:{pct2}%  V:{volume} score:{scoring} C:{close}  SL:{sl}  MACD:{MACD} MACD_S:{MACDS}  S_D:{D} RSI:{RSI}  ADX:{ADX} {patternName} {candlespattern} AI:{AI} \n\n"
                    else:
                        entry_message = f"{asterisk}{tname} {url} c+:{cplus} c-:{cminus} Histogram:{MACD_Histogram} S_K:{K} C:{close} V:{volume} p%:{pct2}%  score:{scoring} SL:{sl}  MACD:{MACD} MACD_S:{MACDS}  S_D:{D} RSI:{RSI} ADX:{ADX} {patternName} {candlespattern} AI:{AI}\n\n"

                telegram_message += entry_message
                entry_message_simplified = f"{asterisk} {url}  p%:{pct2}% V:{volume} {tname}\n"
                telegram_message_simplified += entry_message_simplified
        else:
            telegram_message = market + " EMPTY"
            telegram_message_simplified = market + "EMPTY"
        telegram = messaging(chatTarget=telegramChannel)
        # print(telegram_message)
        # if(telegramChannel!=4): telegram_message +='Execution time:'+str(executionTime)+"s" #il canale 4 e` per i segnali, execution time non serve
        # telegram.sendURLs(telegram_message)
        if len(filtered_df):
            telegram.sendURLs(telegram_message_simplified)

    def sendTradingSystemsResultsWithScoring(self,d, executionTime, market, orderBy='Volume', firstXStocks=0,
                                             allScoringClasses=0, telegramChannel=0, telegramSend=0):
        # allScoring= 1=> All classes; 2 => Classes 4,3;  0 => Class  4 only
        # firstXStocks=0 visualizza tutto, altrimenti il valore indicato viene usato
        # telegramChannel: 0 (BestStocks/Watchlist), 1 (BuySignals/IT_ETC, MIB30), 2 (SellSignals/IT_ETF), 3 (US_stocks)
        # telegramSend: telegram message is sent only if this value is equh al to 1

        print("**** Function: sendTradingSystemsResultsWithScoring ***")
        df_ordered = self.ordina(d, sort_column=orderBy)  # Ordina per gruppo e poi per sort_colum all'interno del gruppo
        if allScoringClasses == 1:  # All classess are included
            print("-- Including all classes for telegram regadless the volume --")
            df_filtered = df_ordered  # Invalida precedente ordinamento ed ordina in base a variazioni percentuali
            df_filtered = df_filtered.sort_values(by='Percent_Change_2', ascending=False)
            a = 1
        elif allScoringClasses == 2:  # Class 4 and 3
            print("-- Including classes 4 and 3 with volume > 1000 for telegram--")
            df_filtered = df_ordered[
                ((df_ordered['Scoring'] == 4) | (df_ordered['Scoring'] == 3)) & (df_ordered['Volume'] > 1000)]
            # df_filtered = df_ordered[((df_ordered['Scoring'] == 4)  & (df_ordered['Volume'] > 1000)] #Scoring 4 and V>1000
            if len(df_filtered) == 0:
                df_filtered = df_ordered[
                    (df_ordered['Scoring'] == 3) & (df_ordered['Volume'] > 1000)]  # Scoring 4 and V>1000
        else:  # Only4
            print("-- Including classe 4 with  volume > 1000 for telegram  --")

            df_filtered = df_ordered[
                (df_ordered['Scoring'] == 4) & (df_ordered['Volume'] > 1000)]  # Scoring 4 and V>1000
            if len(df_filtered) == 0:
                df_filtered = df_ordered[
                    (df_ordered['Scoring'] == 3) & (df_ordered['Volume'] > 1000)]  # Scoring 4 and V>1000

        if firstXStocks:
            df_filtered = df_filtered.head(firstXStocks)
        print("Ordered scoring for " + market)
        print(df_ordered.to_string())
        if telegramSend:
            print("Items included in telegram message as Trading system result:")
            print(df_filtered.to_string())
            self.sendTickerList(market + ' ordered by ' + orderBy + '\n', df_filtered, executionTime,
                           telegramChannel)  # Invia messaggio telegram



    def sendSignalsAlligators(self,market, volumeThreshold=1000, telegramChannel=4):
        print("Signals for market " + market)

        # Apre il file con i segnali
        fh = fileHandling()
        df = fh.fromXLSXToDF("Best_" + market + ".xlsx")

        # Stampa il DataFrame per debug
        print(df.to_string())

        # Filtra il DataFrame per volume maggiore di 1000
        if 'Volume' in df.columns:
            df_filtered = df[df['Volume'] > volumeThreshold]
        else:
            print("La colonna 'Volume' non esiste nel DataFrame.")
            return

        filtered_df_uptrend = df_filtered[df_filtered['Signal6'] == 'Uptrend']
        sorted_df = filtered_df_uptrend.sort_values(by='Scoring', ascending=False)
        print(sorted_df.to_string())

        # Verifica se la colonna 'Signal6' esiste nel DataFrame filtrato
        if 'Signal6' in df_filtered.columns:
            # Conta le occorrenze di ciascun valore unico nella colonna 'Signal6'
            counts = df_filtered['Signal6'].value_counts()


            # Calcola il totale delle righe nel DataFrame filtrato
            total = len(df_filtered)

            # Calcola le percentuali per ogni valore unico
            percentages = round(((counts / total) * 100),2)

            # Crea un DataFrame con i risultati
            result_df = pd.DataFrame({
                'Count': counts,
                'Percentage': percentages
            })

            myDict=counts.to_dict()
            print(f"Numero entry in Uptrend: {myDict['Uptrend']}")


            # Riordina il DataFrame per i conteggi in ordine decrescente (opzionale)
            result_df = result_df.sort_values(by='Count', ascending=False)

            # Stampa il DataFrame dei risultati

            #sending summary to telegram
            # Prepare the 'testo' field to send
            testo = "Summary for market: {}\n\n".format(market)
            testo += "Signal6 Summary (Volume > {}):\n".format(volumeThreshold)
            testo += result_df.to_string(index=True, header=True)


            # If the DataFrame is large, you might want to add pagination or a brief summary instead
            if len(testo) > 4000:  # Telegram message limit is 4096 characters
                testo = testo[:4000] + "\n[Message truncated]"

            # Send the results via Telegram
            self.send(testo)
            #self.send(sorted_df.to_string())
        else:
            print("La colonna 'Signal6' non esiste nel DataFrame filtrato.")



#t=messaging()
#t.sendSignalsAlligators('MyList', volumeThreshold=1000, telegramChannel=4)

#m=messaging(chatTarget=1)
#m.send("PRova")