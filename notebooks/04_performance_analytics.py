#!/usr/bin/env python
# coding: utf-8

# # 04. Performance and Risk Analytics
# This notebook calculates performance and risk metrics for the mutual funds in our dataset. It generates rolling returns, volatility, Sharpe, Sortino, VaR, CVaR, Beta, and Alpha.

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
import os
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


# ## 1. Load the Merged Dataset

# In[2]:


data_path = '../data/processed/merged_dataset.csv'
df = pd.read_csv(data_path)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['fund_id', 'date'])
print(f"Dataset shape: {df.shape}")


# ## 2. Calculate Daily, Monthly, and Annual Returns

# In[3]:


# Daily Return
df['daily_return'] = df.groupby('fund_id')['nav'].pct_change()

# To calculate monthly and annual returns, we resample
# We create copies for the resampled data and then can join if needed, or just keep them separate
df_resample = df.set_index('date')

monthly_returns = df_resample.groupby('fund_id')['nav'].resample('ME').last().groupby('fund_id').pct_change().reset_index(name='monthly_return')
annual_returns = df_resample.groupby('fund_id')['nav'].resample('YE').last().groupby('fund_id').pct_change().reset_index(name='annual_return')

df.dropna(subset=['daily_return'], inplace=True)
print("Calculated Daily Returns.")


# ## 3. Calculate CAGR, Sharpe, and Sortino Ratios
# Using 252 trading days for annualization.

# In[4]:


TRADING_DAYS = 252
RISK_FREE_RATE = 0.05 # Assuming 5% annual risk-free rate
DAILY_RF = RISK_FREE_RATE / TRADING_DAYS

metrics = []

for fund_id, group in df.groupby('fund_id'):
    group = group.sort_values('date')

    # CAGR
    years = (group['date'].iloc[-1] - group['date'].iloc[0]).days / 365.25
    if years > 0:
        cagr = (group['nav'].iloc[-1] / group['nav'].iloc[0]) ** (1 / years) - 1
    else:
        cagr = np.nan

    # Annualized Volatility
    ann_vol = group['daily_return'].std() * np.sqrt(TRADING_DAYS)

    # Sharpe Ratio
    excess_return = group['daily_return'] - DAILY_RF
    sharpe_ratio = np.sqrt(TRADING_DAYS) * excess_return.mean() / group['daily_return'].std()

    # Sortino Ratio
    downside_returns = excess_return[excess_return < 0]
    downside_deviation = np.sqrt(TRADING_DAYS) * downside_returns.std() if len(downside_returns) > 0 else np.nan
    sortino_ratio = np.sqrt(TRADING_DAYS) * excess_return.mean() / downside_deviation if downside_deviation > 0 else np.nan

    # Maximum Drawdown
    cumulative = (1 + group['daily_return']).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()

    # VaR and CVaR (95%)
    var_95 = np.percentile(group['daily_return'].dropna(), 5)
    cvar_95 = group['daily_return'][group['daily_return'] <= var_95].mean()

    metrics.append({
        'fund_id': fund_id,
        'cagr': cagr,
        'annualized_volatility': ann_vol,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown': max_drawdown,
        'var_95': var_95,
        'cvar_95': cvar_95
    })

metrics_df = pd.DataFrame(metrics)
metrics_df


# ## 4. Benchmark Comparison (Alpha and Beta)
# We will fetch NIFTY 50 (`^NSEI`) data using `yfinance` to use as the benchmark.

# In[5]:


start_date = df['date'].min()
end_date = df['date'].max()

try:
    ticker = yf.Ticker('^NSEI')
    benchmark = ticker.history(start=start_date, end=end_date)
    benchmark = benchmark.reset_index()

    if benchmark['Date'].dt.tz is not None:
        benchmark['Date'] = benchmark['Date'].dt.tz_localize(None)

    benchmark = benchmark.rename(columns={'Date': 'date', 'Close': 'benchmark_price'})
    benchmark['benchmark_return'] = benchmark['benchmark_price'].pct_change()

    # Merge with main df
    df = pd.merge(df, benchmark[['date', 'benchmark_return']], on='date', how='left')
    df['benchmark_return'] = df['benchmark_return'].fillna(0) # Fill for missing

    # Calculate Beta and Alpha
    alpha_beta = []
    for fund_id, group in df.groupby('fund_id'):
        group_clean = group.dropna(subset=['daily_return', 'benchmark_return'])
        if len(group_clean) > 0:
            cov = np.cov(group_clean['daily_return'], group_clean['benchmark_return'])[0, 1]
            var = np.var(group_clean['benchmark_return'])
            beta = cov / var if var > 0 else np.nan

            # Annualized Alpha
            alpha = (group_clean['daily_return'].mean() - DAILY_RF) - beta * (group_clean['benchmark_return'].mean() - DAILY_RF)
            ann_alpha = alpha * TRADING_DAYS

            alpha_beta.append({'fund_id': fund_id, 'beta': beta, 'alpha': ann_alpha})

    ab_df = pd.DataFrame(alpha_beta)
    metrics_df = pd.merge(metrics_df, ab_df, on='fund_id', how='left')
    print("Benchmark data successfully processed.")
except Exception as e:
    print("Could not fetch or process benchmark data:", e)


# ## 5. Calculate Rolling Returns & Rolling Volatility

# In[6]:


window = 252 # 1-Year Rolling

df['rolling_return_1y'] = df.groupby('fund_id')['nav'].transform(lambda x: x.pct_change(periods=window))
df['rolling_vol_1y'] = df.groupby('fund_id')['daily_return'].transform(lambda x: x.rolling(window=window).std() * np.sqrt(TRADING_DAYS))
df['rolling_sharpe_1y'] = df.groupby('fund_id')['daily_return'].transform(lambda x: (x.rolling(window=window).mean() - DAILY_RF) / x.rolling(window=window).std() * np.sqrt(TRADING_DAYS))

# Drawdown Curve per fund
def calculate_drawdown(series):
    cum = (1 + series).cumprod()
    peak = cum.cummax()
    return (cum - peak) / peak

df['drawdown'] = df.groupby('fund_id')['daily_return'].transform(calculate_drawdown)
print("Rolling metrics calculated.")


# ## 6. Save Processed Metrics

# In[7]:


os.makedirs('../data/processed', exist_ok=True)
metrics_df.to_csv('../data/processed/performance_metrics.csv', index=False)

# Separate Risk Metrics
risk_cols = ['fund_id', 'annualized_volatility', 'max_drawdown', 'var_95', 'cvar_95', 'beta', 'alpha']
risk_df = metrics_df[[c for c in risk_cols if c in metrics_df.columns]]
risk_df.to_csv('../data/processed/risk_metrics.csv', index=False)

print("Metrics saved successfully.")


# ## 7. Generate Charts

# In[8]:


os.makedirs('../charts', exist_ok=True)
fund_names = df[['fund_id', 'fund_name']].drop_duplicates().set_index('fund_id')['fund_name'].to_dict()

# Helper to get name
def get_name(fid):
    name = fund_names.get(fid, str(fid))
    return name if pd.notna(name) else str(fid)

# 1. Rolling Sharpe Ratio
plt.figure(figsize=(12, 6))
for fund_id, group in df.groupby('fund_id'):
    plt.plot(group['date'], group['rolling_sharpe_1y'], label=get_name(fund_id))
plt.title('1-Year Rolling Sharpe Ratio')
plt.xlabel('Date')
plt.ylabel('Sharpe Ratio')
plt.legend()
plt.tight_layout()
plt.savefig('../charts/rolling_sharpe_ratio.png')
plt.close()

# 2. Rolling Volatility
plt.figure(figsize=(12, 6))
for fund_id, group in df.groupby('fund_id'):
    plt.plot(group['date'], group['rolling_vol_1y'], label=get_name(fund_id))
plt.title('1-Year Rolling Volatility')
plt.xlabel('Date')
plt.ylabel('Volatility')
plt.legend()
plt.tight_layout()
plt.savefig('../charts/rolling_volatility.png')
plt.close()

# 3. Drawdown Curve
plt.figure(figsize=(12, 6))
for fund_id, group in df.groupby('fund_id'):
    plt.plot(group['date'], group['drawdown'], label=get_name(fund_id))
plt.title('Drawdown Curve')
plt.xlabel('Date')
plt.ylabel('Drawdown')
plt.legend()
plt.tight_layout()
plt.savefig('../charts/drawdown_curve.png')
plt.close()

# 4. Risk vs Return Scatter
plt.figure(figsize=(10, 6))
sns.scatterplot(data=metrics_df, x='annualized_volatility', y='cagr', hue='fund_id', s=100)
for i, row in metrics_df.iterrows():
    plt.annotate(get_name(row['fund_id']), (row['annualized_volatility'], row['cagr']))
plt.title('Risk vs Return')
plt.xlabel('Annualized Volatility')
plt.ylabel('CAGR')
plt.tight_layout()
plt.savefig('../charts/risk_vs_return_scatter.png')
plt.close()

# 5. VaR Distribution
plt.figure(figsize=(10, 6))
sns.barplot(data=metrics_df, x='fund_id', y='var_95')
plt.title('Historical VaR (95%) by Fund')
plt.xlabel('Fund ID')
plt.ylabel('Value at Risk (95%)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('../charts/var_distribution.png')
plt.close()

# 6. Beta Comparison
if 'beta' in metrics_df.columns:
    plt.figure(figsize=(10, 6))
    sns.barplot(data=metrics_df, x='fund_id', y='beta')
    plt.title('Beta Comparison vs NIFTY 50')
    plt.xlabel('Fund ID')
    plt.ylabel('Beta')
    plt.axhline(1, color='r', linestyle='--') # Market beta
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('../charts/beta_comparison.png')
    plt.close()

print("Charts generated and saved.")

