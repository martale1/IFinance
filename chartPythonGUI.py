from GenerateScoringAndSignals import GenerateScoringAndSignals
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc


def ensure_volume_sma_obv(df: pd.DataFrame, window: int = 20):
    """
    Funzione di servizio che:
    1) Verifica la lunghezza dei dati.
    2) Calcola la SMA del Volume (rolling 'window' giorni) e l'OBV se non esistono già.
    3) Gestisce il caso in cui i dati siano meno del 'window' specificato.
    """
    data = df.copy()

    # Se ci sono meno di 'window' righe, usiamo una finestra più piccola (la lunghezza del dataframe)
    n_rows = len(data)
    effective_window = min(window, n_rows) if n_rows > 0 else window

    # Se manca la colonna 'Volume_SMA_20', la creiamo
    if 'Volume_SMA_20' not in data.columns:
        data['Volume_SMA_20'] = data['Volume'].rolling(window=effective_window).mean()
        data['Volume_SMA_20'] = data['Volume_SMA_20'].fillna(method='bfill')

    # Se manca la colonna 'OBV', la creiamo
    if 'OBV' not in data.columns:
        data['Returns'] = data['Close'].diff()
        data['Direction'] = 0
        data.loc[data['Returns'] > 0, 'Direction'] = 1
        data.loc[data['Returns'] < 0, 'Direction'] = -1
        data['OBV'] = (data['Volume'] * data['Direction']).cumsum().fillna(0)

    return data


def compute_ta_indicators(df: pd.DataFrame):
    """
    Calcola e aggiunge al DataFrame i principali indicatori tecnici:
      - RSI (14)
      - MACD (12, 26, 9): MACD Line, MACD Signal, MACD Histogram
      - Stochastic (14, 3, 3): Stoch_K, Stoch_D
    """
    data = df.copy()

    # ---------- RSI (periodo 14) -----------
    # Calcolo guadagni/perdite
    period_rsi = 14
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Media mobile esponenziale di guadagni e perdite
    roll_up = gain.ewm(span=period_rsi, adjust=False).mean()
    roll_down = loss.ewm(span=period_rsi, adjust=False).mean()

    # RSI
    rs = roll_up / roll_down
    data['RSI'] = 100.0 - (100.0 / (1.0 + rs))

    # ---------- MACD (12, 26, 9) -----------
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']

    # ---------- Stocastico (14, 3, 3) --------
    low_min = data['Low'].rolling(window=14).min()
    high_max = data['High'].rolling(window=14).max()
    data['Stoch_K'] = 100 * (data['Close'] - low_min) / (high_max - low_min)
    data['Stoch_D'] = data['Stoch_K'].rolling(window=3).mean()

    return data


def create_volume_summary(df: pd.DataFrame):
    """
    Crea un riepilogo testuale (summary) sui volumi e sull'OBV del DataFrame passato.
    Il DataFrame deve contenere almeno le colonne:
       - ['Open', 'High', 'Low', 'Close', 'Volume']
       - 'Volume_SMA_20' (media mobile 20 giorni del Volume)
       - 'OBV'           (On Balance Volume)
    """

    data = df.copy()

    # Assicuriamoci che non ci siano righe con dati mancanti nelle colonne chiave (prezzi e volume)
    data.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'], inplace=True)
    if len(data) == 0:
        print("Nessun dato valido per creare il summary.")
        return

    # -----------------------
    # 1. Panoramica Generale
    # -----------------------
    volume_medio = data['Volume'].mean()
    volume_min = data['Volume'].min()
    volume_max = data['Volume'].max()

    # Trend semplificato: confronto della media delle ultime 5 sedute con le prime 5
    if len(data) >= 10:
        ultima_settimana_data = data.iloc[-5:]
        prima_settimana_data = data.iloc[:5]
        trend_settimana_recente = ultima_settimana_data['Volume'].mean()
        trend_settimana_iniziale = prima_settimana_data['Volume'].mean()

        if trend_settimana_recente > trend_settimana_iniziale:
            trend_volume = "in crescita"
        elif trend_settimana_recente < trend_settimana_iniziale:
            trend_volume = "in calo"
        else:
            trend_volume = "stabile"
    else:
        trend_volume = "non determinabile (pochi dati)"

    # -----------------------
    # 2. Indicatori Chiave
    # -----------------------
    volume_ultimo_giorno = data['Volume'].iloc[-1]

    # Colonna 'Volume_SMA_20'
    if 'Volume_SMA_20' in data.columns:
        volume_ma_20_ultimo_val = data['Volume_SMA_20'].iloc[-1]
        if pd.notna(volume_ma_20_ultimo_val):
            volume_ma_20_str = f"{volume_ma_20_ultimo_val:,.0f}"
        else:
            volume_ma_20_str = "N/A"
    else:
        volume_ma_20_str = "N/A"
        volume_ma_20_ultimo_val = None

    # Calcolo del Relative Volume (se possibile)
    if volume_ma_20_ultimo_val and pd.notna(volume_ma_20_ultimo_val) and volume_ma_20_ultimo_val != 0:
        relative_volume = volume_ultimo_giorno / volume_ma_20_ultimo_val
    else:
        relative_volume = None

    # OBV
    if 'OBV' in data.columns:
        obv_ultimo_val = data['OBV'].iloc[-1]
        obv_media = data['OBV'].mean()
        if pd.notna(obv_ultimo_val) and pd.notna(obv_media):
            if obv_ultimo_val > obv_media:
                obv_commento = "Possibile accumulazione (OBV sopra la media)"
            elif obv_ultimo_val < obv_media:
                obv_commento = "Possibile distribuzione (OBV sotto la media)"
            else:
                obv_commento = "OBV in linea con la media (nessuna indicazione netta)"
        else:
            obv_commento = "OBV non disponibile (NaN)"
    else:
        obv_commento = "OBV non disponibile (colonna mancante)"

    # -----------------------
    # 3. Eventi Straordinari
    # -----------------------
    threshold_picco = volume_medio + 2 * data['Volume'].std()
    picchi = data[data['Volume'] > threshold_picco]

    # -----------------------
    # 4. Conclusioni Operative
    # -----------------------
    conclusioni = (
        " - Se il trend è in crescita con volumi elevati, potrebbe essere confermato un trend rialzista.\n"
        " - Se notiamo divergenze (es. OBV in calo e prezzo in crescita), potrebbero esserci segnali di debolezza.\n"
        " - Livelli di supporto/resistenza si identificano spesso dove il Volume è stato elevato.\n"
    )

    # -----------------------
    # GENERIAMO IL TESTO DEL SUMMARY
    # -----------------------
    if relative_volume is not None:
        relative_vol_str = f"{relative_volume:.2f}"
    else:
        relative_vol_str = "N/A"

    summary = f"""
--- SUMMARY SUI VOLUMI E OBV ---

1) Panoramica Generale
   - Volume medio: {volume_medio:,.0f}
   - Volume minimo: {volume_min:,.0f}
   - Volume massimo: {volume_max:,.0f}
   - Trend volume (confronto inizio-fine periodo): {trend_volume}

2) Indicatori Chiave
   - Volume ultimo giorno: {volume_ultimo_giorno:,.0f}
   - Volume MA 20: {volume_ma_20_str}
   - Relative Volume (vol. attuale / vol. MA 20): {relative_vol_str}
   - OBV: {obv_commento}

3) Eventi Straordinari
   - Soglia picco (media + 2*std) = {threshold_picco:,.0f}
   - Giorni con picco di volume:
{picchi[['Volume']] if not picchi.empty else "   Nessun picco rilevante."}

4) Conclusioni Operative (indicazioni di massima)
{conclusioni}
    """

    print(summary)

def plot_all_in_one(df: pd.DataFrame, n: int = 30, plot_type: str = 'line'):
    """
    Disegna un grafico con 6 pannelli sugli ultimi n giorni di dati:
      1) Candlestick/Line Chart del prezzo
      2) Barre di Volume colorate + SMA(20) del Volume
      3) OBV
      4) RSI
      5) MACD (MACD Line, Signal, Hist)
      6) Stocastico (K e D), con linee di riferimento a 20, 50, 80
    """
    data = df.copy()

    # -- Risolviamo il conflitto 'cannot insert Date, already exists' --
    if data.index.name == 'Date':
        data.index.rename('DateIndex', inplace=True)
    if 'Date' in data.columns:
        data.rename(columns={'Date': 'Date_col'}, inplace=True)

    # Convertiamo l'indice in datetime (se necessario), rimuoviamo righe incomplete e ordiniamo
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index, errors='coerce')

    data.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'], inplace=True)
    data.sort_index(inplace=True)

    # 1) Calcoliamo/aggiorniamo Volume SMA e OBV (se non presenti)
    data = ensure_volume_sma_obv(data, window=20)

    # 2) Calcoliamo RSI, MACD, Stocastico (funzione mostrata in precedenza)
    data = compute_ta_indicators(data)

    # Prendiamo solo gli ultimi n giorni per il plot
    data = data.tail(n).copy()
    data_reset = data.reset_index(drop=False)
    data_reset['x_vals'] = range(len(data_reset))

    fig, (ax_price, ax_volume, ax_obv, ax_rsi, ax_macd, ax_stoch) = plt.subplots(
        6, 1,
        figsize=(12, 18),
        sharex=True
    )

    # ----------------------
    # 1) PREZZO (candlestick / line)
    # ----------------------
    if plot_type.lower() == 'candlestick':
        quotes = data_reset[['x_vals', 'Open', 'High', 'Low', 'Close']].values
        candlestick_ohlc(
            ax_price,
            quotes,
            width=0.6,
            colorup='green',
            colordown='red',
            alpha=0.9
        )
        ax_price.set_title(f"Candlestick - Ultimi {n} dati")
    else:
        ax_price.plot(
            data_reset['x_vals'],
            data_reset['Close'],
            color='blue',
            label='Close'
        )
        ax_price.set_title(f"Line Chart - Ultimi {n} dati")

    ax_price.set_ylabel("Prezzo")
    ax_price.grid(True, alpha=0.3)

    # ----------------------
    # 2) VOLUME
    # ----------------------
    colors = [
        'green' if c >= o else 'red'
        for c, o in zip(data_reset['Close'], data_reset['Open'])
    ]
    ax_volume.bar(
        data_reset['x_vals'],
        data_reset['Volume'],
        color=colors,
        width=0.6,
        label='Volume'
    )
    ax_volume.plot(
        data_reset['x_vals'],
        data_reset['Volume_SMA_20'],
        color='orange',
        linewidth=2,
        label='Vol. SMA 20'
    )
    ax_volume.set_ylabel("Volume")
    ax_volume.grid(True, alpha=0.3)
    ax_volume.legend(loc='upper left')

    # ----------------------
    # 3) OBV
    # ----------------------
    ax_obv.plot(
        data_reset['x_vals'],
        data_reset['OBV'],
        color='purple',
        label='OBV'
    )
    ax_obv.set_ylabel("OBV")
    ax_obv.grid(True, alpha=0.3)
    ax_obv.legend(loc='upper left')

    # ----------------------
    # 4) RSI (con linee di riferimento a 20, 50, 80)
    # ----------------------
    ax_rsi.plot(
        data_reset['x_vals'],
        data_reset['RSI'],
        color='darkorange',
        label='RSI (14)'
    )
    # Linee orizzontali di riferimento
    ax_rsi.axhline(30, color='blue', linestyle='--', alpha=0.5, label='RSI 20')
    ax_rsi.axhline(50, color='gray', linestyle='--', alpha=0.5, label='RSI 50')
    ax_rsi.axhline(70, color='blue', linestyle='--', alpha=0.5, label='RSI 80')
    ax_rsi.set_ylabel("RSI")
    ax_rsi.grid(True, alpha=0.3)
    ax_rsi.legend(loc='upper left')

    # ----------------------
    # 5) MACD
    # ----------------------
    ax_macd.plot(
        data_reset['x_vals'],
        data_reset['MACD'],
        label='MACD',
        color='blue'
    )
    ax_macd.plot(
        data_reset['x_vals'],
        data_reset['MACD_Signal'],
        label='Signal',
        color='red'
    )
    ax_macd.bar(
        data_reset['x_vals'],
        data_reset['MACD_Histogram'],
        color='gray',
        label='Hist'
    )
    ax_macd.set_ylabel("MACD")
    ax_macd.grid(True, alpha=0.3)
    ax_macd.legend(loc='upper left')

    # ----------------------
    # 6) STOCASTICO (K, D) con linee di riferimento a 20, 50, 80
    # ----------------------
    ax_stoch.plot(
        data_reset['x_vals'],
        data_reset['Stoch_K'],
        label='%K',
        color='blue'
    )
    ax_stoch.plot(
        data_reset['x_vals'],
        data_reset['Stoch_D'],
        label='%D',
        color='red'
    )
    # Linee orizzontali di riferimento
    ax_stoch.axhline(20, color='blue', linestyle='--', alpha=0.5, label='Stoch 20')
    ax_stoch.axhline(50, color='gray', linestyle='--', alpha=0.5, label='Stoch 50')
    ax_stoch.axhline(80, color='blue', linestyle='--', alpha=0.5, label='Stoch 80')
    ax_stoch.set_ylabel("Stoch")
    ax_stoch.grid(True, alpha=0.3)
    ax_stoch.legend(loc='upper left')

    # ----------------------
    # FORMAT DELL’ASSE X (DATE)
    # ----------------------
    num_points = len(data_reset)
    step = max(1, num_points // 10)
    ax_stoch.set_xticks(data_reset['x_vals'][::step])
    date_labels = [
        d.strftime('%Y-%m-%d') for d in data_reset[data_reset.columns[0]][::step]
    ]
    ax_stoch.set_xticklabels(date_labels, rotation=45)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    ticker = 'LCOC.MI'
    ticker_name = '3clf.MI'

    # Scarichiamo i dati con la classe GenerateScoringAndSignals
    ts = GenerateScoringAndSignals(ticker, ticker_name, ema_period=50, period='2y', candles=0)

    # Stampiamo i dati (solo a scopo di debug)
    print(ts.data.to_string())

    # 1) Visualizziamo TUTTO (Prezzo, Volume, OBV, RSI, MACD, Stocastico) su 6 pannelli
    plot_all_in_one(ts.data, n=100, plot_type='candlestick')

    # 2) Creiamo il summary sui volumi e OBV
    ts_data_fixed = ensure_volume_sma_obv(ts.data, window=20)
    create_volume_summary(ts_data_fixed)
