import json
import requests
import os
import time
from decimal import Decimal, ROUND_HALF_UP

# OpenExchangeRates API配置
# 优先使用环境变量，然后使用默认key
API_KEY = os.getenv('OPENEXCHANGERATES_API_KEY') or os.getenv('API_KEY') or 'daaf8da9e5fd46bd95bb8f20f4cf1309'
API_URL = f"https://openexchangerates.org/api/latest.json?app_id={API_KEY}"

INPUT_FILE = 'global_fuel_prices.json'
OUTPUT_FILE = 'global_fuel_prices_processed.json'


def get_exchange_rates():
    """获取最新汇率"""
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['rates']
        else:
            print(f"获取汇率失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"获取汇率失败: {e}")
        return None


def convert_to_cny(price: float, currency: str, rates: dict) -> float:
    """将价格转换为CNY"""
    if currency == 'CNY':
        return price

    try:
        # OpenExchangeRates使用USD作为基准货币
        # 转换公式: price_cny = price_currency * (CNY_rate / currency_rate)
        if currency not in rates:
            print(f"警告: 货币 {currency} 不在汇率表中")
            return 0.0

        cny_rate = rates.get('CNY', 7.2)  # CNY对USD的汇率
        currency_rate = rates.get(currency, 1.0)

        # 转换为CNY
        price_in_usd = price / currency_rate
        price_in_cny = price_in_usd * cny_rate

        # 保留2位小数
        return float(Decimal(str(price_in_cny)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    except Exception as e:
        print(f"转换价格失败 ({currency}): {e}")
        return 0.0


def process_fuel_prices():
    """处理燃油价格数据"""
    print("开始处理全球燃油价格...")

    # 加载原始数据
    if not os.path.exists(INPUT_FILE):
        print(f"错误: 找不到文件 {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        fuel_data = json.load(f)

    print(f"加载了 {len(fuel_data)} 个国家的数据")

    # 获取汇率
    print("获取最新汇率...")
    rates = get_exchange_rates()
    if not rates:
        print("无法获取汇率，退出")
        return

    print(f"成功获取 {len(rates)} 种货币的汇率")

    # 处理每个国家的数据
    processed_data = {}
    for country_code, data in fuel_data.items():
        try:
            # 处理汽油价格
            gasoline_data = data.get('gasoline')
            diesel_data = data.get('diesel')
            lpg_data = data.get('lpg')

            processed_country = {
                'country': data.get('country'),
                'country_code': data.get('country_code'),
                'source_url_gasoline': data.get('source_url_gasoline'),
                'source_url_diesel': data.get('source_url_diesel'),
                'source_url_lpg': data.get('source_url_lpg')
            }

            # 转换汽油价格
            if gasoline_data:
                price = gasoline_data.get('price', 0)
                currency = gasoline_data.get('currency', 'USD')
                price_cny = convert_to_cny(price, currency, rates)

                processed_country['gasoline'] = {
                    **gasoline_data,
                    'price_cny': price_cny,
                    'price_cny_formatted': f'{price_cny:.2f} CNY/L'
                }

            # 转换柴油价格
            if diesel_data:
                price = diesel_data.get('price', 0)
                currency = diesel_data.get('currency', 'USD')
                price_cny = convert_to_cny(price, currency, rates)

                processed_country['diesel'] = {
                    **diesel_data,
                    'price_cny': price_cny,
                    'price_cny_formatted': f'{price_cny:.2f} CNY/L'
                }

            # 转换LPG价格
            if lpg_data:
                price = lpg_data.get('price', 0)
                currency = lpg_data.get('currency', 'USD')
                price_cny = convert_to_cny(price, currency, rates)

                processed_country['lpg'] = {
                    **lpg_data,
                    'price_cny': price_cny,
                    'price_cny_formatted': f'{price_cny:.2f} CNY/L'
                }

            processed_data[country_code] = processed_country

        except Exception as e:
            print(f"处理 {country_code} 失败: {e}")
            processed_data[country_code] = data

    # 保存处理后的数据
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    # 保存归档版本
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    year = time.strftime("%Y")
    month = time.strftime("%m")
    archive_dir = f'archive/{year}/{month}'
    os.makedirs(archive_dir, exist_ok=True)
    archive_file = f'{archive_dir}/global_fuel_prices_processed_{timestamp}.json'

    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    print(f"\n已写入 {OUTPUT_FILE} 和 {archive_file}")
    print(f"成功处理 {len(processed_data)} 个国家的数据")

    # 生成排行榜
    generate_rankings(processed_data)


def generate_rankings(data: dict):
    """生成价格排行榜（汽油、柴油和LPG）"""
    print("\n=== 全球燃油价格排行榜 (CNY/升) ===\n")

    # 汽油排行榜
    gasoline_data = [(code, info) for code, info in data.items()
                     if info.get('gasoline') and info['gasoline'].get('price_cny', 0) > 0]

    if gasoline_data:
        print("🚗 汽油价格排行榜:")
        cheapest_gasoline = sorted(gasoline_data, key=lambda x: x[1]['gasoline']['price_cny'])[:10]
        print("\n最便宜的10个国家:")
        for i, (code, info) in enumerate(cheapest_gasoline, 1):
            gasoline = info['gasoline']
            print(f"{i:2d}. {info['country']:25s} {gasoline['price_cny']:6.2f} CNY/L ({gasoline['price']:.2f} {gasoline['currency']}/L)")

        most_expensive_gasoline = sorted(gasoline_data, key=lambda x: x[1]['gasoline']['price_cny'], reverse=True)[:10]
        print("\n最贵的10个国家:")
        for i, (code, info) in enumerate(most_expensive_gasoline, 1):
            gasoline = info['gasoline']
            print(f"{i:2d}. {info['country']:25s} {gasoline['price_cny']:6.2f} CNY/L ({gasoline['price']:.2f} {gasoline['currency']}/L)")

        prices = [info['gasoline']['price_cny'] for _, info in gasoline_data]
        avg_price = sum(prices) / len(prices)
        print(f"\n全球汽油平均价格: {avg_price:.2f} CNY/L")
        print(f"价格范围: {min(prices):.2f} - {max(prices):.2f} CNY/L")

    # 柴油排行榜
    diesel_data = [(code, info) for code, info in data.items()
                   if info.get('diesel') and info['diesel'].get('price_cny', 0) > 0]

    if diesel_data:
        print("\n\n🚛 柴油价格排行榜:")
        cheapest_diesel = sorted(diesel_data, key=lambda x: x[1]['diesel']['price_cny'])[:10]
        print("\n最便宜的10个国家:")
        for i, (code, info) in enumerate(cheapest_diesel, 1):
            diesel = info['diesel']
            print(f"{i:2d}. {info['country']:25s} {diesel['price_cny']:6.2f} CNY/L ({diesel['price']:.2f} {diesel['currency']}/L)")

        most_expensive_diesel = sorted(diesel_data, key=lambda x: x[1]['diesel']['price_cny'], reverse=True)[:10]
        print("\n最贵的10个国家:")
        for i, (code, info) in enumerate(most_expensive_diesel, 1):
            diesel = info['diesel']
            print(f"{i:2d}. {info['country']:25s} {diesel['price_cny']:6.2f} CNY/L ({diesel['price']:.2f} {diesel['currency']}/L)")

        prices = [info['diesel']['price_cny'] for _, info in diesel_data]
        avg_price = sum(prices) / len(prices)
        print(f"\n全球柴油平均价格: {avg_price:.2f} CNY/L")
        print(f"价格范围: {min(prices):.2f} - {max(prices):.2f} CNY/L")

    # LPG排行榜
    lpg_data = [(code, info) for code, info in data.items()
                if info.get('lpg') and info['lpg'].get('price_cny', 0) > 0]

    if lpg_data:
        print("\n\n⛽ LPG价格排行榜:")
        cheapest_lpg = sorted(lpg_data, key=lambda x: x[1]['lpg']['price_cny'])[:10]
        print("\n最便宜的10个国家:")
        for i, (code, info) in enumerate(cheapest_lpg, 1):
            lpg = info['lpg']
            print(f"{i:2d}. {info['country']:25s} {lpg['price_cny']:6.2f} CNY/L ({lpg['price']:.2f} {lpg['currency']}/L)")

        most_expensive_lpg = sorted(lpg_data, key=lambda x: x[1]['lpg']['price_cny'], reverse=True)[:10]
        print("\n最贵的10个国家:")
        for i, (code, info) in enumerate(most_expensive_lpg, 1):
            lpg = info['lpg']
            print(f"{i:2d}. {info['country']:25s} {lpg['price_cny']:6.2f} CNY/L ({lpg['price']:.2f} {lpg['currency']}/L)")

        prices = [info['lpg']['price_cny'] for _, info in lpg_data]
        avg_price = sum(prices) / len(prices)
        print(f"\n全球LPG平均价格: {avg_price:.2f} CNY/L")
        print(f"价格范围: {min(prices):.2f} - {max(prices):.2f} CNY/L")


if __name__ == '__main__':
    process_fuel_prices()
