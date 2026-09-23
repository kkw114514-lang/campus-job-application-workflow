#!/usr/bin/env python3
"""将 v2.1 队列生成本地静态 HTML；不请求网络。"""
import argparse
from collections import Counter
from datetime import datetime
import html
import json
from pathlib import Path
import sys
NAMES = {'ready':'待填写', 'in_progress':'进行中', 'blocked':'待恢复', 'submission_unknown':'结果待核实', 'submitted':'已提交', 'skip':'不投'}
ORDER = ['submission_unknown', 'in_progress', 'ready', 'blocked', 'submitted', 'skip']
def esc(value): return html.escape('' if value is None else str(value))
def render(data):
    if not isinstance(data, dict) or data.get('schema_version') != '2.1' or not isinstance(data.get('applications'), list):
        raise ValueError('只支持 v2.1 applications 队列；迁移见数据结构.md')
    apps = data['applications']
    if not all(isinstance(a, dict) and isinstance(a.get('status'), str) for a in apps):
        raise ValueError('申请须为对象且包含字符串 status；请运行队列检查')
    counts = Counter(a['status'] for a in apps)
    parts = []
    groups = ORDER + sorted(set(counts) - set(ORDER))
    for status in groups:
        records = [a for a in apps if a['status'] == status]
        if not records: continue
        title = NAMES.get(status, '未知状态：' + status)
        parts.append(f'<section><h2>{esc(title)} · {len(records)} 条</h2>')
        for a in records:
            parts.append(f'<article><h3>{esc(a.get("company"))} · {esc(a.get("position"))}</h3>')
            for key, label in [('application_id','申请'),('tier','分级'),('city','城市'),('deadline','截止时间'),('portal','官方入口'),('reason','依据'),('next_action','下一步'),('recovery','恢复点'),('submitted_at','提交时间'),('evidence','证据')]:
                value = a.get(key)
                if key == 'deadline' and value is None: value = '未知，需核实'
                if isinstance(value, list): value = '；'.join(map(str,value))
                if value: parts.append(f'<p><b>{label}</b> {esc(value)}</p>')
            parts.append('</article>')
        parts.append('</section>')
    summary = ' / '.join(f'{NAMES.get(k,"未知状态")} {v}' for k,v in counts.items()) or '暂无申请'
    body = ''.join(parts) or '<p>队列为空。先核实目标岗位，再新增申请记录。</p>'
    now = datetime.now().astimezone().isoformat(timespec='minutes')
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>网申投递看板</title><style>body{{font-family:system-ui,sans-serif;max-width:960px;margin:auto;padding:24px;background:#f4f6fa;color:#1b2430}}h1{{font-size:26px}}h2{{font-size:20px;margin-top:28px}}article{{background:white;padding:16px 20px;border-radius:12px;margin:12px 0;border:1px solid #d8e0ec}}h3{{margin:0 0 12px}}p{{line-height:1.65;overflow-wrap:anywhere}}b{{color:#526077}}.meta{{color:#526077}}</style><h1>网申投递看板</h1><p class="meta">生成于 {esc(now)} · 共 {len(apps)} 条申请 · {esc(summary)}</p><p class="meta">本地静态快照；更新队列后重新生成。截止日期未知不代表没有截止日期。</p>{body}</html>'''
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('queue'); parser.add_argument('output')
    args = parser.parse_args()
    try:
        with open(args.queue, encoding='utf-8') as f: data = json.load(f)
        page = render(data)
        dst = Path(args.output); dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_text(page,encoding='utf-8')
    except (OSError, ValueError) as e:
        print('生成失败：',e,file=sys.stderr); return 1
    print('已生成：',dst); return 0
if __name__ == '__main__':
    sys.exit(main())
