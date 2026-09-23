#!/usr/bin/env python3
"""初始化个人运行文件；只创建缺失文件，不覆盖已有文件。"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def create(relative, text):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('x', encoding='utf-8') as f:
            f.write(text)
        print('已创建：', relative)
    except FileExistsError:
        print('已保留：', relative)

def main():
    for folder in ['材料库/简历', '材料库/照片', '材料库/证明', '证据', '岗位评估卡', '本地攻略']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    for source, target in [
        ('材料库模板/网申基础信息.模板.json', '材料库/网申基础信息.json'),
        ('材料库模板/答案库.模板.md', '材料库/答案库.md'),
        ('共享历史.模板.md', '共享历史.md'),
    ]:
        create(target, (ROOT / source).read_text(encoding='utf-8'))
    create('队列/application-state.json', json.dumps(
        {'schema_version': '2.1', 'mode': 'assist', 'applications': []},
        ensure_ascii=False, indent=2) + '\n')
    create('进度记录.md', '# 网申进度\n\n按轮追加：时间、申请 ID、动作、结果、阻塞原因、恢复条件、下一步。\n')
    print('初始化完成。请填写真实材料与目标申请；初始队列为空。')

if __name__ == '__main__':
    main()
