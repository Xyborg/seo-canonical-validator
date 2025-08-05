"""
Sitemap parser for extracting URLs from various sitemap formats
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from typing import List, Set
import gzip
import json
from io import BytesIO

class SitemapParser:
    """Parser for various sitemap formats (XML, text, compressed)"""
    
    def __init__(self, timeout: int = 30, user_agent: str = None):
        self.timeout = timeout
        self.user_agent = user_agent or "SEO-Canonical-Validator/1.0"
        self.processed_sitemaps = set()  # Track processed sitemaps to avoid loops
        
    def extract_urls(self, sitemap_url: str) -> List[str]:
        """
        Extract URLs from a sitemap
        
        Args:
            sitemap_url: URL of the sitemap to parse
            
        Returns:
            List of URLs found in the sitemap
        """
        if sitemap_url in self.processed_sitemaps:
            return []  # Avoid infinite loops
            
        self.processed_sitemaps.add(sitemap_url)
        
        try:
            # Fetch sitemap content
            response = requests.get(
                sitemap_url,
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent}
            )
            response.raise_for_status()
            
            # Determine content type and parse accordingly
            content_type = response.headers.get('content-type', '').lower()
            content = response.content
            
            # Handle compressed content
            if sitemap_url.endswith('.gz') or 'gzip' in content_type:
                content = self._decompress_content(content)
            
            # Parse based on format
            if self._is_xml_content(content, content_type):
                return self._parse_xml_sitemap(content)
            elif self._is_text_content(content_type):
                return self._parse_text_sitemap(content)
            elif self._is_json_content(content_type):
                return self._parse_json_sitemap(content)
            else:
                # Try to auto-detect format
                return self._auto_detect_and_parse(content)
                
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch sitemap {sitemap_url}: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to parse sitemap {sitemap_url}: {str(e)}")
    
    def _decompress_content(self, content: bytes) -> bytes:
        """Decompress gzipped content"""
        try:
            return gzip.decompress(content)
        except Exception:
            # If decompression fails, return original content
            return content
    
    def _is_xml_content(self, content: bytes, content_type: str) -> bool:
        """Check if content is XML"""
        return ('xml' in content_type or 
                content.startswith(b'<?xml') or 
                b'<urlset' in content[:200] or 
                b'<sitemapindex' in content[:200])
    
    def _is_text_content(self, content_type: str) -> bool:
        """Check if content is plain text"""
        return 'text/plain' in content_type
    
    def _is_json_content(self, content_type: str) -> bool:
        """Check if content is JSON"""
        return 'json' in content_type
    
    def _parse_xml_sitemap(self, content: bytes) -> List[str]:
        """Parse XML sitemap and extract URLs"""
        urls = []
        
        try:
            # Parse XML content
            root = ET.fromstring(content)
            
            # Handle namespace
            namespace = self._get_xml_namespace(root)
            
            # Check if this is a sitemap index
            if root.tag.endswith('sitemapindex'):
                # This is a sitemap index - recursively parse child sitemaps
                for sitemap in root.findall(f'.//{{{namespace}}}sitemap'):
                    loc_elem = sitemap.find(f'{{{namespace}}}loc')
                    if loc_elem is not None and loc_elem.text:
                        child_urls = self.extract_urls(loc_elem.text.strip())
                        urls.extend(child_urls)
            else:
                # This is a regular sitemap - extract URLs
                for url in root.findall(f'.//{{{namespace}}}url'):
                    loc_elem = url.find(f'{{{namespace}}}loc')
                    if loc_elem is not None and loc_elem.text:
                        urls.append(loc_elem.text.strip())
        
        except ET.ParseError as e:
            raise Exception(f"XML parsing error: {str(e)}")
        
        return urls
    
    def _get_xml_namespace(self, root) -> str:
        """Extract XML namespace from root element"""
        tag = root.tag
        if tag.startswith('{'):
            return tag[1:tag.find('}')]
        return ''
    
    def _parse_text_sitemap(self, content: bytes) -> List[str]:
        """Parse text sitemap (one URL per line)"""
        urls = []
        
        try:
            text_content = content.decode('utf-8', errors='ignore')
            lines = text_content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and line.startswith(('http://', 'https://')):
                    urls.append(line)
        
        except Exception as e:
            raise Exception(f"Text parsing error: {str(e)}")
        
        return urls
    
    def _parse_json_sitemap(self, content: bytes) -> List[str]:
        """Parse JSON sitemap"""
        urls = []
        
        try:
            json_data = json.loads(content.decode('utf-8'))
            
            # Handle different JSON sitemap formats
            if isinstance(json_data, list):
                # Array of URLs
                for item in json_data:
                    if isinstance(item, str):
                        urls.append(item)
                    elif isinstance(item, dict) and 'loc' in item:
                        urls.append(item['loc'])
            elif isinstance(json_data, dict):
                # Object with URL array
                if 'urls' in json_data:
                    for url_data in json_data['urls']:
                        if isinstance(url_data, str):
                            urls.append(url_data)
                        elif isinstance(url_data, dict) and 'loc' in url_data:
                            urls.append(url_data['loc'])
        
        except Exception as e:
            raise Exception(f"JSON parsing error: {str(e)}")
        
        return urls
    
    def _auto_detect_and_parse(self, content: bytes) -> List[str]:
        """Auto-detect format and parse accordingly"""
        # Try XML first
        try:
            if b'<' in content[:100]:
                return self._parse_xml_sitemap(content)
        except:
            pass
        
        # Try text format
        try:
            return self._parse_text_sitemap(content)
        except:
            pass
        
        # Try JSON format
        try:
            return self._parse_json_sitemap(content)
        except:
            pass
        
        # If nothing works, return empty list
        return []
    
    def get_sitemap_info(self, sitemap_url: str) -> dict:
        """Get detailed information about a sitemap"""
        try:
            response = requests.head(
                sitemap_url,
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent},
                allow_redirects=True
            )
            
            # Get basic info
            info = {
                'url': sitemap_url,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', 'Unknown'),
                'size': response.headers.get('content-length', 'Unknown'),
                'last_modified': response.headers.get('last-modified', 'Unknown')
            }
            
            # Get URL count by actually parsing (expensive but accurate)
            if response.status_code == 200:
                try:
                    urls = self.extract_urls(sitemap_url)
                    info['url_count'] = len(urls)
                except:
                    info['url_count'] = 'Error'
            else:
                info['url_count'] = 'N/A'
            
            return info
            
        except Exception as e:
            return {
                'url': sitemap_url,
                'status_code': 'Error',
                'error': str(e),
                'url_count': 'Error'
            }