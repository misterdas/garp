"""
Automated Screener for Fetching GARP Strategy
Reference: Refer to Shankar Nath's GARP Investing video for detailed rules

-- Dependencies to be installed --
pip install beautifulsoup4==4.11.2
pip install openpyxl
pip install pandas

Disclaimer:
The information provided is for educational and informational purposes only and
should not be construed as financial, investment, or legal advice. The content is based on publicly available
information and personal opinions and may not be suitable for all investors. Investing involves risks,
including the loss of principal.

Credits / Courtesy : Shankar Nath

Queries on feedback on the python screener can be sent to :
FabTrader (fabtraderinc@gmail.com)
www.fabtrader.in
YouTube: @fabtraderinc
X / Instagram / Telegram :  @fabtraderinc
"""

import time
import pandas as pd
from urllib.error import HTTPError
import os

def fetchScreenerData(link):
    data = pd.DataFrame()
    current_page = 1
    page_limit = 100
    
    print(f"Fetching data from: {link}")
    
    while current_page < page_limit:
        url = f'{link}?page={current_page}'
        print(f"Processing page {current_page}...")
        
        try:
            all_tables = pd.read_html(url, flavor='bs4')
            
            if not all_tables:
                print(f"No tables found on page {current_page}")
                break
                
            combined_df = pd.concat(all_tables, ignore_index=True)
            
            required_columns = ['S.No.', 'Name']
            if not all(col in combined_df.columns for col in required_columns):
                print(f"Required columns {required_columns} not found on page {current_page}")
                break
            
            combined_df = combined_df.drop(combined_df[combined_df['S.No.'].isnull()].index)
            combined_df = combined_df[combined_df['S.No.'] != 'S.No.']
            
            if len(combined_df) == 0:
                print(f"No valid data found on page {current_page}. Stopping.")
                break
            
            print(f"Found {len(combined_df)} rows on page {current_page}")
            data = pd.concat([data, combined_df], axis=0, ignore_index=True)
            
            if len(combined_df) < 25:
                print(f"Page {current_page} has fewer rows ({len(combined_df)}), likely the last page.")
                break
                
        except HTTPError as e:
            if e.code == 404:
                print(f"Page {current_page} not found (404). Reached end of available pages.")
                break
            else:
                print(f"HTTP Error on page {current_page}: {e}")
                break
        except Exception as e:
            print(f"Error processing page {current_page}: {e}")
            break
            
        current_page += 1
        time.sleep(3)
    
    print(f"Total rows fetched: {len(data)}")
    return data

pd.set_option("display.max_rows", None, "display.max_columns", None)

# === Fetch 3 Month Returns ===
print("=== Fetching 3 Month Returns ===")
garp3_link = 'https://www.screener.in/screens/2982716/garp3months/'
garp3_df = fetchScreenerData(garp3_link)
if not garp3_df.empty:
    garp3_df = garp3_df[['Name', 'CMP  Rs.', '3mth return  %']]
    garp3_df['CMP  Rs.'] = pd.to_numeric(garp3_df['CMP  Rs.'], errors='coerce')
    garp3_df['3mth return  %'] = pd.to_numeric(garp3_df['3mth return  %'], errors='coerce')
    garp3_df = garp3_df[garp3_df['3mth return  %'] > 0]
    garp3_df.dropna(inplace=True)
    print(f"3-month data: {len(garp3_df)} stocks after filtering")
else:
    print("No 3-month data fetched. Skipping to next step.")
    garp3_df = pd.DataFrame(columns=['Name', 'CMP  Rs.', '3mth return  %'])

# === Fetch 6 Month Returns ===
print("\n=== Fetching 6 Month Returns ===")
garp6_link = 'https://www.screener.in/screens/2982735/garp6months/'
garp6_df = fetchScreenerData(garp6_link)
if not garp6_df.empty:
    garp6_df = garp6_df[['Name', '6mth return  %']]
    garp6_df['6mth return  %'] = pd.to_numeric(garp6_df['6mth return  %'], errors='coerce')
    garp6_df = garp6_df[garp6_df['6mth return  %'] > 0]
    garp6_df.dropna(inplace=True)
    print(f"6-month data: {len(garp6_df)} stocks after filtering")
else:
    print("No 6-month data fetched. Skipping to next step.")
    garp6_df = pd.DataFrame(columns=['Name', '6mth return  %'])

# === Fetch 12 Month Returns ===
print("\n=== Fetching 12 Month Returns ===")
garp12_link = 'https://www.screener.in/screens/2982726/garp12months/'
garp12_df = fetchScreenerData(garp12_link)
if not garp12_df.empty:
    garp12_df = garp12_df[['Name', '1Yr return  %']]
    garp12_df['1Yr return  %'] = pd.to_numeric(garp12_df['1Yr return  %'], errors='coerce')
    garp12_df = garp12_df[garp12_df['1Yr return  %'] > 0]
    garp12_df.dropna(inplace=True)
    print(f"12-month data: {len(garp12_df)} stocks after filtering")
else:
    print("No 12-month data fetched. Skipping to next step.")
    garp12_df = pd.DataFrame(columns=['Name', '1Yr return  %'])

# === Merge All Return Data ===
print("\n=== Merging Data ===")
merged_df = pd.merge(garp3_df, garp6_df, on='Name', how='inner')
merged_df = pd.merge(merged_df, garp12_df, on='Name', how='inner')
merged_df.dropna(inplace=True)

print(f"Final merged data: {len(merged_df)} stocks")

if not merged_df.empty:
    merged_df = merged_df.sort_values(by=['3mth return  %'], ascending=False)

# === Save Final CSV ===
try:
    merged_df.to_csv('GARP.csv', index=False)
    print(f"\nData saved to: GARP.csv")
except Exception as e:
    print(f"Error saving file: {e}")

# === Rebalance Logic ===
current_file = 'GARP.csv'
previous_file = 'GARP_prev.csv'
rebalance_file = 'GARP_rebalance.csv'

if os.path.exists(previous_file):
    current_df = pd.read_csv(current_file)
    previous_df = pd.read_csv(previous_file)

    current_names = set(current_df['Name'].str.strip())
    previous_names = set(previous_df['Name'].str.strip())

    added = sorted(current_names - previous_names)
    removed = sorted(previous_names - current_names)

    added_cmp = current_df.set_index('Name').reindex(added)['CMP  Rs.']
    removed_cmp = previous_df.set_index('Name').reindex(removed)['CMP  Rs.']

    # Use reset_index to avoid ValueError
    rebalance_df = pd.DataFrame({
        'Added Stocks': pd.Series(added).reset_index(drop=True),
        'CMP Rs. (Added)': added_cmp.reset_index(drop=True),
        'Removed Stocks': pd.Series(removed).reset_index(drop=True),
        'CMP Rs. (Removed)': removed_cmp.reset_index(drop=True)
    })

    rebalance_df.to_csv(rebalance_file, index=False)
    print(f"\nRebalance data saved to: {rebalance_file}")

else:
    print(f"\n{previous_file} not found. Skipping rebalance comparison.")

# === Final Save State ===
os.replace(current_file, previous_file)
merged_df.to_csv(current_file, index=False)

print("\n=== Final Results ===")
print(merged_df)
                
