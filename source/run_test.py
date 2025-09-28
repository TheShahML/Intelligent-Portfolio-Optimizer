# test_original_defaults.py - Using exact project_2.py default values
import sys
sys.path.append('source')

from portfolio.optimizer import PortfolioOptimizer
from portfolio.data_handler import DataHandler
from utils.plotting import PortfolioPlotter
import matplotlib.pyplot as plt

print("Portfolio Optimization with Original Project_2.py Defaults")
print("=" * 60)

# Get the exact 20 default tickers from your original code
data_handler = DataHandler()
default_tickers = data_handler.get_default_tickers()

print(f"Using original 20 default tickers:")
for i, ticker in enumerate(default_tickers):
    if i % 5 == 0:
        print()
    print(f"{ticker:<6}", end="")
print("\n")

# Use EXACT original defaults from project_2.py
optimizer = PortfolioOptimizer(
    tickers=default_tickers,
    start_year=2010,              # Original default
    end_year=2024,                # Original default  
    estimation_window=36,         # Original default
    constraints={
        'min_weight': -1.0,       # Original: allowed full shorts
        'max_weight': 1.0,        # Original: no max constraint
        'allow_short': True,      # Original: shorts allowed
        'long_only': False        # Original: not long-only
    },
    risk_free_rate=0.042,         # Original: 4.2%
    coverage_params={
        'min_observations': 36,   # Original: same as estimation window
        'max_missing_pct': 0.10   # Original: 10%
    }
)

print("Configuration (original project_2.py defaults):")
print(f"Period: 2010-2024 (14 years)")
print(f"Estimation window: 36 months")
print(f"Weight range: [-100%, +100%] (shorts allowed)")
print(f"Risk-free rate: 4.2%")
print(f"Max missing data: 10%")

print("\nRunning analysis with original settings...")

try:
    results = optimizer.run_complete_analysis()
    
    if results['success']:
        print("Analysis completed successfully!")
        
        # Display detailed results
        perf = results['performance_metrics']
        if 'sample' in perf and 'lw' in perf:
            print(f"\nPERFORMANCE RESULTS (Original Settings):")
            print("=" * 55)
            
            print(f"{'METRIC':<25} {'SAMPLE':<12} {'LEDOIT-WOLF':<12} {'DIFF'}")
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
                
                # Format the values first, then align them
                sample_str = f"{sample_val:{fmt}}"
                lw_str = f"{lw_val:{fmt}}"
                diff_str = f"{diff:{fmt}}"
                
                print(f"{name:<25} {sample_str:<12} {lw_str:<12} {diff_str}")
            
            # Winner analysis
            sample_sharpe = perf['sample']['sharpe_ratio']
            lw_sharpe = perf['lw']['sharpe_ratio']
            
            if lw_sharpe > sample_sharpe:
                improvement = (lw_sharpe - sample_sharpe) / sample_sharpe * 100
                print(f"\nWINNER: Ledoit-Wolf (+{improvement:.1f}% Sharpe improvement)")
            else:
                improvement = (sample_sharpe - lw_sharpe) / lw_sharpe * 100 if lw_sharpe != 0 else 0
                print(f"\nWINNER: Sample Covariance (+{improvement:.1f}% Sharpe improvement)")
                
        # Backtest summary
        print(f"\nBACKTEST SUMMARY:")
        print(f"Total periods: {len(results['backtest_results'])}")
        print(f"Valid tickers: {len(results['config']['final_tickers'])}")
        print(f"Analysis span: {results['backtest_results'].index[0].strftime('%Y-%m')} to {results['backtest_results'].index[-1].strftime('%Y-%m')}")
        
        # Generate visualizations
        print(f"\nGenerating visualizations...")
        
        plotter = PortfolioPlotter(style='modern')
        
        # 1. Performance Dashboard
        print("Creating performance dashboard...")
        fig1 = plotter.create_performance_dashboard(
            results['backtest_results'],
            results['portfolio_weights'], 
            results['performance_metrics']
        )
        plt.figure(fig1.number)
        plt.show(block=False)
        
        # 2. Efficient Frontier (with black CAL)
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
        print("This matches your original project_2.py configuration.")
        
    else:
        print("Analysis failed:")
        for error in results['errors']:
            print(f"  - {error}")
            
except Exception as e:
    print(f"Critical error: {e}")
    import traceback
    traceback.print_exc()

print("\nOriginal configuration portfolio optimization complete!")