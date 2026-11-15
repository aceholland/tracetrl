"""Direct local smoke runner; not a replacement for the official Linux worker."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', nargs='+', type=Path)
    parser.add_argument('--target', required=True)
    parser.add_argument('--target-type', choices=['component', 'subsystem', 'system', 'technology'], default='technology')
    parser.add_argument('--application', default='Not specified')
    parser.add_argument('--environment', default='Not specified')
    parser.add_argument('--checklist', type=Path, required=True)
    parser.add_argument('--case-id', default='LOCAL-001')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--semantic', action='store_true', help='Requires declared catalogue MiniLM weights in APCTT_MODEL_STORE')
    args = parser.parse_args()
    if not 1 <= len(args.pdf) <= 3:
        parser.error('Provide one to three PDF reports.')
    start = time.monotonic()
    from pypdf import PdfReader
    from participant_module.adapter import AssessmentModule
    checklist = json.loads(args.checklist.read_text(encoding='utf-8'))
    documents = []
    for i, path in enumerate(args.pdf, 1):
        with path.open('rb') as stream:
            count = len(PdfReader(stream).pages)
        documents.append({'document_id': f'D{i}', 'path': str(path.resolve()), 'title': path.stem,
                          'page_count': count, 'language': 'en', 'document_date': None})
    case = {'schema_version': 'apctt-pdf-example-v1', 'checklist_version': checklist['version'],
            'case_id': args.case_id, 'input_profile': 'pdf_report', 'title': args.target,
            'assessment_target': {'target_id': 'TARGET-1', 'type': args.target_type, 'description': args.target},
            'intended_application': args.application, 'intended_environment': args.environment,
            'assessment_as_of': None, 'documents': documents}
    module = AssessmentModule()
    module.load({'checklist': checklist, 'module': {'settings': {'use_semantic': args.semantic}}}, ROOT / 'assets')
    context = SimpleNamespace(remaining_ms=lambda: max(0, 180000 - (time.monotonic() - start) * 1000))
    try:
        result = module.assess(case, context)
    finally:
        module.reset_case()
        module.close()
    output = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if args.output:
        args.output.write_text(output, encoding='utf-8')
    else:
        print(output, end='')
    print(f'Elapsed: {time.monotonic() - start:.3f} s; backend: {"semantic" if args.semantic else "lexical"}', file=sys.stderr)


if __name__ == '__main__':
    main()
