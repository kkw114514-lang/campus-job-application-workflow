#!/usr/bin/env python3
"""检查申请队列结构；不验证真实事实、网站状态或证据内容。"""
import argparse
import json
import sys
from datetime import datetime
STATUSES = {'ready', 'in_progress', 'blocked', 'submission_unknown', 'submitted', 'skip'}

def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ['顶层必须是 JSON 对象']
    if data.get('schema_version') != '2.1':
        errors.append('schema_version 必须为 2.1；旧版请先人工迁移')
    if data.get('mode') not in {'assist', 'authorized'}:
        errors.append('mode 必须为 assist 或 authorized')
    apps = data.get('applications')
    if not isinstance(apps, list):
        return errors + ['applications 必须为数组']
    ids, identities = set(), set()
    for i, a in enumerate(apps, 1):
        prefix = f'第 {i} 条：'
        def fail(msg): errors.append(prefix + msg)
        if not isinstance(a, dict):
            fail('申请必须是对象'); continue
        for key in ['application_id', 'company_id', 'company', 'recruitment_id', 'job_id', 'position', 'channel']:
            if not isinstance(a.get(key), str) or not a[key].strip(): fail(key + ' 必须为非空字符串')
        ident = a.get('application_id')
        if isinstance(ident, str):
            if ident in ids: fail('application_id 重复')
            ids.add(ident)
        key = tuple(a.get(k) for k in ['company_id', 'recruitment_id', 'job_id'])
        if all(isinstance(k, str) and k.strip() for k in key):
            if key in identities: fail('同一公司/招聘计划/岗位重复；跨渠道也须合并核查')
            identities.add(key)
        st = a.get('status')
        if not isinstance(st, str) or st not in STATUSES: fail('未知 status')
        tier = a.get('tier')
        if not isinstance(tier, str) or tier not in {'S', 'A', 'B', 'C'}: fail('tier 必须为 S/A/B/C')
        if tier == 'C' and st in ('ready', 'in_progress'): fail('C 级不可进入待投或执行状态')
        for key in ['reason', 'next_action', 'owner', 'recovery', 'submitted_at', 'portal', 'city', 'eval', 'rules_source', 'resume_version', 'verified_at']:
            if a.get(key) is not None and not isinstance(a[key], str): fail(key + ' 应为字符串或 null')
        if st in ('blocked', 'submission_unknown') and not a.get('recovery'): fail('必须记录 recovery')
        if st == 'in_progress' and not a.get('owner'): fail('执行中必须记录 owner')
        if st == 'skip' and not a.get('reason'): fail('放弃必须记录 reason')
        if st in ('ready', 'in_progress'):
            for key in ['portal', 'verified_at', 'rules_source', 'resume_version', 'eval']:
                if not a.get(key): fail('可执行申请缺少 ' + key)
        ev = a.get('evidence', [])
        if not isinstance(ev, list) or not all(isinstance(x, str) and x.strip() for x in ev):
            fail('evidence 必须为非空路径字符串组成的数组')
        if st == 'submitted' and (not a.get('submitted_at') or not ev): fail('已提交必须记录时间和证据')
        auth = a.get('authorization')
        if not isinstance(auth, dict) or type(auth.get('submit')) is not bool:
            fail('authorization.submit 必须为布尔值')
        elif auth['submit'] and not (isinstance(auth.get('scope'), str) and auth['scope'].strip() and isinstance(auth.get('confirmed_at'), str) and auth['confirmed_at'].strip()):
            fail('提交授权缺少明确 scope 或 confirmed_at')
        deadline = a.get('deadline')
        if deadline is not None:
            try:
                dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                if dt.tzinfo is None: raise ValueError()
            except (ValueError, TypeError, AttributeError): fail('deadline 须为带时区 ISO 8601 时间或 null')
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('queue', help='队列 JSON 路径')
    args = parser.parse_args()
    try:
        with open(args.queue, encoding='utf-8') as f: data = json.load(f)
    except (OSError, ValueError) as e:
        print('读取失败：', e, file=sys.stderr); return 1
    errors = validate(data)
    if errors:
        print('\n'.join(errors), file=sys.stderr); return 1
    print(f'结构检查通过：{len(data["applications"])} 条申请。事实、授权与证据仍须核实。')
    return 0
if __name__ == '__main__':
    sys.exit(main())
