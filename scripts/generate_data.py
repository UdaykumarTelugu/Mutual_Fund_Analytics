import pandas as pd
import numpy as np
import os
import random
from datetime import timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Ensure data/raw directory exists
os.makedirs('data/raw', exist_ok=True)

print("Generating Data...")

# 1. NAV History (Daily, 40 schemes, 2022-2025)
dates = pd.date_range(start='2022-01-01', end='2025-12-31', freq='B') # Business days
schemes = [f"Scheme_{i}" for i in range(1, 41)]

nav_data = []
for scheme in schemes:
    # Base NAV
    base_nav = np.random.uniform(20, 100)
    
    # Simulate market trends:
    # 2022: Flat/volatile
    # 2023: Bull run
    # 2024: Correction
    # 2025: Recovery
    
    trend = []
    for date in dates:
        year = date.year
        if year == 2022:
            daily_return = np.random.normal(0.0001, 0.005)
        elif year == 2023:
            daily_return = np.random.normal(0.0008, 0.006) # Bull run
        elif year == 2024:
            daily_return = np.random.normal(-0.0002, 0.008) # Correction/Volatile
        else:
            daily_return = np.random.normal(0.0006, 0.005) # Recovery
            
        base_nav = base_nav * (1 + daily_return)
        trend.append(base_nav)
        
    df_scheme = pd.DataFrame({'Date': dates, 'Scheme': scheme, 'NAV': trend})
    nav_data.append(df_scheme)

nav_df = pd.concat(nav_data, ignore_index=True)
nav_df.to_csv('data/raw/nav_history.csv', index=False)
print("Saved nav_history.csv")

# 2. AUM Data (Yearly, 10 AMCs)
amcs = ['SBI', 'HDFC', 'ICICI Prudential', 'Axis', 'Kotak', 'Nippon India', 'Mirae Asset', 'DSP', 'UTI', 'Franklin Templeton']
years = [2022, 2023, 2024, 2025]

aum_data = []
for amc in amcs:
    for year in years:
        if amc == 'SBI':
            if year == 2022: val = 700000
            elif year == 2023: val = 950000
            elif year == 2024: val = 1100000
            elif year == 2025: val = 1250000
        else:
            # Randomize other AMCs but keep them smaller than SBI
            val = np.random.uniform(100000, 600000) * (1 + (year-2022)*0.15)
        aum_data.append({'AMC': amc, 'Year': year, 'AUM_Crore': round(val, 2)})
aum_df = pd.DataFrame(aum_data)
aum_df.to_csv('data/raw/aum_data.csv', index=False)
print("Saved aum_data.csv")


# 3. SIP Inflows (Monthly)
months = pd.date_range(start='2022-01-01', end='2025-12-01', freq='MS')
# Interpolate SIP inflows to reach exactly 31002 in Dec 2025
sip_values = np.linspace(10000, 31002, len(months))
# Add a little noise
noise = np.random.normal(0, 100, len(months))
noise[-1] = 0 # Ensure Dec 2025 is exactly 31002
sip_values = sip_values + noise

sip_df = pd.DataFrame({'Month': months, 'SIP_Inflow_Crore': sip_values})
sip_df['SIP_Inflow_Crore'] = sip_df['SIP_Inflow_Crore'].round(2)
sip_df.to_csv('data/raw/sip_inflows.csv', index=False)
print("Saved sip_inflows.csv")

# 4. Investors (10,000+)
num_investors = 10500
ages = np.random.randint(18, 75, num_investors)
def get_age_group(age):
    if age < 30: return '18-29'
    elif age < 45: return '30-44'
    elif age < 60: return '45-59'
    else: return '60+'
age_groups = [get_age_group(a) for a in ages]
genders = np.random.choice(['Male', 'Female', 'Other'], num_investors, p=[0.6, 0.38, 0.02])
states = ['Maharashtra', 'Gujarat', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal']
investor_states = np.random.choice(states, num_investors)
city_tiers = np.random.choice(['Tier 1', 'Tier 2', 'Tier 3'], num_investors, p=[0.5, 0.3, 0.2])
monthly_sips = np.random.exponential(scale=5000, size=num_investors) + 500
occupations = np.random.choice(['Salaried', 'Business', 'Professional', 'Student', 'Retired'], num_investors)
def get_income_range(sip):
    if sip < 2000: return 'Below 5L'
    elif sip < 10000: return '5L-10L'
    elif sip < 25000: return '10L-20L'
    else: return 'Above 20L'
income_ranges = [get_income_range(s) for s in monthly_sips]

investor_df = pd.DataFrame({
    'Investor_ID': range(1, num_investors + 1),
    'Age': ages,
    'Age_Group': age_groups,
    'Gender': genders,
    'State': investor_states,
    'City_Tier': city_tiers,
    'Monthly_SIP': monthly_sips.round(2),
    'Occupation': occupations,
    'Income_Range': income_ranges
})
investor_df.to_csv('data/raw/investor_data.csv', index=False)
print("Saved investor_data.csv")


# 5. Folio Counts (Monthly)
# Jan 2022 = 13.26 crore, Dec 2025 = 26.12 crore.
folio_values = np.linspace(13.26, 26.12, len(months))
noise_folio = np.random.normal(0, 0.1, len(months))
noise_folio[0] = 0
noise_folio[-1] = 0
folio_values = folio_values + noise_folio

folio_df = pd.DataFrame({'Month': months, 'Folio_Count_Crore': folio_values.round(2)})
folio_df.to_csv('data/raw/folio_counts.csv', index=False)
print("Saved folio_counts.csv")


# 6. Portfolio Holdings (Sector Allocations)
sectors = ['IT', 'Banking', 'Healthcare', 'FMCG', 'Energy', 'Auto', 'Pharma', 'Manufacturing', 'Telecom', 'Cash']

holdings_data = []
for scheme in schemes:
    # Generate random weights
    weights = np.random.rand(len(sectors))
    weights = weights / np.sum(weights) * 100
    
    for i, sector in enumerate(sectors):
        holdings_data.append({
            'Scheme': scheme,
            'Sector': sector,
            'Allocation_Percentage': round(weights[i], 2)
        })
        
holdings_df = pd.DataFrame(holdings_data)
# Fix rounding issues to ensure exactly 100.0% total per scheme
for scheme in schemes:
    idx = holdings_df[holdings_df['Scheme'] == scheme].index
    total = holdings_df.loc[idx, 'Allocation_Percentage'].sum()
    diff = round(100.0 - total, 2)
    # add diff to the first sector of the scheme
    holdings_df.loc[idx[0], 'Allocation_Percentage'] = round(holdings_df.loc[idx[0], 'Allocation_Percentage'] + diff, 2)

holdings_df.to_csv('data/raw/portfolio_holdings.csv', index=False)
print("Saved portfolio_holdings.csv")

print("All data generated successfully!")
