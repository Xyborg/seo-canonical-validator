"""
SEO Canonical Tag Validator
A Streamlit web application for validating canonical tags across websites
"""

import streamlit as st
import pandas as pd
import requests
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Tuple, Optional
import validators

from utils.robots_parser import RobotsParser
from utils.sitemap_parser import SitemapParser
from utils.url_processor import URLProcessor
from utils.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="SEO Canonical Tag Validator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    
    # App header
    st.title("🔍 SEO Canonical Tag Validator")
    st.markdown("Validate canonical tags across your website by analyzing sitemaps and URLs")
    
    # Initialize session state
    if 'discovered_sitemaps' not in st.session_state:
        st.session_state.discovered_sitemaps = []
    if 'selected_sitemaps' not in st.session_state:
        st.session_state.selected_sitemaps = []
    if 'extracted_urls' not in st.session_state:
        st.session_state.extracted_urls = []
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    # Sidebar for configuration
    with st.sidebar:
        # Pets Deli Logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://www.petsdeli.de/images/petsdeli-logo.svg", width=100)
        st.markdown("---")
        
        st.header("⚙️ Configuration")
        
        # Processing settings
        st.subheader("Processing Settings")
        concurrent_requests = st.slider("Concurrent Requests", 1, 20, 10)
        request_timeout = st.slider("Request Timeout (seconds)", 5, 60, 30)
        max_retries = st.slider("Max Retries", 1, 5, 3)
        
        # URL normalization options
        st.subheader("URL Normalization")
        force_https = st.checkbox("Force HTTPS", value=True)
        remove_trailing_slash = st.checkbox("Remove Trailing Slash", value=True)
        ignore_query_params = st.checkbox("Ignore Query Parameters", value=False)
        
        # Export options
        st.subheader("Export Options")
        export_format = st.selectbox("Export Format", ["CSV", "Excel"])
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Step 1: Choose URL Source Method
        st.header("🎯 Step 1: Choose URL Source")
        
        # Method overview
        with st.expander("ℹ️ Method Overview - Click to learn more"):
            st.markdown("""
            **🗺️ From Website Sitemaps:**
            - Automatically discover URLs from your website's sitemaps
            - Best for analyzing entire websites or large sections
            - Requires domain input to fetch robots.txt and sitemaps
            
            **📝 Manual URL List:**
            - Directly paste specific URLs you want to analyze
            - Perfect for testing specific pages or small lists
            - No domain discovery needed - just paste and go
            
            **🔄 Both Methods:**
            - Combine automatic sitemap discovery with manual URLs
            - Great for comprehensive analysis with specific additions
            - Duplicates are automatically removed
            """)
        
        url_source = st.radio(
            "How do you want to provide URLs for analysis?",
            ["🗺️ From Website Sitemaps", "📝 Manual URL List", "🔄 Both Methods"],
            help="Choose your preferred method to provide URLs for canonical tag analysis",
            format_func=lambda x: x.split(' ', 1)[1] if ' ' in x else x
        )
        
        # Initialize session state for URL source
        if 'url_source_method' not in st.session_state:
            st.session_state.url_source_method = None
            
        # Update session state when selection changes
        if st.session_state.url_source_method != url_source:
            st.session_state.url_source_method = url_source
            # Reset relevant session state when switching methods
            if url_source == "📝 Manual URL List":
                st.session_state.discovered_sitemaps = []
                st.session_state.selected_sitemaps = []
        
        st.markdown("---")
        
        # Dynamic workflow based on selection
        if url_source in ["🗺️ From Website Sitemaps", "🔄 Both Methods"]:
            # Sitemap-based workflow
            st.header("🌐 Step 2: Enter Domain")
            domain_input = st.text_input(
                "Enter website domain or URL:",
                placeholder="https://example.com or example.com",
                help="Enter the main domain to analyze. The app will fetch robots.txt and discover sitemaps."
            )
            
            if st.button("🔍 Discover Sitemaps") and domain_input:
                with st.spinner("Fetching robots.txt and discovering sitemaps..."):
                    discover_sitemaps(domain_input)
            
            # Step 3: Sitemap Selection (only if sitemaps discovered)
            if st.session_state.discovered_sitemaps:
                st.header("📋 Step 3: Select Sitemaps")
                
                # Display discovered sitemaps
                st.subheader("Discovered Sitemaps")
                sitemap_data = []
                for sitemap in st.session_state.discovered_sitemaps:
                    sitemap_data.append({
                        "Sitemap URL": sitemap["url"],
                        "Type": sitemap["type"],
                        "Status": sitemap["status"],
                        "URL Count": sitemap.get("url_count", "Unknown")
                    })
                
                df_sitemaps = pd.DataFrame(sitemap_data)
                st.dataframe(df_sitemaps, use_container_width=True)
                
                # Multi-select for sitemaps
                sitemap_options = [f"{s['url']} ({s['type']})" for s in st.session_state.discovered_sitemaps]
                selected_sitemap_indices = st.multiselect(
                    "Select sitemaps to analyze:",
                    range(len(sitemap_options)),
                    format_func=lambda x: sitemap_options[x],
                    help="Choose one or more sitemaps to extract URLs from"
                )
                
                st.session_state.selected_sitemaps = [
                    st.session_state.discovered_sitemaps[i] for i in selected_sitemap_indices
                ]
        
        # Manual URL input section
        manual_urls = []
        if url_source in ["📝 Manual URL List", "🔄 Both Methods"]:
            if url_source == "📝 Manual URL List":
                st.header("📝 Step 2: Enter URLs")
            else:
                st.header("📝 Step 4: Additional Manual URLs")
            
            manual_url_text = st.text_area(
                "Paste URLs (one per line):",
                height=150,
                placeholder="https://example.com/page1\nhttps://example.com/page2\nhttps://example.com/page3",
                help="Enter each URL on a separate line. URLs will be validated automatically."
            )
            
            if manual_url_text:
                manual_urls = [url.strip() for url in manual_url_text.split('\n') if url.strip()]
                st.info(f"📄 {len(manual_urls)} URLs entered manually")
                
                # Show preview of URLs
                if len(manual_urls) > 0:
                    with st.expander(f"👁️ Preview URLs ({len(manual_urls)} total)"):
                        for i, url in enumerate(manual_urls[:10], 1):  # Show first 10
                            if validators.url(url):
                                st.markdown(f"{i}. ✅ `{url}`")
                            else:
                                st.markdown(f"{i}. ❌ `{url}` (invalid)")
                        
                        if len(manual_urls) > 10:
                            st.markdown(f"... and {len(manual_urls) - 10} more URLs")
        
        # Extract URLs button - dynamic step numbering
        if url_source == "📝 Manual URL List":
            next_step = "Step 3"
        elif url_source == "🗺️ From Website Sitemaps":
            next_step = "Step 4"
        else:  # Both methods
            next_step = "Step 5"
            
        if (st.session_state.selected_sitemaps and url_source in ["🗺️ From Website Sitemaps", "🔄 Both Methods"]) or \
           (manual_urls and url_source in ["📝 Manual URL List", "🔄 Both Methods"]):
            
            st.markdown("---")
            st.header(f"📤 {next_step}: Extract URLs")
            
            if st.button("📤 Extract & Validate URLs", type="primary"):
                with st.spinner("Extracting URLs from selected sources..."):
                    extract_urls(url_source, manual_urls)
        
        # Process URLs section - dynamic step numbering
        if st.session_state.extracted_urls:
            if url_source == "📝 Manual URL List":
                final_step = "Step 4"
            elif url_source == "🗺️ From Website Sitemaps":
                final_step = "Step 5"
            else:  # Both methods
                final_step = "Step 6"
                
            st.markdown("---")
            st.header(f"🔄 {final_step}: Process URLs")
            
            st.info(f"📊 Total URLs ready for processing: {len(st.session_state.extracted_urls)}")
            
            if st.button("🚀 Start Canonical Analysis", type="primary"):
                process_urls(concurrent_requests, request_timeout, max_retries, 
                           force_https, remove_trailing_slash, ignore_query_params)
    
    with col2:
        # Progress and status
        st.header("📈 Status")
        
        # Show current URL source method
        if 'url_source_method' in st.session_state and st.session_state.url_source_method:
            method_name = st.session_state.url_source_method.split(' ', 1)[1] if ' ' in st.session_state.url_source_method else st.session_state.url_source_method
            st.info(f"**Method:** {method_name}")
        
        # Sitemap-related metrics (only show for sitemap methods)
        if url_source in ["🗺️ From Website Sitemaps", "🔄 Both Methods"]:
            if st.session_state.discovered_sitemaps:
                st.metric("Discovered Sitemaps", len(st.session_state.discovered_sitemaps))
            
            if st.session_state.selected_sitemaps:
                st.metric("Selected Sitemaps", len(st.session_state.selected_sitemaps))
        
        # URL metrics
        if st.session_state.extracted_urls:
            st.metric("URLs Ready", len(st.session_state.extracted_urls))
        
        # Results metrics
        if st.session_state.results is not None:
            results_df = st.session_state.results
            st.metric("Total Processed", len(results_df))
            
            # Status breakdown
            st.markdown("**Results Breakdown:**")
            status_counts = results_df['Status'].value_counts()
            for status, count in status_counts.items():
                if status == "Match":
                    st.metric("✅ Matches", count)
                elif status == "Mismatch":
                    st.metric("❌ Mismatches", count)
                elif status == "Error":
                    st.metric("⚠️ Errors", count)
                else:
                    st.metric(status, count)
        
        # Quick help section
        st.markdown("---")
        st.markdown("**💡 Quick Tips:**")
        if url_source == "📝 Manual URL List":
            st.markdown("• Enter one URL per line")
            st.markdown("• URLs are validated automatically")
            st.markdown("• Invalid URLs will be skipped")
        elif url_source == "🗺️ From Website Sitemaps":
            st.markdown("• Enter the main domain first")
            st.markdown("• Select relevant sitemaps")
            st.markdown("• Index sitemaps contain most URLs")
        else:  # Both methods
            st.markdown("• Combine sitemaps + manual URLs")
            st.markdown("• Duplicates are removed automatically")
            st.markdown("• Use manual URLs for specific pages")
    
    # Step 5: Results Display
    if st.session_state.results is not None:
        st.header("📊 Results")
        display_results(export_format)
    
    # Footer
    add_footer()

def discover_sitemaps(domain: str):
    """Discover sitemaps from robots.txt"""
    try:
        robots_parser = RobotsParser()
        sitemaps = robots_parser.discover_sitemaps(domain)
        
        if sitemaps:
            st.session_state.discovered_sitemaps = sitemaps
            st.success(f"✅ Found {len(sitemaps)} sitemap(s)")
        else:
            st.warning("⚠️ No sitemaps found in robots.txt")
            st.session_state.discovered_sitemaps = []
            
    except Exception as e:
        st.error(f"❌ Error discovering sitemaps: {str(e)}")
        st.session_state.discovered_sitemaps = []

def extract_urls(url_source: str, manual_urls: List[str]):
    """Extract URLs from selected sources"""
    try:
        all_urls = set()
        
        # From sitemaps
        if url_source in ["🗺️ From Website Sitemaps", "🔄 Both Methods"] and st.session_state.selected_sitemaps:
            sitemap_parser = SitemapParser()
            for sitemap in st.session_state.selected_sitemaps:
                urls = sitemap_parser.extract_urls(sitemap["url"])
                all_urls.update(urls)
                st.info(f"📄 Extracted {len(urls)} URLs from {sitemap['url']}")
        
        # From manual input
        if url_source in ["📝 Manual URL List", "🔄 Both Methods"] and manual_urls:
            # Validate manual URLs
            valid_manual_urls = []
            invalid_count = 0
            for url in manual_urls:
                if validators.url(url):
                    valid_manual_urls.append(url)
                else:
                    invalid_count += 1
                    st.warning(f"⚠️ Invalid URL skipped: {url}")
            
            all_urls.update(valid_manual_urls)
            st.info(f"📝 Added {len(valid_manual_urls)} valid manual URLs")
            if invalid_count > 0:
                st.warning(f"⚠️ {invalid_count} invalid URLs were skipped")
        
        st.session_state.extracted_urls = list(all_urls)
        st.success(f"✅ Total unique URLs extracted: {len(st.session_state.extracted_urls)}")
        
    except Exception as e:
        st.error(f"❌ Error extracting URLs: {str(e)}")

def process_urls(concurrent_requests: int, request_timeout: int, max_retries: int,
                force_https: bool, remove_trailing_slash: bool, ignore_query_params: bool):
    """Process URLs and analyze canonical tags"""
    try:
        url_processor = URLProcessor(
            concurrent_requests=concurrent_requests,
            request_timeout=request_timeout,
            max_retries=max_retries,
            force_https=force_https,
            remove_trailing_slash=remove_trailing_slash,
            ignore_query_params=ignore_query_params
        )
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(processed: int, total: int, current_url: str):
            progress = processed / total
            progress_bar.progress(progress)
            status_text.text(f"Processing {processed}/{total}: {current_url}")
        
        # Process URLs
        results = url_processor.process_urls(st.session_state.extracted_urls, update_progress)
        
        # Convert results to DataFrame
        st.session_state.results = pd.DataFrame(results)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.success("✅ URL processing completed!")
        
    except Exception as e:
        st.error(f"❌ Error processing URLs: {str(e)}")

def display_results(export_format: str):
    """Display and export results"""
    results_df = st.session_state.results
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status:",
            options=results_df['Status'].unique(),
            default=results_df['Status'].unique()
        )
    
    with col2:
        show_only_mismatches = st.checkbox("Show Only Mismatches")
    
    with col3:
        if st.button("📥 Export Results"):
            export_results(results_df, export_format)
    
    # Apply filters
    filtered_df = results_df[results_df['Status'].isin(status_filter)]
    
    if show_only_mismatches:
        filtered_df = filtered_df[filtered_df['Status'] == 'Mismatch']
    
    # Display results table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "URL": st.column_config.LinkColumn("URL"),
            "Canonical URL": st.column_config.LinkColumn("Canonical URL"),
            "Status": st.column_config.TextColumn("Status"),
            "Error": st.column_config.TextColumn("Error Details")
        }
    )
    
    # Summary statistics
    st.subheader("📈 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total URLs", len(results_df))
    with col2:
        matches = len(results_df[results_df['Status'] == 'Match'])
        st.metric("Matches", matches)
    with col3:
        mismatches = len(results_df[results_df['Status'] == 'Mismatch'])
        st.metric("Mismatches", mismatches)
    with col4:
        errors = len(results_df[results_df['Status'] == 'Error'])
        st.metric("Errors", errors)

def export_results(results_df: pd.DataFrame, export_format: str):
    """Export results to file"""
    try:
        report_generator = ReportGenerator()
        
        if export_format == "CSV":
            csv_data = report_generator.export_csv(results_df)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"canonical_analysis_{int(time.time())}.csv",
                mime="text/csv"
            )
        elif export_format == "Excel":
            excel_data = report_generator.export_excel(results_df)
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"canonical_analysis_{int(time.time())}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.success("✅ Export ready for download!")
        
    except Exception as e:
        st.error(f"❌ Error exporting results: {str(e)}")

def add_footer():
    """Add footer with creator information"""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 20px 0; color: #666; font-size: 14px;'>
            <p>🔍 <strong>SEO Canonical Tag Validator</strong></p>
            <p>Created by <strong><a href="https://www.martinaberastegue.com/" target="_blank">Martin Aberastegue</a></strong> | 
            Check the code in <a href="https://github.com/Xyborg/seo-canonical-validator" target="_blank">GitHub</a></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()