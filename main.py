#import sys
from sec import ticker_to_cik, cik_to_url, download_company_info, download_company_filings_data

def main():
    print("")
    print("============ Welcome to SEC filings' processor ============")
    print("")
    ticker = input("Enter a ticker symbol: ")
    print("")
    cik = ticker_to_cik(ticker)
    if cik == None: return
    submissions_url, facts_url = cik_to_url(cik)
    download_company_info(submissions_url)
    download_company_filings_data(facts_url)

if __name__ == "__main__":
    main()