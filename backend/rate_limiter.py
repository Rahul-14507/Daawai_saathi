"""
Sliding-Window Rate Limiter for Dawai Saathi
Protects Gnani AI API credits and LLM inference from automated crawlers and spam.
Maintains generous quotas for hackathon judges and evaluators.
"""
import time
import logging
from collections import defaultdict
from typing import Dict, List, Optional
from fastapi import Request, HTTPException, status

logger = logging.getLogger("dawai.ratelimit")

class SlidingWindowRateLimiter:
    """
    In-memory sliding-window rate limiter per client IP.
    Accounts for reverse proxies (Render, Cloudflare) via X-Forwarded-For.
    """
    def __init__(self):
        # ip -> action_key -> list of timestamp floats
        self._history: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        # Dedicated evaluation tokens for hackathon judges
        self._judge_tokens = {"gnani-eval", "dawai-judge-2026", "hackathon-eval", "judge"}

    def get_client_ip(self, request: Request) -> str:
        """Extract true client IP behind Render / Cloudflare / reverse proxy."""
        # 1. Cloudflare header
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip:
            return cf_ip.strip()
        
        # 2. X-Forwarded-For (first IP in comma-separated list is client)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # 3. Direct client host
        if request.client and request.client.host:
            return request.client.host
        
        return "unknown"

    def is_judge(self, request: Request) -> bool:
        """Check if request carries judge access token or query parameter."""
        header_val = request.headers.get("X-Judge-Access", "").strip()
        if header_val in self._judge_tokens:
            return True
        query_val = request.query_params.get("judge", "").strip().lower()
        if query_val in self._judge_tokens or query_val in ["1", "true", "yes"]:
            return True
        eval_param = request.query_params.get("eval", "").strip().lower()
        if eval_param in ["1", "true", "yes"]:
            return True
        return False

    def check(
        self,
        request: Request,
        action: str,
        max_requests: int,
        window_seconds: int = 600,
        friendly_label: str = "actions"
    ):
        """
        Enforce sliding-window rate limit for a specific action.
        Raises HTTPException(429) if threshold exceeded.
        """
        # Judges and localhost have unrestricted access
        ip = self.get_client_ip(request)
        if ip in ("127.0.0.1", "localhost", "::1") or self.is_judge(request):
            return

        now = time.time()
        window_start = now - window_seconds
        
        # Purge timestamps outside the active window
        history = [ts for ts in self._history[ip][action] if ts > window_start]
        self._history[ip][action] = history

        if len(history) >= max_requests:
            retry_after = int(history[0] + window_seconds - now) + 1
            minutes = max(1, window_seconds // 60)
            logger.warning(
                f"Rate limit hit for IP {ip} on action '{action}'. "
                f"Count: {len(history)}/{max_requests} in {minutes}m. Retry-After: {retry_after}s"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limit reached: Maximum {max_requests} {friendly_label} per {minutes} minutes. "
                    f"Please try again in {retry_after} seconds."
                ),
                headers={"Retry-After": str(retry_after)}
            )

        # Record this request timestamp
        history.append(now)

    def get_quota_status(self, request: Request) -> Dict[str, dict]:
        """Inspect current quota consumption for debugging and evaluation."""
        ip = self.get_client_ip(request)
        now = time.time()
        window_start = now - 600
        
        status_map = {}
        limits = {
            "scan": (8, 600, "Prescription Scans"),
            "voice_enroll": (5, 600, "Voice Enrollments"),
            "reminder_gen": (8, 600, "Reminder Syntheses"),
            "ask_qna": (15, 600, "Voice Questions")
        }
        for action, (max_req, win_sec, label) in limits.items():
            recent = [ts for ts in self._history[ip][action] if ts > now - win_sec]
            status_map[action] = {
                "label": label,
                "used": len(recent),
                "allowed": max_req,
                "remaining": max(0, max_req - len(recent)),
                "window_minutes": win_sec // 60
            }
        
        return {
            "client_ip": ip,
            "is_judge": self.is_judge(request),
            "quotas": status_map
        }

# Global instance
rate_limiter = SlidingWindowRateLimiter()

