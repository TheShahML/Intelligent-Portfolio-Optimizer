# Intelligent Portfolio Optimizer

AI-enhanced portfolio optimization framework implementing modern portfolio theory with intelligent analysis and insights.

## Project Status
**Work in Progress** - Core architecture implemented, full demo coming soon.

## Key Features
Modern Portfolio Theory implementation with minimum variance optimization using CVXPY. Advanced covariance estimation comparing sample vs Ledoit-Wolf shrinkage methods. Rolling window backtesting framework with comprehensive performance metrics. Professional visualizations for risk-return analysis and performance dashboards. AI-powered portfolio analysis and insights through LangChain integration (WIP).

## Tech Stack
Core technologies include Python, NumPy, Pandas, CVXPY, and Scikit-learn. Data sourced from WRDS/CRSP financial databases. AI integration through LangChain and OpenAI GPT (coming soon). Web application built with FastAPI backend and React frontend (planned). Visualizations created with Matplotlib and Seaborn.

## Installation
```bash
git clone https://github.com/theshahml/intelligent-portfolio-optimizer.git
cd intelligent-portfolio-optimizer
pip install -r requirements.txt
```

## Demo Usage
WRDS account required to run the examples. See `examples/` directory for demonstration scripts with default configurations.

## Project Structure
```
src/
├── portfolio/     # Core optimization modules
├── ai/           # LangChain integration  
└── utils/        # Visualization & validation
```

## Planned Features
- AI analysis integration
- Interactive web application  
- Performance attribution dashboard

## Requirements
- Python 3.8+
- WRDS account (for live data)
- OpenAI API key (for AI features)

## Disclaimer
Educational and research purposes only. Not investment advice.
