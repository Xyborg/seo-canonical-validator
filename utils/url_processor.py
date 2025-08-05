"""
URL processor for extracting and analyzing canonical tags
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode
from typing import List, Dict, Callable, Optional
import concurrent.futures
import time

class URLProcessor:
    """Processor for analyzing canonical tags in URLs"""
    
    def __init__(self, 
                 concurrent_requests: int = 10,
                 request_timeout: int = 30,
                 max_retries: int = 3,
                 force_https: bool = True,
                 remove_trailing_slash: bool = True,
                 ignore_query_params: bool = False,
                 user_agent: str = None):
        
        self.concurrent_requests = concurrent_requests
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.force_https = force_https
        self.remove_trailing_slash = remove_trailing_slash
        self.ignore_query_params = ignore_query_params
        self.user_agent = user_agent or "SEO-Canonical-Validator/1.0"
        
        # Create session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def process_urls(self, urls: List[str], progress_callback: Callable = None) -> List[Dict]:
        """
        Process multiple URLs to analyze canonical tags
        
        Args:
            urls: List of URLs to process
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of dictionaries with analysis results
        """
        results = []
        total_urls = len(urls)
        
        # Use ThreadPoolExecutor for concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrent_requests) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self._process_single_url, url): url 
                for url in urls
            }
            
            # Process completed tasks
            for i, future in enumerate(concurrent.futures.as_completed(future_to_url)):
                url = future_to_url[future]
                
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'URL': url,
                        'Canonical URL': None,
                        'Status': 'Error',
                        'Error': f"Processing failed: {str(e)}",
                        'Response Time': None,
                        'HTTP Status': None
                    })
                
                # Update progress
                if progress_callback:
                    progress_callback(i + 1, total_urls, url)
        
        return results
    
    def _process_single_url(self, url: str) -> Dict:
        """Process a single URL to extract and analyze canonical tag"""
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                # Fetch the URL
                response = self.session.get(
                    url,
                    timeout=self.request_timeout,
                    allow_redirects=True,
                    headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                    }
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    return self._analyze_canonical_tag(url, response, response_time)
                else:
                    return {
                        'URL': url,
                        'Canonical URL': None,
                        'Status': 'Error',
                        'Error': f"HTTP {response.status_code}",
                        'Response Time': response_time,
                        'HTTP Status': response.status_code
                    }
                    
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:  # Last attempt
                    return {
                        'URL': url,
                        'Canonical URL': None,
                        'Status': 'Error',
                        'Error': f"Request failed: {str(e)}",
                        'Response Time': time.time() - start_time,
                        'HTTP Status': None
                    }
                else:
                    # Wait before retry
                    time.sleep(1)
    
    def _analyze_canonical_tag(self, original_url: str, response: requests.Response, response_time: float) -> Dict:
        """Analyze canonical tag from HTML response"""
        try:
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find canonical tags
            canonical_tags = soup.find_all('link', rel='canonical')
            
            if not canonical_tags:
                return {
                    'URL': original_url,
                    'Canonical URL': None,
                    'Status': 'Missing',
                    'Error': 'No canonical tag found',
                    'Response Time': response_time,
                    'HTTP Status': response.status_code
                }
            
            if len(canonical_tags) > 1:
                canonical_urls = [tag.get('href', '') for tag in canonical_tags]
                return {
                    'URL': original_url,
                    'Canonical URL': ', '.join(canonical_urls),
                    'Status': 'Multiple',
                    'Error': f'Multiple canonical tags found: {len(canonical_tags)}',
                    'Response Time': response_time,
                    'HTTP Status': response.status_code
                }
            
            # Extract canonical URL
            canonical_tag = canonical_tags[0]
            canonical_href = canonical_tag.get('href', '').strip()
            
            if not canonical_href:
                return {
                    'URL': original_url,
                    'Canonical URL': None,
                    'Status': 'Empty',
                    'Error': 'Canonical tag is empty',
                    'Response Time': response_time,
                    'HTTP Status': response.status_code
                }
            
            # Convert relative URL to absolute
            canonical_url = urljoin(response.url, canonical_href)
            
            # Normalize URLs for comparison
            normalized_original = self._normalize_url(response.url)  # Use final URL after redirects
            normalized_canonical = self._normalize_url(canonical_url)
            
            # Compare URLs
            if normalized_original == normalized_canonical:
                status = 'Match'
                error = None
            else:
                status = 'Mismatch'
                error = 'Canonical URL does not match page URL'
            
            return {
                'URL': original_url,
                'Final URL': response.url,
                'Canonical URL': canonical_url,
                'Status': status,
                'Error': error,
                'Response Time': response_time,
                'HTTP Status': response.status_code
            }
            
        except Exception as e:
            return {
                'URL': original_url,
                'Canonical URL': None,
                'Status': 'Error',
                'Error': f"HTML parsing failed: {str(e)}",
                'Response Time': response_time,
                'HTTP Status': response.status_code
            }
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        if not url:
            return url
        
        # Parse URL
        parsed = urlparse(url)
        
        # Apply normalization rules
        scheme = parsed.scheme
        if self.force_https and scheme == 'http':
            scheme = 'https'
        
        # Handle trailing slash
        path = parsed.path
        if self.remove_trailing_slash and path.endswith('/') and path != '/':
            path = path.rstrip('/')
        
        # Handle query parameters
        query = parsed.query
        if self.ignore_query_params:
            query = ''
        
        # Rebuild URL
        normalized = urlunparse((
            scheme,
            parsed.netloc.lower(),  # Lowercase domain
            path,
            parsed.params,
            query,
            ''  # Remove fragment
        ))
        
        return normalized
    
    def get_url_info(self, url: str) -> Dict:
        """Get detailed information about a single URL"""
        try:
            start_time = time.time()
            
            response = self.session.head(
                url,
                timeout=self.request_timeout,
                allow_redirects=True
            )
            
            response_time = time.time() - start_time
            
            return {
                'url': url,
                'final_url': response.url,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', 'Unknown'),
                'content_length': response.headers.get('content-length', 'Unknown'),
                'last_modified': response.headers.get('last-modified', 'Unknown'),
                'response_time': response_time,
                'redirected': url != response.url
            }
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status_code': 'Error'
            }
    
    def __del__(self):
        """Cleanup session on destruction"""
        if hasattr(self, 'session'):
            self.session.close()