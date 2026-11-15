"""Direct result-contract check with an untouched official kit's own validator."""
import argparse
import json
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit', type=Path, required=True)
    parser.add_argument('--request', type=Path, help='Official-format request JSON; defaults to kit example')
    parser.add_argument('--result-output', type=Path)
    args = parser.parse_args()
    kit = args.kit.resolve()
    sys.path[:0] = [str(ROOT), str(kit / 'src')]
    from apctt_contracts.config import Checklist
    from apctt_contracts.pdf import local_worker_case
    from apctt_contracts.results import validate_result
    from participant_module.adapter import AssessmentModule
    checklist = json.loads((kit / 'contracts/checklist.official.json').read_text(encoding='utf-8'))
    request = json.loads((args.request or kit / 'docs/EXAMPLE_REQUEST.json').read_text(encoding='utf-8'))
    started = time.monotonic()
    with tempfile.TemporaryDirectory() as temp:
        case = local_worker_case(request['case'], Path(temp) / 'documents')
        module = AssessmentModule()
        module.load({'checklist': checklist, 'module': {'settings': {}}}, ROOT / 'assets')
        context = SimpleNamespace(remaining_ms=lambda: max(0, 180000 - (time.monotonic() - started) * 1000))
        try:
            result = module.assess(case, context)
        finally:
            module.reset_case()
            module.close()
        issues = validate_result(result, case=case, checklist=Checklist.model_validate(checklist))
        report = {'check': 'direct official result validator; not the Linux worker',
                  'issues': [{'path': x.path, 'rule': x.rule} for x in issues],
                  'elapsed_seconds': round(time.monotonic() - started, 4), 'result': result}
        if args.result_output:
            args.result_output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({k: v for k, v in report.items() if k != 'result'}, indent=2))
        return bool(issues)


if __name__ == '__main__':
    raise SystemExit(main())
