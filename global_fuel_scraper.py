import re
import json
import time
import os
from typing import Any
from bs4 import BeautifulSoup
import requests


# 全球国家列表 - 基于 globalpetrolprices.com
GLOBAL_COUNTRIES = {
    # 北美洲
    'USA': 'United States',
    'Canada': 'Canada',
    'Mexico': 'Mexico',

    # 中美洲和加勒比
    'Guatemala': 'Guatemala',
    'Honduras': 'Honduras',
    'El-Salvador': 'El Salvador',
    'Nicaragua': 'Nicaragua',
    'Costa-Rica': 'Costa Rica',
    'Panama': 'Panama',
    'Cuba': 'Cuba',
    'Jamaica': 'Jamaica',
    'Dominican-Republic': 'Dominican Republic',
    'Trinidad-and-Tobago': 'Trinidad and Tobago',

    # 南美洲
    'Brazil': 'Brazil',
    'Argentina': 'Argentina',
    'Chile': 'Chile',
    'Colombia': 'Colombia',
    'Peru': 'Peru',
    'Venezuela': 'Venezuela',
    'Ecuador': 'Ecuador',
    'Bolivia': 'Bolivia',
    'Paraguay': 'Paraguay',
    'Uruguay': 'Uruguay',

    # 西欧
    'United-Kingdom': 'United Kingdom',
    'Ireland': 'Ireland',
    'France': 'France',
    'Germany': 'Germany',
    'Italy': 'Italy',
    'Spain': 'Spain',
    'Portugal': 'Portugal',
    'Netherlands': 'Netherlands',
    'Belgium': 'Belgium',
    'Luxembourg': 'Luxembourg',
    'Austria': 'Austria',
    'Switzerland': 'Switzerland',

    # 北欧
    'Sweden': 'Sweden',
    'Norway': 'Norway',
    'Denmark': 'Denmark',
    'Finland': 'Finland',
    'Iceland': 'Iceland',

    # 东欧
    'Poland': 'Poland',
    'Czech-Republic': 'Czech Republic',
    'Slovakia': 'Slovakia',
    'Hungary': 'Hungary',
    'Romania': 'Romania',
    'Bulgaria': 'Bulgaria',
    'Croatia': 'Croatia',
    'Slovenia': 'Slovenia',
    'Serbia': 'Serbia',
    'Bosnia-and-Herzegovina': 'Bosnia and Herzegovina',
    'Albania': 'Albania',
    'North-Macedonia': 'North Macedonia',
    'Estonia': 'Estonia',
    'Latvia': 'Latvia',
    'Lithuania': 'Lithuania',

    # 俄罗斯和前苏联
    'Russia': 'Russia',
    'Ukraine': 'Ukraine',
    'Belarus': 'Belarus',
    'Moldova': 'Moldova',
    'Georgia': 'Georgia',
    'Armenia': 'Armenia',
    'Azerbaijan': 'Azerbaijan',
    'Kazakhstan': 'Kazakhstan',
    'Uzbekistan': 'Uzbekistan',

    # 东亚
    'China': 'China',
    'Japan': 'Japan',
    'South-Korea': 'South Korea',
    'North-Korea': 'North Korea',
    'Mongolia': 'Mongolia',
    'Hong-Kong': 'Hong Kong',
    'Taiwan': 'Taiwan',
    'Macau': 'Macau',

    # 东南亚
    'Singapore': 'Singapore',
    'Malaysia': 'Malaysia',
    'Thailand': 'Thailand',
    'Vietnam': 'Vietnam',
    'Philippines': 'Philippines',
    'Indonesia': 'Indonesia',
    'Myanmar': 'Myanmar',
    'Cambodia': 'Cambodia',
    'Laos': 'Laos',
    'Brunei': 'Brunei',

    # 南亚
    'India': 'India',
    'Pakistan': 'Pakistan',
    'Bangladesh': 'Bangladesh',
    'Sri-Lanka': 'Sri Lanka',
    'Nepal': 'Nepal',
    'Bhutan': 'Bhutan',
    'Maldives': 'Maldives',

    # 中东
    'Turkey': 'Turkey',
    'Saudi-Arabia': 'Saudi Arabia',
    'United-Arab-Emirates': 'United Arab Emirates',
    'Qatar': 'Qatar',
    'Kuwait': 'Kuwait',
    'Bahrain': 'Bahrain',
    'Oman': 'Oman',
    'Yemen': 'Yemen',
    'Iraq': 'Iraq',
    'Iran': 'Iran',
    'Jordan': 'Jordan',
    'Lebanon': 'Lebanon',
    'Syria': 'Syria',
    'Israel': 'Israel',
    'Palestine': 'Palestine',
    'Cyprus': 'Cyprus',

    # 非洲北部
    'Egypt': 'Egypt',
    'Libya': 'Libya',
    'Tunisia': 'Tunisia',
    'Algeria': 'Algeria',
    'Morocco': 'Morocco',
    'Sudan': 'Sudan',

    # 非洲西部
    'Nigeria': 'Nigeria',
    'Ghana': 'Ghana',
    'Senegal': 'Senegal',
    'Ivory-Coast': 'Ivory Coast',
    'Mali': 'Mali',
    'Burkina-Faso': 'Burkina Faso',
    'Niger': 'Niger',
    'Guinea': 'Guinea',
    'Benin': 'Benin',
    'Togo': 'Togo',
    'Sierra-Leone': 'Sierra Leone',
    'Liberia': 'Liberia',
    'Mauritania': 'Mauritania',
    'Gambia': 'Gambia',

    # 非洲中部
    'Cameroon': 'Cameroon',
    'Chad': 'Chad',
    'Central-African-Republic': 'Central African Republic',
    'Congo': 'Congo',
    'Democratic-Republic-of-the-Congo': 'Democratic Republic of the Congo',
    'Gabon': 'Gabon',
    'Equatorial-Guinea': 'Equatorial Guinea',
    'Angola': 'Angola',

    # 非洲东部
    'Ethiopia': 'Ethiopia',
    'Kenya': 'Kenya',
    'Uganda': 'Uganda',
    'Tanzania': 'Tanzania',
    'Rwanda': 'Rwanda',
    'Burundi': 'Burundi',
    'Somalia': 'Somalia',
    'Djibouti': 'Djibouti',
    'Eritrea': 'Eritrea',
    'South-Sudan': 'South Sudan',
    'Madagascar': 'Madagascar',
    'Mauritius': 'Mauritius',
    'Seychelles': 'Seychelles',

    # 非洲南部
    'South-Africa': 'South Africa',
    'Namibia': 'Namibia',
    'Botswana': 'Botswana',
    'Zimbabwe': 'Zimbabwe',
    'Zambia': 'Zambia',
    'Malawi': 'Malawi',
    'Mozambique': 'Mozambique',
    'Eswatini': 'Eswatini',
    'Lesotho': 'Lesotho',

    # 大洋洲
    'Australia': 'Australia',
    'New-Zealand': 'New Zealand',
    'Papua-New-Guinea': 'Papua New Guinea',
    'Fiji': 'Fiji',
    'Solomon-Islands': 'Solomon Islands',
    'Vanuatu': 'Vanuatu',
    'Samoa': 'Samoa',
    'Tonga': 'Tonga',
}


def fetch_country_prices(country_code: str, country_name: str) -> dict[str, Any]:
    """获取单个国家的油价（使用requests，更快）"""
    url = f'https://www.globalpetrolprices.com/{country_code}/gasoline_prices/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[{country_name}] HTTP {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取价格信息
        price_data = extract_price_from_page(soup, country_code, country_name, url)

        if price_data:
            print(f"[{country_name}] 成功获取价格")
        else:
            print(f"[{country_name}] 未找到价格数据")

        return price_data

    except Exception as e:
        print(f"[{country_name}] 获取失败: {e}")
        return None


def extract_price_from_page(soup: BeautifulSoup, country_code: str, country_name: str, url: str) -> dict[str, Any]:
    """从页面提取价格信息"""
    try:
        # 方法1: 查找所有表格，提取价格
        all_tables = soup.find_all('table')
        for table in all_tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    first_col = cols[0].text.strip()
                    second_col = cols[1].text.strip()

                    # 查找包含"Current price"或"Gasoline prices"的行
                    if 'Current price' in first_col or 'Gasoline prices' in first_col:
                        # 解析价格
                        price_match = re.search(r'([\d,.]+)', second_col)
                        if price_match:
                            price_value = parse_price(price_match.group(1))

                            # 从表头或其他行推断货币
                            currency = 'USD'  # 默认USD
                            # 查找货币信息
                            for r in rows:
                                text = r.get_text()
                                curr_match = re.search(r'([A-Z]{3})/Liter', text)
                                if curr_match:
                                    currency = curr_match.group(1)
                                    break

                            return {
                                'country': country_name,
                                'country_code': country_code,
                                'price': price_value,
                                'currency': currency,
                                'unit': 'per liter',
                                'update_date': time.strftime('%Y-%m-%d'),
                                'source_url': url
                            }

        # 方法2: 从meta标签提取
        meta_desc = soup.find('meta', {'name': 'Description'})
        if meta_desc:
            desc_text = meta_desc.get('content', '')
            # 例如: "The average gasoline price is CNY 7.53 per liter"
            price_match = re.search(r'([\d,.]+)\s*([A-Z]{3})\s*per liter', desc_text)
            if price_match:
                return {
                    'country': country_name,
                    'country_code': country_code,
                    'price': parse_price(price_match.group(1)),
                    'currency': price_match.group(2),
                    'unit': 'per liter',
                    'update_date': time.strftime('%Y-%m-%d'),
                    'source_url': url
                }

        return None

    except Exception as e:
        print(f"解析 {country_name} 页面失败: {e}")
        return None


def parse_price(price_str: str) -> float:
    """解析价格字符串"""
    # 移除千位分隔符，处理不同格式
    # 1,234.56 -> 1234.56
    # 1.234,56 -> 1234.56
    price_clean = price_str.replace(',', '')
    try:
        return float(price_clean)
    except ValueError:
        # 尝试欧洲格式 (逗号作为小数点)
        price_clean = price_str.replace('.', '').replace(',', '.')
        try:
            return float(price_clean)
        except ValueError:
            return 0.0


def main():
    """主函数"""
    print("开始抓取全球油价...")
    print(f"总共 {len(GLOBAL_COUNTRIES)} 个国家/地区")

    results = {}
    success_count = 0

    for country_code, country_name in GLOBAL_COUNTRIES.items():
        price_data = fetch_country_prices(country_code, country_name)
        if price_data:
            results[country_code] = price_data
            success_count += 1

        # 避免请求过快
        time.sleep(1)

    # 保存结果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    year = time.strftime("%Y")
    month = time.strftime("%m")

    output_file_latest = 'global_fuel_prices.json'

    # 创建归档目录
    archive_dir = f'archive/{year}/{month}'
    os.makedirs(archive_dir, exist_ok=True)
    output_file_timestamped = f'{archive_dir}/global_fuel_prices_{timestamp}.json'

    # 保存最新版本
    with open(output_file_latest, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 保存带时间戳的版本
    with open(output_file_timestamped, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n已写入 {output_file_latest} 和 {output_file_timestamped}")
    print(f"成功获取 {success_count}/{len(GLOBAL_COUNTRIES)} 个国家/地区的油价")


if __name__ == '__main__':
    main()
