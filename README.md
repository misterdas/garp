# GARP Stock Screener

### Screens Used:
- 3-Month: https://www.screener.in/screens.....
- 6-Month: https://www.screener.in/screens.....
- 12-Month: https://www.screener.in/screens.....

### Output Files:
- `GARP.csv` – Final stock list
- `GARP_prev.csv` – Previous run data
- `GARP_rebalance.csv` – Added/Removed stocks

### Dependencies:
- beautifulsoup4==4.11.2  
- pandas  
- openpyxl
- html5lib

### Run Command:
```bash
python garp_screener.py
