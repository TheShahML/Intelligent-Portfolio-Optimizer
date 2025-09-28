"""
Download comprehensive market data from WRDS
Creates static dataset with S&P 500 + NASDAQ + Top ETFs for 2000-2024

Run this script once to create the data/market_universe_2000_2024.csv file
that can be used for portfolio optimization without requiring WRDS connection.
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
    """Get current S&P 500 constituents"""
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
    """Get major NASDAQ stocks - improved query"""
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
    LIMIT 500
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

def get_top_etfs() -> List[str]:
    """Get list of top 75 ETFs to include"""
    print("Adding top ETFs...")
    
    top_etfs = [
        # Broad Market ETFs
        'SPY', 'VTI', 'VOO', 'IVV', 'VEA', 'IEFA', 'VWO', 'IEMG', 'EEM', 'VTV',
        'VUG', 'IWM', 'IJR', 'VXF', 'VO', 'IJH', 'MDY', 'VB', 'IWF', 'IWD',
        
        # Sector ETFs
        'XLK', 'XLF', 'XLV', 'XLI', 'XLE', 'XLB', 'XLP', 'XLY', 'XLU', 'XLRE',
        'VGT', 'VFH', 'VHT', 'VIS', 'VDE', 'VAW', 'VDC', 'VCR', 'VPU', 'VNQ',
        
        # Bond ETFs
        'AGG', 'BND', 'VGIT', 'VGSH', 'VGLT', 'TLT', 'IEF', 'SHY', 'LQD', 'HYG',
        'VTEB', 'MUB', 'IGSB', 'IGIB', 'IGLB', 'TIP', 'SCHZ', 'GOVT', 'SCHO', 'SCHR',
        
        # International ETFs
        'EFA', 'VEU', 'ACWI', 'VXUS', 'IXUS', 'FTEC', 'FEZ', 'EWJ', 'EWG', 'EWU',
        
        # Specialty/Factor ETFs
        'QQQ', 'DIA', 'GLD', 'SLV', 'USO', 'TNA', 'TQQQ', 'SQQQ', 'SPXL', 'SPXS',
        'VYM', 'NOBL', 'DGRO', 'HDV', 'SCHD', 'DVY', 'VIG', 'MTUM', 'QUAL', 'USMV'
    ]
    
    print(f"Added {len(top_etfs)} ETFs")
    return top_etfs

def fetch_return_data(db, tickers: List[str], start_date: str = '2000-01-01', end_date: str = '2024-12-31'):
    """Fetch monthly return data for all tickers"""
    
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
    """Save data to CSV file in the correct data directory"""
    
    if output_path is None:
        # Get the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the project root, then into data folder
        project_root = os.path.dirname(script_dir)
        output_path = os.path.join(project_root, 'data', 'market_universe_2000_2024.csv')
    
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
    """Main function to orchestrate the data download process"""
    start_time = time.time()
    
    print("=== WRDS Market Data Download Script ===")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Connect to WRDS
    db = connect_to_wrds()
    if db is None:
        print("Cannot proceed without WRDS connection. Exiting.")
        return False
    
    try:
        # Step 2: Gather all tickers
        print("\n--- Gathering ticker lists ---")
        sp500_tickers = get_sp500_tickers(db)
        nasdaq_tickers = get_nasdaq_tickers(db)
        etf_tickers = get_top_etfs()
        
        # Combine and deduplicate
        all_tickers = list(set(sp500_tickers + nasdaq_tickers + etf_tickers))
        print(f"\nTotal unique tickers to download: {len(all_tickers)}")
        
        # Step 3: Fetch return data
        print("\n--- Starting data download ---")
        data = fetch_return_data(db, all_tickers)
        
        if data is None or data.empty:
            print("No data was retrieved. Exiting.")
            return False
        
        # Step 4: Save data
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