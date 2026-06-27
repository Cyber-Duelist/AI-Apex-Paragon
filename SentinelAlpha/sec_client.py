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
    
    headers = {
        "User-Agent": SEC_USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
        "Host": "data.sec.gov"
    }
    url = f"{SEC_BASE_URL}/submissions/CIK{cik}.json"
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 403:
            raise PermissionError("SEC EDGAR blocked this IP (HTTP 403).")
        if resp.status_code != 200:
            raise ValueError(f"SEC EDGAR returned HTTP {resp.status_code}.")
        
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
        raise e


def _find_htm_filing(cik: str, accession_no: str) -> str:
    """
    Look at the filing index to find the best HTML document to parse.
    Prefers the full filing document (not XBRL viewer or R-files).
    """
    accession_clean = accession_no.replace("-", "")
    index_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/"
    headers = {"User-Agent": SEC_USER_AGENT}
    
    try:
        time.sleep(0.12)
        resp = requests.get(index_url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return ""
        
        soup = BeautifulSoup(resp.text, "lxml")
        
        # Look for links to .htm files in the filing index
        candidates = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            fname = href.split("/")[-1].lower()
            
            # Skip R-files (XBRL viewer), xml files, zip files, xsd files
            if fname.startswith("r") and fname[1:].replace(".", "").isdigit():
                continue
            if fname.endswith((".xml", ".xsd", ".zip", ".json", ".xlsx")):
                continue
            if "filingsummary" in fname.lower():
                continue
                
            # Prefer .htm or .html files
            if fname.endswith((".htm", ".html")):
                # Prefer files that look like the main filing (contain 10k, 10-k, annual, etc.)
                text = link.get_text(strip=True).lower()
                size_priority = 0
                if any(kw in fname for kw in ["10k", "10-k", "10q", "10-q", "annual", "quarterly"]):
                    size_priority = 3
                elif any(kw in text for kw in ["10-k", "10-q", "annual report", "quarterly report"]):
                    size_priority = 2
                elif fname.endswith(".htm"):
                    size_priority = 1
                candidates.append((size_priority, href.split("/")[-1]))
        
        # Sort by priority (highest first) and return the best
        candidates.sort(key=lambda x: x[0], reverse=True)
        if candidates:
            return candidates[0][1]
    except Exception as e:
        print(f"[SEC Client] Error browsing filing index: {e}")
    
    return ""


def _clean_ixbrl_text(html_content: str) -> str:
    """
    Parse HTML/iXBRL content and extract clean readable text.
    Strips XBRL metadata, hidden elements, and other noise.
    """
    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove script and style tags
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    # Remove hidden XBRL sections (ix:hidden contains metadata facts)
    for tag in soup.find_all(re.compile(r'^ix:hidden$', re.I)):
        tag.decompose()
    
    # Remove elements with display:none (hidden XBRL data blocks)
    for tag in soup.find_all(style=re.compile(r'display\s*:\s*none', re.I)):
        tag.decompose()
    
    # Remove elements with visibility:hidden
    for tag in soup.find_all(style=re.compile(r'visibility\s*:\s*hidden', re.I)):
        tag.decompose()
    
    # Remove ix:header elements (XBRL document headers with metadata)
    for tag in soup.find_all(re.compile(r'^ix:header$', re.I)):
        tag.decompose()
    
    # Remove ix:references elements 
    for tag in soup.find_all(re.compile(r'^ix:references$', re.I)):
        tag.decompose()
    
    # Remove ix:resources elements (contain hidden context/unit definitions)
    for tag in soup.find_all(re.compile(r'^ix:resources$', re.I)):
        tag.decompose()
    
    # For remaining ix: tags (ix:nonFraction, ix:nonNumeric, etc.), keep text content
    for tag in soup.find_all(re.compile(r'^ix:', re.I)):
        tag.unwrap()
    
    # Get text
    text = soup.get_text(separator="\n", strip=True)
    
    # Remove XBRL namespace URLs and technical metadata from text
    text = re.sub(r'https?://[^\s]*(?:xbrl|fasb|sec\.gov/cgi)[^\s]*', '', text)
    text = re.sub(r'https?://fasb\.org[^\s]*', '', text)
    text = re.sub(r'https?://xbrl\.sec\.gov[^\s]*', '', text)
    
    # Remove lines that are just CIK numbers, accession numbers, or boolean values
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip very short lines that are just metadata
        if stripped in ("TRUE", "FALSE", "true", "false", "FY", "Q1", "Q2", "Q3", "Q4"):
            continue
        # Skip lines that are just numbers (CIK, accession fragments)
        if re.match(r'^[\d\-\.]+$', stripped) and len(stripped) < 20:
            continue
        # Skip empty or near-empty lines
        if len(stripped) < 3:
            continue
        cleaned_lines.append(stripped)
    
    text = "\n".join(cleaned_lines)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    return text


def get_filing_document(filing: dict, max_chars: int = 15000) -> str:
    """
    Download and parse the full text of a filing document.
    Returns cleaned text, truncated to max_chars for LLM context limits.
    """
    cik = filing.get("cik", "")
    accession = filing.get("accessionNumber", "")
    accession_clean = accession.replace("-", "")
    primary_doc = filing.get("primaryDocument", "")
    
    if not all([cik, accession_clean, primary_doc]):
        return ""
    
    headers = {"User-Agent": SEC_USER_AGENT}
    
    # Try the primary document first
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{primary_doc}"
    
    try:
        time.sleep(0.15)  # Respect SEC rate limits
        print(f"[SEC Client] Downloading filing: {url}")
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"[SEC Client] HTTP {resp.status_code} for primary doc")
            return ""
        
        text = _clean_ixbrl_text(resp.text)
        
        # Check if we got useful text (not just XBRL metadata)
        if len(text) < 500 or text.count("http") > text.count(" ") / 10:
            print(f"[SEC Client] Primary doc appears to be XBRL-heavy ({len(text)} chars). Trying filing index...")
            
            # Try finding a better document from the filing index
            alt_doc = _find_htm_filing(cik, accession)
            if alt_doc and alt_doc != primary_doc:
                alt_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{alt_doc}"
                time.sleep(0.15)
                print(f"[SEC Client] Trying alternative doc: {alt_url}")
                alt_resp = requests.get(alt_url, headers=headers, timeout=30)
                if alt_resp.status_code == 200:
                    alt_text = _clean_ixbrl_text(alt_resp.text)
                    if len(alt_text) > len(text):
                        print(f"[SEC Client] Alternative doc is better: {len(alt_text)} chars vs {len(text)}")
                        text = alt_text
        
        print(f"[SEC Client] Extracted {len(text)} chars of clean text")
        return text[:max_chars]
    except Exception as e:
        print(f"[SEC Client] Error downloading filing: {e}")
        return ""


def extract_risk_factors(full_text: str, max_chars: int = 8000) -> str:
    """Extract the 'Risk Factors' section from a 10-K/10-Q filing."""
    patterns = [
        r"(?i)(item\s*1a[\.:\s]*risk\s*factors)(.*?)(item\s*1b|item\s*2[\.:\s])",
        r"(?i)(risk\s*factors)(.*?)(unresolved\s*staff\s*comments|properties|legal\s*proceedings)",
    ]
    for pattern in patterns:
        match = re.search(pattern, full_text, re.DOTALL)
        if match:
            section = match.group(1) + match.group(2)
            if len(section.strip()) > 200:
                print(f"[SEC Client] Extracted Risk Factors: {len(section)} chars")
                return section[:max_chars]
    
    # Fallback: return a chunk around "risk" mentions
    idx = full_text.lower().find("risk factors")
    if idx != -1:
        section = full_text[idx:idx + max_chars]
        print(f"[SEC Client] Risk Factors fallback: {len(section)} chars from position {idx}")
        return section
    
    print("[SEC Client] No Risk Factors section found")
    return full_text[:max_chars]


def extract_mda(full_text: str, max_chars: int = 8000) -> str:
    """Extract Management Discussion & Analysis section."""
    patterns = [
        r"(?i)(item\s*7[\.:\s]*management.s?\s*discussion)(.*?)(item\s*7a|item\s*8[\.:\s])",
        r"(?i)(management.s?\s*discussion\s*and\s*analysis)(.*?)(quantitative\s*and\s*qualitative|financial\s*statements)",
    ]
    for pattern in patterns:
        match = re.search(pattern, full_text, re.DOTALL)
        if match:
            section = match.group(1) + match.group(2)
            if len(section.strip()) > 200:
                print(f"[SEC Client] Extracted MD&A: {len(section)} chars")
                return section[:max_chars]
    
    idx = full_text.lower().find("management's discussion")
    if idx == -1:
        idx = full_text.lower().find("management discussion")
    if idx != -1:
        section = full_text[idx:idx + max_chars]
        print(f"[SEC Client] MD&A fallback: {len(section)} chars from position {idx}")
        return section
    
    print("[SEC Client] No MD&A section found")
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
