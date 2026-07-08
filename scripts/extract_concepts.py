#!/usr/bin/env python3
"""
extract_concepts.py — Phase 1 codebase triage tool.

Walks a codebase directory, performs lightweight static analysis on each
source file, and emits a JSON inventory of candidate concepts that might
warrant IP analysis.

This is a TRIAGE tool, not a judge. The downstream LLM reads the output,
selects the top 5 candidates, then reads those source files directly to
confirm the descriptions are accurate.

Usage:
    python extract_concepts.py <path-to-codebase> [--output <path>] [--max-files 5000]

Output:
    JSON file (default stdout) with structure:
    {
      "codebase_root": "/abs/path",
      "languages": {"python": 23, "javascript": 41, ...},
      "total_files_scanned": 412,
      "candidates": [
        {
          "name": "short identifier",
          "location": "relative/path.py:line",
          "category": "algorithm|data_structure|protocol|optimization|integration|...",
          "complexity_score": 0-100,
          "dependency_count": int,
          "description": "1-2 sentence auto-generated description",
          "signal_keywords": ["keyword1", "keyword2"]
        },
        ...
      ]
    }

The complexity_score is a heuristic combining:
- Cyclomatic complexity (estimated from branch/loop density)
- Function length (longer = more complex, up to a cap)
- Comment-to-code ratio (well-commented complex functions score higher)
- Dependency count (more internal deps = more central)

Higher complexity_score does NOT mean more novel — it means more worth
looking at. The LLM makes the novelty judgment in Phase 3.
"""

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


# ---------- Language detection ----------

LANGUAGE_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript', '.mjs': 'javascript', '.cjs': 'javascript',
    '.jsx': 'javascript', '.tsx': 'typescript', '.ts': 'typescript',
    '.go': 'go',
    '.rs': 'rust',
    '.java': 'java', '.kt': 'kotlin', '.scala': 'scala',
    '.c': 'c', '.h': 'c', '.cpp': 'cpp', '.cc': 'cpp', '.hpp': 'cpp',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.m': 'objc',
    '.cs': 'csharp',
    '.sh': 'shell', '.bash': 'shell',
    '.sql': 'sql',
}

# Directories to skip during walk
SKIP_DIRS = {
    'node_modules', '.git', '.svn', '.hg', 'venv', '.venv', 'env',
    '__pycache__', '.pytest_cache', 'dist', 'build', 'target',
    '.next', '.nuxt', '.idea', '.vscode', 'coverage',
    '.gradle', '.mvn', '.terraform', 'vendor',
}

# Signal keywords — when these appear in function/class names or comments,
# the candidate is more likely to be a novel mechanism worth analyzing.
SIGNAL_KEYWORDS = {
    'algorithm': ['algorithm', 'optimize', 'optimization', 'heuristic', 'solver',
                  'scheduler', 'consensus', 'routing', 'partition', 'sharding'],
    'data_structure': ['tree', 'graph', 'queue', 'heap', 'index', 'cache',
                       'bloom', 'merkle', 'trie', 'skiplist'],
    'protocol': ['protocol', 'handshake', 'negotiation', 'rpc', 'gossip',
                 'broadcast', 'paxos', 'raft', 'quorum'],
    'cryptography': ['encrypt', 'decrypt', 'sign', 'verify', 'hash', 'mac',
                     'zkp', 'zero_knowledge', 'commitment', 'secret_share'],
    'optimization': ['memoize', 'cache', 'prefetch', 'lazy', 'batch',
                     'pipeline', 'vectorize', 'parallelize', 'async'],
    'ml': ['train', 'infer', 'embed', 'attention', 'transformer', 'tokenize',
           'fine_tune', 'distill', 'quantize', 'prune'],
    'security': ['auth', 'authenticate', 'authorize', 'sandbox', 'isolate',
                 'verify', 'attest', 'audit', 'redact'],
    'integration': ['adapter', 'bridge', 'connector', 'sync', 'replicate',
                    'mirror', 'federate'],
}


def detect_language(file_path: Path) -> Optional[str]:
    return LANGUAGE_EXTENSIONS.get(file_path.suffix.lower())


def should_skip_dir(dir_name: str) -> bool:
    return dir_name in SKIP_DIRS or dir_name.startswith('.')


# ---------- Python analyzer ----------

def analyze_python(file_path: Path, source: str) -> List[Dict]:
    """Parse Python source and extract candidate functions/classes."""
    candidates = []
    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return candidates

    # Build a dependency map (function/class names defined in this file)
    defined_names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined_names.add(node.name)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            candidate = analyze_python_function(node, file_path, source, defined_names)
            if candidate:
                candidates.append(candidate)
        elif isinstance(node, ast.ClassDef):
            candidate = analyze_python_class(node, file_path, source, defined_names)
            if candidate:
                candidates.append(candidate)
    return candidates


def analyze_python_function(node, file_path: Path, source: str, defined_names: set) -> Optional[Dict]:
    """Analyze a Python function for novelty-signal value."""
    name = node.name
    # Skip dunder methods and obvious utility functions
    if name.startswith('__') and name.endswith('__'):
        if name not in ('__init__', '__call__', '__enter__', '__exit__'):
            return None
    if name in ('main', 'run', 'test_', 'setUp', 'tearDown'):
        return None
    if name.startswith('test_'):
        return None

    # Compute metrics
    complexity = compute_python_complexity(node)
    length = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
    deps = extract_python_dependencies(node, defined_names)
    signals = detect_signals(name + ' ' + get_python_docstring(node))
    category = classify_category(signals)

    if not signals and complexity < 8 and length < 30:
        return None  # boring function, skip

    complexity_score = min(100, complexity * 3 + length // 2 + len(deps) * 2)

    return {
        'name': name,
        'location': f"{file_path}:{node.lineno}",
        'category': category or 'general',
        'complexity_score': complexity_score,
        'dependency_count': len(deps),
        'description': generate_python_description(node, signals),
        'signal_keywords': signals,
        'language': 'python',
        'metrics': {
            'cyclomatic_complexity': complexity,
            'line_count': length,
            'dependencies': list(deps)[:10],
        }
    }


def analyze_python_class(node, file_path: Path, source: str, defined_names: set) -> Optional[Dict]:
    """Analyze a Python class."""
    name = node.name
    if name in ('TestCase', 'Test', 'Mock', 'Fake'):
        return None

    # Count methods and total complexity
    method_count = 0
    total_complexity = 0
    method_names = []
    for child in ast.walk(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            method_count += 1
            total_complexity += compute_python_complexity(child)
            method_names.append(child.name)

    signals = detect_signals(name + ' ' + get_python_docstring(node) + ' ' + ' '.join(method_names))
    if not signals and method_count < 3:
        return None

    category = classify_category(signals)
    complexity_score = min(100, total_complexity * 2 + method_count * 3)

    return {
        'name': name,
        'location': f"{file_path}:{node.lineno}",
        'category': category or 'general',
        'complexity_score': complexity_score,
        'dependency_count': method_count,
        'description': f"Class with {method_count} methods. Signals: {', '.join(signals) if signals else 'none'}.",
        'signal_keywords': signals,
        'language': 'python',
        'metrics': {
            'method_count': method_count,
            'total_complexity': total_complexity,
            'methods': method_names[:10],
        }
    }


def compute_python_complexity(node) -> int:
    """Estimate cyclomatic complexity."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                              ast.ExceptHandler, ast.With, ast.AsyncWith)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            complexity += 1
    return complexity


def extract_python_dependencies(node, defined_names: set) -> set:
    """Extract names of internal functions/classes this node calls."""
    deps = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            if child.func.id in defined_names and child.func.id != getattr(node, 'name', ''):
                deps.add(child.func.id)
        elif isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            if child.func.attr in defined_names:
                deps.add(child.func.attr)
    return deps


def get_python_docstring(node) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
        if (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
    return ''


def generate_python_description(node, signals: List[str]) -> str:
    """Generate a brief description from name + docstring + signals."""
    doc = get_python_docstring(node).strip()
    if doc:
        # First sentence only
        first_sentence = re.split(r'[.!\n]', doc, 1)[0].strip()
        if first_sentence:
            return first_sentence[:200]
    name = node.name.replace('_', ' ')
    if signals:
        return f"Function involving {', '.join(signals)}. (Auto-generated; LLM must read source to confirm.)"
    return f"Function '{name}'. (Auto-generated; LLM must read source to confirm.)"


# ---------- Generic text-based analyzer (for non-Python files) ----------

def analyze_text_source(file_path: Path, source: str, language: str) -> List[Dict]:
    """For languages we don't have AST parsers for, use regex-based heuristics."""
    candidates = []
    lines = source.splitlines()

    # Function/class detection patterns by language
    patterns = {
        'javascript': [
            r'(?:export\s+)?(?:async\s+)?function\s+(\w+)',
            r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(',
            r'class\s+(\w+)',
        ],
        'typescript': [
            r'(?:export\s+)?(?:async\s+)?function\s+(\w+)',
            r'(?:export\s+)?(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?\(',
            r'class\s+(\w+)',
            r'(?:export\s+)?(?:abstract\s+)?class\s+(\w+)',
        ],
        'go': [
            r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(',
            r'type\s+(\w+)\s+struct',
            r'type\s+(\w+)\s+interface',
        ],
        'rust': [
            r'(?:pub\s+)?fn\s+(\w+)',
            r'(?:pub\s+)?struct\s+(\w+)',
            r'(?:pub\s+)?enum\s+(\w+)',
            r'(?:pub\s+)?trait\s+(\w+)',
        ],
        'java': [
            r'(?:public|private|protected|static|\s)+\s+(\w+)\s*\([^)]*\)\s*(?:throws[^{]*)?\{',
            r'(?:public|private|protected|\s)+\s+class\s+(\w+)',
            r'(?:public|private|protected|\s)+\s+interface\s+(\w+)',
        ],
        'c': [r'(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*\{'],
        'cpp': [
            r'(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*(?:const)?\s*\{',
            r'(?:class|struct)\s+(\w+)',
        ],
        'ruby': [r'def\s+(\w+)', r'class\s+(\w+)', r'module\s+(\w+)'],
        'php': [r'function\s+(\w+)', r'class\s+(\w+)'],
    }

    lang_patterns = patterns.get(language, [])
    if not lang_patterns:
        return candidates

    # Find all matches with line numbers
    matches = []
    for pattern in lang_patterns:
        for i, line in enumerate(lines, 1):
            for m in re.finditer(pattern, line):
                name = m.group(1)
                if name and not name.startswith('test_') and name not in ('main', 'run', 'if', 'for', 'while', 'switch'):
                    matches.append((name, i, line.strip()[:200]))

    # Deduplicate by name (keep first occurrence)
    seen = set()
    for name, line_no, line_text in matches:
        if name in seen:
            continue
        seen.add(name)

        # Compute local complexity (next 50 lines)
        end_line = min(len(lines), line_no + 49)
        body = '\n'.join(lines[line_no-1:end_line])
        complexity = sum(body.count(kw) for kw in ['if ', 'for ', 'while ', 'case ', 'catch ', '&&', '||'])
        length = end_line - line_no + 1

        signals = detect_signals(name + ' ' + body[:500])
        if not signals and complexity < 3 and length < 20:
            continue

        category = classify_category(signals)
        complexity_score = min(100, complexity * 4 + length // 3)

        candidates.append({
            'name': name,
            'location': f"{file_path}:{line_no}",
            'category': category or 'general',
            'complexity_score': complexity_score,
            'dependency_count': 0,  # not computed for text-based analysis
            'description': f"{language} {name}. Signals: {', '.join(signals) if signals else 'none'}. (Auto-generated; LLM must read source to confirm.)",
            'signal_keywords': signals,
            'language': language,
            'metrics': {
                'estimated_complexity': complexity,
                'line_count': length,
            }
        })

    return candidates


# ---------- Signal detection ----------

def detect_signals(text: str) -> List[str]:
    """Detect signal keywords in text. Returns list of categories."""
    text_lower = text.lower()
    found = []
    for category, keywords in SIGNAL_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                if category not in found:
                    found.append(category)
                break
    return found


def classify_category(signals: List[str]) -> Optional[str]:
    """Map signal categories to a single primary category."""
    if not signals:
        return None
    priority = ['cryptography', 'ml', 'protocol', 'algorithm', 'data_structure',
                'optimization', 'security', 'integration']
    for cat in priority:
        if cat in signals:
            return cat
    return 'general'


# ---------- Main ----------

def walk_codebase(root: Path, max_files: int = 5000) -> Tuple[List[Dict], Dict[str, int]]:
    """Walk the codebase, analyze each source file, return candidates + language counts."""
    candidates = []
    lang_counts = defaultdict(int)
    files_scanned = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter out skip directories in-place
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

        for filename in filenames:
            if files_scanned >= max_files:
                print(f"WARNING: hit max_files={max_files}, stopping early", file=sys.stderr)
                return candidates, dict(lang_counts)

            file_path = Path(dirpath) / filename
            language = detect_language(file_path)
            if not language:
                continue

            lang_counts[language] += 1
            files_scanned += 1

            try:
                source = file_path.read_text(encoding='utf-8', errors='ignore')
            except Exception as e:
                print(f"WARNING: could not read {file_path}: {e}", file=sys.stderr)
                continue

            if language == 'python':
                file_candidates = analyze_python(file_path, source)
            else:
                file_candidates = analyze_text_source(file_path, source, language)

            candidates.extend(file_candidates)

    return candidates, dict(lang_counts)


def rank_and_filter(candidates: List[Dict], top_n: int = 30) -> List[Dict]:
    """Rank candidates by complexity_score + signal count, return top N."""
    def score(c):
        signal_bonus = len(c.get('signal_keywords', [])) * 10
        return c.get('complexity_score', 0) + signal_bonus

    return sorted(candidates, key=score, reverse=True)[:top_n]


def main():
    parser = argparse.ArgumentParser(description='Extract candidate concepts from a codebase.')
    parser.add_argument('path', help='Path to codebase root directory')
    parser.add_argument('--output', '-o', help='Output JSON file path (default: stdout)')
    parser.add_argument('--max-files', type=int, default=5000, help='Maximum number of files to scan')
    parser.add_argument('--top', type=int, default=30, help='Number of top candidates to keep')
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists() or not root.is_dir():
        print(f"ERROR: {root} does not exist or is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning codebase at {root}...", file=sys.stderr)
    candidates, lang_counts = walk_codebase(root, max_files=args.max_files)
    print(f"Scanned {sum(lang_counts.values())} files, found {len(candidates)} raw candidates",
          file=sys.stderr)

    top_candidates = rank_and_filter(candidates, top_n=args.top)

    output = {
        'codebase_root': str(root),
        'languages': lang_counts,
        'total_files_scanned': sum(lang_counts.values()),
        'candidates': top_candidates,
    }

    output_json = json.dumps(output, indent=2)
    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Wrote {len(top_candidates)} candidates to {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == '__main__':
    main()
