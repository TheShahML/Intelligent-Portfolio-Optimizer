# examples/assignment_default_demo.py
"""
Assignment Default Portfolio Optimization Demo

This script demonstrates the full capabilities of the quantitative portfolio optimizer
using the original project_2.py default settings with 20 blue-chip stocks.

Features demonstrated:
- 14-year rolling window backtest (2010-2024)
- Sample covariance vs Ledoit-Wolf shrinkage comparison
- Long/short portfolio optimization
- Professional visualization suite
- Performance metrics analysis

Prerequisites:
- WRDS account with valid credentials
- All required packages installed (see requirements.txt)

Usage:
    python examples/comprehensive_demo.py

Expected Runtime: 2-3 minutes
Expected Output: 3 popup windows with visualizations + console performance summary
"""

import sys
import os

# Add source directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'source'))

from portfolio.optimizer import PortfolioOptimizer
from portfolio.data_handler import DataHandler
from portfolio.static_data_handler import StaticDataHandler
from utils.plotting import PortfolioPlotter
import matplotlib.pyplot as plt

def main():
    """
    Run comprehensive portfolio optimization demo
    """
    
    print("Quantitative Portfolio Optimizer - Comprehensive Demo")
    print("=" * 60)
    print("This demo replicates the original project_2.py analysis")
    print("with enhanced class-based architecture and AI capabilities.")
    print()
    
    # Get the 20 default blue-chip tickers
    data_handler = DataHandler()
    default_tickers = data_handler.get_default_tickers()
    
    print(f"Portfolio Universe: {len(default_tickers)} Blue-Chip Stocks")
    print("Technology:", default_tickers[:5])
    print("Financial: ", default_tickers[5:9])
    print("Healthcare:", default_tickers[9:12])
    print("Consumer:  ", default_tickers[12:16])
    print("Industrial:", default_tickers[16:19])
    print("Energy:    ", default_tickers[19:])
    print()
    
    # Configure optimizer with original project_2.py defaults
    optimizer = PortfolioOptimizer(
        tickers=default_tickers,
        start_year=2010,              # 14-year analysis period
        end_year=2024,                
        estimation_window=36,         # 3-year rolling window
        constraints={
            'min_weight': -1.0,       # Allow full short positions
            'max_weight': 1.0,        # No position size limits
            'allow_short': True,      # Enable long/short strategies
            'long_only': False        
        },
        risk_free_rate=0.042,         # 4.2% annual risk-free rate
        coverage_params={
            'min_observations': 36,   # Require full estimation window
            'max_missing_pct': 0.10   # Allow up to 10% missing data
        }
    )
    
    print("Configuration (Original Project_2.py Settings):")
    print(f"  Analysis Period:     2010-2024 (14 years)")
    print(f"  Estimation Window:   36 months")
    print(f"  Position Limits:     -100% to +100% (shorts allowed)")
    print(f"  Risk-Free Rate:      4.2% annually")
    print(f"  Data Quality:        Max 10% missing data allowed")
    print()
    
    print("Connecting to WRDS and running optimization...")
    print("This may take 2-3 minutes for the full analysis...")
    
    try:
        # Execute complete analysis
        results = optimizer.run_complete_analysis()
        
        if results['success']:
            print_results(results)
            generate_visualizations(results, optimizer)
            
        else:
            print("Analysis failed:")
            for error in results['errors']:
                print(f"  - {error}")
                
    except Exception as e:
        print(f"Critical error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure WRDS credentials are configured: python -c 'import wrds; wrds.Connection()'")
        print("2. Check internet connection")
        print("3. Verify all packages are installed: pip install -r requirements.txt")
        
    print("\nDemo completed!")

def print_results(results):
    """Print formatted analysis results"""
    
    print("Analysis completed successfully!")
    print()
    
    perf = results['performance_metrics']
    if 'sample' in perf and 'lw' in perf:
        print("PERFORMANCE COMPARISON")
        print("=" * 55)
        
        print(f"{'METRIC':<25} {'SAMPLE':<12} {'LEDOIT-WOLF':<12} {'DIFFERENCE'}")
        print("-" * 55)
        
        metrics = [
            ('Total Return', 'total_return', '.1%'),
            ('Annualized Return', 'annualized_return', '.2%'),
            ('Annualized Volatility', 'annualized_volatility', '.2%'),
            ('Sharpe Ratio', 'sharpe_ratio', '.3f'),
            ('Sortino Ratio', 'sortino_ratio', '.3f'),
            ('Max Drawdown', 'max_drawdown', '.2%'),
            ('Win Rate', 'win_rate', '.1%'),
            ('Best Month', 'best_month', '.2%'),
            ('Worst Month', 'worst_month', '.2%')
        ]
        
        for name, key, fmt in metrics:
            sample_val = perf['sample'].get(key, 0)
            lw_val = perf['lw'].get(key, 0)
            diff = lw_val - sample_val
            
            # Format values then align
            sample_str = f"{sample_val:{fmt}}"
            lw_str = f"{lw_val:{fmt}}"
            diff_str = f"{diff:{fmt}}"
            
            print(f"{name:<25} {sample_str:<12} {lw_str:<12} {diff_str}")
        
        # Determine winner
        sample_sharpe = perf['sample']['sharpe_ratio']
        lw_sharpe = perf['lw']['sharpe_ratio']
        
        print()
        if lw_sharpe > sample_sharpe:
            improvement = (lw_sharpe - sample_sharpe) / sample_sharpe * 100
            print(f"WINNER: Ledoit-Wolf Shrinkage (+{improvement:.1f}% Sharpe improvement)")
            print("The shrinkage estimator successfully reduced estimation error")
        else:
            improvement = (sample_sharpe - lw_sharpe) / lw_sharpe * 100 if lw_sharpe != 0 else 0
            print(f"WINNER: Sample Covariance (+{improvement:.1f}% Sharpe improvement)")
            print("Sample covariance performed better in this period")
            
    # Analysis summary
    print()
    print("BACKTEST SUMMARY")
    print("-" * 25)
    print(f"Total periods analyzed: {len(results['backtest_results'])}")
    print(f"Valid tickers used: {len(results['config']['final_tickers'])}")
    print(f"Date range: {results['backtest_results'].index[0].strftime('%Y-%m')} to {results['backtest_results'].index[-1].strftime('%Y-%m')}")
    print()

def generate_visualizations(results, optimizer):
    """Generate and display all visualizations"""
    
    print("Generating visualizations...")
    print("Three popup windows will appear:")
    print("1. Performance Dashboard - Comprehensive analysis overview")
    print("2. Efficient Frontier - Risk-return relationship with CAL")
    print("3. Summary Tables - Portfolio weights and metrics")
    print()
    
    plotter = PortfolioPlotter(style='modern')
    
    try:
        # 1. Performance Dashboard
        print("Creating performance dashboard...")
        fig1 = plotter.create_performance_dashboard(
            results['backtest_results'],
            results['portfolio_weights'], 
            results['performance_metrics']
        )
        plt.figure(fig1.number)
        plt.show(block=False)
        
        # 2. Efficient Frontier with Capital Allocation Line
        print("Creating efficient frontier...")
        fig2 = plotter.plot_efficient_frontier_comparison(
            optimizer.returns_data,
            results['config']
        )
        plt.figure(fig2.number)
        plt.show(block=False)
        
        # 3. Summary Tables
        print("Creating summary tables...")
        fig3 = plotter.create_summary_table(
            results['portfolio_weights'],
            results['performance_metrics'],
            results['config']['final_tickers']
        )
        plt.figure(fig3.number)
        plt.show(block=False)
        
        # Keep all windows open
        plt.show(block=True)
        
        print("All visualizations displayed!")
        print()
        print("Key Insights from Charts:")
        print("- Dashboard shows rolling window performance evolution")
        print("- Efficient frontier demonstrates diversification benefits")
        print("- Summary tables provide detailed portfolio composition")
        
    except Exception as e:
        print(f"Visualization error: {e}")
        print("The analysis completed successfully, but charts could not be generated.")

if __name__ == "__main__":
    main()
