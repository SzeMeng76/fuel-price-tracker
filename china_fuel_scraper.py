import re
import json
import time
import os
from typing import Any
from bs4 import BeautifulSoup
import requests


# 中国31个省市区代码（不包括香港、澳门、台湾，数据源不提供）
CHINA_PROVINCES = {
    'beijing': '北京',
    'shanghai': '上海',
    'tianjin': '天津',
    'chongqing': '重庆',
    'hebei': '河北',
    'shanxi': '山西',
    'neimenggu': '内蒙古',
    'liaoning': '辽宁',
    'jilin': '吉林',
    'heilongjiang': '黑龙江',
    'jiangsu': '江苏',
    'zhejiang': '浙江',
    'anhui': '安徽',
    'fujian': '福建',
    'jiangxi': '江西',
    'shandong': '山东',
    'henan': '河南',
    'hubei': '湖北',
    'hunan': '湖南',
    'guangdong': '广东',
    'guangxi': '广西',
    'hainan': '海南',
    'sichuan': '四川',
    'guizhou': '贵州',
    'yunnan': '云南',
    'xizang': '西藏',
    'shanxi-3': '陕西',  # 注意：陕西的URL是 shanxi-3.shtml
    'gansu': '甘肃',
    'qinghai': '青海',
    'ningxia': '宁夏',
    'xinjiang': '新疆'
}


def fetch_province_prices(province_code: str, province_name: str) -> dict[str, Any]:
    """获取单个省份的油价"""
    url = f'http://m.qiyoujiage.com/{province_code}.shtml'
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"[{province_name}] HTTP {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取价格数据 - 不使用class，直接查找所有dd和dt标签
        prices = soup.find_all('dd')
        labels = soup.find_all('dt')

        if len(prices) < 4 or len(labels) < 4:
            print(f"[{province_name}] 未找到完整价格数据 (prices: {len(prices)}, labels: {len(labels)})")
            return None

        # 提取调价信息
        adjustment_info = extract_adjustment_info(soup)

        result = {
            'province': province_name,
            'province_code': province_code,
            '92_gasoline': clean_price(prices[0].text.strip()),
            '95_gasoline': clean_price(prices[1].text.strip()),
            '98_gasoline': clean_price(prices[2].text.strip()),
            '0_diesel': clean_price(prices[3].text.strip()),
            'currency': 'CNY',
            'unit': 'yuan/liter',
            'update_date': time.strftime('%Y-%m-%d'),
            'source_url': url
        }

        if adjustment_info:
            result['adjustment'] = adjustment_info

        print(f"[{province_name}] 成功获取价格")
        return result

    except Exception as e:
        print(f"[{province_name}] 获取失败: {e}")
        return None


def clean_price(price_str: str) -> float:
    """清理价格字符串，转换为浮点数"""
    # 移除非数字字符（保留小数点）
    price_clean = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(price_clean)
    except ValueError:
        return 0.0


def extract_adjustment_info(soup: BeautifulSoup) -> dict[str, str]:
    """提取油价调整信息"""
    try:
        # 查找包含调价信息的元素
        adjustment_text = soup.get_text()

        # 匹配调价信息
        # 例如: "下次油价4月7日24时调整 目前预计下调油价120元/吨"
        date_pattern = re.search(r'下次油价(\d+月\d+日)', adjustment_text)
        trend_pattern = re.search(r'(上调|下调)油价(\d+)元/吨', adjustment_text)
        amount_pattern = re.search(r'(上涨|下跌)\s*([\d.]+)-([\d.]+)元', adjustment_text)

        result = {}
        if date_pattern:
            result['next_adjustment_date'] = date_pattern.group(1)
        if trend_pattern:
            result['expected_trend'] = trend_pattern.group(1)
            result['expected_amount_ton'] = f"{trend_pattern.group(2)} yuan/ton"
        if amount_pattern:
            result['expected_amount_liter'] = f"{amount_pattern.group(2)}-{amount_pattern.group(3)} yuan/liter"

        return result if result else None

    except Exception:
        return None


def main():
    """主函数"""
    print("开始抓取中国各省油价...")
    print(f"总共 {len(CHINA_PROVINCES)} 个省市区")

    results = {}
    success_count = 0

    for province_code, province_name in CHINA_PROVINCES.items():
        price_data = fetch_province_prices(province_code, province_name)
        if price_data:
            results[province_code] = price_data
            success_count += 1

        # 避免请求过快
        time.sleep(0.5)

    # 保存结果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    year = time.strftime("%Y")
    month = time.strftime("%m")

    output_file_latest = 'china_fuel_prices.json'

    # 创建归档目录
    archive_dir = f'archive/{year}/{month}'
    os.makedirs(archive_dir, exist_ok=True)
    output_file_timestamped = f'{archive_dir}/china_fuel_prices_{timestamp}.json'

    # 保存最新版本
    with open(output_file_latest, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 保存带时间戳的版本
    with open(output_file_timestamped, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n已写入 {output_file_latest} 和 {output_file_timestamped}")
    print(f"成功获取 {success_count}/{len(CHINA_PROVINCES)} 个省市区的油价")

    # 生成简单统计
    if results:
        prices_92 = [v['92_gasoline'] for v in results.values() if v['92_gasoline'] > 0]
        if prices_92:
            print(f"\n92号汽油价格统计:")
            print(f"  最高: {max(prices_92):.2f} 元/升")
            print(f"  最低: {min(prices_92):.2f} 元/升")
            print(f"  平均: {sum(prices_92)/len(prices_92):.2f} 元/升")


if __name__ == '__main__':
    main()
