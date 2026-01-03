#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LPR数据爬取工具 - 集成版本
在爬取数据时直接按年份分割，并支持增量更新
"""

import requests
from bs4 import BeautifulSoup
import datetime
import json
import os
import sys
from typing import Dict, List, Set
import csv


class LPRDataFetcher:
    """LPR数据爬取器 - 集成版本"""

    def __init__(self, output_dir: str = "yearly_data"):
        """
        初始化爬取器

        Args:
            output_dir: 按年份分割的数据输出目录
        """
        self.url = "https://www.bankofchina.com/fimarkets/lilv/fd32/201310/t20131031_2591219.html"
        self.output_dir = output_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.ensure_output_dir()

    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建输出目录: {self.output_dir}")

    def load_existing_data(self) -> Dict[int, List[Dict]]:
        """
        加载已存在的年份数据

        Returns:
            按年份分组的已存在数据
        """
        existing_data = {}

        if not os.path.exists(self.output_dir):
            return existing_data

        for file in os.listdir(self.output_dir):
            if file.startswith('LPR_Data_') and file.endswith('.json'):
                try:
                    year = int(file.split('_')[2].split('.')[0])
                    json_file = os.path.join(self.output_dir, file)

                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        existing_data[year] = data.get('data', [])
                        print(f"📂 加载已存在的 {year} 年数据: {len(existing_data[year])} 条记录")
                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    print(f"⚠️ 无法加载文件 {file}: {e}")
                    continue

        return existing_data

    def fetch_loan_rates(self) -> List[Dict]:
        """
        爬取最新的LPR数据

        Returns:
            LPR数据列表
        """
        print("🌐 开始爬取LPR数据...")

        try:
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')

            # 查找包含"LPR"的表格
            lpr_table = None
            for table in tables:
                if 'LPR' in table.get_text():
                    lpr_table = table
                    break

            if not lpr_table:
                print("❌ 未找到包含LPR数据的表格")
                return []

            rows = lpr_table.find_all('tr')
            all_text = []
            lpr_data = []

            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_text = ' '.join(cell.get_text(strip=True) for cell in cells)
                    all_text.append(row_text)

                    # 解析数据行（跳过标题行）
                    if len(cells) >= 3 and cells[0].get_text(strip=True) not in ['日期', '期限']:
                        try:
                            date_str = cells[0].get_text(strip=True)
                            one_year_rate = cells[1].get_text(strip=True).replace('%', '')
                            five_year_rate = cells[2].get_text(strip=True).replace('%', '')

                            # 验证数据格式
                            datetime.datetime.strptime(date_str, '%Y-%m-%d')
                            float(one_year_rate)
                            float(five_year_rate)

                            lpr_data.append({
                                'date': date_str,
                                'year': int(date_str.split('-')[0]),
                                'one_year_rate': one_year_rate,
                                'five_year_rate': five_year_rate
                            })
                        except (ValueError, IndexError):
                            continue

            print(f"✅ 成功爬取 {len(lpr_data)} 条LPR记录")
            return lpr_data, all_text

        except Exception as e:
            print(f"❌ 爬取过程中发生错误: {e}")
            return [], []

    def compare_with_existing(self, new_data: List[Dict], existing_data: Dict[int, List[Dict]]) -> Dict[int, List[Dict]]:
        """
        比较新数据与已存在数据，确定需要更新的年份

        Args:
            new_data: 新爬取的数据
            existing_data: 已存在的年份数据

        Returns:
            需要更新的年份数据
        """
        updates_needed = {}

        # 按年份分组新数据
        new_by_year = {}
        for record in new_data:
            year = record['year']
            if year not in new_by_year:
                new_by_year[year] = []
            new_by_year[year].append(record)

        print(f"🔍 比较新旧数据...")
        print(f"新数据年份: {sorted(new_by_year.keys(), reverse=True)}")
        print(f"已存在年份: {sorted(existing_data.keys(), reverse=True)}")

        # 检查每个年份
        all_years = set(new_by_year.keys()) | set(existing_data.keys())

        for year in sorted(all_years, reverse=True):
            new_records = new_by_year.get(year, [])
            existing_records = existing_data.get(year, [])

            # 检查是否需要更新
            need_update = False

            if not existing_records:
                # 新年份，需要创建
                need_update = True
                print(f"🆕 发现新年份: {year} 年，需要创建数据文件")
            elif len(new_records) != len(existing_records):
                # 记录数不同，需要更新
                need_update = True
                print(f"📊 {year} 年记录数变化: {len(existing_records)} → {len(new_records)}")
            else:
                # 检查最新记录是否相同
                if new_records and existing_records:
                    newest_new = new_records[0]  # 数据已按日期排序
                    newest_existing = existing_records[0]

                    if (newest_new['date'] != newest_existing['date'] or
                        newest_new['one_year_rate'] != newest_existing['one_year_rate'] or
                        newest_new['five_year_rate'] != newest_existing['five_year_rate']):
                        need_update = True
                        print(f"🔄 {year} 年数据有更新，最新记录变化")

                if not need_update:
                    print(f"✅ {year} 年数据已是最新，跳过更新")

            if need_update:
                updates_needed[year] = new_records

        return updates_needed

    def save_yearly_data(self, year: int, records: List[Dict]) -> bool:
        """
        保存单年数据到文件

        Args:
            year: 年份
            records: 该年的数据记录

        Returns:
            是否成功保存
        """
        try:
            base_filename = f"LPR_Data_{year}"

            # 保存CSV格式
            csv_file = os.path.join(self.output_dir, f"{base_filename}.csv")
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['日期', '一年期LPR(%)', '五年期以上LPR(%)'])
                # 按日期排序（从新到旧）
                sorted_records = sorted(records, key=lambda x: x['date'], reverse=True)
                for record in sorted_records:
                    writer.writerow([
                        record['date'],
                        record['one_year_rate'],
                        record['five_year_rate']
                    ])

            # 保存JSON格式
            json_file = os.path.join(self.output_dir, f"{base_filename}.json")
            sorted_records = sorted(records, key=lambda x: x['date'], reverse=True)
            json_data = {
                'year': year,
                'total_records': len(records),
                'date_range': {
                    'start': min(r['date'] for r in records),
                    'end': max(r['date'] for r in records)
                },
                'last_updated': datetime.datetime.now().isoformat(),
                'data': [
                    {
                        'date': r['date'],
                        'one_year_rate': r['one_year_rate'],
                        'five_year_rate': r['five_year_rate']
                    } for r in sorted_records
                ]
            }

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            print(f"💾 成功保存 {year} 年数据: {len(records)} 条记录")
            return True

        except Exception as e:
            print(f"❌ 保存 {year} 年数据失败: {e}")
            return False

    def save_complete_data(self, all_data: List[Dict], all_text: List[str]) -> bool:
        """
        保存完整数据文件（保持兼容性）

        Args:
            all_data: 所有数据记录
            all_text: 原始文本数据

        Returns:
            是否成功保存
        """
        try:
            # 保存原始文本格式
            with open('LPR_Data.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_text))

            # 保存JSON格式数据
            with open('LPR_Data.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'last_updated': datetime.datetime.now().isoformat(),
                    'data': [
                        {
                            'date': item['date'],
                            'one_year_rate': item['one_year_rate'],
                            'five_year_rate': item['five_year_rate']
                        } for item in all_data
                    ]
                }, f, ensure_ascii=False, indent=2)

            # 保存CSV格式数据
            with open('LPR_Data.csv', 'w', encoding='utf-8') as f:
                f.write('日期,一年期LPR(%),五年期以上LPR(%)\n')
                # 按日期排序（从新到旧）
                sorted_data = sorted(all_data, key=lambda x: x['date'], reverse=True)
                for item in sorted_data:
                    f.write(f"{item['date']},{item['one_year_rate']},{item['five_year_rate']}\n")

            print(f"💾 成功保存完整数据文件")
            return True

        except Exception as e:
            print(f"❌ 保存完整数据文件失败: {e}")
            return False

    def ensure_current_year_placeholder(self, existing_data: Dict[int, List[Dict]]) -> bool:
        """
        确保当前年份文件存在（即使没有数据）
        解决每年1月20日之前，因为新数据未发布导致yearly_data中没有当年数据的问题

        例如：现在是2026年1月3日，虽然2026年还没有LPR数据发布，
        但需要创建2026年的占位文件，确保API能正确获取年份列表

        Args:
            existing_data: 已存在的年份数据

        Returns:
            是否创建了新文件
        """
        current_year = datetime.datetime.now().year

        # 检查当前年份是否已存在且有数据
        if current_year in existing_data and existing_data[current_year]:
            print(f"✅ 当前年份 {current_year} 数据已存在，无需创建占位文件")
            return False

        # 检查占位文件是否已存在
        json_file = os.path.join(self.output_dir, f"LPR_Data_{current_year}.json")
        if os.path.exists(json_file):
            # 文件已存在，检查是占位文件还是有数据
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('data'):
                        # 有真实数据
                        print(f"✅ 当前年份 {current_year} 文件已存在且有数据")
                        return False
                    else:
                        # 是占位文件（data为空），更新last_updated时间
                        data['last_updated'] = datetime.datetime.now().isoformat()
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        return False
            except Exception:
                # 文件损坏，继续创建新文件
                pass

        # 创建当前年份的空占位文件
        try:
            base_filename = f"LPR_Data_{current_year}"

            # 创建空的CSV文件（只包含表头）
            csv_file = os.path.join(self.output_dir, f"{base_filename}.csv")
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['日期', '一年期LPR(%)', '五年期以上LPR(%)'])

            # 创建空的JSON占位文件
            json_file = os.path.join(self.output_dir, f"{base_filename}.json")
            json_data = {
                'year': current_year,
                'total_records': 0,
                'date_range': {
                    'start': None,
                    'end': None
                },
                'last_updated': datetime.datetime.now().isoformat(),
                'data': [],
                'note': f'该文件为占位文件，LPR数据通常每月20日发布，{current_year}年的数据将在首次发布后自动更新'
            }

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            print(f"📝 创建当前年份 {current_year} 的占位文件（等待数据发布）")
            return True

        except Exception as e:
            print(f"❌ 创建当前年份占位文件失败: {e}")
            return False

    def fetch_and_save(self, force_update: bool = False) -> bool:
        """
        爬取数据并按年份保存

        Args:
            force_update: 是否强制更新所有数据

        Returns:
            是否成功
        """
        print(f"🚀 LPR数据爬取工具 - 运行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 加载已存在的数据
        existing_data = self.load_existing_data() if not force_update else {}

        # 爬取最新数据
        new_data, all_text = self.fetch_loan_rates()
        if not new_data:
            print("❌ 爬取数据失败")
            return False

        # 比较数据确定需要更新的年份
        if force_update:
            # 强制更新所有年份
            new_by_year = {}
            for record in new_data:
                year = record['year']
                if year not in new_by_year:
                    new_by_year[year] = []
                new_by_year[year].append(record)
            updates_needed = new_by_year
            print(f"🔄 强制更新模式，将更新所有 {len(updates_needed)} 个年份")
        else:
            # 增量更新模式
            updates_needed = self.compare_with_existing(new_data, existing_data)

        if not updates_needed:
            print("📊 所有数据都是最新的，无需更新")
            # 但仍需确保当前年份文件存在（解决每年1月20日前没有当年数据的问题）
            self.ensure_current_year_placeholder(existing_data)
            return True

        # 保存需要更新的年份数据
        success_count = 0
        total_updates = len(updates_needed)

        print(f"\n📝 开始更新 {total_updates} 个年份的数据...")

        for year in sorted(updates_needed.keys(), reverse=True):
            records = updates_needed[year]
            if self.save_yearly_data(year, records):
                success_count += 1

        # 保存完整数据文件（保持兼容性）
        self.save_complete_data(new_data, all_text)

        # 确保当前年份文件存在（解决每年1月20日前没有当年数据的问题）
        # 这会创建当前年份的占位文件，确保API能正确获取年份列表
        self.ensure_current_year_placeholder(existing_data)

        # 输出结果摘要
        print(f"\n📋 更新摘要:")
        print(f"  总年份数: {total_updates}")
        print(f"  成功更新: {success_count}")
        print(f"  失败数量: {total_updates - success_count}")

        if success_count == total_updates:
            print("✅ 所有数据更新成功！")
            return True
        else:
            print("⚠️ 部分数据更新失败")
            return False


def check_data_freshness() -> bool:
    """
    检查数据是否需要更新

    Returns:
        是否需要更新
    """
    try:
        if not os.path.exists('LPR_Data.json'):
            return True

        with open('LPR_Data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        last_updated = datetime.datetime.fromisoformat(data['last_updated'])
        now = datetime.datetime.now()

        # 如果数据超过1天，则需要更新
        return (now - last_updated).days >= 1
    except Exception:
        return True


def main():
    """主函数"""
    # 检查命令行参数
    force_update = '--force' in sys.argv
    incremental_only = '--incremental-only' in sys.argv

    if incremental_only:
        print("📊 增量更新模式")
        force_update = False

    # 检查是否需要更新
    if not force_update and not check_data_freshness():
        print("📊 数据已是最新，无需更新")
        print("💡 使用 --force 强制更新所有数据")

        # 即使数据是最新，也要确保当前年份文件存在
        # 解决每年1月20日前没有当年数据导致API获取年份列表错误的问题
        fetcher = LPRDataFetcher()
        existing_data = fetcher.load_existing_data()
        fetcher.ensure_current_year_placeholder(existing_data)

        return 0

    # 创建爬取器并执行
    fetcher = LPRDataFetcher()
    success = fetcher.fetch_and_save(force_update=force_update)

    if success:
        print("🎉 LPR数据爬取和分割完成！")
        return 0
    else:
        print("❌ LPR数据处理失败！")

        # 即使处理失败，也要确保当前年份文件存在
        existing_data = fetcher.load_existing_data()
        fetcher.ensure_current_year_placeholder(existing_data)

        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)