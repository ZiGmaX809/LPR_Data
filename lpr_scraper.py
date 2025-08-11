import requests
from bs4 import BeautifulSoup
import datetime
import json
import os
import sys

def fetch_loan_rates():
    """爬取中国银行贷款利率数据"""
    url = "https://www.bankofchina.com/fimarkets/lilv/fd32/201310/t20131031_2591219.html"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'  # 确保中文正确显示

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 首先查找页面中的所有表格
            tables = soup.find_all('table')

            # 查找包含"LPR"的表格
            lpr_table = None
            for table in tables:
                if 'LPR' in table.get_text():
                    lpr_table = table
                    break

            # 如果找到了表格，解析其中的数据
            if lpr_table:
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
                                    'one_year_rate': one_year_rate,
                                    'five_year_rate': five_year_rate
                                })
                            except (ValueError, IndexError):
                                continue

                # 保存原始文本格式（保持与原代码兼容）
                with open('LPR_Data.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(all_text))

                # 保存JSON格式数据（便于程序处理）
                with open('LPR_Data.json', 'w', encoding='utf-8') as f:
                    json.dump({
                        'last_updated': datetime.datetime.now().isoformat(),
                        'data': lpr_data
                    }, f, ensure_ascii=False, indent=2)

                # 保存CSV格式数据（便于查看和分析）
                with open('LPR_Data.csv', 'w', encoding='utf-8') as f:
                    f.write('日期,一年期LPR(%),五年期以上LPR(%)\n')
                    for item in lpr_data:
                        f.write(f"{item['date']},{item['one_year_rate']},{item['five_year_rate']}\n")

                print(f"成功获取LPR数据，共{len(lpr_data)}条记录")
                print(f"数据已保存到以下文件：")
                print(f"  - LPR_Data.txt (原始格式)")
                print(f"  - LPR_Data.json (JSON格式)")
                print(f"  - LPR_Data.csv (CSV格式)")
                
                return True
            else:
                print("未找到包含LPR数据的表格")
                return False
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False

    except Exception as e:
        print(f"发生错误: {e}")
        return False

def check_data_freshness():
    """检查数据是否需要更新"""
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
    print(f"LPR数据爬取工具 - 运行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查是否需要强制更新
    force_update = '--force' in sys.argv
    
    if force_update or check_data_freshness():
        print("开始获取LPR数据...")
        success = fetch_loan_rates()
        
        if success:
            print("✅ LPR数据获取成功！")
            return 0
        else:
            print("❌ LPR数据获取失败！")
            return 1
    else:
        print("📊 数据已是最新，无需更新")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)