# 📖 SEO Canonical Tag Validator - Usage Guide

## Quick Start

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run Application**
```bash
streamlit run app.py
```

3. **Open Browser**
The app will automatically open at `http://localhost:8501`

## Step-by-Step Workflow

### 1. 🌐 Enter Domain
- Input your website domain in the text field
- Examples: `example.com`, `https://example.com`, `www.example.com`
- Click **"🔍 Discover Sitemaps"**

### 2. 📋 Review Discovered Sitemaps
The app will show:
- **Sitemap URL**: Full path to each sitemap
- **Type**: XML Sitemap, XML Index, Text Sitemap, etc.
- **Status**: Available/Error
- **URL Count**: Number of URLs in each sitemap

### 3. ✅ Select Sitemaps
- Use the multi-select dropdown to choose sitemaps
- You can select multiple sitemaps for analysis
- Preview option shows first few URLs from each sitemap

### 4. 📝 Choose URL Source
Three options available:

#### Option A: From Selected Sitemaps
- Uses URLs extracted from your chosen sitemaps
- Automatically handles XML parsing and URL extraction

#### Option B: Manual URL List
- Paste your own list of URLs (one per line)
- Perfect for testing specific pages
- Example input:
```
https://example.com/page1
https://example.com/page2
https://example.com/blog/post1
```

#### Option C: Both
- Combines sitemap URLs with manual input
- Removes duplicates automatically

### 5. ⚙️ Configure Settings (Sidebar)

#### Processing Settings
- **Concurrent Requests**: How many URLs to process simultaneously (1-20)
  - Higher = faster, but may overwhelm servers
  - Recommended: 5-10 for most sites
- **Request Timeout**: How long to wait for each page (5-60 seconds)
- **Max Retries**: How many times to retry failed requests (1-5)

#### URL Normalization
- **Force HTTPS**: Convert HTTP URLs to HTTPS for comparison
- **Remove Trailing Slash**: Normalize URLs ending with `/`
- **Ignore Query Parameters**: Remove `?param=value` from URLs

### 6. 🚀 Start Analysis
- Click **"🚀 Start Canonical Analysis"**
- Watch the progress bar and current URL being processed
- Processing time depends on number of URLs and site response times

### 7. 📊 Review Results

#### Result Status Types
- **✅ Match**: Canonical URL matches page URL perfectly
- **❌ Mismatch**: Canonical URL is different from page URL
- **⚠️ Missing**: No canonical tag found on the page
- **🔀 Multiple**: Multiple canonical tags found (SEO issue)
- **📭 Empty**: Canonical tag exists but has no value
- **❌ Error**: Failed to load page or parse HTML

#### Results Table Columns
- **URL**: Original URL from sitemap/input
- **Final URL**: URL after following redirects
- **Canonical URL**: Value found in canonical tag
- **Status**: Match/Mismatch/Error/etc.
- **Error**: Detailed error message if applicable
- **Response Time**: How long the page took to load
- **HTTP Status**: 200, 404, 500, etc.

### 8. 📥 Filter and Export

#### Filtering Options
- Filter by status type (Match, Mismatch, Error, etc.)
- Show only mismatches checkbox
- Use table search for specific URLs

#### Export Options
- **CSV**: Simple comma-separated format
- **Excel**: Multi-sheet workbook with:
  - All Results sheet
  - Summary statistics sheet
  - Issues-only sheet
  - Matches-only sheet

## 🔍 Common Use Cases

### Basic SEO Audit
1. Enter your domain
2. Select main sitemap
3. Use default settings
4. Export mismatches for fixing

### International Site Audit
1. Select multiple language/region sitemaps
2. Enable "Force HTTPS" and "Remove Trailing Slash"
3. Look for canonical issues between language versions

### Post-Migration Validation
1. Manual input old URLs
2. Check if canonicals point to new domain
3. Identify missing canonical tags

### Large Site Analysis
1. Increase concurrent requests to 15-20
2. Select multiple sitemaps
3. Process in batches if memory issues occur

## ⚠️ Troubleshooting

### Common Issues

#### "No sitemaps found"
- Check if robots.txt exists: `yoursite.com/robots.txt`
- Try manual sitemap URLs: `yoursite.com/sitemap.xml`
- Some sites don't list sitemaps in robots.txt

#### "Request timeout errors"
- Increase timeout in sidebar (try 45-60 seconds)
- Reduce concurrent requests (try 3-5)
- Some pages are naturally slow

#### "Memory issues with large datasets"
- Process URLs in smaller batches
- Reduce concurrent requests
- Close other applications

#### "Too many connection errors"
- Reduce concurrent requests to 1-3
- Increase timeout
- Some servers block rapid requests

### Performance Tips

#### For Large Sites (10,000+ URLs)
- Start with 5 concurrent requests
- Use 30-45 second timeout
- Process in chunks if needed
- Monitor memory usage

#### For Slow Sites
- Reduce concurrent requests to 3-5
- Increase timeout to 45-60 seconds
- Enable retry attempts (3-5)

#### For Fast Analysis
- Increase concurrent requests to 15-20
- Use shorter timeout (15-30 seconds)
- Focus on specific sitemaps

## 📈 Interpreting Results

### Healthy Site Indicators
- 90%+ Match status
- Few or no Multiple canonical tags
- Minimal Error rates
- Fast average response times

### Red Flags
- High Mismatch percentage
- Many Missing canonical tags
- Multiple canonical tags on pages
- High Error rates

### Next Steps After Analysis
1. **Fix Mismatches**: Update canonical tags to match page URLs
2. **Add Missing**: Implement canonical tags on pages without them
3. **Remove Duplicates**: Fix pages with multiple canonical tags
4. **Investigate Errors**: Check why pages failed to load

## 🛡️ Best Practices

### Before Running Analysis
- Check robots.txt manually first
- Test with small batch of URLs
- Verify site allows crawling
- Consider server load during analysis

### During Analysis
- Monitor progress and error rates
- Stop if too many errors occur
- Adjust settings if timeouts are frequent

### After Analysis
- Export results immediately
- Review summary statistics first
- Focus on fixing critical issues first
- Re-run analysis after fixes

## 💡 Pro Tips

1. **Start Small**: Test with 10-50 URLs first
2. **Check Robots.txt**: Verify sitemaps are actually listed
3. **Use Manual Input**: For testing specific problem pages
4. **Multiple Runs**: Run before and after fixes to compare
5. **Save Settings**: Note successful configurations for future use
6. **Batch Processing**: For huge sites, process sitemaps individually

## 🔧 Advanced Configuration

### Custom User Agent
Modify `user_agent` in utility classes if needed for specific sites.

### Rate Limiting
Adjust concurrent requests based on target server capacity.

### URL Patterns
Use manual input to test specific URL patterns or problematic sections.

### Export Formats
Use Excel export for stakeholder reports, CSV for further analysis.