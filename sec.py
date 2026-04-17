import requests
from datetime import datetime

def ticker_to_cik(ticker):
    ticker = ticker.upper().strip()
    
    headers = {
        'User-Agent': 'First Last f.last@email.com',
        'Accept-Encoding': 'gzip, deflate'
    }

    mapping_url = "https://www.sec.gov/files/company_tickers.json"
    mapping_res = requests.get(mapping_url, headers=headers)
    mapping_res.raise_for_status()
    ticker_data = mapping_res.json()
        
    cik = next((item['cik_str'] for item in ticker_data.values() if item['ticker'] == ticker), None)
        
    if cik is None:
        print(f"Error: Ticker '{ticker}' not found in SEC mapping.")
        return

    padded_cik = str(cik).zfill(10)
    return padded_cik

def cik_to_url(padded_cik):
    submissions_url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
    facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json"
    return submissions_url, facts_url

def download_company_info(submissions_url):
    format_spaces = 25
    headers = {
        'User-Agent': 'First Last f.last@email.com',
        'Accept-Encoding': 'gzip, deflate'
    }
    subs_res = requests.get(submissions_url, headers=headers)
    subs_res.raise_for_status()
    data = subs_res.json()
    company_name = data["name"]
    company_cik = data["cik"]
    entity_type = data["entityType"]
    sic_description = data["sicDescription"]
    company_ticker = data["tickers"][0].upper()
    exchanges = ", ".join(data["exchanges"])
    fiscal = data["fiscalYearEnd"]
    if int(fiscal[:2]) >= datetime.now().month and int(fiscal[2:]) >= datetime.now().day:
        year = datetime.now().year
    else:
        year = datetime.now().year + 1
    fiscal_year_end = f"{year}-{fiscal[:2]}-{fiscal[2:]}"
    company_address = f"{data["addresses"]["business"]["city"].capitalize()}, {data["addresses"]["business"]["stateOrCountry"].upper()}, {data["addresses"]["business"]["zipCode"]}"
    print(f"{"Company name:":<{format_spaces}} {company_name}")
    print(f"{"Company ticker:":<{format_spaces}} {company_ticker}")
    print(f"{"Company cik:":<{format_spaces}} {company_cik}")
    print(f"{"Industry classification:":<{format_spaces}} {sic_description}")
    print(f"{"Exchanges traded:":<{format_spaces}} {exchanges}")
    print(f"{"Company address:":<{format_spaces}} {company_address}")
    print(f"{"Fiscal year end:":<{format_spaces}} {fiscal_year_end}")
    print("")

def download_company_filings_data(facts_url):
    while True:
        print("For DIVIDENDS enter '1'")
        print("For EARNINGS PER SHARE enter '2'")
        print("For ASSETS enter '3'")
        print("To exit enter 'q'")
        item_choice = input("Choose item to display: ").strip()
        print("")
        match item_choice:
            case '1':
                download_company_dividend_data(facts_url)
            case '2':
                download_company_earnings_data(facts_url)
            case '3':
                download_company_assets_data(facts_url)
            case 'q' | 'Q':
                print("=== Exiting ===")
                break
            case _:
                print("ERROR: This is not a valid choice. Try again!")
                print("")

def download_company_dividend_data(facts_url):
    to_display = 20
    headers = {
        'User-Agent': 'First Last f.last@email.com',
        'Accept-Encoding': 'gzip, deflate'
    }
    subs_res = requests.get(facts_url, headers=headers)
    subs_res.raise_for_status()
    data = subs_res.json()
    facts_data = data["facts"]["us-gaap"]
    dividend_data = facts_data["CommonStockDividendsPerShareDeclared"]["units"]["USD/shares"]
    sorted_dividend_data = sorted(
        dividend_data,
        key=lambda x: datetime.strptime(x["end"], "%Y-%m-%d"),
        reverse=True
    )[:to_display]

    result = [
    {
        "USD/share": item.get("val"),
        "start": item.get("start"),
        "end": item.get("end"),
        "form": item.get("form"),
        "filed": item.get("filed"),
    }
        for item in sorted_dividend_data
    ]

    print("=== Dividends per share ===")
    print_table(result)

def download_company_earnings_data(facts_url):
    to_display = 20
    headers = {
        'User-Agent': 'First Last f.last@email.com',
        'Accept-Encoding': 'gzip, deflate'
    }
    subs_res = requests.get(facts_url, headers=headers)
    subs_res.raise_for_status()
    data = subs_res.json()
    facts_data = data["facts"]["us-gaap"]
    dividend_data = facts_data["EarningsPerShareBasic"]["units"]["USD/shares"]
    sorted_dividend_data = sorted(
        dividend_data,
        key=lambda x: datetime.strptime(x["end"], "%Y-%m-%d"),
        reverse=True
    )[:to_display]

    result = [
    {
        "USD/share": item.get("val"),
        "start": item.get("start"),
        "end": item.get("end"),
        "form": item.get("form"),
        "filed": item.get("filed"),
    }
        for item in sorted_dividend_data
    ]

    print("=== Earnings per share ===")
    print_table(result)

def download_company_assets_data(facts_url):
    to_display = 20
    headers = {
        'User-Agent': 'First Last f.last@email.com',
        'Accept-Encoding': 'gzip, deflate'
    }
    subs_res = requests.get(facts_url, headers=headers)
    subs_res.raise_for_status()
    data = subs_res.json()
    facts_data = data["facts"]["us-gaap"]
    dividend_data = facts_data["Assets"]["units"]["USD"]
    sorted_dividend_data = sorted(
        dividend_data,
        key=lambda x: datetime.strptime(x["end"], "%Y-%m-%d"),
        reverse=True
    )[:to_display]

    result = [
    {
        "USD (mil)": item.get("val") / 1000000,
        "end": item.get("end"),
        "form": item.get("form"),
        "filed": item.get("filed"),
    }
        for item in sorted_dividend_data
    ]

    print("=== Assets ===")
    print_table(result)

def print_table(rows):
    if not rows:
        print("No records available.")
        return

    columns = list(rows[0].keys())
    str_rows = [[str(row.get(col, "")) for col in columns] for row in rows]
    widths = [max(len(col), max(len(r[i]) for r in str_rows)) for i, col in enumerate(columns)]

    separator = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header = "| " + " | ".join(col.ljust(widths[i]) for i, col in enumerate(columns)) + " |"

    print(separator)
    print(header)
    print(separator)
    for row in str_rows:
        print("| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(columns))) + " |")
    print(separator)