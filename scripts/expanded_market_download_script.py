"""
Download expanded market data from WRDS
Creates dataset with S&P 500 + NASDAQ + Russell 2000 + More ETFs for 2000-2024

This expands the working market_universe script to get ~2000-3000 stocks
while keeping the exact same proven approach that was working.
"""

import wrds
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
from typing import List

def connect_to_wrds():
    """Establish WRDS connection"""
    try:
        print("Connecting to WRDS...")
        db = wrds.Connection()
        print("WRDS connection successful!")
        return db
    except Exception as e:
        print(f"WRDS connection failed: {e}")
        return None

def get_sp500_tickers(db) -> List[str]:
    """Get current S&P 500 constituents - EXACT SAME as working script"""
    print("Fetching S&P 500 constituents...")
    
    query = """
    SELECT DISTINCT ticker
    FROM crsp.msenames 
    WHERE ticker IN (
        SELECT ticker 
        FROM crsp.dsp500list 
        WHERE ending IS NULL OR ending >= '2020-01-01'
    )
    AND ticker IS NOT NULL
    ORDER BY ticker
    """
    
    try:
        result = db.raw_sql(query)
        tickers = result['ticker'].tolist()
        print(f"Found {len(tickers)} S&P 500 tickers")
        return tickers
    except Exception as e:
        print(f"Error fetching S&P 500: {e}")
        # Fallback to manual list of major S&P 500 stocks
        return ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOG', 'GOOGL', 'META', 'TSLA', 'BRK.A', 'BRK.B',
                'UNH', 'JNJ', 'XOM', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'ABBV',
                'PFE', 'AVGO', 'KO', 'PEP', 'COST', 'WMT', 'TMO', 'MRK', 'BAC', 'NFLX']

def get_nasdaq_tickers(db) -> List[str]:
    """Get major NASDAQ stocks - EXACT SAME as working script"""
    print("Fetching major NASDAQ stocks...")
    
    # Try a simpler, more inclusive query
    query = """
    SELECT DISTINCT ticker
    FROM crsp.msenames 
    WHERE exchcd IN (3, 31, 32, 33)  -- All NASDAQ exchange codes
    AND nameendt >= '2020-01-01'     -- Still active recently
    AND ticker IS NOT NULL
    AND LENGTH(ticker) BETWEEN 1 AND 5
    AND ticker NOT LIKE '%.%'
    AND ticker NOT LIKE '%-%'
    ORDER BY ticker
    LIMIT 1000
    """
    
    try:
        result = db.raw_sql(query)
        tickers = result['ticker'].tolist()
        print(f"Found {len(tickers)} NASDAQ tickers")
        
        # If still getting low numbers, add manual fallback
        if len(tickers) < 100:
            print("Adding manual NASDAQ tickers to supplement...")
            manual_nasdaq = [
                'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOG', 'GOOGL', 'META', 'TSLA', 'AVGO', 'NFLX',
                'ADBE', 'CRM', 'INTC', 'AMD', 'QCOM', 'TXN', 'INTU', 'ISRG', 'CMCSA', 'AMGN',
                'COST', 'CSCO', 'PEP', 'TMUS', 'PYPL', 'SBUX', 'ADI', 'GILD', 'MDLZ', 'REGN',
                'BKNG', 'ADP', 'VRTX', 'FISV', 'CSX', 'ATVI', 'KLAC', 'MRVL', 'ORLY', 'FTNT'
            ]
            # Combine and deduplicate
            all_tickers = list(set(tickers + manual_nasdaq))
            print(f"Total NASDAQ tickers after manual addition: {len(all_tickers)}")
            return all_tickers
            
        return tickers
        
    except Exception as e:
        print(f"NASDAQ query failed: {e}")
        # Fallback to major NASDAQ stocks
        print("Using fallback NASDAQ list...")
        return [
            'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOG', 'GOOGL', 'META', 'TSLA', 'AVGO', 'NFLX',
            'ADBE', 'CRM', 'INTC', 'AMD', 'QCOM', 'TXN', 'INTU', 'ISRG', 'CMCSA', 'AMGN',
            'COST', 'CSCO', 'PEP', 'TMUS', 'PYPL', 'SBUX', 'ADI', 'GILD', 'MDLZ', 'REGN',
            'BKNG', 'ADP', 'VRTX', 'FISV', 'CSX', 'ATVI', 'KLAC', 'MRVL', 'ORLY', 'FTNT',
            'CHTR', 'DXCM', 'MRNA', 'NXPI', 'WDAY', 'TEAM', 'DOCU', 'ZM', 'CRWD', 'OKTA'
        ]

def get_russell_2000_tickers(db) -> List[str]:
    """Get Russell 2000 stocks to add small/mid cap exposure"""
    print("Fetching Russell 2000 stocks...")
    
    # Get small/mid cap stocks from major exchanges
    query = """
    SELECT DISTINCT ticker
    FROM crsp.msenames 
    WHERE exchcd IN (1, 2, 3, 31, 32, 33)  -- All major exchanges
    AND nameendt >= '2020-01-01'           -- Still active recently
    AND ticker IS NOT NULL
    AND LENGTH(ticker) BETWEEN 1 AND 5
    AND ticker NOT LIKE '%.%'
    AND ticker NOT LIKE '%-%'
    AND ticker NOT IN (
        SELECT DISTINCT ticker FROM crsp.msenames 
        WHERE ticker IN (
            SELECT ticker FROM crsp.dsp500list 
            WHERE ending IS NULL OR ending >= '2020-01-01'
        )
    )  -- Exclude S&P 500 stocks
    ORDER BY ticker
    LIMIT 1500
    """
    
    try:
        result = db.raw_sql(query)
        tickers = result['ticker'].tolist()
        print(f"Found {len(tickers)} Russell 2000/small-mid cap tickers")
        return tickers
    except Exception as e:
        print(f"Russell 2000 query failed: {e}")
        # Fallback to manual small/mid cap list
        return get_manual_small_mid_caps()

def get_manual_small_mid_caps() -> List[str]:
    """Manual list of popular small/mid cap stocks"""
    print("Using manual small/mid cap list...")
    
    small_mid_caps = [
        # Popular small/mid caps
        'ROKU', 'ZM', 'DOCU', 'TEAM', 'WDAY', 'NOW', 'SNOW', 'DDOG', 'NET', 'OKTA',
        'ZS', 'CRWD', 'S', 'PLTR', 'U', 'PATH', 'RBLX', 'HOOD', 'COIN', 'SQ',
        'AFRM', 'UPST', 'SOFI', 'OPEN', 'WISH', 'CLOV', 'SPCE', 'LCID', 'RIVN', 'F',
        'GM', 'FORD', 'NIO', 'XPEV', 'LI', 'BABA', 'JD', 'PDD', 'BIDU', 'TME',
        'BILI', 'VIPS', 'WB', 'DIDI', 'GRAB', 'SE', 'SHOP', 'MELI', 'CPNG', 'BEKE',
        'YMM', 'TCOM', 'NTES', 'HTHT', 'VNET', 'MNSO', 'KC', 'YQ', 'TIGR', 'FUTU',
        
        # Mid cap industrials
        'CAT', 'DE', 'DAL', 'UAL', 'LUV', 'AAL', 'JBLU', 'ALK', 'SAVE', 'HA',
        'CHRW', 'EXPD', 'LSTR', 'KNX', 'ARCB', 'JBHT', 'SNDR', 'ODFL', 'SAIA', 'YRC',
        
        # Mid cap healthcare
        'VEEV', 'IQVIA', 'CNC', 'HUM', 'MOH', 'WCG', 'TECH', 'INCY', 'EXAS', 'PTCT',
        'RARE', 'SRPT', 'BMRN', 'ALNY', 'IONS', 'ARWR', 'CRSP', 'EDIT', 'NTLA', 'BEAM',
        
        # Mid cap tech
        'TWLO', 'ESTC', 'WORK', 'FROG', 'SMAR', 'VEEV', 'COUP', 'BILL', 'PCTY', 'ZI',
        'ASAN', 'GTLB', 'BRZE', 'CFLT', 'DOMO', 'FIVN', 'NEWR', 'YEXT', 'PING', 'MIME',
        
        # Mid cap financial
        'ALLY', 'LC', 'UPST', 'AFRM', 'SQ', 'PYPL', 'SOFI', 'HOOD', 'IBKR', 'TREE',
        'ENVA', 'WRLD', 'GH', 'CACC', 'CURO', 'FCFS', 'CSWC', 'GAIN', 'TCPC', 'PSEC',
        
        # REITs and utilities
        'AMT', 'CCI', 'SBAC', 'EQIX', 'DLR', 'PSA', 'EXR', 'CUBE', 'LSI', 'NSA',
        'WPC', 'O', 'STAG', 'PLD', 'EXR', 'AVB', 'EQR', 'UDR', 'CPT', 'MAA'
    ]
    
    print(f"Manual small/mid cap list contains {len(small_mid_caps)} stocks")
    return small_mid_caps

def get_expanded_etfs() -> List[str]:
    """Get expanded list of ETFs - more than original"""
    print("Adding expanded ETF list...")
    
    expanded_etfs = [
        # Original ETFs from working script
        'SPY', 'VTI', 'VOO', 'IVV', 'VEA', 'IEFA', 'VWO', 'IEMG', 'EEM', 'VTV',
        'VUG', 'IWM', 'IJR', 'VXF', 'VO', 'IJH', 'MDY', 'VB', 'IWF', 'IWD',
        'XLK', 'XLF', 'XLV', 'XLI', 'XLE', 'XLB', 'XLP', 'XLY', 'XLU', 'XLRE',
        'VGT', 'VFH', 'VHT', 'VIS', 'VDE', 'VAW', 'VDC', 'VCR', 'VPU', 'VNQ',
        'AGG', 'BND', 'VGIT', 'VGSH', 'VGLT', 'TLT', 'IEF', 'SHY', 'LQD', 'HYG',
        'VTEB', 'MUB', 'IGSB', 'IGIB', 'IGLB', 'TIP', 'SCHZ', 'GOVT', 'SCHO', 'SCHR',
        'EFA', 'VEU', 'ACWI', 'VXUS', 'IXUS', 'FTEC', 'FEZ', 'EWJ', 'EWG', 'EWU',
        'QQQ', 'DIA', 'GLD', 'SLV', 'USO', 'TNA', 'TQQQ', 'SQQQ', 'SPXL', 'SPXS',
        'VYM', 'NOBL', 'DGRO', 'HDV', 'SCHD', 'DVY', 'VIG', 'MTUM', 'QUAL', 'USMV',
        
        # Additional popular ETFs
        'ARKK', 'ARKQ', 'ARKW', 'ARKG', 'ARKF', 'ICLN', 'PBW', 'QCLN', 'WCLD', 'SKYY',
        'ROBO', 'BOTZ', 'FINX', 'HACK', 'CIBR', 'ESPO', 'GAMR', 'NERD', 'HERO', 'UFO',
        'DBA', 'DBC', 'GSG', 'DJP', 'PDBC', 'CORN', 'WEAT', 'SOYB', 'NIB', 'COW',
        'FXE', 'FXY', 'FXB', 'FXF', 'FXC', 'FXA', 'CYB', 'UUP', 'UDN', 'DBV',
        'VNQ', 'VNQI', 'RWR', 'SCHH', 'USRT', 'REZ', 'FREL', 'MORT', 'REM', 'KBWY'
    ]
    
    print(f"Added {len(expanded_etfs)} ETFs")
    return expanded_etfs

def fetch_return_data(db, tickers: List[str], start_date: str = '2000-01-01', end_date: str = '2024-12-31'):
    """Fetch monthly return data for all tickers - EXACT SAME as working script"""
    
    print(f"Fetching monthly returns for {len(tickers)} securities from {start_date} to {end_date}")
    print("This may take 10-15 minutes...")
    
    # Convert tickers to SQL-safe format
    ticker_str = "', '".join(tickers)
    
    query = f"""
    SELECT date, ticker, ret as return
    FROM crsp.msf a
    LEFT JOIN crsp.msenames b ON a.permno = b.permno
    WHERE DATE_TRUNC('month', b.namedt) <= DATE_TRUNC('month', a.date) 
    AND DATE_TRUNC('month', a.date) <= DATE_TRUNC('month', b.nameendt)
    AND a.date BETWEEN '{start_date}' AND '{end_date}'
    AND ticker IN ('{ticker_str}')
    AND ret IS NOT NULL
    ORDER BY date, ticker
    """
    
    try:
        print("Executing WRDS query...")
        data = db.raw_sql(query)
        
        if data.empty:
            print("No data returned!")
            return None
            
        print(f"Retrieved {len(data)} observations")
        
        # Clean and process data
        data['date'] = pd.to_datetime(data['date'])
        data = data.drop_duplicates(subset=['date', 'ticker'], keep='first')
        
        # Add metadata columns (placeholder for now)
        data['market_cap'] = np.nan  # Could add market cap data later
        data['sector'] = 'Unknown'   # Could add sector classification later
        
        print(f"Final dataset: {len(data)} observations across {data['ticker'].nunique()} unique tickers")
        print(f"Date range: {data['date'].min()} to {data['date'].max()}")
        
        return data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def save_data(data, output_path: str = None):
    """Save data to CSV file - EXACT SAME as working script"""
    
    if output_path is None:
        # Get the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the project root, then into data folder
        project_root = os.path.dirname(script_dir)
        output_path = os.path.join(project_root, 'data', 'expanded_market_universe_2000_2024.csv')
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        print(f"Saving data to {output_path}...")
        data.to_csv(output_path, index=False)
        
        # Print file info
        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        print(f"Data saved successfully!")
        print(f"File location: {output_path}")
        print(f"File size: {file_size:.1f} MB")
        print(f"Records: {len(data)}")
        print(f"Unique tickers: {data['ticker'].nunique()}")
        
        return True
        
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def main():
    """Main function - EXACT SAME structure as working script"""
    start_time = time.time()
    
    print("=== EXPANDED WRDS Market Data Download Script ===")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Connect to WRDS
    db = connect_to_wrds()
    if db is None:
        print("Cannot proceed without WRDS connection. Exiting.")
        return False
    
    try:
        # Step 2: Gather all tickers (expanded from original)
        print("\n--- Gathering ticker lists ---")
        sp500_tickers = get_sp500_tickers(db)
        nasdaq_tickers = get_nasdaq_tickers(db)
        russell_tickers = get_russell_2000_tickers(db)  # NEW: adds small/mid caps
        etf_tickers = get_expanded_etfs()               # EXPANDED: more ETFs
        
        # Combine and deduplicate
        all_tickers = list(set(sp500_tickers + nasdaq_tickers + russell_tickers + etf_tickers))
        print(f"\nTotal unique tickers to download: {len(all_tickers)}")
        print(f"  - S&P 500: {len(sp500_tickers)}")
        print(f"  - NASDAQ: {len(nasdaq_tickers)}")
        print(f"  - Russell 2000/Small-Mid: {len(russell_tickers)}")
        print(f"  - ETFs: {len(etf_tickers)}")
        
        # Step 3: Fetch return data (EXACT SAME)
        print("\n--- Starting data download ---")
        data = fetch_return_data(db, all_tickers)
        
        if data is None or data.empty:
            print("No data was retrieved. Exiting.")
            return False
        
        # Step 4: Save data (EXACT SAME)
        print("\n--- Saving data ---")
        success = save_data(data)
        
        if success:
            elapsed_time = time.time() - start_time
            print(f"\n=== Download Complete! ===")
            print(f"Total time: {elapsed_time/60:.1f} minutes")
            print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print("Failed to save data.")
            return False
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
        
    finally:
        # Close WRDS connection
        if db:
            db.close()
            print("WRDS connection closed.")

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nScript completed with errors.")
        exit(1)
    else:
        print("\nScript completed successfully!")