"""Bounded, page-preserving PDF extraction and lexical retrieval."""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

STOP = set('the a an and or of to in for on with by from is are was were be been it its this that we our as at how what which those assessed technology system component subsystem report describes states presents intended application environment study results based using use used development evaluation assessment scientific technical'.split())


def tokens(text: str) -> set[str]:
    # Normalize common article plurals without stemming proper names or quotations.
    plurals = {'models': 'model', 'sensors': 'sensor', 'algorithms': 'algorithm',
               'instruments': 'instrument', 'devices': 'device', 'maps': 'map',
               'prototypes': 'prototype', 'methods': 'method'}
    return {plurals.get(w, w) for w in re.findall(r'[a-z][a-z0-9-]{2,}', text.lower()) if w not in STOP}


@dataclass(frozen=True)
class Passage:
    document_id: str
    page: int
    text: str

    def reference(self):
        return {'document_id': self.document_id, 'page': self.page, 'supporting_span': self.text}


def extract_passages(case, context, settings):
    """Return (passages, complete). Caps are deliberately not silent truncation."""
    from pypdf import PdfReader

    passages = []
    max_chars = min(int(settings.get('max_page_chars', 60000)), 120000)
    max_passages = min(int(settings.get('max_passages', 6000)), 12000)
    for document in case['documents']:
        if context.remaining_ms() < 3000:
            return passages, False
        # Close the underlying file explicitly; do not retain the PDF after this document.
        with open(document['path'], 'rb') as stream:
            reader = PdfReader(stream, strict=False)
            for page_number, page in enumerate(reader.pages, 1):
                if context.remaining_ms() < 3000 or page_number > document['page_count']:
                    return passages, False
                text = re.sub(r'\s+', ' ', page.extract_text() or '').strip()
                if len(text) > max_chars:
                    return passages, False
                if not text:
                    resources = page.get('/Resources', {})
                    if hasattr(resources, 'get_object'):
                        resources = resources.get_object()
                    objects = resources.get('/XObject', {})
                    if hasattr(objects, 'get_object'):
                        objects = objects.get_object()
                    if any(obj.get_object().get('/Subtype') == '/Image' for obj in objects.values()):
                        return passages, False
                    continue
                # Three sentences retain target -> method -> numerical result context.
                boundaries = [m.end() for m in re.finditer(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)]
                starts = [0] + boundaries
                ends = boundaries + [len(text)]
                for i, start in enumerate(starts):
                    end = ends[min(i + 2, len(ends) - 1)]
                    # Very long sentence/table blocks are split into overlapping excerpts.
                    for offset in range(start, end, 650):
                        span = text[offset:min(offset + 900, end)].strip()
                        if len(span) >= 15:
                            passages.append(Passage(document['document_id'], page_number, span))
                        if len(passages) >= max_passages:
                            return passages, False
    return passages, True


class Retriever:
    """Small BM25-style ranking; similarity never directly sets a criterion status."""
    def __init__(self, passages):
        self.passages = passages
        self.words = [tokens(p.text) for p in passages]
        self.df = Counter(w for words in self.words for w in words)

    def search(self, query, target, limit=64):
        query_words = tokens(query)
        target_words = tokens(target)
        if not target_words:
            return []
        ranked = []
        for passage, words in zip(self.passages, self.words):
            # Target grounding is checked before semantic or lexical ranking.
            overlap = len(words & target_words)
            required = min(2, len(target_words))
            if overlap < required:
                continue
            score = sum(math.log(1 + (len(self.passages) + 1) / (self.df[w] + 1))
                        for w in words & query_words)
            score += 2 * overlap / math.sqrt(max(1, len(words)))
            ranked.append((score, passage))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [p for _, p in ranked[:limit]]


def target_scoped_text(text, target):
    """Use only target-bearing sentences and immediate anaphoric result sentences.

    The full excerpt remains the quotation; an adjacent named technology cannot
    contribute predicates to the target's evidence rule.
    """
    target_words = tokens(target)
    needed = min(2, len(target_words))
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)
    accepted = []
    anchored = False
    for sentence in sentences:
        if target_words and len(tokens(sentence) & target_words) >= needed:
            accepted.append(sentence)
            anchored = True
        elif (anchored
              and not re.search(r'\bmodel of\b|\b(?:of|for)\s+(?:the\s+)?\w+\s+model\b', sentence, re.I)
              and re.match(r'^(Measurements\b|Measured\b|Results\b|The results\b|The (calibrated )?model\b|The (root.mean.square error|RMSE|NRMSE|NSE|R2|error)\b|It\b|This (test|prototype|sensor|system|model)\b|These (tests|results|measurements)\b)', sentence)):
            accepted.append(sentence)
        else:
            anchored = False
    return ' '.join(accepted)
