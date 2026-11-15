"""Optional catalogue-only semantic reranking. No downloads at inference."""
from pathlib import Path

CATALOG_ID = 'all-minilm-l6-v2'
REVISION = '1110a243fdf4706b3f48f1d95db1a4f5529b4d41'


class SemanticRanker:
    def __init__(self, model_store: Path):
        model_path = model_store / 'sentence-transformers' / 'all-MiniLM-L6-v2' / REVISION
        if not (model_path / 'model.safetensors').is_file():
            raise FileNotFoundError(f'Catalogue model is missing from {model_path}; download with the kit before enabling use_semantic.')
        import os
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        import torch
        from sentence_transformers import SentenceTransformer
        torch.set_num_threads(2)
        self.model = SentenceTransformer(str(model_path), device='cpu', local_files_only=True, trust_remote_code=False)
        self.model.max_seq_length = 256

    def rank(self, query, passages):
        if not passages:
            return []
        vectors = self.model.encode([query] + [p.text for p in passages], batch_size=4,
                                    normalize_embeddings=True, show_progress_bar=False)
        scores = vectors[1:] @ vectors[0]
        return [passages[i] for i in sorted(range(len(passages)), key=lambda i: float(scores[i]), reverse=True)]
