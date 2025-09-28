"""
Professional Portfolio Optimization Demo - Simplified Version
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Add source directory to path (same pattern as assignment_default_demo.py)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'source'))

try:
    from portfolio.optimizer import PortfolioOptimizer
    from portfolio.data_handler import DataHandler
    from portfolio.static_data_handler import StaticDataHandler
    from utils.plotting import PortfolioPlotter
    from ai.local_ai_analyzer import LocalAIPortfolioAnalyzer
except ImportError as e:
    print(f"Import Error: {e}")
    print("Please ensure the LocalAIPortfolioAnalyzer is saved in source/ai/local_analyzer.py")
    sys.exit(1)


def main():
    """Main demo function using your existing classes."""
    print("Professional Portfolio Optimization Demo")
    print("FIN 684F - Investment Theory/Advanced Corporate Finance")
    print("=" * 60)
    
    try:
        # Step 1: Initialize components
        print("\nSTEP 1: Initializing Components")
        print("-" * 40)
        
        data_handler = DataHandler()
        default_tickers = data_handler.get_default_tickers()
        
        print(f"Portfolio Universe: {len(default_tickers)} Blue-Chip Stocks")
        print(f"Sample tickers: {default_tickers[:5]}...")
        
        # Step 2: Configure optimizer
        print("\nSTEP 2: Configuring Optimizer")
        print("-" * 40)
        
        optimizer = PortfolioOptimizer(
            tickers=default_tickers[:10],  # Use subset for demo
            start_year=2020,
            end_year=2023,
            estimation_window=36,
            constraints={
                'min_weight': 0.0,
                'max_weight': 0.25,
                'allow_short': False,
                'long_only': True
            },
            risk_free_rate=0.042
        )
        
        print("Configuration complete")
        
        # Step 3: Run analysis
        print("\nSTEP 3: Running Portfolio Analysis")
        print("-" * 40)
        print("This may take a few minutes...")
        
        results = optimizer.run_complete_analysis()
        
        if results['success']:
            print("Analysis completed successfully!")
            
            # Display results
            print_results(results)
            
            # AI Analysis
            print("\nSTEP 4: AI Analysis")
            print("-" * 40)
            
            use_ai = input("Generate AI analysis? [y/N]: ").strip().lower()
            
            if use_ai == 'y':
                ai_analyzer = LocalAIPortfolioAnalyzer()
                
                ai_report = ai_analyzer.generate_complete_report(
                    performance_metrics=results['performance_metrics'],
                    portfolio_weights=results.get('portfolio_weights', {}),
                    turnover_metrics=results.get('turnover_metrics', {}),
                    config=results.get('config', {})
                )
                
                print("\nAI ANALYSIS REPORT:")
                print("=" * 50)
                for section_name, content in ai_report.items():
                    if section_name not in ['generated_at', 'model_used']:
                        print(f"\n{section_name.upper().replace('_', ' ')}:")
                        print("-" * 30)
                        print(content.strip())
                print("=" * 50)
            
        else:
            print("Analysis failed:")
            for error in results.get('errors', ['Unknown error']):
                print(f"  - {error}")
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()


def print_results(results):
    """Print formatted results."""
    perf = results.get('performance_metrics', {})
    
    if 'sample' in perf and 'lw' in perf:
        print("\nPERFORMANCE COMPARISON")
        print("=" * 55)
        
        print(f"{'METRIC':<25} {'SAMPLE':<12} {'LEDOIT-WOLF':<12}")
        print("-" * 55)
        
        metrics = [
            ('Annualized Return', 'annualized_return', '.2%'),
            ('Annualized Volatility', 'annualized_volatility', '.2%'),
            ('Sharpe Ratio', 'sharpe_ratio', '.3f'),
            ('Max Drawdown', 'max_drawdown', '.2%')
        ]
        
        for name, key, fmt in metrics:
            sample_val = perf['sample'].get(key, 0)
            lw_val = perf['lw'].get(key, 0)
            
            sample_str = f"{sample_val:{fmt}}"
            lw_str = f"{lw_val:{fmt}}"
            
            print(f"{name:<25} {sample_str:<12} {lw_str:<12}")
        
        # Winner
        sample_sharpe = perf['sample'].get('sharpe_ratio', 0)
        lw_sharpe = perf['lw'].get('sharpe_ratio', 0)
        
        if lw_sharpe > sample_sharpe:
            print(f"\nWINNER: Ledoit-Wolf Shrinkage")
        else:
            print(f"\nWINNER: Sample Covariance")


if __name__ == "__main__":
    main()