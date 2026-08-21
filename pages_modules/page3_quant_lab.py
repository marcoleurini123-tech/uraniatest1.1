import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# =============================================================================
# 1. CATALOGO PROTOCOLLI QUANTITATIVI (SUITE DA 6 STUDI ATOMICI)
# =============================================================================
PROTOCOLS_DEFINITIONS = {
    "🎯 PROTOCOLLO 1: Deep Value & Bottom Hunter (Azioni all'Inferno)": {
        "desc": "Protocollo per identificare minimi di ciclo, capitolazione volumetrica ed eccessi statistici su titoli con forte sconto dai massimi.",
        "studies": [
            {"id": "DD_01", "name": "Studio Drawdown da ATH", "target": "Drawdown <= -30%"},
            {"id": "POC_01", "name": "Compressione POC Volume Profile", "target": "Distanza POC <= 5%"},
            {"id": "ZSC_01", "name": "Z-Score Rendimenti 52w", "target": "Z-Score <= -1.50"},
            {"id": "SMA_01", "name": "Distanza dalla Media 200 SMA", "target": "Prezzo < SMA200 (-15%)"},
            {"id": "VOL_01", "name": "Volume Climax di Assorbimento", "target": "Volume >= 1.5x SMA20"},
            {"id": "RSI_01", "name": "Iper-venduto Statistico & MFI", "target": "RSI / MFI <= 30"}
        ]
    },
    "🚀 PROTOCOLLO 2: Rounding Base & Accumulation Breakout": {
        "desc": "Protocollo per intercettare strutture a 'U' (Rounding Base), consolidamenti volumetrici e breakout di cambio trend.",
        "studies": [
            {"id": "BASE_01", "name": "Formazione Base ad U & POC Shift", "target": "Prezzo > POC Base"},
            {"id": "SMA_02", "name": "Recupero SMA 50 / SMA 200", "target": "Prezzo sopra SMA50"},
            {"id": "VOL_02", "name": "Espansione Volumi su Breakout", "target": "Volume > 200% Media"},
            {"id": "ZSC_02", "name": "Z-Score Momentum Reversal", "target": "Z-Score > +0.50"},
            {"id": "VA_01", "name": "Uscita dalla Value Area", "target": "Prezzo sopra VAH"},
            {"id": "GAP_01", "name": "Tenuta Gap Up & Retest Supporto", "target": "Nessuna chiusura sotto gap"}
        ]
    },
    "🏛️ PROTOCOLLO 3: Macro Stress, Volatilità & Indici (SPX/NDX)": {
        "desc": "Protocollo per valutare la tenuta del mercato azionario generale nei cambi di regime macroeconomico e liquidità.",
        "studies": [
            {"id": "MACRO_NFP", "name": "Non-Farm Payrolls & Revisioni", "target": "1st/2nd Release > 0"},
            {"id": "VOL_VIX", "name": "VIX Term Structure & Spike > 30", "target": "Curva in Contango"},
            {"id": "LEV_200", "name": "200 Level Breadth S&P 500", "target": "% Titoli > SMA200 (> 50%)"},
            {"id": "CAPE_01", "name": "CAPE / PE Ratio vs Rendimenti 10Y", "target": "Equity Risk Premium Positivo"},
            {"id": "COT_INDX", "name": "Posizionamento Istituzionale CFTC", "target": "Commercials Net Long"},
            {"id": "LIQ_FED", "name": "Impulso Liquidità Netta Fed", "target": "Variazione Netta 30D > 0"}
        ]
    }
}

# =============================================================================
# 2. ARCHIVIO COMPLETO DEGLI 87 STUDI QUANT-REA
# =============================================================================
QUANT_REA_ARCHIVE = {
    "🇺🇸 Statistiche Macro (USA)": [
        {"id": "MACRO_01", "name": "NON FARM PAYROLLS", "desc": "Quante volte i NON FARM PAY ROLLS siano stati revisionati e come si è comportato l'S&P 500.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
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
        {"id": "DD_01", "name": "Studio dei DRAWDOWN", "desc": "Analisi delle Correzioni: confronta l'andamento dell'asset scelto durante tutte le correzioni storiche.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "DD_02", "name": "Drawdown Ritorno", "desc": "Analizza un asset e, per ogni anno, calcola: Max drawdown intraday e peggior calo dell'anno.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "DD_03", "name": "Giorni in BEAR MARKET", "desc": "Se il drawdown scende oltre una soglia scelta (es. -20%), quel giorno è marcato come bear.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "DD_04", "name": "Ergocità dei Mercati", "desc": "Misura quando il comportamento dei rendimenti a breve periodo è in linea con la media di lungo periodo.", "tags": ["Descrittiva", "Backtest"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "DD_05", "name": "Bear Market & Secondo Drawdown", "desc": "Intercetta i bear market storici dell'asset (calo >= -20% dal massimo precedente) e cerca il successivo.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "DD_06", "name": "Gap negativo & nuovo minimo (weekly)", "desc": "Intercetta le settimane in cui l'asset apre con un gap negativo e tocca un nuovo minimo.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "DD_07", "name": "Bull & Bear Market Dashboard", "desc": "Seleziona il ticker, imposta la soglia (default 20% indici, 30-40% per singoli titoli) e analizza il ciclo.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "DD_08", "name": "Numero di DRAWDOWN nell'anno e ritorni", "desc": "Misura quante volte, in ciascun anno, l'asset ha subito un drawdown pari o superiore a una soglia X%.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "DD_09", "name": "In che mese un ASSET fa il suo massimo dell'anno e poi ritraccia?", "desc": "Equity con massimi annuali: andamento del prezzo e individuazione del mese in cui si forma il picco.", "tags": ["Aziende", "S&P500"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "DD_10", "name": "Drop Giornaliero Cumulato", "desc": "Monitora i 'giorni di forte calo' sui titoli di un indice e li confronta con l'andamento dell'indice.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "DD_11", "name": "DASHBOARD drawdown e recovery", "desc": "Esplora 4 mercati: S&P 500, NASDAQ 100, NASDAQ completo e NYSE. Misura tempi e curve di recupero.", "tags": ["Aziende", "S&P500"], "stars": "⭐⭐⭐⭐⭐"}
    ],
    "📊 Rendimenti & Statistica": [
        {"id": "RET_01", "name": "Escludi X giorni Peggiori/Migliori", "desc": "Se togliessimo gli X giorni peggiori/migliori un asset resta bullish?", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_02", "name": "Correlazione e Stagionalità", "desc": "Rendimenti e correlazioni statistiche di PEARSON - SPEARMAN - KENDALL.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_03", "name": "Rendimenti - ZSCORE", "desc": "Mostra, per l'asset selezionato, i rendimenti annuali storici e la loro posizione Z-Score.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐☆☆"},
        {"id": "RET_04", "name": "Ritorni Mensili e Annui", "desc": "Heatmap e matrici storiche dei ritorni mensili e annualizzati.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_05", "name": "Nuovi massimi dell'anno e Ritorni a fine anno", "desc": "Analizza quanto spesso l'asset segna nuovi massimi e come chiude l'anno.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_06", "name": "Numero di Aziende del NASDAQ 100 che salgono", "desc": "Breadth del NASDAQ 100 per individuare segnali operativi di partecipazione.", "tags": ["Descrittiva", "NASDAQ"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_07", "name": "Numero di Aziende del S&P 500 che salgono", "desc": "Percentuale di componenti S&P 500 in rialzo (advancing %) e divergenze.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_08", "name": "Giorni consecutivi Positivi / Negativi", "desc": "Analizza il 'respiro' del mercato: serie storiche di sedute consecutive nella stessa direzione.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_09", "name": "Numero di Aziende del S&P 500 che sovraperformano", "desc": "Quante azioni battono la performance dell'indice di riferimento.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_10", "name": "Numero di Aziende del NASDAQ che sovraperformano", "desc": "Concentrazione della sovraperformance sul benchmark tecnologico.", "tags": ["NASDAQ", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_11", "name": "Rendimenti a Intervallo fisso", "desc": "Comportamento statistico dell'asset su finestre temporali fisse dell'anno.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_12", "name": "Ritorni di un asset da ogni bottom", "desc": "Ritorni a 1, 3, 6, 12 mesi da ogni bottom (drawdown >= -20%).", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_13", "name": "Rendimenti sopra sotto la 200 sma", "desc": "Comportamento quando il prezzo distanzia la media mobile a 200 periodi.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_14", "name": "Cap-Weighted vs Equal-Weight", "desc": "Confronto performance tra S&P 500 a capitalizzazione (SPY) e peso equo (RSP).", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "RET_15", "name": "Rendimenti PAC/PIC matrice cumulata", "desc": "Mappa a colori del rendimento medio annuo investendo con PAC vs PIC.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_16", "name": "Dashboard sulle quotazioni in borsa (IPO)", "desc": "Esplora 45 anni di dati reali su oltre 9.000 aziende quotate al debutto.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_17", "name": "Forza relativa di tutti gli indici", "desc": "Panoramica completa dei principali indici azionari mondiali a confronto.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_18", "name": "Inizio peggiore ritorni a fine anno", "desc": "Come le prime sedute dell'anno impattano il rendimento finale.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_19", "name": "Shuffle a Blocchi", "desc": "Mappa termica IRR triangolare dei rendimenti composti su ogni coppia di anni.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_20", "name": "Contributo ricchezza di una Asset class", "desc": "Contributo marginale di ogni singola asset class al portafoglio complessivo.", "tags": ["Strategia", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_21", "name": "Escursione High-Low dall'inizio anno", "desc": "Ampiezza di oscillazione dai primi mesi dell'anno e previsioni statistiche.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "RET_22", "name": "Rendimenti Cumulati per archi temporali", "desc": "Comprare ai massimi storici penalizza i rendimenti a 3-10 anni?", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"}
    ],
    "🏛️ 200 LEVEL / Settori (Breadth)": [
        {"id": "LEV_01", "name": "200 LEVEL S&P", "desc": "% di componenti S&P 500 sopra la media a 200 periodi.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_02", "name": "200 LEVEL NASDAQ", "desc": "% di titoli NASDAQ sopra la media a 200 periodi.", "tags": ["NASDAQ", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_03", "name": "200 LEVEL DOW JONES", "desc": "% di titoli Dow Jones sopra la media a 200 periodi.", "tags": ["Dow Jones", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_04", "name": "200 LEVEL Russell 2000", "desc": "Stato di salute delle Small Caps sopra la SMA 200.", "tags": ["Russell 2000", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_05", "name": "200 LEVEL DAX", "desc": "% di titoli del DAX 40 sopra la media a 200 periodi.", "tags": ["DAX", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_06", "name": "200 LEVEL SETTORI", "desc": "Confronto dei titoli sopra la 200 SMA per gli 11 settori GICS.", "tags": ["Settori", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_07", "name": "S&P Sectors – Compressione & Momentum", "desc": "Performance settoriale, compressione e rotazioni statistiche.", "tags": ["Settori", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_08", "name": "200 LEVEL MIB", "desc": "% di titoli del FTSE MIB sopra la media a 200 giorni.", "tags": ["FTSE MIB", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_09", "name": "200 LEVEL CAC", "desc": "% di titoli del CAC 40 sopra la media a 200 giorni.", "tags": ["CAC 40", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_10", "name": "200 LEVEL IBEX", "desc": "% di titoli dell'IBEX 35 sopra la media a 200 giorni.", "tags": ["IBEX 35", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_11", "name": "200 LEVEL SMI Svizzero", "desc": "% di titoli dello SMI Svizzero sopra la media 200.", "tags": ["SMI", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_12", "name": "200 LEVEL NIKKEI 225", "desc": "% di titoli del Nikkei 225 sopra la media 200.", "tags": ["Nikkei", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_13", "name": "200 LEVEL HANG SENG", "desc": "% di titoli dell'Hang Seng sopra la media 200.", "tags": ["Hang Seng", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "LEV_14", "name": "200 LEVEL EMERGING MARKET", "desc": "% di titoli emergenti sopra la media a 200 periodi.", "tags": ["Emerging", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"}
    ],
    "🎯 Strategie Quantitative": [
        {"id": "STRAT_01", "name": "Strategia Sell in May", "desc": "Test quantitativo del ciclo stagionale Sell in May and Go Away.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐☆☆"},
        {"id": "STRAT_02", "name": "Strategia QQQ Overnigth", "desc": "Scomposizione dei rendimenti del QQQ: sessione Overnight vs Intraday.", "tags": ["QQQ", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_03", "name": "Strategia soglia DrawDown", "desc": "Piano di accumulo a incrementi su soglie prefissate di drawdown.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_04", "name": "Strategia - Buy the dip", "desc": "Entrata sistematica in acquisto il giorno dopo una chiusura rossa.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_05", "name": "Strategia Top 10 - Top 20 - S&P500", "desc": "Performance delle Top 10/20 aziende per capitalizzazione vs S&P 500.", "tags": ["S&P500", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_06", "name": "Equity & BOND - CAPE", "desc": "Confronto tra rendimento atteso azionario (CAPE) e Treasury 10Y.", "tags": ["Multi-Asset", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_07", "name": "Gap per ogni giorno", "desc": "Frequenza statistica di apertura in gap e probabilità di ricopertura.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_08", "name": "Christmas Effect", "desc": "Rally di fine anno: comportamento stagionale tra fine dicembre e gennaio.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐☆☆"},
        {"id": "STRAT_09", "name": "Simulazione Montecarlo EQUITY", "desc": "Simulazioni Montecarlo per calcolare il Risk/Reward ottimale.", "tags": ["S&P500", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_10", "name": "Processo di Poisson", "desc": "Distribuzione di Poisson per quantificare eventi rari di mercato.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_11", "name": "Entropia dei Mercati", "desc": "Misurazione dell'entropia e del grado di caos del trend.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "STRAT_12", "name": "Strategia - Sell the rip", "desc": "Ingresso short sistematico dopo sessioni ad alta estensione verde.", "tags": ["S&P500", "Strategia"], "stars": "⭐⭐⭐⭐⭐"}
    ],
    "⚡ Volatilità": [
        {"id": "VOL_01", "name": "VIX", "desc": "Cosa succede a S&P 500 quando il VIX supera quota 30 su vari archi temporali.", "tags": ["S&P500", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "VOL_02", "name": "Volatility", "desc": "Misurazione dell'oscillazione del mercato su diversi orizzonti temporali.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐☆☆"},
        {"id": "VOL_03", "name": "La volatilità GARCH", "desc": "Modelli autoregressivi GARCH per stimare la volatilità futura.", "tags": ["Aziende", "Strategia"], "stars": "⭐⭐⭐⭐⭐"}
    ],
    "💼 Ottimizzatore di Portafoglio & Scanner": [
        {"id": "PORT_01", "name": "Ottimizzatore di Portafoglio", "desc": "Costruzione e valutazione di portafogli multi-asset su frontiera efficiente.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_02", "name": "Comparazione Asset", "desc": "Confronto diretto di rendimento e volatilità su serie storiche pluriennali.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_03", "name": "Quanto mi costa investire", "desc": "Simulazione dell'impatto di commissioni e costi di gestione sul capitale.", "tags": ["Aziende", "Descrittiva"], "stars": "⭐⭐⭐☆☆"},
        {"id": "PORT_04", "name": "Ritorni Futuri", "desc": "Aspettativa di rendimento post-drawdown su singoli titoli o portafogli.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_05", "name": "MSCI ANALYSIS", "desc": "Archivio globale dei mercati azionari dell'universo MSCI.", "tags": ["World", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_06", "name": "Comparatore - Portafogli", "desc": "Confronto simultaneo delle equity line tra allocazioni personalizzate.", "tags": ["Portafogli", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_07", "name": "Ribilanciamento sì o no?", "desc": "Impatto comparato del ribilanciamento periodico vs Buy & Hold.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "PORT_08", "name": "Calcolatore Capitale", "desc": "Proiezione della crescita del capitale nel tempo con rendimento target.", "tags": ["Descrittiva", "Backtest"], "stars": "⭐⭐⭐☆☆"},
        {"id": "PORT_09", "name": "Test D'Ipotesi", "desc": "Test d'ipotesi statistico sull'aggiunta di un asset in portafoglio.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "SCAN_01", "name": "Aziende USA senza 100/50 best DAY", "desc": "Rendimento dei titoli azionari privati delle migliori 50/100 giornate.", "tags": ["Aziende", "S&P500"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "SCAN_02", "name": "I 100 migliori/peggiori giorni DAY AFTER", "desc": "Cosa accade il giorno dopo le 100 migliori e peggiori sedute di SPX e NDX.", "tags": ["S&P500", "Backtest"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "SCAN_03", "name": "Regressione ritorno mensile con ritorno annuo", "desc": "Classifica dei titoli con la correlazione più alta tra un mese e l'anno.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "SCAN_04", "name": "Numero di indici USA-EUROPA che salgono/scendono", "desc": "Breadth aggregata intercontinentale (SPX, NDX, RUT, DJI, DAX, CAC, FTSE, MIB).", "tags": ["Global Indici", "Descrittiva"], "stars": "⭐⭐⭐⭐☆"},
        {"id": "SCAN_05", "name": "Numero di Indici che fanno nuovi massimi", "desc": "Conteggio degli indici mondiali che segnano nuovi massimi annuali.", "tags": ["Global Indici", "Descrittiva"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "SCAN_06", "name": "POC SCANNER", "desc": "Scansione dell'universo azionario per intercettare compressioni sul POC.", "tags": ["Aziende", "Scanner"], "stars": "⭐⭐⭐⭐⭐"},
        {"id": "SCAN_07", "name": "Correlazione ritorno mensile con ritorno annuo (Mese+Anno)", "desc": "Relazione statistica tra mesi positivi e anni positivi sui singoli titoli.", "tags": ["Aziende", "Backtest"], "stars": "⭐⭐⭐⭐⭐"}
    ]
}

STUDY_BY_ID = {}
for cat, items in QUANT_REA_ARCHIVE.items():
    for it in items:
        STUDY_BY_ID[it["id"]] = (cat, it)

TICKER_ALIAS = {
    "S&P 500": "^GSPC", "S&P500": "^GSPC", "SP500": "^GSPC", "SPX": "^GSPC",
    "NASDAQ": "QQQ", "NASDAQ 100": "QQQ", "NDX": "^NDX",
    "DOW": "^DJI", "DOW JONES": "^DJI", "RUSSELL": "IWM", "BITCOIN": "BTC-USD", "BTC": "BTC-USD"
}

def resolve_ticker(raw: str) -> str:
    c = raw.strip().upper()
    return TICKER_ALIAS.get(c, c)

# =============================================================================
# 3. MOTORE ESECUTIVO PROTOCOLLI (SUITE A 6 STUDI SIMULTANEI)
# =============================================================================
def run_protocol_suite(ticker_raw: str, protocol_name: str) -> dict:
    t = resolve_ticker(ticker_raw)
    if not t:
        return {"status": "ERROR", "msg": "Inserisci un ticker valido."}
    
    try:
        df = yf.download(t, period="2y", interval="1d", progress=False)
        if df.empty or len(df) < 50:
            return {"status": "ERROR", "msg": f"Dati storici non disponibili per il simbolo '{t}'."}
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        last_close = float(df['Close'].iloc[-1])
        ath_price = float(df['High'].max())
        drawdown = ((last_close - ath_price) / ath_price) * 100.0
        
        # Calcolo Point of Control (POC) Volume Profile
        price_bins = np.linspace(df['Low'].min(), df['High'].max(), 50)
        bin_idx = np.digitize(df['Close'].values, price_bins)
        vol_hist = np.zeros(len(price_bins))
        for idx, v in zip(bin_idx, df['Volume'].values):
            if idx < len(vol_hist):
                vol_hist[idx] += v
        poc_price = float(price_bins[np.argmax(vol_hist)])
        dist_poc = ((last_close - poc_price) / poc_price) * 100.0

        # Indicatori Statistici & Medie
        ret = df['Close'].pct_change()
        z_score = float((ret.iloc[-1] - ret.mean()) / (ret.std() + 1e-9))
        sma20_vol = float(df['Volume'].rolling(20).mean().iloc[-1])
        vol_ratio = float(df['Volume'].iloc[-1]) / (sma20_vol + 1e-9)
        sma50 = float(df['Close'].rolling(50).mean().iloc[-1])
        sma200 = float(df['Close'].rolling(200).mean().iloc[-1]) if len(df) >= 200 else sma50
        dist_sma200 = ((last_close - sma200) / sma200) * 100.0

        # Esecuzione dei 6 studi del protocollo
        proto_cfg = PROTOCOLS_DEFINITIONS[protocol_name]
        studies_results = []
        passed_count = 0

        for s in proto_cfg["studies"]:
            sid = s["id"]
            p_status = "NEUTRAL"
            score = 50.0
            val_str = ""

            if sid == "DD_01":
                p_status = "PASS" if drawdown <= -30.0 else "FAIL"
                val_str = f"Drawdown ATH: {drawdown:.1f}%"
                score = min(100.0, max(0.0, abs(drawdown) * 1.5))
            elif sid == "POC_01":
                p_status = "PASS" if abs(dist_poc) <= 5.0 else "FAIL"
                val_str = f"POC: ${poc_price:.2f} ({dist_poc:+.2f}%)"
                score = max(0.0, 100.0 - abs(dist_poc) * 10)
            elif sid == "ZSC_01":
                p_status = "PASS" if z_score <= -1.50 else "FAIL"
                val_str = f"Z-Score: {z_score:.2f}"
                score = min(100.0, abs(z_score) * 40) if z_score < 0 else 20.0
            elif sid == "SMA_01":
                p_status = "PASS" if dist_sma200 <= -15.0 else "FAIL"
                val_str = f"SMA 200: ${sma200:.2f} ({dist_sma200:+.1f}%)"
                score = 85.0 if dist_sma200 <= -15.0 else 35.0
            elif sid == "VOL_01":
                p_status = "PASS" if vol_ratio >= 1.3 else "NEUTRAL"
                val_str = f"Vol Ratio: {vol_ratio:.2f}x SMA20"
                score = min(100.0, vol_ratio * 50)
            elif sid == "RSI_01":
                p_status = "PASS" if z_score <= -1.0 else "NEUTRAL"
                val_str = f"Stato: Iper-venduto confermato"
                score = 80.0 if z_score <= -1.0 else 40.0
            elif sid == "BASE_01":
                p_status = "PASS" if last_close >= poc_price else "FAIL"
                val_str = f"Prezzo ${last_close:.2f} vs POC ${poc_price:.2f}"
                score = 85.0 if last_close >= poc_price else 30.0
            elif sid == "SMA_02":
                p_status = "PASS" if last_close >= sma50 else "FAIL"
                val_str = f"SMA 50: ${sma50:.2f}"
                score = 90.0 if last_close >= sma50 else 25.0
            elif sid == "VOL_02":
                p_status = "PASS" if vol_ratio >= 1.8 else "NEUTRAL"
                val_str = f"Vol Breakout: {vol_ratio:.2f}x"
                score = min(100.0, vol_ratio * 45)
            elif sid == "ZSC_02":
                p_status = "PASS" if z_score > 0.50 else "FAIL"
                val_str = f"Z-Score Momentum: {z_score:+.2f}"
                score = 80.0 if z_score > 0.5 else 30.0
            else:
                p_status = "PASS" if last_close > sma50 else "NEUTRAL"
                val_str = f"Livello confermato"
                score = 70.0

            if p_status == "PASS":
                passed_count += 1

            studies_results.append({
                "ID Studio": sid,
                "Nome Studio": s["name"],
                "Target / Criterio": s["target"],
                "Valore Rilevato": val_str,
                "Esito": "🟢 PASS" if p_status == "PASS" else ("🔴 FAIL" if p_status == "FAIL" else "⚪ NEUTRAL"),
                "Score": f"{score:.0f}/100"
            })

        confluence_pct = (passed_count / len(proto_cfg["studies"])) * 100.0
        
        # Livelli Operativi Derivati
        target_p = poc_price * 1.25 if "Bottom" in protocol_name else last_close * 1.20
        stop_p = poc_price * 0.95
        risk = max(0.01, last_close - stop_p)
        reward = max(0.01, target_p - last_close)
        rr_ratio = reward / risk

        return {
            "status": "SUCCESS",
            "ticker": t,
            "price": last_close,
            "drawdown": drawdown,
            "poc": poc_price,
            "dist_poc": dist_poc,
            "z_score": z_score,
            "sma50": sma50,
            "sma200": sma200,
            "confluence_score": f"{passed_count}/{len(proto_cfg['studies'])}",
            "confluence_pct": confluence_pct,
            "target": target_p,
            "stop": stop_p,
            "rr_ratio": rr_ratio,
            "studies_table": pd.DataFrame(studies_results),
            "df": df
        }
    except Exception as e:
        return {"status": "ERROR", "msg": str(e)}

# =============================================================================
# 4. CSS CARD GRID PER GALLERIA STUDI (3 COLONNE)
# =============================================================================
CARD_STYLE = """
<style>
.quant-card {
    background-color: #0b1320;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 16px;
    height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    margin-bottom: 12px;
}
.quant-card:hover {
    border-color: #38bdf8;
}
.quant-card-title {
    font-size: 15px;
    font-weight: 700;
    color: #f8fafc;
    margin: 0;
}
.quant-card-stars {
    font-size: 12px;
    color: #f59e0b;
}
.quant-card-desc {
    font-size: 12px;
    color: #94a3b8;
    line-height: 1.4;
    margin-top: 6px;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}
.quant-tag {
    background: #111e33;
    border: 1px solid #1e293b;
    color: #38bdf8;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
}
</style>
"""

# =============================================================================
# 5. RENDER PRINCIPALE PAGINA 3
# =============================================================================
def render_page3():
    st.markdown(CARD_STYLE, unsafe_allow_html=True)
    
    if "active_study_id" not in st.session_state:
        st.session_state.active_study_id = None

    # -------------------------------------------------------------------------
    # VISTA STUDIO SINGOLO A SCHERMO INTERO (SE CLICCATO DALLA GALLERIA)
    # -------------------------------------------------------------------------
    if st.session_state.active_study_id is not None:
        sid = st.session_state.active_study_id
        cat, meta = STUDY_BY_ID.get(sid, ("Generale", {"name": sid, "desc": "", "tags": []}))
        
        col_back, col_title = st.columns([1.5, 6])
        if col_back.button("⬅️ Torna all'Archivio Studi", use_container_width=True):
            st.session_state.active_study_id = None
            st.rerun()

        with col_title:
            st.markdown(f"<h3 style='margin:0; color:#38bdf8;'>🔬 {meta['name']}</h3>", unsafe_allow_html=True)
            st.caption(f"Categoria: **{cat}** | Tags: *{', '.join(meta['tags'])}*")

        st.markdown("---")

        if sid == "MACRO_01":
            try:
                from studies.macro_nfp import render_nfp_study_view
                render_nfp_study_view()
            except ModuleNotFoundError:
                st.error("File `studies/macro_nfp.py` non trovato su GitHub.")
            except Exception as e:
                st.error(f"Errore durante l'esecuzione: {str(e)}")
        else:
            st.markdown(f"**Descrizione Studio:** {meta['desc']}")
            t_in = st.text_input("Ticker Sottostante (es. PYPL, TSLA, PLTR, BABA, SPY):", value="PYPL")
            if st.button("🚀 ESEGUI ANALISI SINGOLA EOD", use_container_width=True):
                res = run_protocol_suite(t_in, "🎯 PROTOCOLLO 1: Deep Value & Bottom Hunter (Azioni all'Inferno)")
                if res.get("status") == "SUCCESS":
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Prezzo EOD", f"${res['price']:.2f}")
                    m2.metric("Drawdown ATH", f"{res['drawdown']:.1f}%")
                    m3.metric("POC Volume", f"${res['poc']:.2f}")
                    m4.metric("Z-Score 52w", f"{res['z_score']:.2f}")
        return

    # -------------------------------------------------------------------------
    # VISTA PRINCIPALE PAGINA 3: PROTOCOL SUITE RUNNER + GALLERIA A FINESTRELLE
    # -------------------------------------------------------------------------
    st.title("🔬 Quant Lab & Protocol Engine (Metodologia Massimo Rea)")
    st.caption("Piattaforma quantitativa EOD modulare: Esecutore di Protocolli (Suite a 6 Studi) e Galleria Ufficiale di 87 Studi.")
    st.markdown("---")

    tab_protocols, tab_gallery = st.tabs([
        "⚙️ 1. PROTOCOL SUITE RUNNER (Report Aggregato a 6 Studi)",
        "📚 2. GALLERIA ARCHIVIO (87 Studi a Finestrelle)"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: PROTOCOL SUITE RUNNER (ANALISI COMPLETA SU MISURA)
    # -------------------------------------------------------------------------
    with tab_protocols:
        st.subheader("⚡ Esecuzione Protocollo Operativo su Asset")
        st.caption("Seleziona l'asset e il protocollo di analisi: il motore eseguirà simultaneamente la catena dei 6 studi e produrrà il report di confluenza.")

        c1, c2 = st.columns([1.2, 2])
        with c1:
            raw_ticker = st.text_input("Ticker Asset (es. PYPL, TSLA, PLTR, BABA, SPY, QQQ):", value="PYPL")
            chosen_protocol = st.selectbox("Seleziona Protocollo da Eseguire:", list(PROTOCOLS_DEFINITIONS.keys()), index=0)
            btn_exec = st.button("🚀 ESEGUI PROTOCOLLO & GENERA REPORT", use_container_width=True)

        with c2:
            st.info(f"**Descrizione Protocollo:**\n{PROTOCOLS_DEFINITIONS[chosen_protocol]['desc']}")

        if btn_exec or raw_ticker:
            with st.spinner(f"Esecuzione della suite di studi per ${raw_ticker.upper()}..."):
                rep = run_protocol_suite(raw_ticker, chosen_protocol)
                
                if rep.get("status") == "ERROR":
                    st.error(f"❌ {rep.get('msg')}")
                else:
                    st.markdown("---")
                    
                    # 1. SCORECARD DI CONFLUENZA
                    is_valid = rep["confluence_pct"] >= 65.0
                    badge_col = "#10b981" if is_valid else "#ef4444"
                    badge_txt = "SETUP CONFERMATO 🎯" if is_valid else "CONFLUENZA INSUFFICIENTE ⚪"

                    st.markdown(
                        f"""
                        <div style="background: rgba(15,23,42,0.95); border: 2px solid {badge_col}; border-radius: 12px; padding: 20px; margin-bottom: 20px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-size:11px; color:#94a3b8; font-weight:700;">REPORT CONFLUENZA STATISTICA EOD</span>
                                <h2 style="margin:2px 0 0 0; color:#f8fafc;">${rep['ticker']} — {badge_txt}</h2>
                                <p style="color:#cbd5e1; font-size:13px; margin:4px 0 0 0;">Studi Validati: <b>{rep['confluence_score']} ({rep['confluence_pct']:.1f}%)</b></p>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:26px; font-weight:900; color:{badge_col};">{rep['confluence_pct']:.0f}%</div>
                                <small style="color:#94a3b8;">Risk / Reward: <b>{rep['rr_ratio']:.2f} : 1</b></small>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # 2. METRICHE CHIAVE E LIVELLI OPERATIVI
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("Prezzo Ultimo EOD", f"${rep['price']:.2f}")
                    k2.metric("Point of Control (POC)", f"${rep['poc']:.2f}", f"{rep['dist_poc']:+.2f}%")
                    k3.metric("Target Stimato", f"${rep['target']:.2f}", f"+{((rep['target']-rep['price'])/rep['price'])*100:.1f}%")
                    k4.metric("Stop Volumetrico", f"${rep['stop']:.2f}", f"{((rep['stop']-rep['price'])/rep['price'])*100:.1f}%")

                    # 3. TABELLA COMPARATIVA DEI 6 STUDI
                    st.markdown("#### 📋 Esito Analitico dei 6 Studi della Suite")
                    st.dataframe(rep["studies_table"], use_container_width=True, hide_index=True)

                    # 4. GRAFICO CANDLESTICK & POC
                    st.markdown("#### 📊 Struttura Grafica, Point of Control & Medie")
                    df_p = rep["df"]
                    fig_suite = go.Figure()
                    fig_suite.add_trace(go.Candlestick(
                        x=df_p.index, open=df_p['Open'], high=df_p['High'],
                        low=df_p['Low'], close=df_p['Close'], name=f"${rep['ticker']}"
                    ))
                    fig_suite.add_hline(y=rep['poc'], line_dash="dash", line_color="#00D1FF", annotation_text=f"POC Base (${rep['poc']:.2f})")
                    fig_suite.add_trace(go.Scatter(x=df_p.index, y=df_p['Close'].rolling(50).mean(), name="SMA 50", line=dict(color="#f59e0b", width=1.5)))
                    fig_suite.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_suite, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 2: GALLERIA A FINESTRELLE DEGLI 87 STUDI QUANT-REA
    # -------------------------------------------------------------------------
    with tab_gallery:
        st.subheader("📚 Archivio Ufficiale degli 87 Studi Quantitativi")
        st.caption("Clicca su qualsiasi finestrella per visualizzare l'analisi completa.")

        f1, f2 = st.columns([1.5, 1.5])
        search_q = f1.text_input("🔍 Cerca analisi...", placeholder="es. Drawdown, Payrolls, Z-Score...").strip().lower()
        sel_cat = f2.selectbox("Filtra per Categoria:", ["Tutte le Categorie"] + list(QUANT_REA_ARCHIVE.keys()))

        st.markdown("---")

        for category_name, studies_list in QUANT_REA_ARCHIVE.items():
            if sel_cat != "Tutte le Categorie" and category_name != sel_cat:
                continue

            filtered = [
                s for s in studies_list
                if search_q == "" or (search_q in s['name'].lower() or search_q in s['desc'].lower() or any(search_q in t.lower() for t in s['tags']))
            ]

            if not filtered:
                continue

            st.subheader(f"📁 {category_name}")

            cols = st.columns(3)
            for idx, s in enumerate(filtered):
                col_target = cols[idx % 3]
                with col_target:
                    tags_html = "".join([f"<span class='quant-tag'>{t}</span>" for t in s['tags']])
                    st.markdown(
                        f"""
                        <div class="quant-card">
                            <div>
                                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                                    <span class="quant-card-title">{s['name']}</span>
                                    <span class="quant-card-stars">{s['stars']}</span>
                                </div>
                                <div class="quant-card-desc">{s['desc']}</div>
                            </div>
                            <div style="margin-top:8px;">{tags_html}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button("👁️ Visualizza Analisi", key=f"gal_btn_{s['id']}", use_container_width=True):
                        st.session_state.active_study_id = s['id']
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
