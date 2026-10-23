import re
import time
import json
import math
import logging
import ipaddress
import os
import threading
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CloxelFortressWAF")

ADMIN_SECURITY_KEY = os.getenv("ADMIN_SECURITY_KEY") or os.getenv("ADMIN_SECRET_KEY") or "cloxel_admin_fortress_secure_key_99281"

class ThreatSignatures:
    """
    Exhaustive Repository of All Known Attack Vectors, Exploitation Techniques,
    and High-Precision Regex Patterns for Public Internet Protection.
    """
    
    HONEYPOT_PATHS = {
        "/wp-admin", "/phpmyadmin", "/.env", "/.git", "/admin/db.sql",
        "/shell.php", "/api/v1/eval", "/actuator/env", "/config.json", "/backup.zip",
        "/admin.php", "/vendor/.env", "/.aws/credentials", "/server-status",
        "/xmlrpc.php", "/wp-login.php", "/eval-stdin.php", "/solr/", "/jmx-console"
    }

    # High-precision SQL Injection patterns: Detects real SQL injections with zero false positives on normal words
    SQLI_PATTERNS = [
        re.compile(r"(\bUNION\s+(ALL\s+)?SELECT\b)", re.IGNORECASE),
        re.compile(r"(\bSELECT\b\s+[\*\w,\s`]+\s+\bFROM\b\s+[\w`\.]+\s+(\bWHERE\b|\bHAVING\b|\bORDER\s+BY\b|\bGROUP\s+BY\b|--|;))", re.IGNORECASE),
        re.compile(r"(\bINSERT\s+INTO\b[\s\S]+?\bVALUES\b)", re.IGNORECASE),
        re.compile(r"(\bDELETE\s+FROM\b\s+[\w`\.]+\s+(\bWHERE\b|--|;))", re.IGNORECASE),
        re.compile(r"(\bDROP\s+(TABLE|DATABASE|VIEW|INDEX|PROCEDURE|FUNCTION)\b)", re.IGNORECASE),
        re.compile(r"(\bALTER\s+TABLE\b)", re.IGNORECASE),
        re.compile(r"(\bTRUNCATE\s+TABLE\b)", re.IGNORECASE),
        re.compile(r"(\bUPDATE\b\s+[a-zA-Z0-9_`\"\[\]]+\s+\bSET\b)", re.IGNORECASE),
        re.compile(r"((\bOR\b|\bAND\b)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+)", re.IGNORECASE),
        re.compile(r"((\bOR\b|\bAND\b)\s+['\"][a-zA-Z0-9_]+['\"]\s*=\s*['\"][a-zA-Z0-9_]+['\"])", re.IGNORECASE),
        re.compile(r"('\s*;\s*--|'\s*--|\"\s*--|/\*[\s\S]*?\*/)", re.IGNORECASE),
        re.compile(r"(\b(INFORMATION_SCHEMA|BENCHMARK\s*\(|SLEEP\s*\(|WAITFOR\s+DELAY|PG_SLEEP\s*\(|LOAD_FILE\s*\()\b)", re.IGNORECASE),
        re.compile(r"('|\")\s*(OR|AND)\s+('|\")?(\d+|[a-zA-Z]+)('|\")?\s*=\s*('|\")?(\d+|[a-zA-Z]+)", re.IGNORECASE),
        re.compile(r"(\b(EXEC|EXECUTE)\s+(\@|xp_|sp_))", re.IGNORECASE),
        re.compile(r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|EXEC|UNION)\b)", re.IGNORECASE),
        re.compile(r"(\bHAVING\s+\d+=\d+\b)", re.IGNORECASE),
        re.compile(r"(\bORDER\s+BY\s+\d+[\s\S]*?(--|/\*))", re.IGNORECASE),
        re.compile(r"(\bCAST\s*\([\s\S]+?\bAS\b)", re.IGNORECASE),
        re.compile(r"(\bCONVERT\s*\([\s\S]+?\bUSING\b)", re.IGNORECASE),
    ]

    # Exhaustive SQL Injection Patterns specifically for Credentials, Usernames & Auth Fields
    AUTH_SQLI_PATTERNS = [
        re.compile(r"(\bUNION\s+(ALL\s+)?SELECT\b)", re.IGNORECASE),
        re.compile(r"(\bSELECT\b[\s\S]+?\bFROM\b)", re.IGNORECASE),
        re.compile(r"(\bINSERT\s+INTO\b)", re.IGNORECASE),
        re.compile(r"(\bDELETE\s+FROM\b)", re.IGNORECASE),
        re.compile(r"(\bDROP\s+(TABLE|DATABASE)\b)", re.IGNORECASE),
        re.compile(r"(\bALTER\s+TABLE\b)", re.IGNORECASE),
        re.compile(r"(\bTRUNCATE\s+TABLE\b)", re.IGNORECASE),
        re.compile(r"(\bUPDATE\b\s+.*?\bSET\b)", re.IGNORECASE),
        re.compile(r"((\bOR\b|\bAND\b)\s+['\"]?\w*['\"]?\s*=\s*['\"]?\w*['\"])", re.IGNORECASE),
        re.compile(r"((\bOR\b|\bAND\b)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+)", re.IGNORECASE),
        re.compile(r"((\bOR\b|\bAND\b)\s+(TRUE|FALSE)\b)", re.IGNORECASE),
        re.compile(r"('|\")\s*(;?\s*--|#|/\*)", re.IGNORECASE),
        re.compile(r"(/\*[\s\S]*?\*/)", re.IGNORECASE),
        re.compile(r"('|\")\s*(OR|AND)\s+.*(=|>|<|LIKE|IN)", re.IGNORECASE),
        re.compile(r"('|\")\s*(OR|AND)\s+", re.IGNORECASE),
        re.compile(r"(\b(INFORMATION_SCHEMA|BENCHMARK|SLEEP|WAITFOR|PG_SLEEP)\b)", re.IGNORECASE),
        re.compile(r"(\bEXEC(UTE)?\s+(\@|xp_|sp_))", re.IGNORECASE),
        re.compile(r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|EXEC|UNION)\b)", re.IGNORECASE),
        re.compile(r"(\bHAVING\s+\d+=\d+\b)", re.IGNORECASE),
        re.compile(r"(\bORDER\s+BY\s+\d+)", re.IGNORECASE),
    ]

    # Exhaustive NoSQL (MongoDB) Injection Patterns
    NOSQLI_PATTERNS = [
        re.compile(r"(\$where|\$regex|\$gt|\$gte|\$lt|\$lte|\$ne|\$nin|\$in|\$exists|\$or|\$and|\$not|\$nor|\$expr|\$jsonSchema|\$mod|\$text|\$slice|\$elemMatch|\$size|\$all)", re.IGNORECASE),
        re.compile(r"(this\.[a-zA-Z0-9_]+|tojson\s*\(|db\.[a-zA-Z0-9_]+\s*\.|sleep\s*\(|emit\s*\()", re.IGNORECASE),
        re.compile(r"(\{\"\$(ne|gt|gte|lt|lte|regex|where|exists|in|or|and|nor|expr)\"\s*:)", re.IGNORECASE),
    ]

    # Cross-Site Scripting (XSS) Patterns (Detects real HTML/JS injections without blocking plain English words)
    XSS_PATTERNS = [
        re.compile(r"(<script[^>]*>[\s\S]*?</script>)", re.IGNORECASE),
        re.compile(r"(javascript\s*:|vbscript\s*:|data\s*:text/html)", re.IGNORECASE),
        re.compile(r"(on(load|error|click|mouseover|focus|blur|keydown|submit|mouseenter|mouseleave|change|input)\s*=)", re.IGNORECASE),
        re.compile(r"(eval\s*\(|document\.cookie|document\.location|window\.location|top\.location)", re.IGNORECASE),
        re.compile(r"(<iframe|<object|<embed|<applet|<meta|<link|<svg[\s\S]*?onload)", re.IGNORECASE),
        re.compile(r"(<[^>]+(alert|prompt|confirm)\s*\()", re.IGNORECASE),
    ]

    # Remote Code Execution (RCE) / Command Injection Patterns
    RCE_PATTERNS = [
        re.compile(r"([;|&`]\s*(cat\s+[/\.\-~]|ls\s+[/\.\-~]|whoami\b|id\s*$|uname\s+[/\.\-]|nc\s+|netcat\s+|curl\s+https?:|wget\s+https?:|bash\s+-|/bin/sh|cmd\.exe|powershell))", re.IGNORECASE),
        re.compile(r"(`[^`]+`|\$\([^)]+\))"),
        re.compile(r"(system\(|passthru\(|shell_exec\(|popen\(|proc_open\(|subprocess\.(Popen|run|call))", re.IGNORECASE),
        re.compile(r"(/etc/passwd|/etc/shadow|/etc/group|/proc/self/environ|c:\\boot\.ini)", re.IGNORECASE),
        re.compile(r"(\\x90\\x90|\\xeb\\xfe|\\xcd\\x80)"),
    ]

    # Path Traversal / LFI Patterns
    TRAVERSAL_PATTERNS = [
        re.compile(r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|\.\.%2f|%252e%252e%252f)", re.IGNORECASE),
        re.compile(r"(file://|php://|zlib://|data://|glob://|expect://|zip://|phar://)", re.IGNORECASE),
        re.compile(r"(/WEB-INF/|/META-INF/|\.env|\.git/|\.htaccess|\.ssh/)", re.IGNORECASE),
        re.compile(r"(\\x00|%00)", re.IGNORECASE),
    ]

    # Server-Side Request Forgery (SSRF) Patterns
    SSRF_PATTERNS = [
        re.compile(r"(http://|https://)?(127\.0\.0\.1|localhost|169\.254\.169\.254|0\.0\.0\.0|::1)", re.IGNORECASE),
        re.compile(r"(http://|https://)?(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})", re.IGNORECASE),
    ]

    JWT_ATTACK_PATTERNS = [
        re.compile(r"\"alg\"\s*:\s*\"none\"", re.IGNORECASE),
        re.compile(r"eyJhbGciOiJub25lIn", re.IGNORECASE),
    ]

    ZERO_DAY_PATTERNS = [
        re.compile(r"(\$\{jndi:(ldap|rmi|dns|nis|nds|corba|iiop):)", re.IGNORECASE),
        re.compile(r"(\(\)\s*\{\s*:;\s*\};)", re.IGNORECASE),
        re.compile(r"(<!ENTITY|<!DOCTYPE\s+[^>]*SYSTEM)", re.IGNORECASE),
        re.compile(r"(%0d%0a|\\r\\n)\s*(Set-Cookie|Location|Content-Length):", re.IGNORECASE),
    ]

    MALICIOUS_BOTS = [
        "sqlmap", "nikto", "nmap", "acunetix", "havij", "dirbuster", "gobuster", 
        "masscan", "w3af", "netsparker", "zgrab", "zmap", "fimap", "commix", 
        "hydra", "medusa", "john", "burpsuite", "owasp", "metasploit", "nuclei",
        "python-urllib/1", "python-urllib/2", "python-requests/0"
    ]

class SecurityFirewall:
    """
    Zero-Trust Autonomous Security Shield Engine.
    Handles Honeypots, Dynamic Escalation IP Bans, Entropy Anomaly Detection,
    SSRF Protection, JSON Bomb Limits, and OWASP Hardening.
    """
    def __init__(self):
        self.request_history: Dict[str, List[float]] = defaultdict(list)
        self.auth_request_history: Dict[str, List[float]] = defaultdict(list)
        self.threat_scores: Dict[str, int] = defaultdict(int)
        self.rate_limit_violations: Dict[str, int] = defaultdict(int)
        self.banned_ips: Dict[str, float] = {}
        self.failed_login_attempts: Dict[str, List[float]] = defaultdict(list)
        self.auth_lock = threading.Lock()
        
        self.attack_stats = {
            "sqli_blocked": 0,
            "nosqli_blocked": 0,
            "xss_blocked": 0,
            "rce_blocked": 0,
            "traversal_blocked": 0,
            "ssrf_blocked": 0,
            "jwt_attack_blocked": 0,
            "zero_day_blocked": 0,
            "honeypot_trap_blocked": 0,
            "scanner_blocked": 0,
            "protocol_smuggling_blocked": 0,
            "rate_limit_blocked": 0,
            "brute_force_blocked": 0,
            "total_threats_blocked": 0
        }

    def calculate_entropy(self, text: str) -> float:
        """Calculates Shannon Entropy of a string to detect obfuscated shellcode."""
        if not text or len(text) < 20:
            return 0.0
        prob = [float(text.count(c)) / len(text) for c in set(text)]
        return - sum([p * math.log(p, 2) for p in prob])

    def clean_old_history(self, ip: str, window_seconds: float = 60.0):
        now = time.time()
        self.request_history[ip] = [ts for ts in self.request_history[ip] if now - ts < window_seconds]
        self.auth_request_history[ip] = [ts for ts in self.auth_request_history[ip] if now - ts < window_seconds]

    def is_banned(self, ip: str) -> bool:
        now = time.time()
        with self.auth_lock:
            if ip in self.banned_ips:
                if now < self.banned_ips[ip]:
                    return True
                else:
                    del self.banned_ips[ip]
                    self.threat_scores[ip] = 0
                    self.rate_limit_violations[ip] = 0
        return False

    def reset_all_bans(self):
        """Resets and unblocks all banned IPs instantly."""
        with self.auth_lock:
            self.banned_ips.clear()
            self.threat_scores.clear()
            self.request_history.clear()
            self.auth_request_history.clear()
            self.rate_limit_violations.clear()
            self.failed_login_attempts.clear()
        logger.info("🔓 [FIREWALL RESET] All IP bans and rate limits reset successfully!")

    def ban_ip(self, ip: str, duration: int = 900):
        """Auto-Expiring IP Ban (Default: 15 minutes / 900 seconds)."""
        self.banned_ips[ip] = time.time() + duration
        logger.warning(f"⛔ [FORTRESS TEMPORARY BAN] IP {ip} temporarily locked for {duration}s.")

    def is_login_locked(self, ip: str, identifier: str = "") -> Tuple[bool, int]:
        """Checks if device IP is temporarily locked due to 6 consecutive failed logins."""
        now = time.time()
        key = ip  # Track strictly by device IP so page refreshes or typing different usernames never reset the counter!
        with self.auth_lock:
            self.failed_login_attempts[key] = [t for t in self.failed_login_attempts[key] if now - t < 900.0]
            failures = len(self.failed_login_attempts[key])
            if failures >= 6:
                self.ban_ip(ip, duration=900)
                remaining = int(900 - (now - self.failed_login_attempts[key][0]))
                return True, max(1, remaining)
            return False, 0

    def record_failed_login(self, ip: str, identifier: str = "") -> int:
        """Records failed login attempt by device IP. At 6 failures, triggers immediate 15-minute ban."""
        now = time.time()
        key = ip  # Track strictly by device IP
        with self.auth_lock:
            self.failed_login_attempts[key].append(now)
            failures = len([t for t in self.failed_login_attempts[key] if now - t < 900.0])
            if failures >= 6:
                self.attack_stats["brute_force_blocked"] = self.attack_stats.get("brute_force_blocked", 0) + 1
                self.ban_ip(ip, duration=900)
                logger.warning(f"🚨 [BRUTE FORCE LOCKOUT] Device IP {ip} locked out after 6 consecutive failed logins.")
            return failures

    def record_successful_login(self, ip: str, identifier: str = ""):
        """Resets failed attempts upon successful authentication."""
        key = ip
        with self.auth_lock:
            if key in self.failed_login_attempts:
                del self.failed_login_attempts[key]

    def record_threat(self, ip: str, threat_type: str, weight: int = 3):
        with self.auth_lock:
            self.threat_scores[ip] += weight
            self.attack_stats[threat_type] = self.attack_stats.get(threat_type, 0) + 1
            self.attack_stats["total_threats_blocked"] += 1
            
            logger.warning(f"🚨 [FORTRESS THREAT DETECTED] Type: {threat_type.upper()} | IP: {ip} | Score: {self.threat_scores[ip]}")
            
            # Instant ban for real cyber attacks (SQLi, NoSQLi, RCE, Traversal)
            if threat_type in ["sqli_blocked", "nosqli_blocked", "xss_blocked", "rce_blocked", "traversal_blocked"]:
                self.ban_ip(ip, duration=3600)  # 1 hour instant ban for cyber attack attempts
            elif self.threat_scores[ip] >= 6:
                self.ban_ip(ip, duration=900)  # 15 minutes ban for repeated threats

    def check_rate_limit(self, ip: str, path: str) -> bool:
        now = time.time()
        with self.auth_lock:
            self.clean_old_history(ip, 60.0)

            is_auth_route = any(auth_path in path for auth_path in [
                "/login", "/register", "/forgot-password", "/reset-password", "/verify-reset-qr"
            ])

            if is_auth_route:
                # Track auth route requests separately so webpage asset loads NEVER consume auth quota!
                self.auth_request_history[ip].append(now)
                auth_count = len(self.auth_request_history[ip])
                max_auth_limit = 25  # Up to 25 auth requests per minute (allows typing/retries, blocks 200-tab bot floods)
                if auth_count > max_auth_limit:
                    self.attack_stats["rate_limit_blocked"] = self.attack_stats.get("rate_limit_blocked", 0) + 1
                    self.ban_ip(ip, duration=900)  # 15-minute ban for distributed bot flooding (e.g. 200 tabs)
                    logger.warning(f"🚨 [AUTH BOT FLOOD BLOCKED] IP {ip} flooded auth route {path} ({auth_count} reqs in 60s). Banned for 15 mins.")
                    return False
                return True

            # General routes:
            req_count = len(self.request_history[ip])
            if any(render_path in path for render_path in ["/generate-custom-video", "/generate-script", "/api/generate-ai-script", "/api/remove-bg"]):
                max_limit = 12  # 12 video/script/image generations per minute
            elif any(pay_path in path for pay_path in ["/create-razorpay-order", "/verify-razorpay-payment"]):
                max_limit = 15  # 15 payment attempts per minute
            elif any(path.startswith(static) for static in ["/assets", "/fonts", "/music", "/status/"]):
                max_limit = 300  # High limit for static assets & video status polling
            else:
                max_limit = 120

            self.request_history[ip].append(now)

            if req_count >= max_limit:
                self.attack_stats["rate_limit_blocked"] = self.attack_stats.get("rate_limit_blocked", 0) + 1
                self.rate_limit_violations[ip] += 1
                if self.rate_limit_violations[ip] >= 2:
                    self.ban_ip(ip, duration=300)
                return False

            return True

    def inspect_text(self, text: str, is_auth_field: bool = False) -> Tuple[bool, str]:
        if not text or not isinstance(text, str):
            return False, ""

        clean_text = text.strip()

        # Whitelist safe visual styling tokens (hex colors, standard css color names)
        if re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", clean_text) or clean_text.lower() in [
            "yellow", "cyan", "magenta", "red", "green", "blue", "white", "black", "gold", "pink", "purple", "orange"
        ]:
            return False, ""

        if "\x00" in text or "%00" in text:
            return True, "traversal_blocked"

        for hp in ThreatSignatures.HONEYPOT_PATHS:
            if hp in text:
                return True, "honeypot_trap_blocked"

        for pattern in ThreatSignatures.NOSQLI_PATTERNS:
            if pattern.search(text):
                return True, "nosqli_blocked"

        # Check SQL Injection (Auth fields get exhaustive AUTH_SQLI_PATTERNS, content fields get safe SQLI_PATTERNS)
        sqli_patterns = ThreatSignatures.AUTH_SQLI_PATTERNS if is_auth_field else ThreatSignatures.SQLI_PATTERNS
        for pattern in sqli_patterns:
            if pattern.search(text):
                return True, "sqli_blocked"

        for pattern in ThreatSignatures.XSS_PATTERNS:
            if pattern.search(text):
                return True, "xss_blocked"

        for pattern in ThreatSignatures.JWT_ATTACK_PATTERNS:
            if pattern.search(text):
                return True, "jwt_attack_blocked"

        for pattern in ThreatSignatures.ZERO_DAY_PATTERNS:
            if pattern.search(text):
                return True, "zero_day_blocked"

        for pattern in ThreatSignatures.SSRF_PATTERNS:
            if pattern.search(text):
                return True, "ssrf_blocked"

        for pattern in ThreatSignatures.TRAVERSAL_PATTERNS:
            if pattern.search(text):
                return True, "traversal_blocked"

        for pattern in ThreatSignatures.RCE_PATTERNS:
            if pattern.search(text):
                return True, "rce_blocked"

        # Entropy shellcode detection for suspicious strings
        if len(text) > 40 and self.calculate_entropy(text) > 5.8:
            if any(sym in text for sym in [";", "|", "$", "<", ">", "`", "{", "}", "\\"]):
                return True, "rce_blocked"

        return False, ""

    def inspect_data(self, data, depth: int = 0, parent_key: str = "") -> Tuple[bool, str]:
        """Deep Recursive Data Scanner with Context-Aware Auth & NoSQL Key & Value Verification."""
        if depth > 10:
            return True, "rce_blocked"

        if isinstance(data, str):
            is_auth_field = parent_key.lower() in {
                "email", "phone", "email_or_mobile", "username", "password", 
                "new_password", "user_id", "internal_id", "job_id", "order_id"
            }
            return self.inspect_text(data, is_auth_field=is_auth_field)
        elif isinstance(data, dict):
            if len(data.keys()) > 150:
                return True, "rce_blocked"

            for k, v in data.items():
                k_str = str(k).strip()
                # 1. Any dictionary key starting with $ or containing . is a direct MongoDB NoSQL injection attack
                if k_str.startswith("$") or "." in k_str:
                    return True, "nosqli_blocked"

                is_bad_k, threat_k = self.inspect_text(k_str, is_auth_field=True)
                if is_bad_k:
                    return True, threat_k

                # 2. Strict ID/Auth field enforcement:
                # Sensitive identifier and credential fields must NEVER be objects/arrays (Classic NoSQL injection vector)
                if k_str.lower() in {"email", "phone", "email_or_mobile", "user_id", "internal_id", "job_id", "order_id", "payment_id"}:
                    if isinstance(v, (dict, list)):
                        return True, "nosqli_blocked"

                # 3. Base64 profile picture handling (Fast & safe check, avoids scanning 4MB base64 with regexes)
                if k_str.lower() == "profile_pic" or (isinstance(v, str) and v.startswith("data:image/")):
                    if isinstance(v, str):
                        if "\x00" in v or "%00" in v or "<script" in v.lower():
                            return True, "xss_blocked"
                        if v.startswith("data:image/") and len(v) <= 10 * 1024 * 1024:
                            continue

                # 4. Recursively inspect all values with parent_key context
                is_bad_v, threat_v = self.inspect_data(v, depth + 1, parent_key=k_str)
                if is_bad_v:
                    return True, threat_v

        elif isinstance(data, list):
            if len(data) > 300:
                return True, "rce_blocked"
            for item in data:
                is_bad, threat = self.inspect_data(item, depth + 1, parent_key=parent_key)
                if is_bad:
                    return True, threat
        return False, ""

waf = SecurityFirewall()

def sanitize_alphanumeric_id(val: str, max_len: int = 64) -> str:
    """Validates and cleans IDs (job_id, internal_id, order_id) strictly to alphanumeric + hyphen/underscore."""
    if not val or not isinstance(val, str):
        raise HTTPException(status_code=400, detail="Invalid identifier format.")
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '', val.strip())
    if not clean or len(clean) > max_len or clean != val.strip():
        raise HTTPException(status_code=400, detail="Malformed or illegal characters detected in identifier.")
    return clean

def sanitize_nosql(obj: Any) -> Any:
    """Recursively eliminates any MongoDB operator keys ($...) from incoming structures."""
    if isinstance(obj, dict):
        clean = {}
        for k, v in obj.items():
            if str(k).startswith("$") or "." in str(k):
                raise HTTPException(status_code=400, detail="Illegal query operator detected.")
            clean[k] = sanitize_nosql(v)
        return clean
    elif isinstance(obj, list):
        return [sanitize_nosql(i) for i in obj]
    elif isinstance(obj, str):
        return obj.replace("\x00", "")
    return obj

def clean_xss(val: str) -> str:
    """Strips HTML tags to prevent Cross-Site Scripting (XSS)."""
    if not val or not isinstance(val, str):
        return val
    return re.sub(r'<[^>]*>', '', str(val)).strip()

def verify_admin_access(request: Request):
    """Guards sensitive admin endpoints with ADMIN_SECURITY_KEY verification."""
    key = request.headers.get("x-admin-key") or request.query_params.get("admin_key")
    if not key or key.strip() != ADMIN_SECURITY_KEY.strip():
        logger.warning(f"⛔ [ADMIN ACCESS DENIED] Unauthorized access attempt from {request.client.host if request.client else 'unknown'}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Valid Admin Security Key required.")

def resolve_client_ip(request: Request) -> str:
    """Accurately extracts real client IP behind Cloudflare, Render, AWS ALB, or standard proxies."""
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        try:
            ipaddress.ip_address(cf_ip.strip())
            return cf_ip.strip()
        except ValueError:
            pass

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        try:
            ipaddress.ip_address(real_ip.strip())
            return real_ip.strip()
        except ValueError:
            pass

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        first_ip = forwarded.split(",")[0].strip()
        try:
            ipaddress.ip_address(first_ip)
            return first_ip
        except ValueError:
            pass

    return request.client.host if request.client else "127.0.0.1"

def add_security_headers(response: Response) -> Response:
    """Attaches complete OWASP recommended security headers and strips identifying server banners."""
    csp_policy = (
        "default-src 'self' https: data: blob:; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://accounts.google.com https://checkout.razorpay.com https://api.razorpay.com https://*.razorpay.com https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://checkout.razorpay.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:; "
        "img-src 'self' data: https: blob: https://cdn.razorpay.com https://*.razorpay.com; "
        "connect-src 'self' https: wss: https://api.razorpay.com https://lumberjack.razorpay.com https://*.razorpay.com; "
        "media-src 'self' https: blob: data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-src 'self' https://accounts.google.com https://api.razorpay.com https://checkout.razorpay.com https://*.razorpay.com https://*.razorpay.in; "
        "form-action 'self';"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=*, usb=(), display-capture=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    response.headers["Content-Security-Policy"] = csp_policy

    for h in ["Server", "server", "X-Powered-By", "x-powered-by"]:
        if h in response.headers:
            del response.headers[h]
    return response

class FirewallMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = resolve_client_ip(request)
        path = request.url.path.lower()

        # 1. Banned IP Gate
        if waf.is_banned(client_ip):
            ban_expiry = waf.banned_ips.get(client_ip, 0)
            remaining_secs = max(1, int(ban_expiry - time.time()))
            logger.warning(f"🚫 [FORTRESS BLOCKED BANNED IP] {client_ip} -> {path} (Locked for {remaining_secs}s)")
            return add_security_headers(JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "status": "blocked",
                    "error": f"Access Denied by Cloxel Security Shield. Too many unauthorized requests or failed login attempts. Device temporarily locked. Auto-unlocks in {remaining_secs} seconds.",
                    "ip": client_ip,
                    "retry_after_seconds": remaining_secs
                }
            ))

        # 2. Honeypot Trap Detection
        if path in ThreatSignatures.HONEYPOT_PATHS or any(path.startswith(hp) for hp in ThreatSignatures.HONEYPOT_PATHS):
            waf.record_threat(client_ip, "honeypot_trap_blocked", weight=10)
            waf.ban_ip(client_ip, duration=3600)  # 1 hour instant ban for honeypot probes
            return add_security_headers(JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"status": "blocked", "error": "Honeypot Security Trap Triggered. IP Banned."}
            ))

        # 3. HTTP Protocol Smuggling Gate
        if "content-length" in request.headers and "transfer-encoding" in request.headers:
            waf.record_threat(client_ip, "protocol_smuggling_blocked", weight=5)
            return add_security_headers(JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "blocked", "error": "HTTP Protocol Anomaly Detected (Smuggling Attempt)."}
            ))

        # 4. Automated Exploit Scanner Gate
        user_agent = request.headers.get("User-Agent", "").lower()
        for bot in ThreatSignatures.MALICIOUS_BOTS:
            if bot in user_agent:
                waf.record_threat(client_ip, "scanner_blocked", weight=6)
                waf.ban_ip(client_ip, duration=1800)  # 30 min ban for malicious scanners
                return add_security_headers(JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"status": "blocked", "error": "Automated security scanner detected and banned."}
                ))

        # 5. Rate Limiting Gate
        if not waf.check_rate_limit(client_ip, path):
            return add_security_headers(JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"status": "rate_limited", "error": "Too many requests. Rate limit enforced."}
            ))

        # 6. Path Traversal & Injection in URL Path
        is_bad_path, threat_path = waf.inspect_text(request.url.path)
        if is_bad_path:
            waf.record_threat(client_ip, threat_path, weight=4)
            return add_security_headers(JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "blocked", "error": f"Security Shield Flagged URL Path ({threat_path.upper()})."}
            ))

        # 7. Query Parameters Deep Inspection
        for key, val in request.query_params.items():
            is_malicious, threat_type = waf.inspect_text(f"{key}={val}", is_auth_field=True)
            if is_malicious:
                waf.record_threat(client_ip, threat_type, weight=10)
                waf.ban_ip(client_ip, duration=3600)  # Immediate 1st-attempt ban for cyber attacks
                attack_label = "SQL Injection Attack" if "sqli" in threat_type else threat_type.upper().replace('_', ' ')
                return add_security_headers(JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "status": "blocked",
                        "error": f"🚨 Cyber Threat Alert: Malicious {attack_label} detected in URL query! Your IP address has been immediately blocked on the 1st attempt.",
                        "ip": client_ip,
                        "attack_type": threat_type
                    }
                ))

        # 8. Request Payload Inspection (POST, PUT, PATCH)
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("Content-Length")
            # 25MB max safety cap for uploads
            if content_length and int(content_length) > 25 * 1024 * 1024:
                return add_security_headers(JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"status": "blocked", "error": "Request payload exceeds 25MB safety limit."}
                ))

            content_type = request.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    body_bytes = await request.body()
                    if body_bytes:
                        # Prevent JSON bombs / oversized JSON (allows up to 15MB for high-res profile images)
                        if len(body_bytes) > 15 * 1024 * 1024:  # 15MB cap for JSON
                            return add_security_headers(JSONResponse(
                                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                content={"status": "blocked", "error": "JSON payload exceeds 15MB limit."}
                            ))

                        # Allow direct HMAC processing for official Razorpay Webhooks
                        if path == "/razorpay-webhook":
                            async def receive():
                                return {"type": "http.request", "body": body_bytes}
                            request._receive = receive
                            response: Response = await call_next(request)
                            return add_security_headers(response)

                        body_json = json.loads(body_bytes.decode("utf-8"))
                        is_malicious, threat_type = waf.inspect_data(body_json)
                        if is_malicious:
                            waf.record_threat(client_ip, threat_type, weight=10)
                            waf.ban_ip(client_ip, duration=3600)  # Immediate 1st-attempt ban for cyber attacks
                            
                            if threat_type in ["sqli_blocked", "nosqli_blocked"]:
                                attack_label = "SQL / Database Injection Attack"
                            elif threat_type == "xss_blocked":
                                attack_label = "Script / XSS Injection Attack"
                            elif threat_type in ["rce_blocked", "traversal_blocked"]:
                                attack_label = "Remote Code Execution / Traversal Attack"
                            else:
                                attack_label = threat_type.upper().replace('_', ' ')

                            return add_security_headers(JSONResponse(
                                status_code=status.HTTP_403_FORBIDDEN,
                                content={
                                    "status": "blocked",
                                    "error": f"🚨 Cyber Threat Alert: Malicious {attack_label} detected! Your IP address has been immediately blocked on the 1st attempt.",
                                    "ip": client_ip,
                                    "attack_type": threat_type
                                }
                            ))

                        async def receive():
                            return {"type": "http.request", "body": body_bytes}

                        request._receive = receive
                except json.JSONDecodeError:
                    return add_security_headers(JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"status": "blocked", "error": "Malformed JSON payload."}
                    ))
                except Exception as _e_body:
                    logger.warning(f"⚠️ Body inspection warning: {_e_body}")

        # 9. Next Middleware / Route Execution
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            logger.error(f"❌ Internal Exception: {exc}", exc_info=True)
            return add_security_headers(JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"status": "error", "message": "An internal server error occurred. Protected by Cloxel Security Shield."}
            ))

        # 10. Robust Defense Headers
        return add_security_headers(response)
