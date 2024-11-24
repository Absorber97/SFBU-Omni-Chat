from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from urllib.parse import urlparse, urljoin
import urllib.robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import requests
from bs4 import BeautifulSoup
import time

@dataclass
class URLProcessingConfig:
    max_delay: float = 1.0
    min_delay: float = 0.2
    max_retries: int = 3
    max_workers: int = 5
    recursion_enabled: bool = False
    max_links_per_page: int = 50  # Limit links to process per page
    timeout: int = 30  # Request timeout in seconds

@dataclass
class ProcessingStats:
    processed_urls: Set[str] = field(default_factory=set)
    failed_urls: Dict[str, str] = field(default_factory=dict)
    skipped_urls: Dict[str, str] = field(default_factory=dict)

class URLProcessor:
    def __init__(self, config: Optional[URLProcessingConfig] = None):
        self.config = config or URLProcessingConfig()
        self.logger = logging.getLogger(__name__)
        self.stats = ProcessingStats()
        self.robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
        
    def _process_single_url(self, url: str) -> Optional[Dict]:
        """Process a single URL and extract content"""
        if url in self.stats.processed_urls:
            self.logger.info(f"URL already processed: {url}")
            return None

        try:
            # Respect rate limiting
            time.sleep(self.config.min_delay)
            
            # Make request with retries
            response = self._make_request_with_retry(url)
            if not response:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract content
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            content = self._extract_content(soup)
            links = self._extract_links(soup, url) if self.config.recursion_enabled else set()
            
            # Mark as processed
            self.stats.processed_urls.add(url)
            self.logger.info(f"Successfully processed URL: {url}")
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'links': links
            }
            
        except Exception as e:
            self.logger.error(f"Error processing {url}: {str(e)}")
            self.stats.failed_urls[url] = str(e)
            return None

    def _make_request_with_retry(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        for attempt in range(self.config.max_retries):
            try:
                response = requests.get(
                    url, 
                    timeout=self.config.timeout,
                    headers=headers,
                    allow_redirects=True
                )
                
                if response.status_code == 403:
                    self.logger.warning(f"Access forbidden for {url}. Site may be blocking automated access.")
                    self.stats.skipped_urls[url] = "Access forbidden (403)"
                    return None
                    
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    self.logger.error(f"Failed to fetch {url} after {self.config.max_retries} attempts: {str(e)}")
                    self.stats.failed_urls[url] = str(e)
                    return None
                time.sleep(self.config.min_delay * (attempt + 1))
        return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title = soup.find('title')
        return title.get_text().strip() if title else ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""

    def _extract_content(self, soup: BeautifulSoup) -> List[str]:
        """Extract main content from HTML"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'noscript']):
            element.decompose()

        # Extract text from remaining elements
        paragraphs = []
        main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': ['content', 'main-content']}) or soup
        
        for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
            text = ' '.join(element.stripped_strings)  # Better text extraction
            if text and len(text) > 20:  # Filter out short snippets
                # Clean the text
                text = ' '.join(text.split())  # Normalize whitespace
                text = text.replace('\n', ' ').strip()
                if text:
                    paragraphs.append({
                        'type': element.name,  # Save element type (h1, p, etc.)
                        'text': text,
                        'section': self._get_section_context(element)  # Get parent section if any
                    })

        return paragraphs

    def _get_section_context(self, element) -> str:
        """Get the section context for an element"""
        # Look for parent section or article
        section = element.find_parent(['section', 'article'])
        if section:
            # Try to find section title
            heading = section.find(['h1', 'h2', 'h3'])
            if heading:
                return heading.get_text().strip()
        return "main"

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract and normalize links from HTML"""
        links = set()
        base_domain = urlparse(base_url).netloc
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            
            # Only include HTTP(S) links from same domain
            if (parsed.scheme in ('http', 'https') and 
                parsed.netloc == base_domain and
                '#' not in absolute_url):  # Exclude anchors
                links.add(absolute_url)
                
        return links

    def _log_processing_summary(self):
        """Log processing statistics"""
        summary = f"""
URL Processing Summary:
- Processed URLs: {len(self.stats.processed_urls)}
- Failed URLs: {len(self.stats.failed_urls)}
- Skipped URLs: {len(self.stats.skipped_urls)}
"""
        if self.stats.failed_urls:
            summary += "\nFailed URLs:\n"
            for url, reason in self.stats.failed_urls.items():
                summary += f"- {url}: {reason}\n"
                
        if self.stats.skipped_urls:
            summary += "\nSkipped URLs:\n"
            for url, reason in self.stats.skipped_urls.items():
                summary += f"- {url}: {reason}\n"
                
        self.logger.info(summary)

    def process_with_recursion(self, base_url: str) -> List[Dict]:
        """Process URL with optional recursion"""
        self.logger.info(f"Starting URL processing for: {base_url}")
        all_content = []
        
        # Process base URL
        base_content = self._process_single_url(base_url)
        if base_content:
            all_content.append(base_content)
            
        if self.config.recursion_enabled:
            self.logger.info("Recursion enabled - processing linked pages")
            links = base_content.get('links', set()) if base_content else set()
            
            # Filter and limit links
            filtered_links = self._filter_links(links, base_url)
            self.logger.info(f"Found {len(filtered_links)} valid links to process:")
            for link in filtered_links:
                self.logger.info(f"- {link}")
            
            # Process filtered links concurrently
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                future_to_url = {
                    executor.submit(self._process_single_url, url): url 
                    for url in filtered_links
                }
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        content = future.result()
                        if content:
                            all_content.append(content)
                            self.logger.info(f"Successfully processed: {url}")
                    except Exception as e:
                        self.logger.error(f"Error processing {url}: {str(e)}")
                        self.stats.failed_urls[url] = str(e)

        # Log processing summary
        self._log_processing_summary()
        
        # Even if some URLs failed, return what we could process
        if all_content:
            return all_content
        else:
            self.logger.warning("No content could be extracted from any URLs")
            return []

    def _can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            if base_url not in self.robots_cache:
                robots_parser = urllib.robotparser.RobotFileParser()
                robots_parser.set_url(f"{base_url}/robots.txt")
                robots_parser.read()
                self.robots_cache[base_url] = robots_parser
            
            return self.robots_cache[base_url].can_fetch("*", url)
        except Exception:
            # If robots.txt cannot be fetched, assume allowed
            return True

    def _filter_links(self, links: Set[str], base_url: str) -> Set[str]:
        """Filter and limit links for processing"""
        base_domain = urlparse(base_url).netloc
        filtered = set()
        
        for link in links:
            parsed = urlparse(link)
            
            # Skip if already processed or failed
            if (link in self.stats.processed_urls or 
                link in self.stats.failed_urls or 
                link in self.stats.skipped_urls):
                continue
                
            # Check domain and robots.txt
            if (parsed.netloc == base_domain and 
                self._can_fetch(link)):
                filtered.add(link)
                
            if len(filtered) >= self.config.max_links_per_page:
                self.logger.info(f"Reached maximum links limit ({self.config.max_links_per_page})")
                break
                
        return filtered 