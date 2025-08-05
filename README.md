# 🔍 SEO Canonical Tag Validator

A comprehensive Streamlit web application for validating canonical tags across websites by analyzing sitemaps and URLs.

## 🌐 Online Demo

Try the live application: **[SEO Canonical Checker](https://seo-canonical-checker.streamlit.app/)**

## 🚀 Features

### Core Functionality
- **Automatic Sitemap Discovery**: Fetches robots.txt and discovers all sitemaps
- **Multi-Format Support**: Handles XML, text, compressed, and JSON sitemaps
- **Flexible URL Input**: Use sitemaps, manual URL lists, or both
- **Canonical Analysis**: Extracts and compares canonical tags with actual URLs
- **Comprehensive Reporting**: Detailed analysis with export capabilities

### Advanced Features
- **URL Normalization**: Configurable options for HTTPS, trailing slashes, query parameters
- **Concurrent Processing**: Fast analysis with configurable concurrency limits
- **Progress Tracking**: Real-time progress indicators during processing
- **Error Handling**: Robust error handling with detailed error reporting
- **Export Options**: CSV and Excel export with summary statistics

## 📋 Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## 🛠️ Installation

1. Clone or download the project files
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## 🎯 Usage

### Step 1: Enter Domain
- Input your website domain (with or without protocol)
- Click "Discover Sitemaps" to fetch robots.txt and find sitemaps

### Step 2: Select Sitemaps
- Review discovered sitemaps with their types and status
- Select one or more sitemaps for analysis
- Preview sitemap contents if needed

### Step 3: Choose URL Sources
- **From Selected Sitemaps**: Extract URLs from chosen sitemaps
- **Manual URL List**: Paste your own list of URLs
- **Both**: Combine sitemap URLs with manual input

### Step 4: Configure Processing
Use the sidebar to configure:
- **Concurrent Requests**: Number of simultaneous requests (1-20)
- **Request Timeout**: Timeout for each request (5-60 seconds)
- **Max Retries**: Retry attempts for failed requests (1-5)
- **URL Normalization**: HTTPS forcing, trailing slash handling, query parameters

### Step 5: Analyze & Export
- Start canonical analysis and monitor progress
- Review results with filtering options
- Export to CSV or Excel format

## 📊 Analysis Results

The application provides detailed analysis for each URL:

### Status Types
- ✅ **Match**: Canonical URL matches the page URL
- ❌ **Mismatch**: Canonical URL differs from page URL
- ⚠️ **Missing**: No canonical tag found
- 🔀 **Multiple**: Multiple canonical tags detected
- 📭 **Empty**: Canonical tag exists but is empty
- ❌ **Error**: Failed to process URL (network/parsing errors)

### Report Includes
- Original URL and final URL (after redirects)
- Canonical URL found in the page
- HTTP status codes and response times
- Detailed error messages for failed URLs
- Summary statistics and performance metrics

## 🏗️ Architecture

### Main Components
- `app.py`: Main Streamlit application interface
- `utils/robots_parser.py`: Robots.txt parsing and sitemap discovery
- `utils/sitemap_parser.py`: Multi-format sitemap parsing
- `utils/url_processor.py`: URL processing and canonical tag extraction
- `utils/report_generator.py`: Report generation and export functionality

### Key Features
- **Modular Design**: Clean separation of concerns
- **Error Resilience**: Comprehensive error handling at all levels
- **Performance Optimized**: Concurrent processing with connection pooling
- **User-Friendly**: Intuitive interface with progress feedback
- **Extensible**: Easy to add new features or modify existing ones

## 🔧 Configuration Options

### Processing Settings
- Concurrent request limits
- Request timeouts and retries
- User agent customization

### URL Normalization
- Force HTTPS protocol
- Trailing slash handling
- Query parameter inclusion/exclusion
- Case sensitivity options

### Export Options
- Multiple format support (CSV, Excel, JSON)
- Customizable report sections
- Summary statistics inclusion

## 🛡️ Error Handling

The application handles various error scenarios:
- Network timeouts and connection errors
- Invalid URLs and malformed sitemaps
- Missing robots.txt files
- HTTP errors (4xx, 5xx status codes)
- Malformed HTML and missing canonical tags
- Large dataset processing

## 📈 Performance

### Optimizations
- Connection pooling for HTTP requests
- Concurrent processing with configurable limits
- Efficient memory usage for large datasets
- Progress tracking for long operations

### Benchmarks
- Processes 1000+ URLs efficiently
- Handles sitemaps with 10,000+ URLs
- Memory usage optimized for large datasets
- Average processing: ~100-200 URLs per minute (depending on site response times)

## 🔍 Use Cases

### SEO Audits
- Validate canonical implementation across entire website
- Identify canonical tag issues and inconsistencies
- Monitor canonical tag compliance over time

### Site Migrations
- Verify canonical tags during domain migrations
- Check canonical implementation on new sites
- Validate redirect and canonical tag combinations

### Technical SEO
- Bulk canonical tag analysis
- Identify duplicate content issues
- Verify international SEO canonical implementation

## 🤝 Contributing

The application is designed to be easily extensible:
- Add new sitemap formats in `sitemap_parser.py`
- Extend analysis in `url_processor.py`
- Add new export formats in `report_generator.py`
- Enhance UI in `app.py`

## 📝 License

This project is provided as-is for educational and professional use.

## 🆘 Support

For issues or questions:
1. Check the error messages in the application
2. Review the configuration settings
3. Verify network connectivity to target websites
4. Check that target websites allow crawling

## 🎉 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) for the web interface
- [Requests](https://requests.readthedocs.io/) for HTTP handling
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [pandas](https://pandas.pydata.org/) for data manipulation