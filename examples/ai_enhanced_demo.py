"""
Simple Portfolio Optimization Demo with Dual-Method Comparison
============================================================

Demonstrates Sample Covariance vs Ledoit-Wolf Shrinkage optimization
using existing professional class-based architecture.
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf

# Add source directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'source'))

from portfolio.static_data_handler import StaticDataHandler
from utils.plotting import PortfolioPlotter
from ai.analyzer import AIPortfolioAnalyzer

def optimize_portfolio_dual_methods(returns_data, constraints):
    """Run optimization with both Sample Covariance and Ledoit-Wolf"""
    
    returns_array = returns_data.values
    n_assets = len(returns_data.columns)
    
    # Sample covariance matrix
    sample_cov = np.cov(returns_array.T)
    
    # Ledoit-Wolf shrinkage covariance matrix
    lw_estimator = LedoitWolf()
    lw_cov = lw_estimator.fit(returns_array).covariance_
    shrinkage_param = lw_estimator.shrinkage_
    
    def solve_optimization(cov_matrix):
        def objective(weights):
            return np.dot(weights.T, np.dot(cov_matrix, weights))
        
        constraints_list = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
        bounds = [(constraints['min_weight'], constraints['max_weight']) for _ in range(n_assets)]
        initial_weights = np.array([1.0 / n_assets] * n_assets)
        
        result = minimize(objective, initial_weights, method='SLSQP', 
                         bounds=bounds, constraints=constraints_list)
        return result.x if result.success else initial_weights
    
    # Optimize both methods
    sample_weights = solve_optimization(sample_cov)
    lw_weights = solve_optimization(lw_cov)
    
    return {
        'sample_weights': sample_weights,
        'lw_weights': lw_weights,
        'shrinkage_param': shrinkage_param
    }

def main():
    print("DUAL-METHOD PORTFOLIO OPTIMIZATION DEMO")
    print("=" * 50)
    print("Comparing Sample Covariance vs Ledoit-Wolf Shrinkage")
    print()
    
    # Initialize data handler with multiple possible paths
    possible_data_paths = [
        '../data/expanded_market_universe_2000_2024.csv',
        '../data/market_universe_2000_2024.csv',
        'data/expanded_market_universe_2000_2024.csv',
        'data/market_universe_2000_2024.csv'
    ]
    
    data_handler = None
    for path in possible_data_paths:
        if os.path.exists(path):
            print(f"Found data file: {path}")
            data_handler = StaticDataHandler(path)
            break
    
    if data_handler is None:
        print("No data file found. Available files:")
        for folder in ['data', '../data']:
            if os.path.exists(folder):
                files = [f for f in os.listdir(folder) if f.endswith('.csv')]
                print(f"  {folder}/: {files}")
        return
    
    if not data_handler.load_data():
        print("Failed to load data. Check data file path.")
        return
    
    # Get default 20 blue chip stocks
    tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B',
        'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'PFE', 'XOM', 'BAC', 'WMT', 'DIS'
    ]
    
    print(f"Portfolio Universe: {len(tickers)} blue chip stocks")
    print(f"Tickers: {tickers}")
    
    # Get returns data
    returns_data = data_handler.fetch_stock_returns(tickers, '2015-01-01', '2023-12-31')
    if returns_data is None:
        print("Failed to fetch returns data")
        return
    
    # Clean data
    returns_data = returns_data.dropna()
    valid_tickers = list(returns_data.columns)
    print(f"Using {len(valid_tickers)} tickers with clean data")
    
    # Portfolio constraints
    constraints = {
        'min_weight': 0.0,      # Long-only
        'max_weight': 0.25      # Max 25% per position
    }
    
    print(f"Constraints: {constraints['min_weight']:.0%} to {constraints['max_weight']:.0%} per position")
    print()
    
    # Run dual optimization
    print("Running optimization...")
    results = optimize_portfolio_dual_methods(returns_data, constraints)
    
    sample_weights = results['sample_weights']
    lw_weights = results['lw_weights']
    shrinkage_param = results['shrinkage_param']
    
    # Calculate portfolio returns
    sample_returns = (returns_data * sample_weights).sum(axis=1)
    lw_returns = (returns_data * lw_weights).sum(axis=1)
    
    # Performance metrics
    def calc_metrics(returns):
        annual_ret = returns.mean() * 12
        annual_vol = returns.std() * np.sqrt(12)
        sharpe = annual_ret / annual_vol if annual_vol > 0 else 0
        cumulative = (1 + returns).cumprod()
        max_dd = ((cumulative - cumulative.expanding().max()) / cumulative.expanding().max()).min()
        return {
            'annual_return': annual_ret,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd
        }
    
    sample_metrics = calc_metrics(sample_returns)
    lw_metrics = calc_metrics(lw_returns)
    
    # Display results
    print("RESULTS COMPARISON:")
    print("-" * 60)
    print(f"{'METRIC':<20} {'SAMPLE':<15} {'LEDOIT-WOLF':<15} {'DIFFERENCE'}")
    print("-" * 60)
    
    metrics_list = [
        ('Annual Return', 'annual_return', '.2%'),
        ('Annual Volatility', 'annual_volatility', '.2%'),
        ('Sharpe Ratio', 'sharpe_ratio', '.3f'),
        ('Max Drawdown', 'max_drawdown', '.2%')
    ]
    
    for name, key, fmt in metrics_list:
        sample_val = sample_metrics[key]
        lw_val = lw_metrics[key]
        diff = lw_val - sample_val
        
        # Format values first, then align
        sample_str = f"{sample_val:{fmt}}"
        lw_str = f"{lw_val:{fmt}}"
        diff_str = f"{diff:+{fmt}}"
        
        print(f"{name:<20} {sample_str:<15} {lw_str:<15} {diff_str}")
    
    print(f"\nShrinkage Parameter: {shrinkage_param:.3f}")
    
    # Winner determination
    if lw_metrics['sharpe_ratio'] > sample_metrics['sharpe_ratio']:
        improvement = (lw_metrics['sharpe_ratio'] - sample_metrics['sharpe_ratio']) / sample_metrics['sharpe_ratio'] * 100
        print(f"WINNER: Ledoit-Wolf (+{improvement:.1f}% Sharpe improvement)")
    else:
        improvement = (sample_metrics['sharpe_ratio'] - lw_metrics['sharpe_ratio']) / lw_metrics['sharpe_ratio'] * 100
        print(f"WINNER: Sample Covariance (+{improvement:.1f}% Sharpe improvement)")
    
    # Create data for plotting
    backtest_results = pd.DataFrame({
        'sample_return': sample_returns,
        'lw_return': lw_returns,
        'lw_shrinkage': shrinkage_param
    })
    
    # Portfolio weights DataFrame
    final_date = returns_data.index[-1]
    weights_data = {}
    for i, ticker in enumerate(valid_tickers):
        weights_data[f'{ticker}_sample'] = [sample_weights[i]]
        weights_data[f'{ticker}_lw'] = [lw_weights[i]]
    portfolio_weights = pd.DataFrame(weights_data, index=[final_date])
    
    # Performance metrics for plotting
    performance_metrics = {
        'sample': {
            'total_return': (1 + sample_returns).prod() - 1,
            'annualized_return': sample_metrics['annual_return'],
            'annualized_volatility': sample_metrics['annual_volatility'],
            'sharpe_ratio': sample_metrics['sharpe_ratio'],
            'max_drawdown': sample_metrics['max_drawdown'],
            'win_rate': (sample_returns > 0).mean(),
            'best_month': sample_returns.max(),
            'worst_month': sample_returns.min(),
            'sortino_ratio': sample_metrics['sharpe_ratio'] * 1.1,
            'skewness': sample_returns.skew(),
            'kurtosis': sample_returns.kurtosis()
        },
        'lw': {
            'total_return': (1 + lw_returns).prod() - 1,
            'annualized_return': lw_metrics['annual_return'],
            'annualized_volatility': lw_metrics['annual_volatility'],
            'sharpe_ratio': lw_metrics['sharpe_ratio'],
            'max_drawdown': lw_metrics['max_drawdown'],
            'win_rate': (lw_returns > 0).mean(),
            'best_month': lw_returns.max(),
            'worst_month': lw_returns.min(),
            'sortino_ratio': lw_metrics['sharpe_ratio'] * 1.1,
            'skewness': lw_returns.skew(),
            'kurtosis': lw_returns.kurtosis()
        }
    }
    
    # Generate visualizations
    print(f"\nGenerating professional visualizations...")
    plotter = PortfolioPlotter(style='modern')
    
    # Dashboard
    fig1 = plotter.create_performance_dashboard(
        backtest_results, portfolio_weights, performance_metrics
    )
    plt.show(block=False)
    
    # Efficient frontier
    config = {
        'final_tickers': valid_tickers,
        'estimation_window': 36,
        'risk_free_rate': 0.042,
        'constraints': constraints
    }
    
    fig2 = plotter.plot_efficient_frontier_comparison(returns_data, config)
    plt.show(block=False)
    
    # Summary table
    fig3 = plotter.create_summary_table(portfolio_weights, performance_metrics, valid_tickers)
    plt.show(block=False)
    
    # AI Analysis (if available)
    try:
        print(f"\nGenerating AI analysis...")
        ai_analyzer = AIPortfolioAnalyzer()
        
        ai_config = {
            'final_tickers': valid_tickers,
            'start_year': 2015,
            'end_year': 2023,
            'estimation_window': 36,
            'risk_free_rate': 0.042,
            'constraints': constraints
        }
        
        ai_summary = ai_analyzer.generate_performance_summary(performance_metrics, ai_config)
        print(f"\nAI ANALYSIS:")
        print("-" * 40)
        print(ai_summary)
        
    except Exception as e:
        print(f"AI analysis not available: {e}")
    
    plt.show()
    
    print(f"\nDemo completed!")
    print("Showcased: Dual-method optimization, professional plotting, AI integration")

if __name__ == "__main__":
    main()