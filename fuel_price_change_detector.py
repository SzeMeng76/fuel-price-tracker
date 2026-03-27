import json
import os
from datetime import datetime
from typing import Any


def load_json_file(filepath: str) -> dict:
    """加载JSON文件"""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def detect_changes(old_data: dict, new_data: dict, data_type: str) -> list[dict[str, Any]]:
    """检测价格变化"""
    changes = []

    for key in new_data:
        if key not in old_data:
            # 新增的地区/国家
            changes.append({
                'type': 'new',
                'location': new_data[key].get('province') or new_data[key].get('country'),
                'data': new_data[key]
            })
        else:
            # 检查价格变化
            old_item = old_data[key]
            new_item = new_data[key]

            if data_type == 'china':
                # 检查中国油价变化
                price_changes = {}
                for fuel_type in ['92_gasoline', '95_gasoline', '98_gasoline', '0_diesel']:
                    old_price = old_item.get(fuel_type, 0)
                    new_price = new_item.get(fuel_type, 0)
                    if old_price != new_price and new_price > 0:
                        price_changes[fuel_type] = {
                            'old': old_price,
                            'new': new_price,
                            'change': new_price - old_price,
                            'change_percent': ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
                        }

                if price_changes:
                    changes.append({
                        'type': 'price_change',
                        'location': new_item.get('province'),
                        'changes': price_changes
                    })

            elif data_type == 'global':
                # 检查全球油价变化
                old_price = old_item.get('price', 0)
                new_price = new_item.get('price', 0)
                if old_price != new_price and new_price > 0:
                    changes.append({
                        'type': 'price_change',
                        'location': new_item.get('country'),
                        'old_price': old_price,
                        'new_price': new_price,
                        'change': new_price - old_price,
                        'change_percent': ((new_price - old_price) / old_price * 100) if old_price > 0 else 0,
                        'currency': new_item.get('currency')
                    })

    return changes


def generate_changelog(china_changes: list, global_changes: list) -> str:
    """生成CHANGELOG内容"""
    today = datetime.now().strftime('%Y-%m-%d')
    changelog = f"# Fuel Price Changes - {today}\n\n"

    if china_changes:
        changelog += "## China Price Changes\n\n"
        for change in china_changes:
            if change['type'] == 'price_change':
                changelog += f"### {change['location']}\n\n"
                for fuel_type, details in change['changes'].items():
                    fuel_name = fuel_type.replace('_', ' ').title()
                    trend = "📈" if details['change'] > 0 else "📉"
                    changelog += f"- **{fuel_name}**: {details['old']:.2f} → {details['new']:.2f} CNY/L "
                    changelog += f"{trend} {details['change']:+.2f} ({details['change_percent']:+.2f}%)\n"
                changelog += "\n"

    if global_changes:
        changelog += "## Global Price Changes\n\n"
        for change in global_changes:
            if change['type'] == 'price_change':
                trend = "📈" if change['change'] > 0 else "📉"
                changelog += f"### {change['location']}\n\n"
                changelog += f"- **Price**: {change['old_price']:.2f} → {change['new_price']:.2f} {change['currency']}/L "
                changelog += f"{trend} {change['change']:+.2f} ({change['change_percent']:+.2f}%)\n\n"

    if not china_changes and not global_changes:
        changelog += "No price changes detected.\n"

    return changelog


def main():
    """主函数"""
    print("检测价格变化...")

    # 查找最新的两个归档文件
    archive_dir = 'archive'
    china_files = []
    global_files = []

    if os.path.exists(archive_dir):
        for root, dirs, files in os.walk(archive_dir):
            for file in files:
                if file.startswith('china_fuel_prices_'):
                    china_files.append(os.path.join(root, file))
                elif file.startswith('global_fuel_prices_'):
                    global_files.append(os.path.join(root, file))

    china_files.sort()
    global_files.sort()

    # 加载数据
    old_china_data = load_json_file(china_files[-2]) if len(china_files) >= 2 else {}
    new_china_data = load_json_file('china_fuel_prices.json')

    old_global_data = load_json_file(global_files[-2]) if len(global_files) >= 2 else {}
    new_global_data = load_json_file('global_fuel_prices.json')

    # 检测变化
    china_changes = detect_changes(old_china_data, new_china_data, 'china')
    global_changes = detect_changes(old_global_data, new_global_data, 'global')

    # 生成CHANGELOG
    changelog_content = generate_changelog(china_changes, global_changes)

    # 保存CHANGELOG
    with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
        f.write(changelog_content)

    print(f"检测到 {len(china_changes)} 个中国价格变化")
    print(f"检测到 {len(global_changes)} 个全球价格变化")
    print("CHANGELOG.md 已更新")


if __name__ == '__main__':
    main()
