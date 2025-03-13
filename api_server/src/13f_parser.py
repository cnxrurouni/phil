import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import re
from pathlib import Path
import csv
from typing import Dict, Set, List, Tuple
import time
from datetime import datetime
from sqlalchemy.orm import Session
from Company import InstitutionalHolding, Session as DBSession

class SEC13FParser:
    def __init__(self, target_quarter: str = None):
        self.headers = {
            'User-Agent': 'NoCap puppyia.o@gmail.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        self.cusip_to_ticker: Dict[str, str] = {}
        self.filings_processed = 0
        self.start_time = None
        self.target_quarter = target_quarter or self._get_current_quarter()
        self.db_session = DBSession()

    def _get_current_quarter(self) -> str:
        """Get the most recent completed quarter date in format MM-DD-YYYY"""
        now = datetime.now()
        year = now.year
        month = now.month
        
        if month <= 3:
            return f"12-31-{year-1}"  # Previous year Q4
        elif month <= 6:
            return f"03-31-{year}"    # Q1
        elif month <= 9:
            return f"06-30-{year}"    # Q2
        else:
            return f"09-30-{year}"    # Q3

    def _validate_quarter_format(self, date_str: str) -> bool:
        """Validate if the date string matches the required quarter end format"""
        valid_patterns = [
            r'12-31-\d{4}',  # Q4
            r'09-30-\d{4}',  # Q3
            r'06-30-\d{4}',  # Q2
            r'03-31-\d{4}'   # Q1
        ]
        return any(re.match(pattern, date_str) for pattern in valid_patterns)

    def _get_quarter_from_date(self, date_str: str) -> str:
        """Convert date string to quarter format (e.g., 'Q4-2024')"""
        if not self._validate_quarter_format(date_str):
            raise ValueError(f"Invalid date format: {date_str}")
        
        month = date_str.split('-')[0]
        year = date_str.split('-')[2]
        quarter_map = {'03': 'Q1', '06': 'Q2', '09': 'Q3', '12': 'Q4'}
        return f"{quarter_map[month]}-{year}"

    def load_company_mappings(self, ticker_file: str = '13FTickers.csv'):
        """Load CUSIP to ticker mappings"""
        df = pd.read_csv(ticker_file)
        self.cusip_to_ticker = dict(zip(df['Cusip'], df['Ticker']))

    def process_13f_filing(self, url: str):
        """Process a single 13F-HR filing"""
        try:
            response = self.make_request(url)
            soup = BeautifulSoup(response.content, 'lxml')
            
            filing_period = self._get_filing_period(soup)
            if not self._validate_quarter_format(filing_period) or filing_period != self.target_quarter:
                return
                
            manager_name = self._get_manager_name(soup)
            holdings = self._parse_holdings(soup)
            quarter = self._get_quarter_from_date(filing_period)
            filing_date = datetime.strptime(filing_period, '%m-%d-%Y').date()
            
            # Store holdings in database
            for cusip, shares in holdings.items():
                if cusip in self.cusip_to_ticker:
                    ticker = self.cusip_to_ticker[cusip]
                    holding = InstitutionalHolding(
                        company_ticker=ticker,
                        holder_name=manager_name,
                        shares=shares,
                        filing_date=filing_date,
                        quarter=quarter
                    )
                    self.db_session.add(holding)
            
            self.db_session.commit()
                    
        except Exception as e:
            print(f"Error processing 13F filing {url}: {e}")
            self.db_session.rollback()

    def cleanup(self):
        """Cleanup database session"""
        self.db_session.close()

    def print_progress(self):
        """Print progress update with timing information"""
        if self.filings_processed % 200 == 0 and self.filings_processed > 0:
            elapsed_time = time.time() - self.start_time
            avg_time_per_filing = elapsed_time / self.filings_processed
            print(f"\nProgress Update:")
            print(f"Total 13F filings processed: {self.filings_processed}")
            print(f"Average processing time per filing: {avg_time_per_filing:.2f} seconds")
            print(f"Total elapsed time: {elapsed_time/60:.2f} minutes")
            print("Still processing...\n")

    def make_request(self, url: str, max_retries: int = 3) -> requests.Response:
        """Make HTTP request with retry logic and rate limiting"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                time.sleep(0.1)  # Rate limiting
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1 * (attempt + 1))
        raise Exception(f"Failed to fetch {url} after {max_retries} attempts")

    def should_process_file(self, file_date: str) -> bool:
        """Determine if a file should be processed based on last run date"""
        if not self.target_quarter:
            return True
        return file_date > self.target_quarter

    def process_index_page(self, url: str):
        """Process the quarterly index page to find daily company indices"""
        print("Starting to process SEC index page...")
        self.start_time = time.time()
        
        response = self.make_request(url)
        soup = BeautifulSoup(response.content, 'lxml')
        base_url = 'https://www.sec.gov/Archives/edgar/daily-index/2025/QTR1/'
        
        # Sort links by date to process in chronological order
        links = []
        for link in soup.find_all('a', href=re.compile(r'company.*\.idx')):
            date_match = re.search(r'(\d{8})', link['href'])
            if date_match:
                file_date = date_match.group(1)
                if self.should_process_file(file_date):
                    links.append((file_date, base_url + link['href']))
        
        print(f"Found {len(links)} daily index files to process")
        
        # Process links in chronological order
        for file_date, daily_url in sorted(links):
            print(f"Processing files for date: {file_date}")
            self.process_daily_index(daily_url)

    def process_daily_index(self, url: str):
        """Process a daily index file to find 13F-HR filings"""
        response = self.make_request(url)
        
        for line in response.text.split('\n'):
            if '13F-HR' in line and '.txt' in line:
                try:
                    filing_path = line.split('edgar/data/')[-1].split('.txt')[0] + '.txt'
                    filing_url = f'https://www.sec.gov/Archives/edgar/data/{filing_path}'
                    self.process_13f_filing(filing_url)
                    self.filings_processed += 1
                    self.print_progress()
                except Exception as e:
                    print(f"Error processing line in daily index: {e}")
                    continue

    def _get_filing_period(self, soup) -> str:
        """Extract filing period from document"""
        try:
            filer_xml = soup.find_all('xml')[0]
            return filer_xml.filerinfo.periodofreport.text
        except:
            return ""

    def _get_manager_name(self, soup) -> str:
        """Extract manager name from document"""
        try:
            filer_xml = soup.find_all('xml')[0]
            return filer_xml.formdata.filingmanager.find('name').string.strip()
        except:
            return "Unknown Manager"

    def _parse_holdings(self, soup) -> Dict[str, int]:
            """Parse holdings from document, handling both ns1 and regular formats"""
            holdings: Dict[str, int] = {}
            main_filing = soup.find_all('xml')[1]
            
            # Try ns1 format first
            info_tables = main_filing.find_all('ns1:infotable') or main_filing.find_all('infotable')
            
            for table in info_tables:
                try:
                    # Handle both namespace variants
                    cusip = (table.find('ns1:cusip') or table.find('cusip')).text.strip()
                    sshprnamttype = (table.find('ns1:sshprnamttype') or 
                                    table.find('shrsorprnamt').find('sshprnamttype')).text.strip()
                    
                    # Skip if not shares or if it's a put/call
                    if sshprnamttype != "SH" or table.find('putcall'):
                        continue
                        
                    shares = int((table.find('ns1:sshprnamt') or 
                                table.find('shrsorprnamt').find('sshprnamt')).text.strip())
                    
                    holdings[cusip] = holdings.get(cusip, 0) + shares
                    
                except Exception as e:
                    print(f"Error parsing holding: {e}")
                    continue
                    
            return holdings

def main():
    print("Initializing 13F parser...")
    
    # Example: Parse Q4 2024 data
    parser = SEC13FParser(target_quarter="12-31-2024")
    
    print("Loading company mappings...")
    parser.load_company_mappings()
    
    try:
        parser.process_index_page('https://www.sec.gov/Archives/edgar/daily-index/2025/QTR1/index.html')
        
        print("\nProcessing complete!")
        print(f"Total 13F filings processed: {parser.filings_processed}")
        total_time = time.time() - parser.start_time
        print(f"Total execution time: {total_time/60:.2f} minutes")
        
        parser.cleanup()
        print("All done!")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        parser.cleanup()

if __name__ == "__main__":
    main()