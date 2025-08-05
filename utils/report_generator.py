"""
Report generator for exporting analysis results
"""

import pandas as pd
from io import BytesIO, StringIO
from typing import Dict, List
import json

class ReportGenerator:
    """Generator for various report formats"""
    
    def __init__(self):
        pass
    
    def export_csv(self, results_df: pd.DataFrame) -> str:
        """Export results to CSV format"""
        # Create string buffer
        output = StringIO()
        
        # Write CSV
        results_df.to_csv(output, index=False, encoding='utf-8')
        
        # Get CSV string
        csv_string = output.getvalue()
        output.close()
        
        return csv_string
    
    def export_excel(self, results_df: pd.DataFrame) -> bytes:
        """Export results to Excel format with multiple sheets"""
        # Create bytes buffer
        output = BytesIO()
        
        # Create Excel writer
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main results sheet
            results_df.to_excel(writer, sheet_name='All Results', index=False)
            
            # Summary sheet
            summary_df = self._create_summary_dataframe(results_df)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Issues sheet (mismatches and errors)
            issues_df = results_df[results_df['Status'].isin(['Mismatch', 'Error', 'Multiple', 'Empty'])]
            if not issues_df.empty:
                issues_df.to_excel(writer, sheet_name='Issues', index=False)
            
            # Matches sheet
            matches_df = results_df[results_df['Status'] == 'Match']
            if not matches_df.empty:
                matches_df.to_excel(writer, sheet_name='Matches', index=False)
        
        # Get Excel bytes
        excel_bytes = output.getvalue()
        output.close()
        
        return excel_bytes
    
    def _create_summary_dataframe(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """Create summary statistics dataframe"""
        total_urls = len(results_df)
        
        # Count by status
        status_counts = results_df['Status'].value_counts()
        
        # Calculate percentages
        summary_data = []
        
        for status, count in status_counts.items():
            percentage = (count / total_urls) * 100
            summary_data.append({
                'Status': status,
                'Count': count,
                'Percentage': f"{percentage:.1f}%"
            })
        
        # Add total row
        summary_data.append({
            'Status': 'TOTAL',
            'Count': total_urls,
            'Percentage': '100.0%'
        })
        
        # Additional metrics
        if 'Response Time' in results_df.columns:
            avg_response_time = results_df['Response Time'].mean()
            if pd.notna(avg_response_time):
                summary_data.append({
                    'Status': 'Avg Response Time',
                    'Count': f"{avg_response_time:.2f}s",
                    'Percentage': ''
                })
        
        # HTTP status codes
        if 'HTTP Status' in results_df.columns:
            http_status_counts = results_df['HTTP Status'].value_counts()
            for status_code, count in http_status_counts.items():
                if pd.notna(status_code):
                    summary_data.append({
                        'Status': f'HTTP {status_code}',
                        'Count': count,
                        'Percentage': f"{(count / total_urls) * 100:.1f}%"
                    })
        
        return pd.DataFrame(summary_data)
    
    def export_json(self, results_df: pd.DataFrame) -> str:
        """Export results to JSON format"""
        # Convert DataFrame to dictionary
        results_dict = results_df.to_dict('records')
        
        # Add metadata
        export_data = {
            'metadata': {
                'total_urls': len(results_df),
                'export_timestamp': pd.Timestamp.now().isoformat(),
                'summary': self._get_summary_stats(results_df)
            },
            'results': results_dict
        }
        
        return json.dumps(export_data, indent=2, default=str)
    
    def _get_summary_stats(self, results_df: pd.DataFrame) -> Dict:
        """Get summary statistics as dictionary"""
        status_counts = results_df['Status'].value_counts().to_dict()
        
        summary = {
            'total_urls': len(results_df),
            'status_breakdown': status_counts
        }
        
        # Add response time stats if available
        if 'Response Time' in results_df.columns:
            response_times = results_df['Response Time'].dropna()
            if not response_times.empty:
                summary['response_time_stats'] = {
                    'average': float(response_times.mean()),
                    'median': float(response_times.median()),
                    'min': float(response_times.min()),
                    'max': float(response_times.max())
                }
        
        return summary
    
    def create_detailed_report(self, results_df: pd.DataFrame) -> str:
        """Create a detailed text report"""
        total_urls = len(results_df)
        status_counts = results_df['Status'].value_counts()
        
        report_lines = [
            "SEO CANONICAL TAG VALIDATION REPORT",
            "=" * 50,
            "",
            f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total URLs Analyzed: {total_urls:,}",
            "",
            "SUMMARY BY STATUS:",
            "-" * 20
        ]
        
        for status, count in status_counts.items():
            percentage = (count / total_urls) * 100
            report_lines.append(f"{status:15} : {count:6,} ({percentage:5.1f}%)")
        
        # Add issues section if there are any
        issues_df = results_df[results_df['Status'].isin(['Mismatch', 'Error', 'Multiple', 'Empty'])]
        if not issues_df.empty:
            report_lines.extend([
                "",
                "DETAILED ISSUES:",
                "-" * 15,
                ""
            ])
            
            for _, row in issues_df.iterrows():
                report_lines.append(f"URL: {row['URL']}")
                report_lines.append(f"Status: {row['Status']}")
                if pd.notna(row.get('Canonical URL')):
                    report_lines.append(f"Canonical: {row['Canonical URL']}")
                if pd.notna(row.get('Error')):
                    report_lines.append(f"Error: {row['Error']}")
                report_lines.append("")
        
        # Add performance metrics
        if 'Response Time' in results_df.columns:
            response_times = results_df['Response Time'].dropna()
            if not response_times.empty:
                report_lines.extend([
                    "",
                    "PERFORMANCE METRICS:",
                    "-" * 19,
                    f"Average Response Time: {response_times.mean():.2f}s",
                    f"Median Response Time: {response_times.median():.2f}s",
                    f"Fastest Response: {response_times.min():.2f}s",
                    f"Slowest Response: {response_times.max():.2f}s"
                ])
        
        return "\n".join(report_lines)