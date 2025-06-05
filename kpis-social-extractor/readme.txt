# KPIs Social Extractor

KPIs Social Extractor is a powerful web application built with Python and Flask that automatically extracts and analyzes key performance indicators (KPIs) from social media platforms using a hybrid approach combining official APIs, advanced web scraping, and human behavior simulation.

## Features

- **Hybrid Extraction System**: Three-tiered approach for maximum reliability
  - Level 1: Official APIs when available
  - Level 2: Advanced web scraping with anti-detection
  - Level 3: Human behavior simulation for challenging platforms

- **Supported Platforms**:
  - Facebook
  - Instagram
  - YouTube
  - LinkedIn
  - Twitter/X
  - TikTok

- **Key Metrics Extracted**:
  - Follower/Subscriber counts
  - Post/Content counts
  - Engagement metrics (likes, comments, shares)
  - Growth trends and historical data
  - Engagement rates and performance scores

- **Advanced Anti-Detection**:
  - Browser fingerprint randomization
  - Human-like mouse movements and scrolling
  - Timing variations and natural delays
  - Proxy rotation support
  - Session persistence

- **Interactive Dashboard**:
  - Visual KPI comparisons across platforms
  - Engagement analysis and trends
  - Performance scoring
  - Actionable recommendations

## Technical Details

- **Backend**: Python 3.8+ with Flask
- **Web Scraping**: Playwright with custom anti-detection
- **API Integration**: Native Python requests with rate limiting
- **Frontend**: HTML5, CSS3, JavaScript with Chart.js
- **Data Processing**: Pandas and NumPy

## Use Cases

- **Business Intelligence**: Track social media performance metrics
- **Competitive Analysis**: Compare KPIs against competitors
- **Marketing Strategy**: Identify high-performing platforms and content
- **ROI Measurement**: Quantify social media investment returns

## Security and Ethics

This tool is designed for legitimate business analytics purposes only. It:
- Respects robots.txt directives
- Implements rate limiting to prevent server overload
- Does not extract private or protected information
- Complies with platform terms of service when using official APIs

## Getting Started

See the included `kse_installation.txt` file for detailed installation and usage instructions.
