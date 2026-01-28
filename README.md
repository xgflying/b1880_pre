# Stock Analysis
Pulls historical price data for given stocks (currently maximum of two), plots the prices, and outputs statistics about them (High Price, Low Price, Return, and Sortino and Sharpe ratios)

## Requirements
- plotly
- yfinance 

Use pip to install
``` 
pip install yfinance
pip install plotly
```

Should run on any Python 3.x (was developed on Python 3.13.0)

##  Notes
No API keys are necessary to use yfinance

# 本地运行
## 需要保证系统安装了 Tkinter，否则会报错
## 根据安装的 Tkinter ，选择是否需要使用虚拟环境。
## 创建虚拟环境并安装依赖
``` 
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
```
## 启动项目
```
    python stock_graph.py
```
