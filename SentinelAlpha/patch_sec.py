import re
with open('D:/Apex_Paragon/AI-APEX-PARAGON/SentinelAlpha/sec_client.py', 'r', encoding='utf-8') as f:
    content = f.read()

robust_funcs = '''
import random

def _get_free_proxy() -> str | None:
    try:
        url = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=US&ssl=yes&anonymity=elite'
        # We must use requests directly here to avoid infinite recursion
        import requests as _req
        resp = _req.get(url, timeout=5)
        proxies = [p for p in resp.text.strip().split('\\r\\n') if p]
        if proxies:
            return random.choice(proxies)
    except Exception:
        pass
    return None

def _robust_get(url: str, headers: dict, timeout: int = 15):
    import requests as _req
    try:
        resp = _req.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 403:
            raise PermissionError("403 Forbidden")
        return resp
    except Exception as e:
        print(f"[SEC Client] Direct connection failed ({e}). Attempting proxy rotation...")
        for i in range(3):
            proxy = _get_free_proxy()
            if not proxy:
                continue
            print(f"[SEC Client] Trying proxy: {proxy}")
            try:
                proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
                resp = _req.get(url, headers=headers, proxies=proxies, timeout=timeout)
                if resp.status_code == 200:
                    print("[SEC Client] Proxy request successful.")
                    return resp
            except Exception:
                continue
        # Fallback to a final direct request that will raise the actual HTTP error
        return _req.get(url, headers=headers, timeout=timeout)

'''

# Insert after the imports
imports_end = content.find('def get_cik')
if imports_end != -1:
    content = content[:imports_end] + robust_funcs + content[imports_end:]

# Replace requests.get
content = re.sub(r'requests\.get\(', '_robust_get(', content)

with open('D:/Apex_Paragon/AI-APEX-PARAGON/SentinelAlpha/sec_client.py', 'w', encoding='utf-8') as f:
    f.write(content)
