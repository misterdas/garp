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
            
            # Check if required columns exist
            required_columns = ['S.No.', 'Name']
            if not all(col in combined_df.columns for col in required_columns):
                print(f"Required columns {required_columns} not found on page {current_page}")
                break
            
            # Remove rows where S.No. is null
            combined_df = combined_df.drop(
                combined_df[combined_df['S.No.'].isnull()].index)
            
            # Remove header rows that might appear in data
            combined_df = combined_df[combined_df['S.No.'] != 'S.No.']
            
            # If no valid data rows found, we've reached the end
            if len(combined_df) == 0:
                print(f"No valid data found on page {current_page}. Stopping.")
                break
            
            print(f"Found {len(combined_df)} rows on page {current_page}")
            data = pd.concat([data, combined_df], axis=0, ignore_index=True)
            
            # Check if this is the last page
            if len(combined_df) < 25:  # Screener.in typically shows 25 rows per page
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
        time.sleep(3)  # Be respectful to the server
    
    print(f"Total rows fetched: {len(data)}")
    return data

pd.set_option("display.max_rows", None, "display.max_columns", None)

# Fetch 3 month return
print("=== Fetching 3 Month Returns ===")
garp3_link = 'https://www.screener.in/screens/2115435/garp3months/'
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

# Fetch 6 month return
print("\n=== Fetching 6 Month Returns ===")
garp6_link = 'https://www.screener.in/screens/2115440/garp6months/'
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

# Fetch 1 year return
print("\n=== Fetching 12 Month Returns ===")
garp12_link = 'https://www.screener.in/screens/2115445/garp12months/'
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

# Merge 3 / 6 / 12 Months Returns data into a single dataset
print("\n=== Merging Data ===")
merged_df = pd.merge(garp3_df, garp6_df, on='Name', how='inner')
merged_df = pd.merge(merged_df, garp12_df, on='Name', how='inner')
merged_df.dropna(inplace=True)

print(f"Final merged data: {len(merged_df)} stocks")

# Sort by 6 months return
if not merged_df.empty:
    merged_df = merged_df.sort_values(by=['6mth return  %'], ascending=False)
else:
    print("No data to sort. Merged DataFrame is empty.")

# Save final result in an excel
try:
    merged_df.to_excel('GARP.xlsx', index=False)
    print(f"\nData saved to: GARP.xlsx")
except Exception as e:
    print(f"Error saving file: {e}")
    print("Failed to save data to GARP.xlsx")

print("\n=== Final Results ===")
print(merged_df)
