import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# =============================================================================
# DATASET COMPLETO 87 STUDI QUANT-REA (USA / WORLD)
# =============================================================================
STUDIES_DB = [
    # USA -> Statistiche Macro
    {"id": "MACRO_01", "macro": "Usa", "subcat": "Statistiche Macro", "name": "NON FARM PAYROLLS", "desc": "Quante volte si è presentato che i NON FARM PAY ROLLS siano stati revisionati e come si è comportato il mercato.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "MACRO_02", "macro": "Usa", "subcat": "Statistiche Macro", "name": "Tassi - Inflazione - Disoccupazione", "desc": "Come si comporta l'S&P 500 con Disoccupazione - Inflazione - tassi alti o bassi?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "MACRO_03", "macro": "Usa", "subcat": "Statistiche Macro", "name": "Tassi", "desc": "Come si comporta il mercato con Tassi Alti o meno?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐☆", "premium": True},
    {"id": "MACRO_04", "macro": "Usa", "subcat": "Statistiche Macro", "name": "Inflazione", "desc": "S&P con INFLAZIONE alta che return/drawdown ha?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "MACRO_05", "macro": "Usa", "subcat": "Statistiche Macro", "name": "Disoccupazione", "desc": "Come si comporta S&P500 con disoccupazione che sale o che scende?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "MACRO_06", "macro": "Usa", "subcat": "Statistiche Macro", "name": "GDP", "desc": "Come si comporta S&P500 sopra o sotto la media a 6 periodi della variazione del PIL USA?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "MACRO_07", "macro": "Usa", "subcat": "Statistiche Macro", "name": "Recessione- Ritorni S&P", "desc": "E' vero che in RECESSIONE o PARZIALE RECESSIONE S&P va male? E' vero che in fasi di no recessione sale sempre?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "MACRO_08", "macro": "Usa", "subcat": "Statistiche Macro", "name": "CAPE - PE - UTILI in rapporto al S&P 500", "desc": "Mette insieme tre indicatori di valutazione dell'S&P 500 e li confronta con i rendimenti annui dell'indice.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐☆", "premium": True},
    {"id": "MACRO_09", "macro": "Usa", "subcat": "Statistiche Macro", "name": "Eventi Geopolitici - Analisi Impatto", "desc": "Cosa succede su vari asset quando si presentano shock ed eventi geopolitici?", "tags": ["Multi-Asset", "Descrittiva"], "stars": "⭐⭐⭐⭐☆", "premium": False},

    # WORLD -> Ottimizzatore di Portafoglio
    {"id": "PORT_01", "macro": "World", "subcat": "Ottimizzatore di Portafoglio", "name": "Ottimizzatore di Portafoglio", "desc": "Una dashboard interattiva per costruire e valutare portafogli multi-asset.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "PORT_02", "macro": "World", "subcat": "Ottimizzatore di Portafoglio", "name": "Comparazione Asset", "desc": "Una dashboard interattiva per confrontare asset finanziari su lunghe serie storiche.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "PORT_03", "macro": "World", "subcat": "Ottimizzatore di Portafoglio", "name": "Quanto mi costa investire", "desc": "Facciamo una simulazione di tot anni per vedere quanto mi costa investire in base ai costi.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐☆☆", "premium": False},
    {"id": "PORT_04", "macro": "World", "subcat": "Ottimizzatore di Portafoglio", "name": "Ritorni Futuri", "desc": "Strumento interattivo per studiare cosa succede dopo un drawdown su singoli titoli o portafogli.", "tags": ["Aziende", "Backtest", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "PORT_05", "macro": "World", "subcat": "Ottimizzatore di Portafoglio", "name": "MSCI ANALYSIS", "desc": "Analizzare tutti gli archivi delle equity di tutto il mondo del MSCI.", "tags": ["World", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "PORT_06", "macro": "World", "subcat": "Ottimizzatore di Portafoglio", "name": "Comparatore - Portafogli", "desc": "Una volta creati dei portafogli si possono esportare le equity line e confrontarle.", "tags": ["Portafogli", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "PORT_07", "macro": "World", "subcat": "Ottimizzatore di Portafoglio", "name": "Ribilanciamento si o no?", "desc": "Come usare e interpretare il ribilanciamento periodico su portafoglio multi-asset.", "tags": ["Aziende", "Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "PORT_08", "macro": "World", "subcat": "Ottimizzatore di Portafoglio", "name": "Calcolatore Capitale", "desc": "Calcolatore Capitale ti permette di capire come cresce un capitale nel tempo.", "tags": ["Descrittiva", "Backtest"], "stars": "⭐⭐⭐☆☆", "premium": False},
    {"id": "PORT_09", "macro": "World", "subcat": "Ottimizzatore di Portafoglio", "name": "Test D'Ipotesi", "desc": "Testa in modo semplice se aggiungere un asset a un portafoglio migliora le performance.", "tags": ["Aziende", "Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},

    # WORLD -> Bear Market - Drawdown
    {"id": "DD_01", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "Studio dei DRAWDOWN", "desc": "Analisi delle Correzioni: confronta l'andamento dell'asset scelto durante tutte le correzioni storiche.", "tags": ["Descrittiva", "Aziende"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "DD_02", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "Drawdown Ritorno", "desc": "Analizza un asset e per ogni anno calcola: Max drawdown intraday e peggior calo dell'anno.", "tags": ["Descrittiva", "Aziende"], "stars": "⭐⭐⭐⭐☆", "premium": True},
    {"id": "DD_03", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "Ergocità dei Mercati", "desc": "Questo studio misura quando il comportamento dei rendimenti a breve periodo è in linea con la media.", "tags": ["Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐☆", "premium": True},
    {"id": "DD_04", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "Giorni in BEAR MARKET", "desc": "Se il drawdown scende oltre una soglia scelta (es. -20%), quel giorno è marcato come bear.", "tags": ["Descrittiva", "Aziende"], "stars": "⭐⭐⭐⭐☆", "premium": True},
    {"id": "DD_05", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "Bear Market & Secondo Drawdown", "desc": "Intercetta i cali >= -20% dal massimo e cerca l'ampiezza del secondo ribasso.", "tags": ["Descrittiva", "Aziende"], "stars": "⭐⭐⭐⭐☆", "premium": True},
    {"id": "DD_06", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "Gap negativo & nuovo minimo (weekly)", "desc": "Intercetta le settimane in cui l'asset apre con un gap negativo e tocca un nuovo minimo.", "tags": ["Descrittiva", "Aziende"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "DD_07", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "Bull & Bear Market Dashboard", "desc": "Seleziona il ticker, imposta la soglia (default 20% indici, 30-40% per singoli) e calcola.", "tags": ["Aziende", "Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "DD_08", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "Numero di DRAWDOWN nell'anno e ritorni", "desc": "Misura quante volte, in ciascun anno, l'asset ha subito un drawdown pari o superiore a X%.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐☆", "premium": True},
    {"id": "DD_09", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "In che mese un ASSET fa il suo massimo dell'anno e poi ritraccia?", "desc": "Equity con massimi annuali: andamento del prezzo e mese in cui si forma il picco.", "tags": ["Aziende", "Descrittiva", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "DD_10", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "Drop Giornaliero Cumulato", "desc": "Monitora i giorni di forte calo sui titoli di un indice e li confronta con l'indice.", "tags": ["Descrittiva", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "DD_11", "macro": "World", "subcat": "Bear Market - Drawdown", "name": "DASHBOARD drawdown e recovey", "desc": "Esplora 4 mercati: S&P 500, NASDAQ 100, NASDAQ completo e NYSE con tempi di recupero.", "tags": ["Aziende", "Descrittiva", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},

    # WORLD -> Rendimenti
    {"id": "RET_01", "macro": "World", "subcat": "Rendimenti", "name": "Escludi X giorni Peggiori/Migliori", "desc": "Se togliessimo gli X giorni peggiori/migliori un asset resta bullish? E dopo quanti giorni si riprende?", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_02", "macro": "World", "subcat": "Rendimenti", "name": "Correlazione e Stagionalità", "desc": "Rendimenti e correlazioni di PEARSON - SPEARMAN - KENDALL.", "tags": ["Descrittiva", "Backtest", "Aziende"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_03", "macro": "World", "subcat": "Rendimenti", "name": "Rendimenti - ZSCORE", "desc": "Mostra per l'asset selezionato i rendimenti annuali storici e la loro posizione statistica Z-Score.", "tags": ["Descrittiva", "Aziende"], "stars": "⭐⭐⭐☆☆", "premium": False},
    {"id": "RET_04", "macro": "World", "subcat": "Rendimenti", "name": "Ritorni Mensili e Annui", "desc": "Ritorni mensili e annualizzati.", "tags": ["Descrittiva", "Aziende"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_05", "macro": "World", "subcat": "Rendimenti", "name": "Nuovi massimi dell'anno e Ritorni a fine anno", "desc": "Analizza un asset e misura quanto spesso segna nuovi massimi e come chiude l'anno.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_06", "macro": "World", "subcat": "Rendimenti", "name": "Numero di Aziende del NASDAQ 100 che salgono", "desc": "Mostra quanta parte del NASDAQ-100 chiude in rialzo e come usare questa informazione.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_07", "macro": "World", "subcat": "Rendimenti", "name": "Numero di Aziende del S&P 500 che salgono", "desc": "Vista breadth dell'S&P 500: percentuale di componenti in rialzo (advancing %).", "tags": ["Descrittiva", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_08", "macro": "World", "subcat": "Rendimenti", "name": "Giorni consecutivi Positivi / Negativi", "desc": "Questa pagina analizza il respiro del mercato: quante sedute passano senza due rialzi consecutivi.", "tags": ["Backtest", "Aziende"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_09", "macro": "World", "subcat": "Rendimenti", "name": "Numero di Aziende del S&P 500 che sovraperformano", "desc": "Raccoglie quante azioni battono la performance dell'S&P 500.", "tags": ["Descrittiva", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_10", "macro": "World", "subcat": "Rendimenti", "name": "Numero di Aziende del NASDAQ che sovraperformano", "desc": "Quante azioni battono la performance dell'indice NASDAQ.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_11", "macro": "World", "subcat": "Rendimenti", "name": "Rendimenti a Intervallo fisso", "desc": "Come si comporta un asset in determinati periodi dell'anno? Tutte le metriche statistiche.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_12", "macro": "World", "subcat": "Rendimenti", "name": "Ritorni di un asset da ogni bottom", "desc": "Mostra i ritorni da ogni bottom (di almeno un -20% di drawdown) su vari archi temporali.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_13", "macro": "World", "subcat": "Rendimenti", "name": "Rendimenti sopra sotto la 200 sma", "desc": "Come si comporta un asset quando si distanzia molto dalla sua media a 200 periodi.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_14", "macro": "World", "subcat": "Rendimenti", "name": "Cap-Weighted vs Equal-Weight", "desc": "Chi guida davvero il mercato? Mostra le performance ponderate a capitalizzazione vs peso equo.", "tags": ["Descrittiva", "S&P500"], "stars": "⭐⭐⭐⭐☆", "premium": True},
    {"id": "RET_15", "macro": "World", "subcat": "Rendimenti", "name": "Rendimenti PAC/PIC matrice comulata", "desc": "Mappa a colori dove ogni cella mostra il rendimento annuo medio (%) investendo con PAC vs PIC.", "tags": ["Aziende", "Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_16", "macro": "World", "subcat": "Rendimenti", "name": "Dashboard sulle quotazioni in borsa (IPO)", "desc": "1980/2025: Esplora 45 anni di dati reali su oltre 9.000 aziende quotate al debutto.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_17", "macro": "World", "subcat": "Rendimenti", "name": "Forza relativa di tutti gli indici", "desc": "Panoramica completa dei principali indici mondiali: forza relativa e caratteristiche.", "tags": ["Descrittiva", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_18", "macro": "World", "subcat": "Rendimenti", "name": "Inizio peggiore ritorni a fine anno", "desc": "Come si comporta un asset nei primi giorni dell'anno e come determinano il ritorno di fine anno.", "tags": ["Aziende", "Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_19", "macro": "World", "subcat": "Rendimenti", "name": "Shuffle a Blocchi", "desc": "Triangolo (mappa termica IRR) Y = anno di partenza, X = anno di fine. Cella = rendimento composto.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_20", "macro": "World", "subcat": "Rendimenti", "name": "Contributo ricchezza di una Asset class", "desc": "Analisi dell'impatto cumulato di ogni singola asset class al portafoglio complessivo.", "tags": ["Descrittiva", "Strategia"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_21", "macro": "World", "subcat": "Rendimenti", "name": "Escursione High-Low dall'inizio anno", "desc": "Quanto si muove un asset nei primi mesi dell'anno e previsioni statistiche sull'escursione.", "tags": ["Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "RET_22", "macro": "World", "subcat": "Rendimenti", "name": "Rendimenti Cumulati per archi temporali", "desc": "Comprare ai massimi storici penalizza i rendimenti? Risponde per ogni orizzonte.", "tags": ["Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},

    # WORLD -> Strategie
    {"id": "STRAT_01", "macro": "World", "subcat": "Strategie", "name": "Strategia Sell in May", "desc": "Mostra come un asset si comporta con la narrativa SELL IN MAY AND GO AWAY.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐☆☆", "premium": True},
    {"id": "STRAT_02", "macro": "World", "subcat": "Strategie", "name": "Strategia QQQ Overnigth", "desc": "Dove performa meglio il mercato: overnight o intraday? Rendimento cumulato Tre linee.", "tags": ["Strategia"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "STRAT_03", "macro": "World", "subcat": "Strategie", "name": "Strategia soglia DrawDown", "desc": "Strategia d'investimento a capitale iniziale su soglie prefissate di drawdown.", "tags": ["Aziende", "Strategia", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "STRAT_04", "macro": "World", "subcat": "Strategie", "name": "Strategia - Buy the dip", "desc": "Ogni volta che l'S&P 500 chiude in rosso, si entra sul mercato il giorno successivo.", "tags": ["Aziende", "Strategia", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "STRAT_05", "macro": "World", "subcat": "Strategie", "name": "Strategia Top 10 - Top 20 - S&P500", "desc": "Come hanno performato le top 10 e 20 versus l'S&P 500.", "tags": ["Strategia", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "STRAT_06", "macro": "World", "subcat": "Strategie", "name": "Equity & BOND - CAPE", "desc": "Dashboard di analisi che confronta un indice azionario con un Treasury USA 10Y.", "tags": ["Strategia"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "STRAT_07", "macro": "World", "subcat": "Strategie", "name": "Gap per ogni giorno", "desc": "La strategia osserva come il mercato 'salta' all'apertura rispetto alla chiusura del giorno prima.", "tags": ["Strategia", "Aziende"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "STRAT_08", "macro": "World", "subcat": "Strategie", "name": "Christmas Effect", "desc": "Una strategia di stagionalità che prova a sfruttare il 'rally di fine anno'.", "tags": ["Strategia", "S&P500", "Aziende"], "stars": "⭐⭐⭐☆☆", "premium": False},
    {"id": "STRAT_09", "macro": "World", "subcat": "Strategie", "name": "Simulazione Montecarlo EQUITY", "desc": "Quale il migliore Risk/Reward da adottare e il rischio massimo per un'operatività profittevole.", "tags": ["No tags"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "STRAT_10", "macro": "World", "subcat": "Strategie", "name": "Processo di Poisson", "desc": "La Poisson è un modo semplice per descrivere quante volte succede un evento in un periodo.", "tags": ["Aziende", "Strategia", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "STRAT_11", "macro": "World", "subcat": "Strategie", "name": "Entropia dei Mercati", "desc": "L'entropia misura quanto il mercato è prevedibile o caotico in un dato periodo.", "tags": ["Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "STRAT_12", "macro": "World", "subcat": "Strategie", "name": "Strategia - Sell the rip", "desc": "Ogni volta che l'asset chiude in forte verde, si va short sul mercato il giorno successivo.", "tags": ["Strategia", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},

    # WORLD -> 200 LEVEL / Settori
    {"id": "LEV_01", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL S&P", "desc": "Come si comporta il S&P 500 quando poche aziende restano sopra la 200 periodi giornaliera?", "tags": ["Descrittiva", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_02", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL NASDAQ", "desc": "Come si comporta il NASDAQ quando poche aziende restano sopra la media a 200 periodi?", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_03", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL DOW JONES", "desc": "Come si comporta il DOW JONES quando poche aziende restano sopra la media 200.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_04", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL Russell 2000", "desc": "Come si comporta il RUSSELL 2000 quando poche aziende rimangono sopra la media 200 periodi.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_05", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL DAX", "desc": "Come si comporta il DAX quando poche aziende che lo compongono rimangono sopra la media 200.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_06", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL SETTORI", "desc": "Come si comportano i SETTORI del S&P 500 quando poche aziende rimangono sopra la media 200.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_07", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "S&P Sectors – Compressione & Momentum", "desc": "Analisi settoriale su performance - Momentum e Compressioni Correlazioni e analisi avanzate.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_08", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL MIB", "desc": "Come si comporta il MIB quando poche aziende rimangono sopra la media 200.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_09", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL CAC", "desc": "Come si comporta il CAC 40 quando poche aziende rimangono sopra la media 200.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_10", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL IBEX", "desc": "Come si comporta il IBEX 35 quando poche aziende rimangono sopra la media 200.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_11", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL SMI Svizzero", "desc": "Come si comporta lo SMI Svizzero quando poche aziende rimangono sopra la media 200.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_12", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL NIKKEI 225", "desc": "Come si comporta il NIKKEI 225 quando poche aziende rimangono sopra la media 200.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_13", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL HANG SENG", "desc": "Come si comporta il HANG SENG quando poche aziende rimangono sopra la media 200.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "LEV_14", "macro": "World", "subcat": "200 LEVEL / Settori", "name": "200 LEVEL EMERGING MARKET", "desc": "Come si comporta l'EMERGING MARKET quando poche aziende restano sopra la 200.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},

    # WORLD -> Volatilità
    {"id": "VOL_01", "macro": "World", "subcat": "Volatilità", "name": "VIX", "desc": "Cosa succede ad S&P 500 quando il VIX è sopra il livello 30 su vari archi temporali.", "tags": ["S&P500"], "stars": "⭐⭐⭐⭐☆", "premium": False},
    {"id": "VOL_02", "macro": "World", "subcat": "Volatilità", "name": "Volatility", "desc": "Questa pagina ti mostra come si muove e quanto 'trema' un mercato su diversi orizzonti.", "tags": ["Descrittiva", "Aziende"], "stars": "⭐⭐⭐☆☆", "premium": False},
    {"id": "VOL_03", "macro": "World", "subcat": "Volatilità", "name": "La volatilità GARCH", "desc": "Questa pagina serve per confrontare tre misure di volatilità nel tempo e stime GARCH.", "tags": ["Aziende", "Descrittiva", "Strategia"], "stars": "⭐⭐⭐⭐⭐", "premium": True},

    # WORLD -> Scanner
    {"id": "SCAN_01", "macro": "World", "subcat": "Scanner", "name": "Aziende USA senza 100/50 best DAY", "desc": "Quante aziende dell'S&P 500, NASDAQ 100 e NYSE senza i migliori giorni restano positive.", "tags": ["Aziende", "Descrittiva", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "SCAN_02", "macro": "World", "subcat": "Scanner", "name": "I 100 migliori/peggiori giorni DAY AFTER", "desc": "Due blocchi separati: S&P 500 e NASDAQ. Cosa succede il giorno successivo.", "tags": ["Backtest", "S&P500", "Aziende"], "stars": "⭐⭐⭐⭐☆", "premium": True},
    {"id": "SCAN_03", "macro": "World", "subcat": "Scanner", "name": "Regressione ritorno mensile con ritorno annuo", "desc": "Classifica dei titoli NYSE con la relazione statistica più forte tra mese e anno.", "tags": ["Descrittiva", "S&P500", "Aziende", "Strategia", "Backtest"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "SCAN_04", "macro": "World", "subcat": "Scanner", "name": "Numero di indici USA-EUROPA che salgono/scendono", "desc": "Quanti indici salgono o scendono nello stesso periodo: breadth aggregata.", "tags": ["Descrittiva", "S&P500"], "stars": "⭐⭐⭐⭐☆", "premium": True},
    {"id": "SCAN_05", "macro": "World", "subcat": "Scanner", "name": "Numero di Indici che fanno nuovi massimi", "desc": "La pagina conta quanti indici fanno un nuovo massimo rispetto all'ultimo anno.", "tags": ["Descrittiva"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "SCAN_06", "macro": "World", "subcat": "Scanner", "name": "POC SCANNER", "desc": "Strumento per selezionare un universo di titoli e intercettare la compressione sul POC.", "tags": ["No tags"], "stars": "⭐⭐⭐⭐⭐", "premium": True},
    {"id": "SCAN_07", "macro": "World", "subcat": "Scanner", "name": "Correlazione ritorno mensile con ritorno annuo (Mese+Anno)", "desc": "Analisi divisa in due blocchi: Mese positivo & Anno positivo, mostra i titoli correlati.", "tags": ["Aziende", "Descrittiva", "Strategia", "S&P500"], "stars": "⭐⭐⭐⭐⭐", "premium": True}
]

STUDY_MAP = {s["id"]: s for s in STUDIES_DB}

QR_CSS = """
<style>
.filter-title {
    font-size: 13px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.banner-premium {
    background-color: #064e3b;
    border: 1px solid #059669;
    border-radius: 8px;
    padding: 12px 18px;
    color: #ecfdf5;
    font-size: 13px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.qr-card {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 16px;
    height: 225px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    margin-bottom: 12px;
}
.qr-card:hover {
    border-color: #38bdf8;
}
.qr-title-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 6px;
}
.qr-title {
    font-size: 14px;
    font-weight: 700;
    color: #f8fafc;
    line-height: 1.3;
}
.qr-badge-prem {
    background-color: #d97706;
    color: #000000;
    font-size: 10px;
    font-weight: 800;
    padding: 1px 6px;
    border-radius: 4px;
    white-space: nowrap;
}
.qr-stars {
    color: #f59e0b;
    font-size: 11px;
    margin: 4px 0;
}
.qr-desc {
    color: #94a3b8;
    font-size: 12px;
    line-height: 1.35;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}
.qr-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    justify-content: flex-end;
}
.qr-tag {
    background-color: #1e293b;
    color: #93c5fd;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
}
</style>
"""

def render_generic_study_view(meta):
    st.markdown(f"### 🔬 {meta['name']}")
    st.caption(f"Categoria: **{meta['macro']} / {meta['subcat']}** | Tags: *{', '.join(meta['tags'])}*")
    st.markdown(f"**Descrizione Metodologia:** {meta['desc']}")
    st.markdown("---")

    c1, c2 = st.columns([1, 2])
    with c1:
        t_in = st.text_input("Inserisci Ticker Sottostante (es. PYPL, TSLA, SPY, QQQ):", value="PYPL").upper().strip()
        btn = st.button("🚀 ESEGUI ANALISI EOD", use_container_width=True)

    with c2:
        if btn or t_in:
            with st.spinner(f"Calcolo metriche per ${t_in}..."):
                try:
                    df = yf.download(t_in, period="2y", interval="1d", progress=False)
                    if df.empty or len(df) < 30:
                        st.error(f"Dati non trovati per il simbolo {t_in}.")
                        return
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                    lc = float(df['Close'].iloc[-1])
                    ath = float(df['High'].max())
                    dd = ((lc - ath) / ath) * 100.0
                    
                    price_bins = np.linspace(df['Low'].min(), df['High'].max(), 50)
                    bin_idx = np.digitize(df['Close'].values, price_bins)
                    vol_hist = np.zeros(len(price_bins))
                    for idx, v in zip(bin_idx, df['Volume'].values):
                        if idx < len(vol_hist): vol_hist[idx] += v
                    poc = float(price_bins[np.argmax(vol_hist)])
                    dist_poc = ((lc - poc) / poc) * 100.0

                    ret = df['Close'].pct_change()
                    z = float((ret.iloc[-1] - ret.mean()) / (ret.std() + 1e-9))
                    sma50 = float(df['Close'].rolling(50).mean().iloc[-1])

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Prezzo Ultimo", f"${lc:.2f}")
                    m2.metric("Drawdown ATH", f"{dd:.1f}%")
                    m3.metric("POC Base", f"${poc:.2f}", f"{dist_poc:+.2f}%")
                    m4.metric("Z-Score 52w", f"{z:.2f}")

                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=t_in))
                    fig.add_hline(y=poc, line_dash="dash", line_color="#00D1FF", annotation_text=f"POC (${poc:.2f})")
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(50).mean(), name="SMA 50", line=dict(color="#f59e0b", width=1.5)))
                    fig.update_layout(height=420, template="plotly_dark", xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Errore: {str(e)}")

# =============================================================================
# RENDER PRINCIPALE PAGINA 3
# =============================================================================
def render_page3():
    st.markdown(QR_CSS, unsafe_allow_html=True)

    if "active_study_id" not in st.session_state:
        st.session_state.active_study_id = None

    # -------------------------------------------------------------------------
    # VISTA STUDIO SINGOLO A TUTTO SCHERMO
    # -------------------------------------------------------------------------
    if st.session_state.active_study_id is not None:
        sid = st.session_state.active_study_id
        meta = STUDY_MAP.get(sid, {"name": sid, "macro": "Usa", "subcat": "Generale", "desc": "", "tags": []})

        col_b, _ = st.columns([2, 5])
        if col_b.button("⬅️ Torna all'Archivio", use_container_width=True):
            st.session_state.active_study_id = None
            st.rerun()

        st.markdown("---")

        # 1. STUDIO NFP (Studio 01)
        if sid == "MACRO_01":
            try:
                from studies.macro_nfp import render_nfp_study_view
                render_nfp_study_view()
            except ModuleNotFoundError:
                st.error("File `studies/macro_nfp.py` non trovato su GitHub.")
            except Exception as e:
                st.error(f"Errore esecuzione NFP: {str(e)}")

        # 2. STUDIO TASSI - INFLAZIONE - DISOCCUPAZIONE (Studio 02)
        elif sid == "MACRO_02":
            try:
                from studies.macro_tassi_inflazione import render_tassi_inflazione_view
                render_tassi_inflazione_view()
            except ModuleNotFoundError:
                st.error("File `studies/macro_tassi_inflazione.py` non trovato su GitHub.")
            except Exception as e:
                st.error(f"Errore esecuzione Tassi-Inflazione: {str(e)}")

        # 3. ROUTING GENERICO PER ALTRI STUDI IN ATTESA DI SVILUPPO
        else:
            render_generic_study_view(meta)
        return

    # -------------------------------------------------------------------------
    # VISTA GALLERIA ARCHIVIO (PANNELLO FILTRI + GRID)
    # -------------------------------------------------------------------------
    col_filters, col_main = st.columns([1, 3.2])

    with col_filters:
        st.markdown("#### 🔍 Cerca analisi...")
        search_kw = st.text_input("Cerca", placeholder="Cerca analisi...", label_visibility="collapsed").strip().lower()

        st.markdown("---")
        st.markdown("<div class='filter-title'>📁 Categories</div>", unsafe_allow_html=True)
        cat_usa = st.checkbox("Usa", value=True)
        cat_world = st.checkbox("World", value=True)

        st.markdown("---")
        st.markdown("<div class='filter-title'>📑 Subcategories</div>", unsafe_allow_html=True)
        all_subcats = [
            "200 LEVEL / Settori", "Bear Market - Drawdown", "Ottimizzatore di Portafoglio",
            "Rendimenti", "Scanner", "Statistiche Macro", "Strategie", "Volatilità"
        ]
        subcat_selection = []
        for sc in all_subcats:
            if st.checkbox(sc, value=True, key=f"sc_{sc}"):
                subcat_selection.append(sc)

        st.markdown("---")
        st.markdown("<div class='filter-title'>🏷️ Tags</div>", unsafe_allow_html=True)
        all_tags = ["Aziende", "Backtest", "Descrittiva", "S&P500", "Strategia"]
        tag_selection = []
        for tg in all_tags:
            if st.checkbox(tg, value=True, key=f"tg_{tg}"):
                tag_selection.append(tg)

        st.markdown("---")
        st.markdown("<div class='filter-title'>⭐ Content Type</div>", unsafe_allow_html=True)
        content_type = st.radio(
            "Content Type",
            ["Tutti i Contenuti (87)", "Contenuti Gratuiti (7)", "Contenuti Premium (80)"],
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        b1.button("📌 Applica", use_container_width=True)
        if b2.button("🗑️ Reset", use_container_width=True):
            st.rerun()

    with col_main:
        st.markdown(
            """
            <h2 style='color:#f8fafc; margin:0 0 4px 0;'>Immergiti nelle nostre analisi quantitative!</h2>
            <div class="banner-premium">
                <span>⭐</span>
                <span><b>Accesso Premium Attivo</b><br>Hai accesso a tutte le 87 analisi inclusi 80 contenuti premium.</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        allowed_macros = []
        if cat_usa: allowed_macros.append("Usa")
        if cat_world: allowed_macros.append("World")

        filtered_studies = []
        for s in STUDIES_DB:
            if s["macro"] not in allowed_macros:
                continue
            if s["subcat"] not in subcat_selection:
                continue
            if not any(t in tag_selection for t in s["tags"]) and s["tags"] != ["No tags"]:
                continue
            if content_type == "Contenuti Gratuiti (7)" and s["premium"]:
                continue
            if content_type == "Contenuti Premium (80)" and not s["premium"]:
                continue
            if search_kw != "" and (search_kw not in s["name"].lower() and search_kw not in s["desc"].lower()):
                continue
            filtered_studies.append(s)

        macros_present = ["Usa", "World"]
        for m in macros_present:
            m_studies = [s for s in filtered_studies if s["macro"] == m]
            if not m_studies:
                continue

            st.markdown(f"<h3 style='color:#38bdf8; margin-top:20px;'>{m}</h3>", unsafe_allow_html=True)

            subcats_in_m = sorted(list(set([s["subcat"] for s in m_studies])))
            for sc in subcats_in_m:
                sc_studies = [s for s in m_studies if s["subcat"] == sc]
                if not sc_studies:
                    continue

                st.markdown(f"<h4 style='color:#94a3b8; font-size:15px; margin:14px 0 8px 0;'>{sc}</h4>", unsafe_allow_html=True)

                cols = st.columns(3)
                for idx, s in enumerate(sc_studies):
                    col = cols[idx % 3]
                    with col:
                        badge_prem_html = "<span class='qr-badge-prem'>★ Premium</span>" if s["premium"] else ""
                        tags_html = "".join([f"<span class='qr-tag'>{t}</span>" for t in s["tags"]])

                        st.markdown(
                            f"""
                            <div class="qr-card">
                                <div>
                                    <div class="qr-title-row">
                                        <span class="qr-title">{s['name']}</span>
                                        {badge_prem_html}
                                    </div>
                                    <div class="qr-stars">{s['stars']}</div>
                                    <div class="qr-desc">{s['desc']}</div>
                                </div>
                                <div>
                                    <div class="qr-tags">{tags_html}</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        if st.button("👁️ Visualizza Analisi", key=f"btn_qr_{s['id']}", use_container_width=True):
                            st.session_state.active_study_id = s["id"]
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
