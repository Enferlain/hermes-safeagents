"""Fixed trusted decision-model choices. Importing performs no I/O."""
import os
import re
from pathlib import Path

# Single source of truth for the decision-model directory (Windows-native path).
# Relocating the weights changes this default (or sets SAFEAGENTS_DECISION_DIR).
DECISION_DIR = os.environ.get('SAFEAGENTS_DECISION_DIR', 'D:/AI-Models/llm/decision')


def model_path(filename):
    """Windows-native path of a decision-model file."""
    return DECISION_DIR + '/' + filename


def wsl_path(filename):
    """WSL-side path of a decision-model file, for local hashing."""
    native = model_path(filename)
    wsl = '/mnt/d/' + native[3:] if native.startswith('D:/') else native
    return Path(wsl)


MODEL_SPECS = {
    'lite': {'id': 'lite', 'label': 'D3 Lite', 'filename': 'vllm-d3-lite-Q8_0.gguf',
             'model_path': model_path('vllm-d3-lite-Q8_0.gguf')},
    'qev': {'id': 'qev', 'label': 'QEV', 'filename': 'qev-0.8b-text-Q8_0.gguf',
            'model_path': model_path('qev-0.8b-text-Q8_0.gguf')},
}


def get_model(key):
    if not isinstance(key, str) or key not in MODEL_SPECS:
        raise ValueError('unknown decision model')
    return dict(MODEL_SPECS[key])


def model_identity(provenance):
    """Return only allowlisted metadata; aliases and basenames prove nothing."""
    provenance = provenance if isinstance(provenance, dict) else {}
    identity = {'id': None, 'label': 'Unknown model',
                'model_file_sha256': None, 'native_template_sha256': None}
    path = provenance.get('model_path')
    if isinstance(path, str):
        normalized = path.replace('\\', '/').casefold()
        for key, spec in MODEL_SPECS.items():
            if normalized == spec['model_path'].casefold():
                identity.update(id=key, label=spec['label'])
                break
    for key in ('model_file_sha256', 'native_template_sha256'):
        value = provenance.get(key)
        if isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value):
            identity[key] = value
    return identity
