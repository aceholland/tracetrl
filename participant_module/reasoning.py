"""Conservative evidence rules; readiness is a reasoned estimate, not calibrated ML."""
from __future__ import annotations

import re
import json
from pathlib import Path

from .evidence import Retriever, tokens, target_scoped_text

MEANINGS = json.loads(Path(__file__).with_name('criterion_meanings.json').read_text(encoding='utf-8'))


def has(pattern, text):
    return bool(re.search(pattern, text, flags=re.I))


def criterion_kind(description):
    # Match the supported meaning, never just a TRL token or a criterion ID.
    normalized = ' '.join(description.lower().split())
    return MEANINGS.get(normalized)


def judgement(kind, text, intended_environment):
    """Return supported / rejected / unknown from the actual excerpt."""
    text = text.lower()
    # The month in a completed study period is not the modal verb "may".
    planning_text = re.sub(r'\bmay(?=\s+(?:through|to|\d{1,2}\b))', 'month', text)
    planning_text = re.sub(r'\bcriteria proposed by\b', 'criteria cited from', planning_text)
    planned = has(r'\b(will|would|could|should|may|might|plan\w*|future|next year|expected to|scheduled|upcoming|anticipat\w*|intend\w*|propos\w*)\b|\bto be (tested|validated|demonstrated|qualified|evaluated|calibrated|compared|measured)\b', planning_text)
    tested = has(r'\b(tested|validated|demonstrated|evaluated|measured|verified)\b', text)
    article = has(r'\b(prototypes?|breadboards?|components?|sensors?|instruments?|models?|systems?|software|algorithms?|methods?|devices?)\b', text)
    lab = has(r'\b(laboratory|lab|bench|benchtop|in vitro)\b', text)
    relevant = has(r'\b(simulat\w*|representative|relevant environment|environmental chamber|testbed|test bed)\b', text)
    operation = has(r'\b(actual|operational|field|real-world|routine|in service|deployment)\b', text)
    final = has(r'\b(final|production|completed|fully integrated|near-final|close to.*final)\b', text)
    prototype = has(r'\b(prototype|representative model|pilot|subsystem)\b', text)
    demonstrated = has(r'\b(demonstrated|demonstration|trialled|trialed)\b', text)
    measured = has(r'\b(measured|measurements|achieved|results (showed|indicated|demonstrated)|accuracy|sensitivity|error|precision|performance|efficiency)\b', text)
    missing_results = has(r'\b(no|without|lack of)\s+(measured\s+)?(measurements?|results?|performance data)\b|\bnot\s+(yet\s+)?(been\s+)?(measured|obtained|reported)\b', text)
    measured = measured and not missing_results
    # A numerical simulation is not a relevant-environment prototype demonstration.
    # Quantitative model-to-observation comparisons can establish analytical proof.
    metric = r'\b(error|rmse|nrmse|nse|r2|bias|coefficient of determination)\b'
    reported_metric = (has(metric + r'[^.!?]{0,300}\b(was|were|is|equals?)\s+(?:about\s+|approximately\s+)?[-\u2212]?\d+(?:\.\d+)?', text)
                       or (has(r'\bassessed as (satisfactory|good|acceptable|accurate)\b', text)
                           and has(metric + r'\s*\([-\u2212]?\d+\.\d+\)', text))
                       or (has(r'\bmodel performance measures?\b', text)
                           and has(r'\bobserved\b', text)
                           and has(metric + r'\s+[-\u2212]?\d+\.\d+', text)))
    model_result = (has(r'\bmodels?\b', text)
                    and has(r'\b(calibrated|evaluated|tested|assessed|compared)\b', text)
                    and (has(r'\b(observed|measured|surveyed)\b', text)
                         or has(r'\bstatistical measures?\b', text))
                    and reported_metric
                    and not missing_results
                    and not has(r'\b(not|never)\s+(?:yet\s+)?(?:been\s+)?(?:calibrated|compared|assessed|evaluated)\b', text)
                    and not has(r'\b(unsatisfactory|unacceptable|inadequate|failed)\b|\bacceptance threshold\b|\bnot satisfactory\b', text)
                    and not has(r'\b(desired|target)\s+(?:\w+\s+){0,3}(error|rmse|nrmse|nse|r2|bias)\b', text))
    outcome = has(r'\b(success\w*|met|meets|exceeded|satisf\w*|passed|achieved|failed|did not meet)\b', text)
    requirements = has(r'\b(requirement\w*|acceptance|threshold|specification\w*|criteria)\b', text)
    quantified = has(r'\b\d+(\.\d+)?\s*(percent|%|mg|mm|cm|km|hz|db|seconds|minutes|hours|w|kw|degrees)|\b\d+\.\d+\b', text)
    negative_testing = has(r'\b(not|never)\s+(yet\s+)?(been\s+)?(tested|validated|demonstrated|evaluated|qualified|deployed)\b|\b(no|without)\s+(laboratory\s+)?(testing|validation|demonstration|deployment)\b', text)
    # Each kind has distinct requirements. A general failure is not a failed laboratory test.
    negative = {
        3: negative_testing and (lab or 'analytical' in text),
        4: negative_testing and lab,
        5: negative_testing and relevant,
        6: negative_testing and prototype and relevant,
        7: negative_testing and prototype and operation,
        8: (negative_testing and final) or has(r'failed qualification|not qualified', text),
        9: has(r'not (yet )?(been )?(successfully )?(used|deployed|operated)|never (used|deployed|operated)|unsuccessful.*operation|not successfully', text),
    }.get(kind, False)
    if negative:
        return 'rejected'
    if planned and kind not in (1, 2):
        return 'unknown'
    environment_match = bool(tokens(intended_environment) & tokens(text))
    demonstrated_environment = relevant and environment_match
    supported = {
        1: has(r'\b(principle\w*|physical basis|theoretical basis|based on|governing equation\w*)\b', text)
           and has(r'\b(observ\w*|experiment\w*|stud\w*|literature|theory|equation\w*)\b', text),
        2: (has(r'\b(concept|designed to|intended to|operates by|works by|consists of)\b', text)
            and has(r'\b(application|monitor\w*|detect\w*|measur\w*|process\w*|control\w*)\b', text))
           or (article and has(r'\b(reads|accepts|takes)\b', text)
               and has(r'\b(creates|produces|writes|computes)\b', text)
               and has(r'\b(files?|records?|data|inputs?|outputs?)\b', text)
               and has(r'\b(simulat\w*|predict\w*|monitor\w*|detect\w*|measur\w*|control\w*)\b', text)),
        3: ((lab or has(r'\b(analytical|proof of concept|proof-of-concept)\b', text)) and measured and (tested or quantified)) or model_result,
        4: article and lab and tested and measured,
        5: article and tested and measured and demonstrated_environment,
        6: prototype and demonstrated and demonstrated_environment,
        7: prototype and final and demonstrated and operation and environment_match,
        8: final and tested and requirements and has(r'\b(qualified|qualification|certified|passed)\b', text),
        9: final and operation and environment_match and has(r'\b(operated|used|running|in service|deployed)\b', text)
           and has(r'\bsuccess\w*\b', text)
           and has(r'\b(for|over|during)\s+\d+\s+(days?|weeks?|months?|years?)\b|\bsince\s+(19|20)\d{2}\b', text),
        'performance': measured and quantified and requirements and outcome,
        'conditions': article and tested and (lab or operation or relevant or has(r'\b(temperature|salinity|pressure|humidity)\b', text)),
        'scope': article and (tested or demonstrated or has(r'\b(operated|deployed|designed to)\b', text)),
    }.get(kind, False)
    return 'supported' if supported else 'unknown'


def assess_passages(case, checklist, passages, context, semantic=None):
    retriever = Retriever(passages)
    statuses, evidence, missing, rationales = {}, {}, {}, {}
    achieved = []
    conflict = False
    for criterion in checklist['criteria']:
        cid, description = criterion['criterion_id'], criterion['description']
        kind = criterion_kind(description)
        statuses[cid] = 'insufficient evidence'
        evidence[cid] = []
        missing[cid] = f'No target-specific passage establishes: {description}'
        if kind is None or context.remaining_ms() < 1500:
            continue
        query = description
        if kind == 3:
            # Scientific reports often call analytical tests calibration or comparison.
            # Retrieval vocabulary only selects excerpts; judgement still requires results.
            query += ' calibrated calibration statistical error observed measured simulated comparison RMSE NSE performance'
        candidates = retriever.search(query, case['assessment_target']['description'])
        if semantic is not None and context.remaining_ms() > 15000:
            candidates = semantic.rank(description, candidates[:32]) + candidates[32:]
        positive, negative = [], []
        for passage in candidates:
            scoped = target_scoped_text(passage.text, case['assessment_target']['description'])
            decision = judgement(kind, scoped, case.get('intended_environment') or '')
            if decision == 'supported':
                positive.append(passage)
            elif decision == 'rejected':
                negative.append(passage)
        if positive and negative:
            conflict = conflict or isinstance(kind, int)
            missing[cid] = 'The reports contain both supporting and contradictory target-specific evidence; reconciliation is needed.'
            rationales[cid] = missing[cid]
            evidence[cid] = [positive[0].reference(), negative[0].reference()]
        elif positive or negative:
            chosen = positive or negative
            statuses[cid] = 'met' if positive else 'not met'
            del missing[cid]
            seen = set()
            for passage in chosen:
                key = (passage.document_id, passage.page)
                if key not in seen:
                    evidence[cid].append(passage.reference())
                    seen.add(key)
                if len(seen) == 3:
                    break
            rationales[cid] = ('Target-specific excerpt satisfies the implemented evidence rule.' if positive
                               else 'Target-specific excerpt explicitly reports the condition was not achieved.')
            if positive and isinstance(kind, int):
                achieved.append(kind)
    level = max(achieved, default=None)
    result = {'criterion_status': statuses, 'evidence_reference': evidence, 'missing_evidence': missing,
              'criterion_rationale': rationales, 'assessment_status': 'abstained', 'predicted_trl': None,
              'abstention_reason': 'conflicting evidence' if conflict else 'insufficient evidence', 'error_code': None}
    if level is not None and not conflict:
        result.update(assessment_status='completed', predicted_trl=level, abstention_reason=None,
                      trl_rationale=f'TRL {level} is the highest maturity milestone with directly cited target-specific evidence under the supplied checklist. Unestablished criteria remain explicit; this is an uncalibrated rule-based estimate.')
    return result
