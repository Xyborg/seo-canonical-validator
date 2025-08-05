# SEO Canonical Tag Validator - Project Plan

## Project Overview
A Streamlit web application that validates canonical tags across websites by fetching sitemaps from robots.txt, allowing users to select URLs for analysis, and generating comprehensive reports on canonical tag compliance.

## Core Features

### 1. Domain Input & Sitemap Discovery
- Input field for domain/website URL
- Fetch and parse robots.txt automatically
- Extract all sitemap URLs from robots.txt
- Handle various sitemap formats (XML, text, compressed)
- Error handling for missing robots.txt

### 2. Sitemap Management
- Display discovered sitemaps in a clear list
- Multi-select interface for sitemap selection
- Preview sitemap contents (first 10-20 URLs)
- Support for nested sitemaps (sitemap index files)
- Parse and extract all URLs from selected sitemaps

### 3. URL Input Options
- **Primary**: URLs from selected sitemaps
- **Secondary**: Manual URL input (paste list of URLs)
- **Hybrid**: Combine both sources
- URL validation and deduplication
- Support for various URL formats

### 4. Canonical Tag Processing
- Fetch each URL individually with proper error handling
- Extract canonical tag from HTML `<head>` section
- Handle various canonical tag formats:
  - `<link rel="canonical" href="...">`
  - Multiple canonical tags (report as error)
  - Missing canonical tags
  - Relative vs absolute canonical URLs

### 5. Analysis & Reporting
- Compare canonical tag value with actual URL
- URL normalization for accurate comparison:
  - Protocol standardization (http/https)
  - Trailing slash handling
  - Query parameter handling
  - Fragment removal
- Generate detailed reports with:
  - Match status (✓ Match, ✗ Mismatch, ⚠️ Missing, ❌ Error)
  - Actual URL vs Canonical URL
  - Error details for failed requests
  - Summary statistics

### 6. Export & Results
- Display results in interactive table
- Export to CSV/Excel
- Filter and sort capabilities
- Progress tracking during processing

## Technical Architecture

### Dependencies
```python
streamlit              # Web app framework
requests              # HTTP requests
beautifulsoup4        # HTML parsing
pandas                # Data manipulation
urllib.parse          # URL parsing and normalization
xml.etree.ElementTree # XML sitemap parsing
gzip                  # Compressed sitemap handling
```

### Application Structure
```
app.py                 # Main Streamlit application
utils/
├── robots_parser.py   # robots.txt parsing
├── sitemap_parser.py  # sitemap fetching and parsing
├── url_processor.py   # canonical tag extraction
├── url_normalizer.py  # URL normalization utilities
└── report_generator.py # report generation and export
requirements.txt       # Dependencies
```

### Data Flow
1. **Input** → Domain URL
2. **Discovery** → Fetch robots.txt → Extract sitemap URLs
3. **Selection** → User selects sitemaps + optional manual URLs
4. **Extraction** → Parse sitemaps → Extract all URLs
5. **Processing** → Fetch each URL → Extract canonical tag
6. **Analysis** → Compare canonical vs actual URL
7. **Output** → Generate report → Display/Export results

## Implementation Phases

### Phase 1: Core Infrastructure (Day 1)
- [x] Project setup and structure
- [ ] Basic Streamlit app layout
- [ ] robots.txt fetching and parsing
- [ ] Simple sitemap parsing
- [ ] URL validation utilities

### Phase 2: Sitemap Management (Day 1-2)
- [ ] Multi-sitemap discovery
- [ ] Sitemap selection interface
- [ ] URL extraction from various sitemap formats
- [ ] Manual URL input functionality

### Phase 3: Canonical Processing (Day 2)
- [ ] HTTP request handling with proper headers/timeouts
- [ ] HTML parsing for canonical tags
- [ ] URL normalization logic
- [ ] Error handling and retry mechanisms

### Phase 4: Reporting & UI (Day 2-3)
- [ ] Results display table
- [ ] Progress indicators
- [ ] Summary statistics
- [ ] Export functionality
- [ ] UI polish and validation

### Phase 5: Testing & Optimization (Day 3)
- [ ] Error handling edge cases
- [ ] Performance optimization for large datasets
- [ ] User experience improvements
- [ ] Documentation and deployment

## Configuration Options

### Processing Settings
- Concurrent request limit (default: 10)
- Request timeout (default: 30 seconds)
- Retry attempts (default: 3)
- User agent string
- Batch processing size

### URL Normalization Options
- Protocol normalization (force HTTPS)
- Trailing slash handling
- Query parameter inclusion
- Case sensitivity settings

### Report Customization
- Result filtering options
- Export format selection
- Column customization
- Error detail levels

## Performance Considerations

### Scalability
- Implement request rate limiting
- Use session-based caching for sitemaps
- Batch processing for large URL sets
- Progress bars for long operations

### Error Handling
- Network timeout handling
- Invalid URL detection
- HTTP error status handling
- Malformed HTML parsing
- Missing canonical tag scenarios

### Memory Management
- Stream processing for large sitemaps
- Pagination for large result sets
- Cleanup of temporary data

## Security Considerations
- Input sanitization for URLs
- Request header spoofing prevention
- Rate limiting to prevent abuse
- Validation of sitemap URLs
- Safe HTML parsing (no script execution)

## Success Metrics
- Successfully processes 1000+ URLs without memory issues
- Handles various sitemap formats and structures
- Accurate canonical tag detection (95%+ accuracy)
- Clear error reporting for failed URLs
- Intuitive user interface with good UX
- Export functionality works reliably

## Future Enhancements (Post-MVP)
- Bulk domain processing
- Historical tracking and comparison
- Advanced canonical analysis (chains, loops)
- API endpoint for programmatic access
- Scheduled monitoring capabilities
- Integration with SEO tools