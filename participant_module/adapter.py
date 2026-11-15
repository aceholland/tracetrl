"""APCTT worker entry point. The default path does not import torch."""
from __future__ import annotations

from .evidence import extract_passages
from .reasoning import assess_passages


class AssessmentModule:
    def __init__(self):
        self.checklist = {'version': '', 'criteria': []}
        self.settings = {}
        self.semantic = None

    def load(self, config, asset_root):
        self.checklist = config['checklist']
        self.settings = dict(config['module'].get('settings', {}))
        if self.settings.get('use_semantic', False):
            import os
            from pathlib import Path
            from .semantic import SemanticRanker
            self.semantic = SemanticRanker(Path(os.environ['APCTT_MODEL_STORE']))

    def assess(self, case, context):
        base = {key: case[key] for key in ('schema_version', 'case_id', 'assessment_target')}
        base['checklist_version'] = self.checklist['version']
        try:
            passages, complete = extract_passages(case, context, self.settings)
        except (OSError, ValueError) as exc:
            return self._abstain(base, f'PDF extraction was unavailable ({type(exc).__name__}); readable report text is needed.')
        if not complete:
            return self._abstain(base, 'The text or time budget was exhausted before the reports could be assessed completely.')
        result = assess_passages(case, self.checklist, passages, context, self.semantic)
        if context.remaining_ms() < 1500:
            return self._abstain(base, 'The time budget was exhausted before every criterion could be assessed.')
        return dict(base, **result)

    def _abstain(self, base, reason):
        ids = [c['criterion_id'] for c in self.checklist['criteria']]
        return dict(base, assessment_status='abstained', predicted_trl=None,
                    criterion_status={cid: 'insufficient evidence' for cid in ids},
                    evidence_reference={cid: [] for cid in ids}, missing_evidence={cid: reason for cid in ids},
                    abstention_reason='insufficient evidence', error_code=None)

    def reset_case(self):
        """All extraction and case state is local to assess()."""

    def close(self):
        self.semantic = None
