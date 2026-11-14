import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'pipeline.py'


def run_cmd(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], text=True, capture_output=True)


class PipelineTests(unittest.TestCase):
    def test_end_to_end_and_stale_detection(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            src = base / 'raw'
            src.mkdir()
            article = src / 'article.json'
            raw_text = '作者说：选词前先确认是否有真实搜索需求。\n不要把低竞争度直接当作高需求，必须看搜索结果。'
            record = {'title': '测试文章', 'author': '测试署名', 'published_at': '2026-01-01', 'source_url': 'https://example.com/article1', 'content': raw_text}
            article.write_text(json.dumps(record, ensure_ascii=False), encoding='utf-8')
            project = base / 'kb'
            res = run_cmd('ingest', '--input', src, '--project', project)
            self.assertEqual(res.returncode, 0, res.stderr)
            corpus = [json.loads(x) for x in (project / 'corpus/articles.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(corpus), 1)
            row = corpus[0]
            self.assertIn('真实搜索需求', row['raw_text'])
            prompt = run_cmd('prompt', '--project', project, '--article-id', row['article_id'])
            self.assertEqual(prompt.returncode, 0, prompt.stderr)
            self.assertIn(raw_text, prompt.stdout)
            valid = {
                'schema_version': '1.0',
                'article_id': row['article_id'],
                'content_sha256': row['content_sha256'],
                'source_assessment': {'main_thesis': '确认搜索需求', 'article_type': 'tutorial', 'intended_audience': '建站者', 'source_limitations': []},
                'knowledge_units': [{
                    'unit_id': 'K001', 'dimensions': ['D2'], 'kind': 'decision_rule',
                    'claim': '选词要确认真实搜索需求', 'applies_when': '选词阶段', 'action': '核实需求', 'avoid': '仅看低竞争',
                    'steps': ['确认需求'], 'metrics': [], 'counterexamples': [], 'time_scope': 'evergreen', 'attribution': 'author',
                    'evidence': [{'quote': '选词前先确认是否有真实搜索需求。', 'line_start': 1, 'line_end': 1}],
                    'confidence': 'high', 'unknowns': [], 'tool_requirements': ['搜索需求数据'], 'agent_use': ['kb', 'skill']
                }],
                'open_questions': []
            }
            out = project / 'extractions' / (row['article_id'] + '.json')
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(valid, ensure_ascii=False), encoding='utf-8')
            self.assertEqual(run_cmd('validate', '--project', project).returncode, 0)
            self.assertEqual(run_cmd('compile', '--project', project).returncode, 0)
            compiled = [json.loads(x) for x in (project / 'compiled/knowledge.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(compiled), 1)
            self.assertEqual(compiled[0]['knowledge_id'], row['article_id'] + '#K001')
            # Fabricated/absent evidence must fail.
            valid['knowledge_units'][0]['evidence'][0]['quote'] = '原文不存在这句话'
            out.write_text(json.dumps(valid, ensure_ascii=False), encoding='utf-8')
            self.assertEqual(run_cmd('validate', '--project', project).returncode, 2)
            # Changed source must invalidate old extraction even if text contains quote.
            valid['knowledge_units'][0]['evidence'][0]['quote'] = '选词前先确认是否有真实搜索需求。'
            out.write_text(json.dumps(valid, ensure_ascii=False), encoding='utf-8')
            record['content'] = record['content'] + '\n新版本正文补充内容。'
            article.write_text(json.dumps(record, ensure_ascii=False), encoding='utf-8')
            self.assertEqual(run_cmd('ingest', '--input', src, '--project', project).returncode, 0)
            self.assertEqual(run_cmd('validate', '--project', project).returncode, 2)

    def test_markdown_frontmatter_and_dedupe(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            src = base / 'raw'
            src.mkdir()
            (src / 'a.md').write_text('---\ntitle: 测试标题\nauthor: 作者甲\nsource_url: https://example.com/x\npublished_at: 2026-01-03\n---\n这是一份正文，包含若干句话，用来测试完整导入，而不是一个摘要。本文还讨论如何验证用户搜索需求，并对比不同网站的竞争格局。', encoding='utf-8')
            project = base / 'kb'
            self.assertEqual(run_cmd('ingest', '--input', src, '--project', project).returncode, 0)
            self.assertEqual(run_cmd('ingest', '--input', src, '--project', project).returncode, 0)
            corpus = [json.loads(x) for x in (project / 'corpus/articles.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(corpus), 1)
            self.assertEqual(corpus[0]['title'], '测试标题')
            self.assertEqual(corpus[0]['author'], '作者甲')


if __name__ == '__main__':
    unittest.main()
