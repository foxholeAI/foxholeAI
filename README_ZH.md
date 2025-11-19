# Foxhole AI

Foxhole AI 是一个端到端的开源原型，面向交易者与研究员，实时监控影响力社交账号，提供关键词检测、合约地址验证与基础风险审计，并实时推送结果，帮助用户更快识别潜在交易机会与风险。

## 1. Deliverables

- [x] GitHub 仓库：包含完整代码与本 README
- [x] Video：[Youtube](https://www.youtube.com/watch?v=nn3zgyBGgdQ)
- [x] Pitch Deck：[Google Drive](https://docs.google.com/presentation/d/1BfsnzbwMK1iYdB9Vr3OD1x7NMVJrydJ9/edit?usp=sharing&ouid=114972223476033742889&rtpof=true&sd=true)

## 2. Overview

- **项目名称**：Foxhole AI
- **一句话介绍**：实时监控影响力 Twitter 账号（CZ、Heyi、Elon Musk 等）的加密关键词，即时推送经过 AI 验证的合约地址，让交易者无需手动搜索，实现一键代币购买。
- **目标用户**：加密货币交易者（量化/手动）、链上狙击手、加密研究员、信息流机器人开发者。
- **核心问题与动机（Pain Points）**：
  - **通知延迟问题**：交易者错过关键意见领袖（KOL）的重要关键词提及，失去早期入场机会。
  - **手动猎寻合约地址**：耗时的合约地址查找过程导致错失交易，甚至遭遇诈骗项目与 Rug Pull。
  - **信息过载**：人工同时监控多个高影响力社交账号在规模化运作中根本不可能。
  - **速度劣势**：手动流程无法与毫秒级执行交易的自动化系统竞争。在加密货币世界，几秒钟就可能意味着盈利与亏损的差别。
- **解决方案（Solution）**：

  - **实时情报引擎**：先进的关键词检测算法 7×24 小时监控高影响力账号（CZ、Heyi、Elon Musk 等），零延迟响应。
  - Monitor 子系统持续抓取 Dex Screener token 数据（高频、去重、CSV 持久化）。

  - Extractor 子系统（BERT/TF-IDF/规则/正则/NER）对文本做关键词与实体抽取。

  - **验证合约地址**：AI 驱动的验证机制确保用户获得合法 CA，防范 Rug Pull 与诈骗项目。
  - **即时通知推送**：关键词检测的瞬间，交易机会直接通过 WebSocket 推送到用户设备。
  - **自动化优势**：采用与专业狙击机器人相同的高频交易技术，毫秒级响应。
  - **风险缓释**：内置安全功能在推荐前分析代币合法性与市场状况。

## 3. Architecture & Implementation

- **总览图**

![](https://cdn.jsdelivr.net/gh/timerring/scratchpad2023/2024/2025-10-31-20-36-03.png)

- **关键模块**：
  - 前端（Frontend）：https://github.com/yidongw/foxhole-bot-frontend
  - 监控（Monitor）：`monitor/token_monitor.py`、`monitor/config.py`、`monitor/start.sh`、`monitor/redis_api.py`
  - 社媒监听：`monitor/twitter_listener.py`
  - 抽取（Extractor）：`extractor/bert_extractor.py`、`extractor/spacy_ner_extractor.py`、`extractor/tfidf_extractor.py`、`extractor/rule_based_extractor.py`、`extractor/regex_extractor.py`、`extractor/realtime_bert_analyzer.py`、`extractor/redis_token_matcher.py`
  - 审计（Audit）：`audit/realtime_auditor.py`、`audit/audit_tokens.py`
  - 实时分发：`ws_server.py`、`realtime_ca_detector.py`
  - Telegram 推送：`telegram/webhook_forwarder.py`、`telegram/telegram_bot.py`、`telegram/start.sh`
  - 日志管理：`scripts/log_rotation.py`、`scripts/setup_log_rotation.sh`、`scripts/cleanup_old_logs.sh`
  - Redis 层：`monitor/redis_api.py`、`monitor/migrate_csv_to_redis.py`、`monitor/query_redis_tokens.py`、`monitor/add_token_manual.py`
  - 主启动脚本：`start.sh`
- **依赖与技术栈**：
  - 语言与运行时：Python 3.10+（建议使用虚拟环境）
  - 核心依赖：见 `requirements.txt`（包含 `requests`、`aiohttp`、`websockets`、`python-dotenv` 等）
  - 监控依赖：见 `monitor/requirements.txt`（`aiohttp`、`asyncio`、`redis`、`flask`）
  - 抽取依赖：见 `extractor/requirements_extractor.txt`（`transformers`、`torch`、`spacy` 等）
  - Telegram 依赖：见 `telegram/requirements.txt`（`requests`、`websockets`、`python-dotenv`）
  - 异步与网络：`asyncio`、`aiohttp`、`websockets`
  - NLP：`transformers`/`torch`（BERT）、`spaCy`（NER）
  - 数据存储：SQLite（本地数据库）、CSV（数据持久化）、Redis（高性能缓存层）

## 4. Run & Reproduce

- **前置要求**：

  - Python 3.10+ 与 `pip`
  - Redis 6.0+（必需，用于高性能缓存层）
  - 稳定的网络连接
  - （可选）Telegram Bot Token（如需 Telegram 推送）

- **环境变量配置**：

```bash
# telegram/.env（示例，用于 Telegram 推送模块）
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
WS_URL=ws://localhost:8765
```

- **安装依赖（分模块）**：

```bash
# 进入项目根目录
cd /root/nlpmeme

# 方式1：安装核心依赖（推荐先安装）
pip install -r requirements.txt

# 方式2：分模块安装
# Monitor 监控模块依赖
pip install -r monitor/requirements.txt

# Extractor 抽取模块依赖（按需，包含 BERT、spaCy 等）
pip install -r extractor/requirements_extractor.txt
# 如需使用 spaCy，还需下载模型：
# python -m spacy download en_core_web_sm

# Telegram 推送模块依赖（按需）
pip install -r telegram/requirements.txt
```

- **快速体验（仅运行代币监控）**：

```bash
# 确保 Redis 已启动
redis-cli ping

cd monitor

# 方式1: 使用启动脚本
bash start.sh

# 方式2: 直接运行
python token_monitor.py
# 运行中会实时写入 Redis 和 CSV，并打印实时统计
```

- **一键启动所有服务（推荐）**：

```bash
# 在项目根目录
bash start.sh start

# 查看服务状态
bash start.sh status

# 查看日志
bash start.sh logs all

# 停止所有服务
bash start.sh stop
```

- **分模块启动**：

```bash
# 1. 启动 WebSocket 服务器（核心服务）
python ws_server.py --host 0.0.0.0 --port 8765 --watch-file data/ws.json

# 2. 启动实时合约地址检测器
python realtime_ca_detector.py --no-bert --no-ai --min-confidence 0.5

# 3. 启动 Telegram 转发器（可选）
cd telegram
bash start.sh
# 或直接运行
python webhook_forwarder.py
```

- **数据与样例**：

  - 数据目录：`data/`
    - 示例推文：`user_tweets_44196397.json`（Elon Musk）、`user_tweets_902926941413453824.json`（CZ）、`user_tweets_1003840309166366721.json`（Heyi）
    - 数据库：`meme_coins.db`（SQLite 数据库）
    - WebSocket 数据：`ws.json`（实时推送的合约地址数据）
  - 监控数据：`monitor/tokens_data.csv`（代币监控历史数据）
  - 抽取结果：`extractor/output/`（各种抽取器的输出结果）
  - 日志文件：`monitor/monitor.log`、`telegram/logs/`、`ws_server.txt`、`realtime_ca_detector.txt`

- **服务管理**：

```bash
# 使用 systemd 安装 Monitor 服务（可选）
cd monitor
sudo bash install_service.sh

# 使用 systemd 安装 Telegram 服务（可选）
cd telegram
sudo bash install_service.sh

# 日志轮转设置（可选）
cd scripts
bash setup_log_rotation.sh
```

## 5. Key Flows

- **关键用例步骤**：
  
  **用例 1：实时代币监控与数据采集**
  - 启动 `token_monitor.py`，持续从 DexScreener 抓取热门代币数据
  - 自动去重并存储到 `tokens_data.csv`，统计抓取频率和唯一代币数
  - 数据可供后续关键词匹配和审计使用
  
  **用例 2：社交媒体关键词抽取与合约地址检测**
  - 使用多种 Extractor（BERT、TF-IDF、spaCy NER、规则、正则）批量处理影响力账号推文
  - 从推文中提取加密相关关键词和潜在合约地址
  - **Redis Token Matcher**：从 Redis 缓存加载已监控代币，在推文中实时匹配
    - 支持 `$SYMBOL` 格式（如 `$BTC`、`$KITKAT`）
    - 支持纯文本匹配（如 `BITCOIN`）
    - 支持中文代币名称匹配
    - 根据上下文计算置信度，减少误报
  - 运行 `realtime_ca_detector.py` 实时监听推文流，自动检测和验证合约地址
  - 结果使用 WebSocket 服务器推送
  
  **用例 3：实时推送与 Telegram 告警**
  - 启动 `ws_server.py` 监听 `ws.json` 文件变化，向所有连接的客户端推送
  - 前端或移动端通过 WebSocket 接收实时交易机会通知
  - 可选：启动 `telegram/webhook_forwarder.py` 将检测结果转发到 Telegram 群组/频道
  - 交易者收到通知后可快速决策并执行交易

## 6. Verifiable Scope

- 本仓库包含用于复现的核心代码与脚本：
  - 代币监控：`monitor/token_monitor.py` 从 DexScreener 抓取数据并持久化到 Redis + CSV
  - Redis 缓存层：
    - `monitor/redis_api.py`：RESTful API 服务，提供代币查询、搜索、统计接口
    - `extractor/redis_token_matcher.py`：从 Redis 加载代币列表，在推文中智能匹配
    - `monitor/migrate_csv_to_redis.py`：CSV ↔ Redis 数据迁移工具
    - `monitor/query_redis_tokens.py`：命令行查询 Redis 代币数据
  - 多策略抽取器：6 种不同的关键词和实体抽取方法（BERT、TF-IDF、spaCy NER、规则、正则、RAKE）
  - 实时合约地址检测：`realtime_ca_detector.py` 自动检测和验证合约地址
  - WebSocket 服务器：`ws_server.py` 文件监听与实时推送
  - Telegram 转发：完整的 Telegram Bot 集成和 WebSocket 转发器
  - 审计模块：代币审计和实时审计器
  - 数据样例：包含 3 个影响力账号的真实推文数据
  - 日志管理：自动日志轮转和清理脚本
- **需自备配置**：
  - Redis 6.0+ 服务（必需）
  - Telegram Bot Token 和 Chat ID（如使用 Telegram 推送功能）
  - Twitter API 访问（如需实时监听 Twitter，当前使用示例数据）
- **已包含**：
  - 所有核心功能的完整实现
  - 示例数据和配置文件
  - 服务安装和管理脚本

## 7. Roadmap & Impact

- **已完成**：
  - DexScreener 实时代币监控与数据持久化
  - 6 种关键词抽取策略（BERT、TF-IDF、spaCy、规则、正则、RAKE）
  - 实时合约地址检测与验证系统
  - WebSocket 实时推送架构
  - Telegram Bot 集成与告警转发
  - 系统日志管理与轮转
  - 服务化部署（systemd 集成）

- **1-3 周**：
  - 优化关键词检测算法，提高准确率和召回率
  - Redis 性能优化：
    - 实现 Redis 集群支持（高可用）
    - 添加缓存预热机制
    - 优化查询性能（索引优化、Pipeline 批处理）
  - 增加更多影响力账号监控（支持自定义账号列表）
  - 增强合约地址验证机制：
    - 流动性深度检查
    - 持有者分布分析
    - 蜜罐检测（Honeypot Detection）
    - 代码审计集成
  - 完善告警策略：支持自定义规则和阈值
  - Discord 集成支持

- **1-3 个月**：
  - 完整的链上安全评分系统：
    - 合约源码验证
    - 交易历史分析
    - 巨鲸地址监控
  - 前端仪表盘优化：
    - 实时数据可视化
    - 历史趋势图表
    - 自定义监控面板
  - 一键交易集成：
    - DEX 聚合器对接（1inch、Uniswap、PancakeSwap）
    - 智能滑点控制
    - Gas 价格优化
  - AI 增强功能：
    - 向量数据库存储历史模式
    - 基于 LLM 的推文情感分析
    - 智能交易时机推荐

- **对加密生态的价值**：
  - **信息透明化**：降低普通交易者的信息不对称，提供机构级的实时监控与分析能力
  - **安全性提升**：通过多层验证减少 Rug Pull、诈骗项目和蜜罐合约造成的资金损失
  - **开源基础设施**：为社区提供可复用的社交情报采集、NLP 分析、实时分发与风控组件
  - **速度优势**：毫秒级响应，帮助交易者在价格发现阶段早期入场

## 8. Team & Contacts

- **团队名**：foxhole ai
- **成员与分工**：Alan 负责推特监控前端跟交易，Neo 负责 ai 关键词提取
- **联系方式（Email/TG/X）**：alan_ywang
- **可演示时段（时区）**：北京时间
