"""
SentinelAlpha — SEC EDGAR API Client
Fetches and parses SEC filings (10-K, 10-Q, 8-K) from the EDGAR database.
"""

import requests
import re
import time
from bs4 import BeautifulSoup
from config import SEC_BASE_URL, SEC_USER_AGENT, TICKER_CIK_MAP


def get_cik(ticker: str) -> str | None:
    """Resolve a stock ticker to its SEC CIK number."""
    ticker = ticker.upper().strip()
    if ticker in TICKER_CIK_MAP:
        return TICKER_CIK_MAP[ticker]
    
    # Fallback: query SEC company tickers JSON
    try:
        headers = {"User-Agent": SEC_USER_AGENT}
        resp = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=headers, timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            for entry in data.values():
                if entry.get("ticker", "").upper() == ticker:
                    return str(entry["cik_str"]).zfill(10)
    except Exception:
        pass
    return None


def get_recent_filings(ticker: str, form_type: str | list[str] = "10-K", count: int = 5) -> list[dict]:
    """
    Get a list of recent SEC filings for a given ticker.
    Returns list of dicts with keys: accessionNumber, filingDate, form, primaryDocument.
    """
    cik = get_cik(ticker)
    if not cik:
        return []
    
    headers = {"User-Agent": SEC_USER_AGENT}
    url = f"{SEC_BASE_URL}/submissions/CIK{cik}.json"
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        recent = data.get("filings", {}).get("recent", {})
        
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])
        
        target_forms = form_type if isinstance(form_type, list) else [form_type]
        
        filings = []
        for i, form in enumerate(forms):
            if form in target_forms and len(filings) < count:
                filings.append({
                    "accessionNumber": accessions[i],
                    "filingDate": dates[i],
                    "form": form,
                    "primaryDocument": primary_docs[i] if i < len(primary_docs) else "",
                    "cik": cik.lstrip("0"),
                })
        return filings
    except Exception as e:
        print(f"[SEC Client] Error fetching filings: {e}")
        return []


def get_filing_document(filing: dict, max_chars: int = 15000) -> str:
    """
    Download and parse the full text of a filing document.
    Returns cleaned text, truncated to max_chars for LLM context limits.
    """
    cik = filing.get("cik", "")
    accession = filing.get("accessionNumber", "").replace("-", "")
    primary_doc = filing.get("primaryDocument", "")
    
    if not all([cik, accession, primary_doc]):
        return ""
    
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_doc}"
    headers = {"User-Agent": SEC_USER_AGENT}
    
    try:
        time.sleep(0.15)  # Respect SEC rate limits
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            return ""
        
        content_type = resp.headers.get("Content-Type", "")
        
        if "html" in content_type or primary_doc.endswith(".htm") or primary_doc.endswith(".html"):
            soup = BeautifulSoup(resp.text, "lxml")
            # Remove scripts, styles, and tables (too noisy)
            for tag in soup(["script", "style"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
        else:
            text = resp.text
        
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text[:max_chars]
    except Exception as e:
        print(f"[SEC Client] Error downloading filing: {e}")
        return ""


def extract_risk_factors(full_text: str, max_chars: int = 8000) -> str:
    """Extract the 'Risk Factors' section from a 10-K/10-Q filing."""
    patterns = [
        r"(?i)(item\s*1a[\.\s]*risk\s*factors)(.*?)(item\s*1b|item\s*2[\.\s])",
        r"(?i)(risk\s*factors)(.*?)(unresolved\s*staff\s*comments|properties|legal\s*proceedings)",
    ]
    for pattern in patterns:
        match = re.search(pattern, full_text, re.DOTALL)
        if match:
            section = match.group(1) + match.group(2)
            return section[:max_chars]
    
    # Fallback: return a chunk around "risk" mentions
    idx = full_text.lower().find("risk factors")
    if idx != -1:
        return full_text[idx:idx + max_chars]
    
    return full_text[:max_chars]


def extract_mda(full_text: str, max_chars: int = 8000) -> str:
    """Extract Management Discussion & Analysis section."""
    patterns = [
        r"(?i)(item\s*7[\.\s]*management.s?\s*discussion)(.*?)(item\s*7a|item\s*8[\.\s])",
        r"(?i)(management.s?\s*discussion\s*and\s*analysis)(.*?)(quantitative\s*and\s*qualitative|financial\s*statements)",
    ]
    for pattern in patterns:
        match = re.search(pattern, full_text, re.DOTALL)
        if match:
            section = match.group(1) + match.group(2)
            return section[:max_chars]
    
    idx = full_text.lower().find("management's discussion")
    if idx == -1:
        idx = full_text.lower().find("management discussion")
    if idx != -1:
        return full_text[idx:idx + max_chars]
    
    return ""


def get_company_name(ticker: str) -> str:
    """Get the official company name from SEC."""
    cik = get_cik(ticker)
    if not cik:
        return ticker
    
    headers = {"User-Agent": SEC_USER_AGENT}
    url = f"{SEC_BASE_URL}/submissions/CIK{cik}.json"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("name", ticker)
    except Exception:
        pass
    return ticker
