#!/usr/bin/env python3
"""Offline corpus ingestion, provenance validation, and knowledge compilation.

No network requests, model calls, tokens, or external Python dependencies.
Semantic extraction is performed by an LLM using references/per_article_prompt.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from collections import Counter

SUPPORTED = {'.md', '.txt', '.json', '.jsonl', '.html', '.htm'}
SKIP_DIRS = {'.git', 'node_modules', 'corpus', 'compiled', 'extractions', 'synthesis', '__pycache__'}
DIMENSIONS = {f'D{i}' for i in range(1, 9)}
KINDS = {'observed_fact', 'principle', 'decision_rule', 'procedure', 'case', 'anti_pattern', 'tool_requirement', 'hypothesis'}
TIME_SCOPES = {'evergreen', 'time_sensitive', 'historical', 'unknown'}
ATTRIBUTIONS = {'author', 'quoted', 'reported', 'editorial', 'unknown'}
CONFIDENCES = {'high', 'medium', 'low'}
AGENT_USES = {'kb', 'skill', 'tool_spec', 'eval'}
ARTICLE_TYPES = {'methodology', 'case_study', 'tutorial', 'news', 'opinion', 'interview', 'community_digest', 'other'}
UNIT_KEYS = {'unit_id', 'dimensions', 'kind', 'claim', 'applies_when', 'action', 'avoid', 'steps', 'metrics', 'counterexamples', 'time_scope', 'attribution', 'evidence', 'confidence', 'unknowns', 'tool_requirements', 'agent_use'}


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def json_write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def jsonl_write(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def jsonl_read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for no, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            if not isinstance(data, dict):
                raise ValueError('row is not an object')
            rows.append(data)
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f'{path}:{no}: {exc}') from exc
    return rows


class HTMLText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'noscript'}:
            self.skip_depth += 1
        elif not self.skip_depth and tag in {'p','br','div','h1','h2','h3','h4','li','section','article','blockquote','tr'}:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'noscript'} and self.skip_depth:
            self.skip_depth -= 1
        elif not self.skip_depth and tag in {'p','div','li','h1','h2','h3','h4','tr'}:
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    parser = HTMLText()
    parser.feed(html)
    return re.sub(r'\n\s*\n\s*\n+', '\n\n', ''.join(parser.parts)).strip()


def parse_markdown(source: str) -> tuple[dict, str]:
    # Minimal frontmatter parser: key: value on one line; no yaml dependency.
    match = re.match(r'\A---\s*\n(.*?)\n---\s*\n', source, re.S)
    if not match:
        return {}, source
    meta = {}
    for line in match.group(1).splitlines():
        if ':' in line and not line.startswith((' ', '\t', '-')):
            key, value = line.split(':', 1)
            meta[key.strip()] = value.strip().strip('"\'')
    return meta, source[match.end():]


def first_str(mapping: dict, names: list[str]) -> str:
    for key in names:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ''


def read_items(path: Path):
    suffix = path.suffix.lower()
    if suffix in {'.md', '.txt'}:
        contents = path.read_text(encoding='utf-8-sig')
        meta, body = parse_markdown(contents) if suffix == '.md' else ({}, contents)
        yield meta, body, 'markdown' if suffix == '.md' else 'text', '0'
    elif suffix in {'.html', '.htm'}:
        raw = path.read_text(encoding='utf-8-sig')
        title_match = re.search(r'<title[^>]*>(.*?)</title>', raw, re.S | re.I)
        title = html_to_text(title_match.group(1)) if title_match else path.stem
        yield {'title': title}, html_to_text(raw), 'html_extracted_text', '0'
    elif suffix == '.jsonl':
        for i, obj in enumerate(jsonl_read(path), 1):
            yield from object_to_items(obj, str(i))
    elif suffix == '.json':
        obj = json.loads(path.read_text(encoding='utf-8-sig'))
        if isinstance(obj, list):
            for i, item in enumerate(obj, 1):
                yield from object_to_items(item, str(i))
        elif isinstance(obj, dict):
            for key in ('articles', 'items', 'data'):
                if isinstance(obj.get(key), list):
                    for i, item in enumerate(obj[key], 1):
                        yield from object_to_items(item, str(i))
                    return
            yield from object_to_items(obj, '0')


def object_to_items(obj, row):
    if isinstance(obj, str):
        yield {}, obj, 'json_string', row
    elif isinstance(obj, dict):
        if isinstance(obj.get('data'), dict):
            # Only shallowly flatten when relevant fields are nested in data.
            obj = {**obj['data'], **obj}
        content = first_str(obj, ['raw_text', 'content', 'body', 'text', 'article', 'content_html', 'html'])
        if not content:
            return
        if ('<p' in content.lower() or '<div' in content.lower()) and content.lstrip().startswith('<'):
            content = html_to_text(content)
            format_label = 'json_html_extracted_text'
        else:
            format_label = 'json_text'
        yield obj, content, format_label, row


def all_input_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    if not root.is_dir():
        raise ValueError(f'Input is not a readable file or folder: {root}')
    files = []
    for path in root.rglob('*'):
        if path.is_file() and path.suffix.lower() in SUPPORTED and not set(path.relative_to(root).parts[:-1]).intersection(SKIP_DIRS):
            files.append(path)
    return sorted(files)


def make_article(metadata: dict, content: str, source_path: Path, row: str, fmt: str):
    text = content.replace('\r\n', '\n').replace('\r', '\n')
    if len(text.strip()) < 40:
        return None
    url = first_str(metadata, ['source_url', 'url', 'link', 'article_url'])
    title = first_str(metadata, ['title', 'name', 'article_title']) or source_path.stem
    published = first_str(metadata, ['published_at', 'publish_time', 'pub_time', 'date', 'create_time'])
    author = first_str(metadata, ['author', 'nickname', 'account_name'])
    identity = url.strip() if url else f'{source_path.resolve()}:{row}'
    article_id = 'a_' + hashlib.sha1(identity.encode('utf-8')).hexdigest()[:14]
    return {
        'article_id': article_id,
        'title': title,
        'author': author,
        'published_at': published,
        'source_url': url,
        'source_path': str(source_path.resolve()),
        'source_row': row,
        'source_format': fmt,
        'content_sha256': sha256(text),
        'raw_text': text,
    }


def ingest(args):
    project = Path(args.project).resolve()
    corpus_file = project / 'corpus' / 'articles.jsonl'
    existing = {r['article_id']: r for r in jsonl_read(corpus_file)}
    counters = Counter()
    errors = []
    for file in all_input_files(Path(args.input)):
        try:
            for meta, text, fmt, row in read_items(file):
                article = make_article(meta, text, file, row, fmt)
                if article is None:
                    counters['too_short'] += 1
                    continue
                aid = article['article_id']
                if aid not in existing:
                    counters['added'] += 1
                elif existing[aid]['content_sha256'] != article['content_sha256']:
                    counters['updated'] += 1
                else:
                    counters['unchanged'] += 1
                existing[aid] = article
        except Exception as exc:
            errors.append(f'{file}: {exc}')
    rows = sorted(existing.values(), key=lambda x: x['article_id'])
    jsonl_write(corpus_file, rows)
    stats = {
        'articles': len(rows), 'added': counters['added'], 'updated': counters['updated'],
        'unchanged': counters['unchanged'], 'too_short': counters['too_short'],
        'missing_url': sum(not r['source_url'] for r in rows),
        'missing_date': sum(not r['published_at'] for r in rows),
        'formats': dict(Counter(r['source_format'] for r in rows)), 'errors': errors,
    }
    json_write(project / 'corpus' / 'stats.json', stats)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if errors:
        return 2
    return 0


def check_extraction(data: dict, article: dict) -> list[str]:
    errors = []
    def error(message):
        errors.append(message)
    if data.get('schema_version') != '1.0':
        error('schema_version must be 1.0')
    if data.get('article_id') != article['article_id']:
        error('article_id mismatch')
    if data.get('content_sha256') != article['content_sha256']:
        error('content_sha256 stale or mismatch')
    assess = data.get('source_assessment')
    if not isinstance(assess, dict) or assess.get('article_type') not in ARTICLE_TYPES:
        error('source_assessment.article_type invalid')
    for required in ('main_thesis', 'intended_audience', 'source_limitations'):
        if not isinstance(assess, dict) or required not in assess:
            error(f'source_assessment missing {required}')
    if not isinstance(data.get('open_questions'), list):
        error('open_questions must be an array')
    units = data.get('knowledge_units')
    if not isinstance(units, list):
        error('knowledge_units must be an array')
        return errors
    ids = set()
    lines = article['raw_text'].splitlines()
    for idx, unit in enumerate(units, 1):
        prefix = f'unit {idx}'
        if not isinstance(unit, dict):
            error(f'{prefix} must be object')
            continue
        missing = UNIT_KEYS - unit.keys()
        if missing:
            error(f'{prefix}: missing keys {sorted(missing)}')
        uid = unit.get('unit_id')
        if not isinstance(uid, str) or not uid.strip() or uid in ids:
            error(f'{prefix}: duplicate/empty unit_id')
        ids.add(uid)
        dims = unit.get('dimensions')
        if not isinstance(dims, list) or not dims or any(d not in DIMENSIONS for d in dims):
            error(f'{prefix}: invalid dimensions')
        for name, allowed in [('kind', KINDS), ('time_scope', TIME_SCOPES), ('attribution', ATTRIBUTIONS), ('confidence', CONFIDENCES)]:
            if unit.get(name) not in allowed:
                error(f'{prefix}: invalid {name}')
        if not isinstance(unit.get('claim'), str) or not unit['claim'].strip():
            error(f'{prefix}: claim is blank')
        for name in ('steps', 'metrics', 'counterexamples', 'unknowns', 'tool_requirements', 'agent_use'):
            if not isinstance(unit.get(name), list):
                error(f'{prefix}: {name} must be array')
        for name in ('applies_when', 'action', 'avoid'):
            if unit.get(name, ...) is not None and not isinstance(unit.get(name), str):
                error(f'{prefix}: {name} must be string or null')
        if isinstance(unit.get('agent_use'), list) and any(x not in AGENT_USES for x in unit['agent_use']):
            error(f'{prefix}: invalid agent_use')
        evs = unit.get('evidence')
        if not isinstance(evs, list) or not evs:
            error(f'{prefix}: missing evidence')
            continue
        for eidx, ev in enumerate(evs, 1):
            if not isinstance(ev, dict):
                error(f'{prefix}: evidence {eidx} is not object')
                continue
            quote = ev.get('quote')
            if not isinstance(quote, str) or not quote.strip():
                error(f'{prefix}: evidence {eidx} empty quote')
                continue
            if quote not in article['raw_text']:
                error(f'{prefix}: evidence {eidx} quote not found verbatim in raw article')
            a, b = ev.get('line_start'), ev.get('line_end')
            if (a is None) != (b is None):
                error(f'{prefix}: evidence {eidx} line_start/line_end must both exist or both be absent')
            if a is not None:
                if not isinstance(a, int) or not isinstance(b, int) or a < 1 or b < a or b > len(lines):
                    error(f'{prefix}: evidence {eidx} invalid line range')
                elif quote not in '\n'.join(lines[a-1:b]):
                    error(f'{prefix}: evidence {eidx} quote does not match line range')
    return errors


def validate_project(project: Path):
    corpus = {r['article_id']: r for r in jsonl_read(project / 'corpus' / 'articles.jsonl')}
    files = sorted((project / 'extractions').glob('*.json')) if (project / 'extractions').exists() else []
    valid = []
    problems = []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            aid = data.get('article_id', path.stem)
            if aid not in corpus:
                issues = [f'unknown article_id {aid}']
            else:
                issues = check_extraction(data, corpus[aid])
            if issues:
                problems.append({'file': str(path), 'errors': issues})
            else:
                valid.append((data, corpus[aid]))
        except Exception as exc:
            problems.append({'file': str(path), 'errors': [str(exc)]})
    summary = {
        'corpus_articles': len(corpus), 'extraction_files': len(files),
        'valid_extractions': len(valid), 'missing_extractions': sorted(set(corpus) - {d['article_id'] for d,a in valid}),
        'problems': problems,
    }
    return summary, valid


def validate(args):
    project = Path(args.project)
    summary, _ = validate_project(project)
    json_write(project / 'compiled' / 'validation_report.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 2 if summary['problems'] else 0


def compile_project(args):
    project = Path(args.project)
    summary, valid = validate_project(project)
    if summary['problems']:
        print('Refusing to compile: extraction errors found. Run validate.', file=sys.stderr)
        return 2
    if not valid:
        print('No valid extractions. Run the per-article AI distillation first.', file=sys.stderr)
        return 2
    units = []
    for extraction, article in valid:
        for unit in extraction['knowledge_units']:
            units.append({
                'knowledge_id': article['article_id'] + '#' + unit['unit_id'],
                'article_id': article['article_id'],
                'source_title': article['title'],
                'source_url': article['source_url'],
                'published_at': article['published_at'],
                'author': article['author'],
                'content_sha256': article['content_sha256'],
                **unit,
            })
    units.sort(key=lambda x: x['knowledge_id'])
    jsonl_write(project / 'compiled' / 'knowledge.jsonl', units)
    index = {
        'compiled_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'total_corpus_articles': summary['corpus_articles'],
        'extracted_articles': len(valid),
        'pending_articles': len(summary['missing_extractions']),
        'total_knowledge_units': len(units),
        'dimensions': dict(Counter(d for x in units for d in x['dimensions'])),
        'kinds': dict(Counter(x['kind'] for x in units)),
        'attributions': dict(Counter(x['attribution'] for x in units)),
        'coverage_warning': 'Only validated, extracted articles are represented. Figures/visuals may be missing from corpus.'
    }
    json_write(project / 'compiled' / 'index.json', index)
    print(json.dumps(index, ensure_ascii=False, indent=2))
    return 0


def status(args):
    project = Path(args.project)
    summary, _ = validate_project(project)
    print(json.dumps({k: v for k,v in summary.items() if k != 'problems'} | {'invalid_extraction_files': len(summary['problems'])}, ensure_ascii=False, indent=2))
    return 0


def make_prompt(args):
    project = Path(args.project)
    article_id = args.article_id
    corpus = {r['article_id']: r for r in jsonl_read(project / 'corpus' / 'articles.jsonl')}
    if article_id not in corpus:
        print('Unknown article_id', file=sys.stderr)
        return 2
    article = corpus[article_id]
    template = (Path(__file__).resolve().parent.parent / 'references' / 'per_article_prompt.md').read_text(encoding='utf-8')
    for field in ['article_id','content_sha256','title','published_at','author','source_url','raw_text']:
        template = template.replace('{{' + field + '}}', article.get(field, '') or '')
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(template, encoding='utf-8')
        print(f'Prompt written to {path}')
    else:
        print(template)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('ingest', help='Import local raw articles')
    p.add_argument('--input', required=True)
    p.add_argument('--project', required=True)
    p.set_defaults(func=ingest)
    for command, fn in [('status', status), ('validate', validate), ('compile', compile_project)]:
        p = sub.add_parser(command)
        p.add_argument('--project', required=True)
        p.set_defaults(func=fn)
    p = sub.add_parser('prompt', help='Render full per-article LLM prompt')
    p.add_argument('--project', required=True)
    p.add_argument('--article-id', required=True)
    p.add_argument('--out')
    p.set_defaults(func=make_prompt)
    args = parser.parse_args()
    try:
        raise SystemExit(args.func(args))
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        raise SystemExit(2)


if __name__ == '__main__':
    main()
