# Fuel Price Tracker

[中文](#中文说明) | [English](#english)

A comprehensive tool for tracking fuel prices from China provinces and 150+ countries worldwide.

## 🌟 Features

- **China Coverage**: Scrapes fuel prices from all 31 provinces/municipalities
  - 92# Gasoline, 95# Gasoline, 98# Gasoline, 0# Diesel
- **Global Coverage**: Scrapes fuel prices from 190+ countries worldwide
- **Price Change Detection**: Tracks price changes over time
- **Automated Archiving**: Organizes historical data by year/month
- **GitHub Actions**: Automated daily data collection

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenExchangeRates API key (free tier available at https://openexchangerates.org/)

### Installation

```bash
git clone https://github.com/yourusername/fuel-price-tracker.git
cd fuel-price-tracker
pip install -r requirements.txt
```

### Configuration

Set your OpenExchangeRates API key:
```bash
# Option 1: Environment variable
export API_KEY="your_api_key_here"

# Option 2: GitHub Secrets (for Actions)
# Add OPENEXCHANGERATES_API_KEY to your repository secrets
```

### Usage

#### Scrape China Fuel Prices
```bash
python china_fuel_scraper.py
```
Generates: `china_fuel_prices.json`

#### Scrape Global Fuel Prices
```bash
python global_fuel_scraper.py
```
Generates: `global_fuel_prices.json`

#### Convert to CNY
```bash
python fuel_rate_converter.py
```
Generates: `global_fuel_prices_processed.json` with CNY prices and rankings

#### Detect Price Changes
```bash
python fuel_price_change_detector.py
```
Generates: `CHANGELOG.md`

## 📁 File Structure

```
├── china_fuel_prices.json          # Latest China prices
├── global_fuel_prices.json         # Latest global prices (original currency)
├── global_fuel_prices_processed.json # Global prices converted to CNY
├── CHANGELOG.md                    # Price change history
├── archive/                        # Historical data
├── china_fuel_scraper.py           # China scraper
├── global_fuel_scraper.py          # Global scraper
├── fuel_rate_converter.py          # Currency converter
└── fuel_price_change_detector.py   # Change detector
```

## 📊 Data Sources

- **China**: [qiyoujiage.com](http://m.qiyoujiage.com/)
- **Global**: [GlobalPetrolPrices.com](https://www.globalpetrolprices.com/)

---

## 中文说明

全球燃油价格追踪工具，覆盖中国34个省市和全球150+国家。

### 功能特点

- **中国覆盖**：抓取全国31个省市油价（不含港澳台）
  - 92号汽油、95号汽油、98号汽油、0号柴油
- **全球覆盖**：抓取190+国家油价
- **价格变动追踪**：自动检测价格变化
- **自动归档**：按年月组织历史数据
- **自动化**：GitHub Actions每日自动抓取

### 数据来源

- **中国**：汽油价格网 (qiyoujiage.com)
- **全球**：GlobalPetrolPrices.com

## 📄 License

MIT License
