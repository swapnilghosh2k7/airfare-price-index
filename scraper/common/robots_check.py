"""Robots.txt compliance checker for AirFareX scrapers.
Caches RobotFileParser instances per domain to avoid repetitive network overhead.
"""
import logging
import urllib.parse
import urllib.robotparser
from typing import Dict, Optional

logger = logging.getLogger("scraper.robots")

DEFAULT_USER_AGENT = "AirFareX-Research-Bot/1.0 (+https://airfarex.local/policy)"


class RobotsChecker:
    _parsers: Dict[str, Optional[urllib.robotparser.RobotFileParser]] = {}

    @classmethod
    def get_parser(cls, base_url: str, timeout: float = 5.0) -> Optional[urllib.robotparser.RobotFileParser]:
        parsed = urllib.parse.urlparse(base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if not parsed.netloc:
            return None

        if origin in cls._parsers:
            return cls._parsers[origin]

        robots_url = f"{origin}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
            cls._parsers[origin] = rp
            logger.info("Successfully fetched and parsed %s", robots_url)
        except Exception as exc:
            logger.warning("Failed to fetch or parse %s (%s). Permitting request by default.", robots_url, exc)
            cls._parsers[origin] = rp  # Empty parser allows all

        return cls._parsers[origin]

    @classmethod
    def is_allowed(cls, url: str, user_agent: str = DEFAULT_USER_AGENT, timeout: float = 5.0) -> bool:
        """Check whether the given URL is permissible under the domain's robots.txt."""
        try:
            rp = cls.get_parser(url, timeout=timeout)
            if rp is None:
                return True
            allowed = rp.can_fetch(user_agent, url)
            if not allowed:
                logger.warning("URL disallowed by robots.txt: %s (User-Agent: %s)", url, user_agent)
            return allowed
        except Exception as exc:
            logger.warning("Error evaluating robots.txt for %s: %s. Defaulting to True.", url, exc)
            return True


def is_allowed(url: str, user_agent: str = DEFAULT_USER_AGENT) -> bool:
    """Convenience function to check URL permission against robots.txt."""
    return RobotsChecker.is_allowed(url, user_agent=user_agent)


if __name__ == "__main__":
    import sys
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.goindigo.in/"
    res = is_allowed(test_url)
    print(f"URL: {test_url} -> Allowed: {res}")
