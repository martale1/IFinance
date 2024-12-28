
import warnings

from GenerateScoringAndSignals import GenerateScoringAndSignals
import matplotlib.pyplot as plt
ticker='3CFL.MI'
ticker_name='3clf.MI'
ts = GenerateScoringAndSignals(ticker, ticker_name, ema_period=50, period='2y', candles=0)
#ts.run()
#print(ts.data.to_string())



# Funzione per calcolare i supporti e resistenze
def calculate_support_resistance(data, window=14):
    data['Support'] = data['Low'].rolling(window=window, center=False).min()
    data['Resistance'] = data['High'].rolling(window=window, center=False).max()
    return data

# Applica la funzione ai dati
data = calculate_support_resistance(ts.data)
print(data.tail(20))


# Filtra i dati per mostrare solo le ultime righe
print(data.tail(20))



##########

# Filtra i dati per mostrare solo le ultime righe
recent_data = data.tail(100)

# Crea il grafico
fig, ax1 = plt.subplots(figsize=(14, 7))

# Grafico dei prezzi di chiusura, supporti e resistenze
ax1.plot(recent_data.index, recent_data['Close'], label='Chiusura', color='blue')
ax1.plot(recent_data.index, recent_data['Support'], label='Supporto', linestyle='--', color='green')
ax1.plot(recent_data.index, recent_data['Resistance'], label='Resistenza', linestyle='--', color='red')
ax1.set_xlabel('Data')
ax1.set_ylabel('Prezzo')
ax1.legend(loc='upper left')
ax1.grid()

# Creazione del secondo asse per i volumi
ax2 = ax1.twinx()
ax2.bar(recent_data.index, recent_data['Volume'], alpha=0.3, color='gray', label='Volume')
ax2.set_ylabel('Volume')

fig.suptitle('Supporti, Resistenze e Volume per il Ticker {}'.format(ticker))
fig.tight_layout()
plt.show()
