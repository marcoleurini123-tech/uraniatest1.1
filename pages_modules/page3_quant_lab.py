import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# =============================================================================
# ARCHIVIO UFFICIALE COMPLETO DEI DEGLI 87 STUDI QUANTITATIVI QUANT-REA
# =============================================================================
QUANT_REA_ARCHIVE = {
    "🇺🇸 Statistiche Macro (USA)": [
        {"id": "MACRO_01", "name": "NON FARM PAYROLLS", "desc": "Quante volte si è presentato che i NON FARM PAY ROLLS siano stati revisionati e come si è comportato il mercato.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "MACRO_02", "name": "Tassi - Inflazione - Disoccupazione", "desc": "Come si comporta l'S&P 500 con Disoccupazione - Inflazione - tassi alti o bassi?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "MACRO_03", "name": "Tassi", "desc": "Come si comporta il mercato con Tassi Alti o meno?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "MACRO_04", "name": "Inflazione", "desc": "S&P con INFLAZIONE alta che return/drawdown ha?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "MACRO_05", "name": "Disoccupazione", "desc": "Come si comporta S&P500 con disoccupazione che sale o che scende?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "MACRO_06", "name": "GDP", "desc": "Come si comporta S&P500 sopra o sotto la media a 6 periodi della variazione del PIL USA?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "MACRO_07", "name": "Recessione - Ritorni S&P", "desc": "E' vero che in RECESSIONE o PARZIALE RECESSIONE S&P va male? E' vero che in fasi di no recessione sale sempre?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "MACRO_08", "name": "CAPE - PE - UTILI in rapporto al S&P 500", "desc": "Mette insieme tre indicatori di valutazione dell'S&P 500 e li confronta con i rendimenti annui dell'indice.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "MACRO_09", "name": "Eventi Geopolitici - Analisi Impatto", "desc": "Cosa succede su vari asset quando si presentano shock ed eventi geopolitici?", "tags": ["Multi-Asset", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"}
    ],
    "📉 Bear Market - Drawdown": [
        {"id": "DD_01", "name": "Studio dei DRAWDOWN", "desc": "Analisi delle Correzioni: confronta l'andamento dell'asset scelto (es. S&P 500) durante tutte le correzioni storiche.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "DD_02", "name": "Drawdown Ritorno", "desc": "Analizza un asset (es. SPX, AMEX:SPY, NASDAQ:NDX) e, per ogni anno, calcola: Max drawdown intraday e peggior calo dell'anno.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "DD_03", "name": "Giorni in BEAR MARKET", "desc": "Se il drawdown scende oltre una soglia scelta (es. -20%), quel giorno è marcato come bear. Conteggio per anno.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "DD_04", "name": "Ergocità dei Mercati", "desc": "Misura quando il comportamento dei rendimenti a breve periodo è in linea con la media di lungo periodo.", "tags": ["Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "DD_05", "name": "Bear Market & Secondo Drawdown", "desc": "Intercetta i bear market storici dell'asset (calo >= -20% dal massimo precedente) e cerca il successivo.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "DD_06", "name": "Gap negativo & nuovo minimo (weekly)", "desc": "Intercetta le settimane in cui l'asset apre con un gap negativo (<= soglia impostata) e tocca un nuovo minimo.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "DD_07", "name": "Bull & Bear Market Dashboard", "desc": "Seleziona il ticker, imposta la soglia (default 20% indici, 30-40% per singoli titoli) e analizza il ciclo.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "DD_08", "name": "Numero di DRAWDOWN nell'anno e ritorni", "desc": "Misura quante volte, in ciascun anno, l'asset ha subito un drawdown pari o superiore a una soglia X%.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "DD_09", "name": "In che mese un ASSET fa il suo massimo dell'anno e poi ritraccia?", "desc": "Equity con massimi annuali: andamento del prezzo e individuazione del mese in cui si forma il picco.", "tags": ["Aziende", "S&P500"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "DD_10", "name": "Drop Giornaliero Cumulato", "desc": "Monitora i 'giorni di forte calo' sui titoli di un indice e li confronta con l'andamento dell'indice.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "DD_11", "name": "DASHBOARD drawdown e recovery", "desc": "Esplora 4 mercati: S&P 500, NASDAQ 100, NASDAQ completo e NYSE. Misura tempi e curve di recupero.", "tags": ["Aziende", "S&P500"], "stars": "⭐⭐⭐⭐⭐"}
    ],
    "📊 Rendimenti & Statistica": [
        {"id": "RET_01", "name": "Escludi X giorni Peggiori/Migliori", "desc": "Se togliessimo gli X giorni peggiori/migliori un asset resta bullish? E dopo gli X giorni peggiori entro quanto si riprende?", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_02", "name": "Correlazione e Stagionalità", "desc": "Rendimenti e correlazioni statistiche lineari e non lineari di PEARSON - SPEARMAN - KENDALL.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_03", "name": "Rendimenti - ZSCORE", "desc": "Mostra, per l'asset selezionato, i rendimenti annuali storici e la loro posizione statistica (Z-Score) rispetto alla media.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐☆☆"},
        {"id": "RET_04", "name": "Ritorni Mensili e Annui", "desc": "Heatmap e matrici storiche dei ritorni mensili e annualizzati.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_05", "name": "Nuovi massimi dell'anno e Ritorni a fine anno", "desc": "Analizza un asset e misura quanto spesso, all'interno di ciascun anno, segna nuovi massimi e come chiude l'anno.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_06", "name": "Numero di Aziende del NASDAQ 100 che salgono", "desc": "Mostra quanta parte del NASDAQ-100 chiude in rialzo e come usare questa informazione per segnali operativi.", "tags": ["Descrittiva", "NASDAQ"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_07", "name": "Numero di Aziende del S&P 500 che salgono", "desc": "Vista 'breadth' dell'S&P 500: percentuale di componenti in rialzo (advancing %) e segnali di divergenza.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_08", "name": "Giorni consecutivi Positivi / Negativi", "desc": "Analizza il 'respiro' del mercato: quante sedute passano senza due rialzi consecutivi e quante sedute positive si susseguono.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_09", "name": "Numero di Aziende del S&P 500 che sovraperformano", "desc": "Raccoglie e quantifica quante azioni battono la performance dell'indice di riferimento.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_10", "name": "Numero di Aziende del NASDAQ che sovraperformano", "desc": "Concentrazione dei flussi: quante aziende sovraperformano il benchmark tecnologico.", "tags": ["NASDAQ", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_11", "name": "Rendimenti a Intervallo fisso", "desc": "Come si comporta un asset in determinati periodi dell'anno? Tutte le metriche statistiche a finestre temporali.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_12", "name": "Ritorni di un asset da ogni bottom", "desc": "Mostra i ritorni da ogni bottom (di almeno un -20% di drawdown) su vari archi temporali.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_13", "name": "Rendimenti sopra sotto la 200 sma", "desc": "Come si comporta un asset quando si distanzia molto dalla sua media mobile a 200 periodi.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_14", "name": "Cap-Weighted vs Equal-Weight", "desc": "Chi guida davvero il mercato? Mostra le performance dei settori e dell'S&P 500 a capitalizzazione vs peso equo.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "RET_15", "name": "Rendimenti PAC/PIC matrice cumulata", "desc": "Mappa a colori dove ogni cella mostra il rendimento annuo medio (%) ottenuto investendo dallo start con PAC vs PIC.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_16", "name": "Dashboard sulle quotazioni in borsa (IPO)", "desc": "1980/2025: Esplora 45 anni di dati reali su oltre 9.000 aziende quotate al debutto.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_17", "name": "Forza relativa di tutti gli indici", "desc": "Panoramica completa dei principali indici azionari mondiali confrontandone andamento, forza relativa e momentum.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_18", "name": "Inizio peggiore ritorni a fine anno", "desc": "Come si comporta un asset nei primi giorni dell'anno e come questi determinano il ritorno di fine anno.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_19", "name": "Shuffle a Blocchi", "desc": "Triangolo (mappa termica IRR) Y = anno di partenza, X = anno di fine. Ogni cella mostra il rendimento composto.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_20", "name": "Contributo ricchezza di una Asset class", "desc": "Analisi dell'impatto cumulato e contributo marginale di ogni singola asset class al portafoglio complessivo.", "tags": ["Strategia", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_21", "name": "Escursione High-Low dall'inizio anno", "desc": "Analizza quanto si muove un asset nei primi mesi dell'anno e fornisce previsioni statistiche sull'ampiezza di range.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_22", "name": "Rendimenti Cumulati per archi temporali", "desc": "Comprare ai massimi storici penalizza i rendimenti? Risponde con curve empiriche per ogni orizzonte (da 3 a 10 anni).", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"}
    ],
    "🏛️ 200 LEVEL / Settori (Breadth)": [
        {"id": "LEV_01", "name": "200 LEVEL S&P", "desc": "Come si comporta l'S&P 500 quando poche aziende del listino restano sopra la media a 200 periodi giornaliera?", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_02", "name": "200 LEVEL NASDAQ", "desc": "Come si comporta il NASDAQ quando poche aziende restano sopra la propria media a 200 periodi?", "tags": ["NASDAQ", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_03", "name": "200 LEVEL DOW JONES", "desc": "Come si comporta il DOW JONES quando poche aziende che lo compongono rimangono sopra la media 200.", "tags": ["Dow Jones", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_04", "name": "200 LEVEL Russell 2000", "desc": "Comportamento del Russell 2000 quando poche aziende Small Cap restano sopra la media 200 periodi.", "tags": ["Russell 2000", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_05", "name": "200 LEVEL DAX", "desc": "Comportamento dell'indice tedesco DAX quando poche aziende rimangono sopra la media a 200 periodi.", "tags": ["DAX", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_06", "name": "200 LEVEL SETTORI", "desc": "Come si comportano i SETTORI dell'S&P 500 quando poche aziende che li compongono rimangono sopra la media 200.", "tags": ["Settori", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_07", "name": "S&P Sectors – Compressione & Momentum", "desc": "Analisi settoriale su performance, Momentum, Compressione, Correlazioni e rotazioni statistiche avanzate.", "tags": ["Settori", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_08", "name": "200 LEVEL MIB", "desc": "Come si comporta il FTSE MIB quando poche aziende italiane rimangono sopra la media 200 periodi.", "tags": ["FTSE MIB", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_09", "name": "200 LEVEL CAC", "desc": "Come si comporta il CAC 40 quando poche aziende francesi rimangono sopra la media 200 periodi.", "tags": ["CAC 40", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_10", "name": "200 LEVEL IBEX", "desc": "Come si comporta l'IBEX 35 quando poche aziende spagnole rimangono sopra la media 200 periodi.", "tags": ["IBEX 35", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_11", "name": "200 LEVEL SMI Svizzero", "desc": "Come si comporta lo SMI Svizzero quando poche aziende che lo compongono rimangono sopra la media 200.", "tags": ["SMI", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_12", "name": "200 LEVEL NIKKEI 225", "desc": "Come si comporta il NIKKEI 225 quando poche aziende giapponesi rimangono sopra la media 200.", "tags": ["Nikkei", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_13", "name": "200 LEVEL HANG SENG", "desc": "Come si comporta l'HANG SENG quando poche aziende cinesi rimangono sopra la media 200 periodi.", "tags": ["Hang Seng", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_14", "name": "200 LEVEL EMERGING MARKET", "desc": "Come si comporta l'indice EMERGING MARKETS quando poche aziende dei paesi emergenti restano sopra la media 200.", "tags": ["Emerging", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"}
    ],
    "🎯 Strategie Quantitative": [
        {"id": "STRAT_01", "name": "Strategia Sell in May", "desc": "Mostra come un asset si comporta con la narrativa SELL IN MAY AND GO AWAY (Maggio-Ottobre vs Nov-Apr).", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐☆☆"},
        {"id": "STRAT_02", "name": "Strategia QQQ Overnigth", "desc": "Dove performa meglio il mercato: overnight o intraday? Rendimento cumulato su tre linee (Open-Close vs Close-Open).", "tags": ["QQQ", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_03", "name": "Strategia soglia DrawDown", "desc": "Strategia d'investimento a incrementi su soglie di drawdown prefissate (-20%, -30%, -40%).", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_04", "name": "Strategia - Buy the dip", "desc": "Ogni volta che l'S&P 500 / Asset chiude in rosso, entra sul mercato il giorno successivo.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_05", "name": "Strategia Top 10 - Top 20 - S&P500", "desc": "Come hanno performato le prime 10 e 20 aziende per market cap versus l'intero S&P 500.", "tags": ["S&P500", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_06", "name": "Equity & BOND - CAPE", "desc": "Confronta un indice azionario (SPX) con il 'prezzo teorico' e rendimento di un Treasury USA a 10 anni.", "tags": ["Multi-Asset", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_07", "name": "Gap per ogni giorno", "desc": "Analizza come il mercato salta all'apertura rispetto alla chiusura del giorno prima e la frequenza di fill.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_08", "name": "Christmas Effect", "desc": "Strategia di stagionalità che sfrutta il rally di fine anno: storicamente attivo tra fine dicembre e gennaio.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐☆☆"},
        {"id": "STRAT_09", "name": "Simulazione Montecarlo EQUITY", "desc": "Qual è il migliore Risk/Reward da adottare e il rischio massimo per un'operatività profittevole nel tempo.", "tags": ["S&P500", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_10", "name": "Processo di Poisson", "desc": "La distribuzione di Poisson per descrivere quante volte si presenta un evento raro di mercato in un arco temporale.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_11", "name": "Entropia dei Mercati", "desc": "L'entropia statistica misura quanto il mercato è prevedibile o caotico in un dato intervallo di tempo.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_12", "name": "Strategia - Sell the rip", "desc": "Ogni volta che l'asset chiude in forte verde, va short sul mercato il giorno successivo.", "tags": ["S&P500", "Strategia"], "stars": "⭐⭐⭐⭐⭐"}
    ],
    "⚡ Volatilità": [
        {"id": "VOL_01", "name": "VIX", "desc": "Cosa succede ad S&P 500 quando il VIX è sopra il livello 30 su vari archi temporali e distribuzione dei rendimenti.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "VOL_02", "name": "Volatility", "desc": "Mostra come si muove e quanto 'trema' un mercato su diversi orizzonti temporali per stimare il rischio.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐☆☆"},
        {"id": "VOL_03", "name": "La volatilità GARCH", "desc": "Confronta tre misure di volatilità nel tempo per capire quanto bene una stima GARCH anticipa la volatilità futura.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐⭐⭐"}
    ],
    "💼 Ottimizzatore di Portafoglio & Scanner": [
        {"id": "PORT_01", "name": "Ottimizzatore di Portafoglio", "desc": "Costruisce e valuta portafogli multi-asset. Seleziona i ticker, imposta benchmark e numero di simulazioni.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_02", "name": "Comparazione Asset", "desc": "Confronta asset finanziari su lunghe serie storiche. Imposta data di inizio, metriche e curve comparative.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_03", "name": "Quanto mi costa investire", "desc": "Simulazione pluriennale per quantificare l'impatto reale dei costi di gestione e commissioni sul capitale.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐☆☆"},
        {"id": "PORT_04", "name": "Ritorni Futuri", "desc": "Studia cosa succede dopo un drawdown: analizza un singolo asset o un intero portafoglio multi-asset.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_05", "name": "MSCI ANALYSIS", "desc": "Analizza tutti gli archivi delle equity di tutto il mondo dell'universo MSCI.", "tags": ["World", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_06", "name": "Comparatore - Portafogli", "desc": "Esporta le equity line dei portafogli creati con l'Ottimizzatore e confrontale simultaneamente.", "tags": ["Portafogli", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_07", "name": "Ribilanciamento sì o no?", "desc": "Analizza l'impatto e il timing del ribilanciamento periodico di portafoglio rispetto al non ribilanciamento.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_08", "name": "Calcolatore Capitale", "desc": "Permette di capire come cresce un capitale nel tempo e quale rendimento serve per raggiungere un obiettivo prefissato.", "tags": ["Descrittiva", "Backtest"], "stars": "⭐⭐⭐☆☆"},
        {"id": "PORT_09", "name": "Test D'Ipotesi", "desc": "Testa in modo rapido l'aggiunta di un asset a un portafoglio per verificare se migliora il rendimento o riduce il drawdown.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "SCAN_01", "name": "Aziende USA senza 100/50 best DAY", "desc": "Quante aziende dell'S&P 500, NASDAQ 100 e NYSE private dei 50/100 giorni migliori hanno ancora un rendimento positivo?", "tags": ["Aziende", "S&P500"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "SCAN_02", "name": "I 100 migliori/peggiori giorni DAY AFTER", "desc": "Due blocchi separati (S&P 500 e NASDAQ): per ogni ticker analizza cosa succede il giorno successivo ai picchi.", "tags": ["S&P500", "Backtest"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "SCAN_03", "name": "Regressione ritorno mensile con ritorno annuo", "desc": "Classifica dei titoli NYSE/NASDAQ con la relazione statistica più forte tra il rendimento di un mese e l'anno.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "SCAN_04", "name": "Numero di indici USA-EUROPA che salgono/scendono", "desc": "Quanti indici salgono o scendono nello stesso periodo: breadth aggregata (NDX, SPX, RUT, DJI, DAX, CAC, FTSE, MIB).", "tags": ["Global Indici", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "SCAN_05", "name": "Numero di Indici che fanno nuovi massimi", "desc": "Conta quanti indici azionari globali segnano un nuovo massimo rispetto all'ultimo anno e mostra l'ampiezza a barre.", "tags": ["Global Indici", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "SCAN_06", "name": "POC SCANNER", "desc": "Strumento per selezionare un universo di titoli (S&P 500, NASDAQ 100, NYSE) e intercettare la compressione volumetrica sul POC.", "tags": ["Aziende", "Scanner"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "SCAN_07", "name": "Correlazione ritorno mensile con ritorno annuo (Mese+Anno)", "desc": "Analisi divisa in due blocchi: Mese positivo & Anno positivo, mostra i titoli per cui, negli anni storici, vale la correlazione.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"}
    ]
}

# =============================================================================
# ENGINE EOD PER IL CALCOLO DEI MODULI QUANT-REA SU ASSET
# =============================================================================
def compute_quant_rea_study(ticker: str, study_id: str) -> dict:
    """Esegue il calcolo quantitativo EOD specifico sul sottostante."""
    try:
        df = yf.download(ticker, period="2y", interval="1d", progress=False)
        if df.empty or len(df) < 50:
            return {"status": "ERROR", "msg": "Serie storica insufficiente per il ticker."}
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        last_close = float(df['Close'].iloc[-1])
        ath_price = float(df['High'].max())
        drawdown = ((last_close - ath_price) / ath_price) * 100.0
        
        # POC Volume Profile (50 Bins)
        price_bins = np.linspace(df['Low'].min(), df['High'].max(), 50)
        bin_idx = np.digitize(df['Close'].values, price_bins)
        vol_hist = np.zeros(len(price_bins))
        for idx, v in zip(bin_idx, df['Volume'].values):
            if idx < len(vol_hist):
                vol_hist[idx] += v
        poc_price = float(price_bins[np.argmax(vol_hist)])
        dist_poc = ((last_close - poc_price) / poc_price) * 100.0

        # Z-Score Rendimenti 52w
        ret = df['Close'].pct_change()
        z_score = float((ret.iloc[-1] - ret.mean()) / (ret.std() + 1e-9))
        
        sma50 = float(df['Close'].rolling(50).mean().iloc[-1])
        sma200 = float(df['Close'].rolling(200).mean().iloc[-1]) if len(df) >= 200 else sma50

        # Logica di valutazione
        is_pass = False
        notes = ""
        
        if "DD_" in study_id:
            is_pass = (drawdown <= -20.0)
            notes = f"Drawdown da ATH: {drawdown:.1f}% | POC Base: ${poc_price:.2f} ({dist_poc:+.2f}%)"
        elif "RET_03" in study_id or "ZSCORE" in study_id:
            is_pass = (z_score <= -1.85)
            notes = f"Z-Score 52w: {z_score:.2f} (Livello di capitolazione <= -1.85)"
        elif "LEV_" in study_id:
            is_pass = (last_close > sma200)
            notes = f"Prezzo ${last_close:.2f} vs SMA 200 ${sma200:.2f} ({((last_close-sma200)/sma200)*100:+.2f}%)"
        elif "SCAN_06" in study_id or "POC" in study_id:
            is_pass = (drawdown <= -30.0 and abs(dist_poc) <= 5.0)
            notes = f"Compressione Volumetrica POC Base: ${poc_price:.2f} | Distanza: {dist_poc:+.2f}%"
        else:
            is_pass = (last_close > sma50 and z_score > 0)
            notes = f"Prezzo ${last_close:.2f} | SMA50: ${sma50:.2f} | Z-Score: {z_score:.2f}"

        return {
            "status": "PASS" if is_pass else "NEUTRAL",
            "price": last_close,
            "drawdown": drawdown,
            "poc": poc_price,
            "poc_dist": dist_poc,
            "z_score": z_score,
            "sma50": sma50,
            "sma200": sma200,
            "notes": notes,
            "df": df
        }
    except Exception as e:
        return {"status": "ERROR", "msg": str(e)}

# =============================================================================
# RENDER PRINCIPALE PAGINA 3
# =============================================================================
def render_page3():
    st.title("🔬 Quant Lab: Archivio Studi Quantitativi (87 Studi Quant-Rea)")
    st.caption("Catalogo completo e modulare: Statistiche Macro, Drawdown, Rendimenti Z-Score, 200 Level Settori, Strategie e Volatilità.")
    st.markdown("---")

    tab_cat, tab_runner = st.tabs([
        "📚 1. Catalogo Ufficiale (87 Analisi)",
        "🧪 2. Esecutore Singolo Studio EOD"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: CATALOGO COMPLETO 87 STUDI QUANT-REA
    # -------------------------------------------------------------------------
    with tab_cat:
        st.subheader("📋 Esploratore degli Studi Quantitativi")
        
        total_studies = sum(len(v) for v in QUANT_REA_ARCHIVE.values())
        st.success(f"⭐ **Accesso Premium Attivo**: Totale **{total_studies} analisi quantitative** caricate su URANIA.")

        f_c1, f_c2 = st.columns([1, 2])
        search_query = f_c1.text_input("🔍 Cerca Studio o Parola Chiave:", placeholder="es. Drawdown, ZSCORE, POC, Tassi...").strip().lower()
        selected_macro_cat = f_c2.selectbox("Filtra per Categoria:", ["Tutte le Categorie"] + list(QUANT_REA_ARCHIVE.keys()))

        for category_title, studies in QUANT_REA_ARCHIVE.items():
            if selected_macro_cat != "Tutte le Categorie" and category_title != selected_macro_cat:
                continue
            
            filtered_studies = []
            for s in studies:
                if search_query == "" or (search_query in s['name'].lower() or search_query in s['desc'].lower() or any(search_query in t.lower() for t in s['tags'])):
                    filtered_studies.append({
                        "Rating": s['stars'],
                        "ID Modulo": s['id'],
                        "Titolo Studio": s['name'],
                        "Descrizione Analisi": s['desc'],
                        "Tags": ", ".join(s['tags'])
                    })

            if filtered_studies:
                with st.expander(f"📁 {category_title} — ({len(filtered_studies)} Studi)", expanded=(selected_macro_cat != "Tutte le Categorie" or search_query != "")):
                    st.dataframe(pd.DataFrame(filtered_studies), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 2: ESECUTORE SINGOLO STUDIO EOD
    # -------------------------------------------------------------------------
    with tab_runner:
        st.subheader("🔬 Esecuzione ed Analisi del Singolo Studio su Asset")
        st.caption("Seleziona qualsiasi studio dall'archivio e calcola i parametri quantitativi su dati storici EOD.")

        c1, c2 = st.columns([1, 2])
        with c1:
            ticker_input = st.text_input("Ticker Sottostante (es. PYPL, TSLA, PLTR, BABA, SPY, QQQ):", value="PYPL").upper().strip()
            
            all_flat = []
            for cat, stds in QUANT_REA_ARCHIVE.items():
                for s in stds:
                    all_flat.append(f"{s['id']} ➔ {s['name']}")
            
            selected_str = st.selectbox("Seleziona lo Studio da Calcolare:", all_flat, index=0)
            selected_id = selected_str.split(" ➔ ")[0]

            btn_run = st.button("🚀 ESEGUI STUDIO SU DATI EOD", use_container_width=True)

        with c2:
            if btn_run or ticker_input:
                with st.spinner(f"Calcolo metriche EOD per ${ticker_input}..."):
                    res = compute_quant_rea_study(ticker_input, selected_id)
                    
                    if res.get("status") == "ERROR":
                        st.error(f"❌ Errore durante l'elaborazione: {res.get('msg')}")
                    else:
                        status_badge = "🟢 SETUP CONFERMATO (PASS)" if res["status"] == "PASS" else "⚪ SEGNALE NEUTRO"
                        badge_color = "#10b981" if res["status"] == "PASS" else "#94a3b8"

                        st.markdown(
                            f"""
                            <div style="background: #0b1320; border: 1px solid #1e293b; border-radius: 12px; padding: 18px; margin-bottom: 15px;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <h4 style="margin:0; color:#f8fafc;">Asset: ${ticker_input} | {selected_id}</h4>
                                    <span style="background:{badge_color}; color:#030712; font-weight:900; padding:4px 10px; border-radius:6px; font-size:12px;">{status_badge}</span>
                                </div>
                                <p style="color:#cbd5e1; font-size:13px; margin:8px 0 0 0;"><b>Esito Analisi:</b> {res['notes']}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Prezzo Ultimo EOD", f"${res['price']:.2f}")
                        m2.metric("Drawdown da ATH", f"{res['drawdown']:.1f}%")
                        m3.metric("Point of Control (POC)", f"${res['poc']:.2f}", f"{res['poc_dist']:+.2f}%")
                        m4.metric("Z-Score 52w", f"{res['z_score']:.2f}")

                        df_plot = res["df"]
                        fig = go.Figure()
                        fig.add_trace(go.Candlestick(
                            x=df_plot.index,
                            open=df_plot['Open'],
                            high=df_plot['High'],
                            low=df_plot['Low'],
                            close=df_plot['Close'],
                            name=f"${ticker_input}"
                        ))
                        fig.add_hline(y=res['poc'], line_dash="dash", line_color="#00D1FF", annotation_text=f"POC Base (${res['poc']:.2f})")
                        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'].rolling(50).mean(), name="SMA 50", line=dict(color="#f59e0b", width=1.5)))
                        fig.update_layout(height=450, template="plotly_dark", title=f"Struttura Volumetrica & POC: ${ticker_input}", xaxis_rangeslider_visible=False)
                        st.plotly_chart(fig, use_container_width=True)
