#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd

performance_df = pd.read_csv(...)

plt.figure(figsize=(8,5))

avg_returns.plot(
    kind="bar",
    color=["royalblue", "orange", "green"]
)

plt.title("Average Returns Comparison")
plt.xlabel("Return Period")
plt.ylabel("Average Return (%)")

plt.xticks(rotation=0)

plt.tight_layout()
plt.savefig("../reports/charts/average_returns_comparison.png", dpi=300)
plt.show()


# In[ ]:


import matplotlib.pyplot as plt

transactions_df["transaction_type"].value_counts().plot(
    kind="bar",
    figsize=(8,5),
    color="red"
)

plt.title("Transaction Type Distribution")
plt.xlabel("Transaction Type")
plt.ylabel("Count")

plt.tight_layout()
plt.savefig("../reports/charts/transaction_type_distribution.png", dpi=300)
plt.show()


# In[ ]:


import matplotlib.pyplot as plt

transactions_df["kyc_status"].value_counts().plot(
    kind="bar",
    figsize=(8,5),
    color="purple"
)

plt.title("KYC Status Distribution")
plt.xlabel("KYC Status")
plt.ylabel("Count")

plt.tight_layout()
plt.savefig("../reports/charts/kyc_status_distribution.png", dpi=300)
plt.show()


# In[ ]:


import matplotlib.pyplot as plt

state_transactions = (
    transactions_df["state"]
    .value_counts()
)

plt.figure(figsize=(12,6))
state_transactions.plot(kind="bar", color="orange")

plt.title("State-wise Transactions")
plt.xlabel("State")
plt.ylabel("Number of Transactions")

plt.tight_layout()
plt.savefig("../reports/charts/state_transactions.png", dpi=300)
plt.show()


# In[ ]:


import matplotlib.pyplot as plt

state_amount = (
    transactions_df.groupby("state")["amount"]
    .sum()
    .sort_values(ascending=False)
)

plt.figure(figsize=(12,6))
state_amount.plot(kind="bar", color="green")

plt.title("State-wise Investment Amount")
plt.xlabel("State")
plt.ylabel("Investment Amount")

plt.tight_layout()
plt.savefig("../reports/charts/state_investment_amount.png", dpi=300)
plt.show()


# In[ ]:


import matplotlib.pyplot as plt

top_funds = (
    aum_df.groupby("fund_id")["aum"]
    .max()
    .sort_values(ascending=False)
)

plt.figure(figsize=(10,6))
top_funds.plot(kind="bar", color="steelblue")

plt.title("Top Funds by AUM")
plt.xlabel("Fund ID")
plt.ylabel("AUM")

plt.tight_layout()
plt.savefig("../reports/charts/top_funds_aum.png", dpi=300)
plt.show()


# In[ ]:


print("="*60)
print("NAV DATA COLUMNS")
print(nav_df.columns.tolist())

print("\n" + "="*60)
print("TRANSACTIONS DATA COLUMNS")
print(transactions_df.columns.tolist())

print("\n" + "="*60)
print("AUM DATA COLUMNS")
print(aum_df.columns.tolist())

print("\n" + "="*60)
print("PERFORMANCE DATA COLUMNS")

try:
    print(performance_df.columns.tolist())
except NameError:
    print("performance_df is not loaded. Run the 'Load Scheme Performance' cell first.")


# In[ ]:


print(performance_df.columns.tolist())


# In[ ]:


print(aum_df.columns.tolist())
print(transactions_df.columns.tolist())


# In[ ]:


print(nav_df.columns.tolist())


# In[ ]:


print(performance_df.columns.tolist())


# In[ ]:


print(nav_df.columns.tolist())


# In[ ]:


print(transactions_df.columns.tolist())


# In[ ]:


print(aum_df.columns.tolist())


# In[ ]:


plt.tight_layout()
plt.savefig("../reports/charts/aum_trend_over_time.png", dpi=300, bbox_inches="tight")
plt.show()


# In[ ]:


# Daily NAV Trend

fig_daily = px.line(
    nav_df,
    x="date",
    y="nav",
    title="Daily NAV Trend"
)

fig_daily.update_layout(
    template="plotly_white",
    title_x=0.5,
    width=1200,
    height=600,
    xaxis_title="Date",
    yaxis_title="NAV"
)

fig_daily.show()


# In[ ]:


# Save the current figure (run immediately after creating each chart)

plt.savefig("../reports/charts/monthly_transaction_count.png", dpi=300, bbox_inches="tight")

plt.savefig("../reports/charts/total_investment_by_fund.png", dpi=300, bbox_inches="tight")

plt.savefig("../reports/charts/aum_trend_over_time.png", dpi=300, bbox_inches="tight")

print("Charts saved successfully!")


# In[ ]:


aum_df["date"] = pd.to_datetime(aum_df["date"])

daily_aum = (
    aum_df
    .groupby("date")["aum"]
    .sum()
    .reset_index()
)

plt.figure(figsize=(12,5))

sns.lineplot(
    data=daily_aum,
    x="date",
    y="aum",
    marker="o"
)

plt.title("AUM Trend Over Time")

plt.tight_layout()

plt.savefig("../reports/charts/aum_trend_over_time.png", dpi=300, bbox_inches="tight")

plt.show()


# In[ ]:


fund_amount = (
    transactions_df
    .groupby("fund_id")["amount"]
    .sum()
    .reset_index()
)

plt.figure(figsize=(10,5))

sns.barplot(
    data=fund_amount,
    x="fund_id",
    y="amount"
)

plt.title("Total Investment by Fund")

plt.tight_layout()

plt.savefig("../reports/charts/total_investment_by_fund.png", dpi=300, bbox_inches="tight")

plt.show()


# In[ ]:


transactions_df["transaction_date"] = pd.to_datetime(transactions_df["transaction_date"])

monthly_transactions = (
    transactions_df
    .groupby(transactions_df["transaction_date"].dt.to_period("M"))
    .size()
    .reset_index(name="Transaction Count")
)

monthly_transactions["transaction_date"] = monthly_transactions["transaction_date"].astype(str)

plt.figure(figsize=(10,5))

sns.lineplot(
    data=monthly_transactions,
    x="transaction_date",
    y="Transaction Count",
    marker="o"
)

plt.title("Monthly Transaction Count")
plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig("../reports/charts/monthly_transaction_count.png", dpi=300, bbox_inches="tight")

plt.show()


# In[ ]:


plt.figure(figsize=(8,5))

sns.histplot(
    aum_df["aum"],
    bins=10,
    kde=True
)

plt.title("AUM Distribution")
plt.xlabel("AUM")
plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig(
    "../reports/charts/aum_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# In[ ]:


plt.figure(figsize=(8,5))

sns.histplot(
    transactions_df["amount"],
    bins=10,
    kde=True
)

plt.title("Investment Amount Distribution")
plt.xlabel("Amount")
plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig(
    "../reports/charts/investment_amount_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# In[ ]:


# Correlation Matrix

corr = transactions_df[["fund_id", "amount"]].corr()

plt.figure(figsize=(6,5))

sns.heatmap(
    corr,
    annot=True,
    cmap="Blues",
    linewidths=0.5
)

plt.title("Correlation Matrix")

plt.tight_layout()

plt.savefig(
    "../reports/charts/correlation_matrix.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# In[ ]:


fig.write_html("../reports/charts/monthly_nav_trend.html")


# In[ ]:


fig.write_html("../reports/charts/daily_nav_trend.html")


# In[ ]:


monthly_nav = (
    nav_df
    .set_index("date")
    .resample("M")
    .mean()
    .reset_index()
)

fig = px.line(
    monthly_nav,
    x="date",
    y="nav",
    title="Monthly Average NAV",
    markers=True
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5
)

fig.show()


# In[ ]:


print("Average NAV")

print(round(nav_df["nav"].mean(),2))


# In[ ]:


print("Highest NAV")

display(nav_df.loc[nav_df["nav"].idxmax()])

print("\nLowest NAV")

display(nav_df.loc[nav_df["nav"].idxmin()])


# In[ ]:


import plotly.express as px

fig = px.line(
    nav_df,
    x="date",
    y="nav",
    title="Daily NAV Trend",
    labels={
        "date": "Date",
        "nav": "NAV"
    }
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    width=1000,
    height=500
)

fig.show()


# In[ ]:


# Sort NAV Data by Date

nav_df = nav_df.sort_values("date")

nav_df.head()


# In[ ]:


nav_df.dtypes


# In[ ]:


# Convert Date Columns

nav_df["date"] = pd.to_datetime(nav_df["date"])

transactions_df["transaction_date"] = pd.to_datetime(
    transactions_df["transaction_date"]
)

aum_df["date"] = pd.to_datetime(aum_df["date"])


# In[ ]:


# Check Data Types

print("NAV Data")
display(nav_df.dtypes)

print("\nTransactions")
display(transactions_df.dtypes)

print("\nPerformance")
display(performance_df.dtypes)

print("\nAUM")
display(aum_df.dtypes)


# In[ ]:


# Statistical Summary

display(nav_df.describe())

display(transactions_df.describe())

display(performance_df.describe())

display(aum_df.describe())


# In[ ]:


# Missing Values

print("NAV")
display(nav_df.isnull().sum())

print("\nTransactions")
display(transactions_df.isnull().sum())

print("\nPerformance")

display(performance_df.isnull().sum())

print("\nAUM")
display(aum_df.isnull().sum())


# In[ ]:


print("NAV DATA")
nav_df.info()

print("\nTRANSACTION DATA")
transactions_df.info()


print("\nPERFORMANCE DATA")
performance_df.info()

print("\nAUM DATA")
aum_df.info()


# In[ ]:


# Dataset Shapes

print("NAV:", nav_df.shape)
print("Transactions:", transactions_df.shape)

print("Performance:", performance_df.shape)
print("AUM:", aum_df.shape)


# In[ ]:


# Load AUM Data

aum_df = pd.read_sql("SELECT * FROM aum", conn)

aum_df.head()


# In[ ]:


# Load Scheme Performance

performance_df = pd.read_sql("SELECT * FROM scheme_performance", conn)

performance_df.head()


# In[ ]:


# Load Investor Transactions

transactions_df = pd.read_sql("SELECT * FROM investor_transactions", conn)

transactions_df.head()


# In[ ]:


# Load NAV Data

nav_df = pd.read_sql("SELECT * FROM nav_processed", conn)

nav_df.head()


# In[ ]:


# Show Available Tables

query = """
SELECT name
FROM sqlite_master
WHERE type='table';
"""

tables = pd.read_sql(query, conn)

tables


# In[ ]:


# Database Connection

import sqlite3

conn = sqlite3.connect("../bluestock_mf.db")


# In[ ]:


import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

import plotly.express as px
import plotly.graph_objects as go

import sqlite3
import warnings

warnings.filterwarnings("ignore")

plt.style.use("ggplot")

print("EDA Notebook Started Successfully!")


# # Mutual Fund Analytics - Exploratory Data Analysis (EDA)
# 
# ## Objective
# 
# This notebook performs Exploratory Data Analysis (EDA) on Mutual Fund datasets.
# 
# ### Analysis Covered
# 
# - NAV Trend Analysis
# - AUM Growth Analysis
# - SIP Inflow Analysis
# - Category-wise Analysis
# - Investor Demographics
# - Geographic Distribution
# - Correlation Analysis
# - Sector Allocation
# - Business Insights
