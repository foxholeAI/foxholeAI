> Homepage is English README. You can view the [简体中文](README_ZH.md) version.

# Foxhole AI

Foxhole AI is an end-to-end open-source prototype designed for traders and researchers, providing real-time monitoring of influential social media accounts, keyword detection, contract address verification, and basic risk auditing, with instant push notifications to help users identify potential trading opportunities and risks faster.

## 1. Deliverables

- [x] GitHub Repository: Contains complete code and this README
- [x] Video: [Youtube](https://www.youtube.com/watch?v=nn3zgyBGgdQ)
- [x] Pitch Deck: [Google Drive](https://docs.google.com/presentation/d/1BfsnzbwMK1iYdB9Vr3OD1x7NMVJrydJ9/edit?usp=sharing&ouid=114972223476033742889&rtpof=true&sd=true)

## 2. Overview

- **Project Name**: Foxhole AI
- **One-Liner**: Real-time monitoring of influential Twitter accounts (CZ, Heyi, Elon Musk, etc.) for crypto keywords, instantly pushing AI-verified contract addresses to traders, eliminating manual searches and enabling one-click token purchases.
- **Target Users**: Cryptocurrency traders (quantitative/manual), on-chain snipers, crypto researchers, information flow bot developers.
- **Pain Points**:
  - **Notification Delays**: Traders miss critical mentions from key opinion leaders (KOLs), losing early entry opportunities.
  - **Manual Contract Address Hunting**: Time-consuming contract address searches lead to missed trades and exposure to scam projects and rug pulls.
  - **Information Overload**: Manually monitoring multiple high-influence social media accounts simultaneously is impossible at scale.
  - **Speed Disadvantage**: Manual processes cannot compete with automated systems executing trades in milliseconds. In the crypto world, seconds can mean the difference between profit and loss.
- **Solution**:

  - **Real-time Intelligence Engine**: Advanced keyword detection algorithms monitor high-influence accounts (CZ, Heyi, Elon Musk, etc.) 24/7 with zero latency response.
  - Monitor subsystem continuously scrapes Dex Screener token data (high-frequency, deduplication, CSV persistence).

  - Extractor subsystem (BERT/TF-IDF/rule-based/regex/NER) performs keyword and entity extraction on text.

  - **Contract Address Verification**: AI-driven validation ensures users receive legitimate contract addresses, preventing rug pulls and scam projects.
  - **Instant Notification Push**: The moment keywords are detected, trading opportunities are pushed directly to user devices via WebSocket.
  - **Automation Advantage**: Uses the same high-frequency trading technology as professional sniping bots, with millisecond-level response.
  - **Risk Mitigation**: Built-in security features analyze token legitimacy and market conditions before recommendations.

## 3. Architecture & Implementation

- **Overview Diagram**

![](https://cdn.jsdelivr.net/gh/timerring/scratchpad2023/2024/2025-10-31-20-36-03.png)

- **Key Modules**:
  - Frontend: https://github.com/yidongw/foxhole-bot-frontend
  - Monitor: `monitor/token_monitor.py`, `monitor/config.py`, `monitor/start.sh`, `monitor/redis_api.py`
  - Social Media Listener: `monitor/twitter_listener.py`
  - Extractor: `extractor/bert_extractor.py`, `extractor/spacy_ner_extractor.py`, `extractor/tfidf_extractor.py`, `extractor/rule_based_extractor.py`, `extractor/regex_extractor.py`, `extractor/realtime_bert_analyzer.py`, `extractor/redis_token_matcher.py`
  - Audit: `audit/realtime_auditor.py`, `audit/audit_tokens.py`
  - Real-time Distribution: `ws_server.py`, `realtime_ca_detector.py`
  - Telegram Push: `telegram/webhook_forwarder.py`, `telegram/telegram_bot.py`, `telegram/start.sh`
  - Log Management: `scripts/log_rotation.py`, `scripts/setup_log_rotation.sh`, `scripts/cleanup_old_logs.sh`
  - Redis Layer: `monitor/redis_api.py`, `monitor/migrate_csv_to_redis.py`, `monitor/query_redis_tokens.py`, `monitor/add_token_manual.py`
  - Main Startup Script: `start.sh`
- **Dependencies & Tech Stack**:
  - Language & Runtime: Python 3.10+ (virtual environment recommended)
  - Core Dependencies: See `requirements.txt` (includes `requests`, `aiohttp`, `websockets`, `python-dotenv`, etc.)
  - Monitor Dependencies: See `monitor/requirements.txt` (`aiohttp`, `asyncio`, `redis`, `flask`)
  - Extractor Dependencies: See `extractor/requirements_extractor.txt` (`transformers`, `torch`, `spacy`, etc.)
  - Telegram Dependencies: See `telegram/requirements.txt` (`requests`, `websockets`, `python-dotenv`)
  - Async & Networking: `asyncio`, `aiohttp`, `websockets`
  - NLP: `transformers`/`torch` (BERT), `spaCy` (NER)
  - Data Storage: SQLite (local database), CSV (data persistence), Redis (high-performance caching layer)

## 4. Run & Reproduce

- **Prerequisites**:

  - Python 3.10+ with `pip`
  - Redis 6.0+ (required for high-performance caching layer)
  - Stable network connection
  - (Optional) Telegram Bot Token (if using Telegram push notifications)

- **Environment Variable Configuration**:

```bash
# telegram/.env (example for Telegram push module)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
WS_URL=ws://localhost:8765
```

- **Install Dependencies (by module)**:

```bash
# Navigate to project root
cd /root/nlpmeme

# Method 1: Install core dependencies (recommended first)
pip install -r requirements.txt

# Method 2: Install by module
# Monitor module dependencies
pip install -r monitor/requirements.txt

# Extractor module dependencies (on-demand, includes BERT, spaCy, etc.)
pip install -r extractor/requirements_extractor.txt
# If using spaCy, also download the model:
# python -m spacy download en_core_web_sm

# Telegram push module dependencies (on-demand)
pip install -r telegram/requirements.txt
```

- **Quick Start (token monitoring only)**:

```bash
# Ensure Redis is running
redis-cli ping

cd monitor

# Method 1: Use startup script
bash start.sh

# Method 2: Direct run
python token_monitor.py
# Will write to Redis and CSV in real-time, printing statistics
```

- **One-Click Start All Services (recommended)**:

```bash
# In project root directory
bash start.sh start

# Check service status
bash start.sh status

# View logs
bash start.sh logs all

# Stop all services
bash start.sh stop
```

- **Module-by-Module Startup**:

```bash
# 1. Start WebSocket server (core service)
python ws_server.py --host 0.0.0.0 --port 8765 --watch-file data/ws.json

# 2. Start real-time contract address detector
python realtime_ca_detector.py --no-bert --no-ai --min-confidence 0.5

# 3. Start Telegram forwarder (optional)
cd telegram
bash start.sh
# Or run directly
python webhook_forwarder.py
```

- **Data & Examples**:

  - Data Directory: `data/`
    - Example Tweets: `user_tweets_44196397.json` (Elon Musk), `user_tweets_902926941413453824.json` (CZ), `user_tweets_1003840309166366721.json` (Heyi)
    - Database: `meme_coins.db` (SQLite database)
    - WebSocket Data: `ws.json` (real-time push contract address data)
  - Monitor Data: `monitor/tokens_data.csv` (token monitoring historical data)
  - Extraction Results: `extractor/output/` (output from various extractors)
  - Log Files: `monitor/monitor.log`, `telegram/logs/`, `ws_server.txt`, `realtime_ca_detector.txt`

- **Service Management**:

```bash
# Install Monitor service using systemd (optional)
cd monitor
sudo bash install_service.sh

# Install Telegram service using systemd (optional)
cd telegram
sudo bash install_service.sh

# Setup log rotation (optional)
cd scripts
bash setup_log_rotation.sh
```

## 5. Key Flows

- **Key Use Case Steps**:
  
  **Use Case 1: Real-time Token Monitoring & Data Collection**
  - Launch `token_monitor.py` to continuously scrape popular token data from DexScreener
  - Automatically deduplicate and store to `tokens_data.csv`, tracking scrape frequency and unique token count
  - Data available for subsequent keyword matching and auditing
  
  **Use Case 2: Social Media Keyword Extraction & Contract Address Detection**
  - Use multiple Extractors (BERT, TF-IDF, spaCy NER, rule-based, regex) to batch process tweets from influential accounts
  - Extract crypto-related keywords and potential contract addresses from tweets
  - **Redis Token Matcher**: Load monitored tokens from Redis cache, match in tweets in real-time
    - Supports `$SYMBOL` format (e.g., `$BTC`, `$KITKAT`)
    - Supports plain text matching (e.g., `BITCOIN`)
    - Supports Chinese token name matching
    - Calculates confidence based on context, reducing false positives
  - Run `realtime_ca_detector.py` to listen to tweet streams in real-time, automatically detect and verify contract addresses
  - Results pushed via WebSocket server
  
  **Use Case 3: Real-time Push & Telegram Alerts**
  - Start `ws_server.py` to monitor `ws.json` file changes, pushing to all connected clients
  - Frontend or mobile apps receive real-time trading opportunity notifications via WebSocket
  - Optional: Start `telegram/webhook_forwarder.py` to forward detection results to Telegram groups/channels
  - Traders can quickly make decisions and execute trades after receiving notifications

## 6. Verifiable Scope

- This repository contains core code and scripts for reproduction:
  - Token Monitoring: `monitor/token_monitor.py` scrapes data from DexScreener and persists to Redis + CSV
  - Redis Caching Layer:
    - `monitor/redis_api.py`: RESTful API service providing token query, search, and statistics endpoints
    - `extractor/redis_token_matcher.py`: Load token list from Redis, intelligently match in tweets
    - `monitor/migrate_csv_to_redis.py`: CSV ↔ Redis data migration tool
    - `monitor/query_redis_tokens.py`: Command-line tool to query Redis token data
  - Multi-strategy Extractors: 6 different keyword and entity extraction methods (BERT, TF-IDF, spaCy NER, rule-based, regex, RAKE)
  - Real-time Contract Address Detection: `realtime_ca_detector.py` automatically detects and verifies contract addresses
  - WebSocket Server: `ws_server.py` file monitoring and real-time push
  - Telegram Forwarding: Complete Telegram Bot integration and WebSocket forwarder
  - Audit Module: Token auditing and real-time auditor
  - Data Examples: Contains real tweet data from 3 influential accounts
  - Log Management: Automatic log rotation and cleanup scripts
- **User Must Provide**:
  - Redis 6.0+ service (required)
  - Telegram Bot Token and Chat ID (if using Telegram push functionality)
  - Twitter API access (if real-time Twitter listening is needed; currently uses example data)
- **Included**:
  - Complete implementation of all core features
  - Example data and configuration files
  - Service installation and management scripts

## 7. Roadmap & Impact

- **Completed**:
  - DexScreener real-time token monitoring and data persistence
  - 6 keyword extraction strategies (BERT, TF-IDF, spaCy, rule-based, regex, RAKE)
  - Real-time contract address detection and verification system
  - WebSocket real-time push architecture
  - Telegram Bot integration and alert forwarding
  - System log management and rotation
  - Service deployment (systemd integration)

- **1-3 Weeks**:
  - Optimize keyword detection algorithms, improve accuracy and recall
  - Redis performance optimization:
    - Implement Redis cluster support (high availability)
    - Add cache warming mechanism
    - Optimize query performance (index optimization, Pipeline batch processing)
  - Add more influential account monitoring (support custom account lists)
  - Enhanced contract address verification:
    - Liquidity depth checking
    - Holder distribution analysis
    - Honeypot detection
    - Code audit integration
  - Improved alert strategies: support custom rules and thresholds
  - Discord integration support

- **1-3 Months**:
  - Complete on-chain security scoring system:
    - Contract source code verification
    - Transaction history analysis
    - Whale address monitoring
  - Frontend dashboard optimization:
    - Real-time data visualization
    - Historical trend charts
    - Custom monitoring panels
  - One-click trading integration:
    - DEX aggregator integration (1inch, Uniswap, PancakeSwap)
    - Intelligent slippage control
    - Gas price optimization
  - AI enhancement features:
    - Vector database for storing historical patterns
    - LLM-based tweet sentiment analysis
    - Intelligent trading timing recommendations

- **Value to Crypto Ecosystem**:
  - **Information Transparency**: Reduces information asymmetry for ordinary traders, providing institutional-level real-time monitoring and analysis capabilities
  - **Enhanced Security**: Multi-layer verification reduces capital losses from rug pulls, scam projects, and honeypot contracts
  - **Open-source Infrastructure**: Provides reusable components for social intelligence collection, NLP analysis, real-time distribution, and risk control
  - **Speed Advantage**: Millisecond-level response helps traders enter early during the price discovery phase

## 8. Team & Contacts

- **Team Name**: foxhole ai
- **Members & Roles**: Alan handles Twitter monitoring frontend and trading, Neo handles AI keyword extraction
- **Contact (Email/TG/X)**: alan_ywang
- **Demo Availability (Timezone)**: Beijing Time
