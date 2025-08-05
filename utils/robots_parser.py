"""
Robots.txt parser for discovering sitemaps
"""

import requests
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import re

class RobotsParser:
    """Parser for robots.txt files to discover sitemaps"""
    
    def __init__(self, timeout: int = 30, user_agent: str = None):
        self.timeout = timeout
        self.user_agent = user_agent or "SEO-Canonical-Validator/1.0"
        
    def discover_sitemaps(self, domain: str) -> List[Dict]:
        """
        Discover sitemaps from robots.txt
        
        Args:
            domain: The domain to check (with or without protocol)
            
        Returns:
            List of sitemap dictionaries with url, type, status, and metadata
        """
        # Normalize domain
        if not domain.startswith(('http://', 'https://')):
            domain = f"https://{domain}"
        
        # Parse domain to get base URL
        parsed = urlparse(domain)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = urljoin(base_url, '/robots.txt')
        
        try:
            # Fetch robots.txt
            response = requests.get(
                robots_url,
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent}
            )
            
            if response.status_code == 200:
                return self._parse_robots_content(response.text, base_url)
            else:
                # Try common sitemap locations if robots.txt not found
                return self._check_common_sitemap_locations(base_url)
                
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch robots.txt from {robots_url}: {str(e)}")
    
    def _parse_robots_content(self, content: str, base_url: str) -> List[Dict]:
        """Parse robots.txt content to extract sitemap URLs"""
        sitemaps = []
        
        # Look for sitemap directives
        sitemap_pattern = re.compile(r'^sitemap:\s*(.+)$', re.IGNORECASE | re.MULTILINE)
        matches = sitemap_pattern.findall(content)
        
        for match in matches:
            sitemap_url = match.strip()
            
            # Convert relative URLs to absolute
            if not sitemap_url.startswith(('http://', 'https://')):
                sitemap_url = urljoin(base_url, sitemap_url)
            
            # Validate and categorize sitemap
            sitemap_info = self._validate_sitemap(sitemap_url)
            if sitemap_info:
                sitemaps.append(sitemap_info)
        
        # If no sitemaps found in robots.txt, check common locations
        if not sitemaps:
            sitemaps = self._check_common_sitemap_locations(base_url)
        
        return sitemaps
    
    def _check_common_sitemap_locations(self, base_url: str) -> List[Dict]:
        """Check common sitemap locations"""
        common_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemaps.xml',
            '/sitemap.txt',
            '/sitemap'
        ]
        
        sitemaps = []
        
        for path in common_paths:
            sitemap_url = urljoin(base_url, path)
            sitemap_info = self._validate_sitemap(sitemap_url)
            if sitemap_info:
                sitemaps.append(sitemap_info)
        
        return sitemaps
    
    def _validate_sitemap(self, sitemap_url: str) -> Optional[Dict]:
        """Validate sitemap URL and determine type"""
        try:
            # Quick HEAD request to check if sitemap exists
            response = requests.head(
                sitemap_url,
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent},
                allow_redirects=True
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                # Determine sitemap type
                sitemap_type = self._determine_sitemap_type(sitemap_url, content_type)
                
                return {
                    'url': sitemap_url,
                    'type': sitemap_type,
                    'status': 'Available',
                    'content_type': content_type,
                    'size': response.headers.get('content-length', 'Unknown')
                }
            else:
                return None
                
        except requests.RequestException:
            return None
    
    def _determine_sitemap_type(self, url: str, content_type: str) -> str:
        """Determine the type of sitemap based on URL and content type"""
        url_lower = url.lower()
        
        if 'xml' in content_type or url_lower.endswith('.xml'):
            if 'index' in url_lower:
                return 'XML Index'
            else:
                return 'XML Sitemap'
        elif 'text' in content_type or url_lower.endswith('.txt'):
            return 'Text Sitemap'
        elif url_lower.endswith('.gz'):
            return 'Compressed Sitemap'
        elif 'json' in content_type or url_lower.endswith('.json'):
            return 'JSON Sitemap'
        else:
            return 'Unknown Format'
    
    def get_sitemap_preview(self, sitemap_url: str, max_urls: int = 10) -> List[str]:
        """Get a preview of URLs from a sitemap"""
        try:
            from .sitemap_parser import SitemapParser
            parser = SitemapParser()
            urls = parser.extract_urls(sitemap_url)
            return urls[:max_urls]
        except Exception:
            return []