"""
analyzer.py
-----------
Reads a Python source file and reduces it to a small, deterministic
"signature": a bundle of structural numbers (functions, classes, loops,
branches, nesting depth, imports, comment density, etc).

This signature is the only thing the rest of the pipeline looks at.
It never looks at variable names or string contents (only their counts),
so the output is about the *shape* of the code, not its meaning.
"""

import ast
import hashlib
from dataclasses import dataclass, field

 
@dataclass 
class CodeSignature:
    file_name: str
    line_count: int = 0
    char_count: int = 0
    comment_ratio: float = 0.0

    function_count: int = 0
    class_count: int = 0
    loop_count: int = 0
    branch_count: int = 0
    try_count: int = 0
    import_count: int = 0
    return_count: int = 0

    max_depth: int = 0
    avg_depth: float = 0.0

    function_lengths: list = field(default_factory=list)

    # A stable hex digest of the raw source. Used downstream as a seed
    # so the same file always produces the same artwork.
    digest: str = ""

    @property
    def complexity(self) -> float:
        """A rough single-number stand-in for 'how busy' the code is."""
        return (
            self.function_count * 1.5
            + self.class_count * 2.0
            + self.loop_count * 1.2
            + self.branch_count * 1.0
            + self.try_count * 1.3
        )


class _DepthVisitor(ast.NodeVisitor):
    """Walks the AST tracking nesting depth and counting node kinds."""

    LOOP_NODES = (ast.For, ast.While, ast.AsyncFor)
    BRANCH_NODES = (ast.If, ast.IfExp)
    DEPTH_INCREASING = (
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.If,
        ast.With,
        ast.AsyncWith,
        ast.Try,
    )

    def __init__(self):
        self.depth = 0
        self.depths_seen = []
        self.function_count = 0
        self.class_count = 0
        self.loop_count = 0
        self.branch_count = 0
        self.try_count = 0
        self.import_count = 0
        self.return_count = 0
        self.function_lengths = []

    def generic_visit(self, node):
        increased = isinstance(node, self.DEPTH_INCREASING)
        if increased:
            self.depth += 1
            self.depths_seen.append(self.depth)

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.function_count += 1
            start = getattr(node, "lineno", 0)
            end = getattr(node, "end_lineno", start)
            self.function_lengths.append(max(1, end - start + 1))
        elif isinstance(node, ast.ClassDef):
            self.class_count += 1
        elif isinstance(node, self.LOOP_NODES):
            self.loop_count += 1
        elif isinstance(node, self.BRANCH_NODES):
            self.branch_count += 1
        elif isinstance(node, ast.Try):
            self.try_count += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            self.import_count += 1
        elif isinstance(node, ast.Return):
            self.return_count += 1

        super().generic_visit(node)

        if increased:
            self.depth -= 1


def analyze_source(source: str, file_name: str = "source.py") -> CodeSignature:
    """Turn raw source text into a CodeSignature."""
    lines = source.splitlines() or [""]
    comment_lines = sum(1 for ln in lines if ln.strip().startswith("#"))

    sig = CodeSignature(
        file_name=file_name,
        line_count=len(lines),
        char_count=len(source),
        comment_ratio=comment_lines / max(1, len(lines)),
        digest=hashlib.sha256(source.encode("utf-8", "ignore")).hexdigest(),
    )

    try:
        tree = ast.parse(source)
    except SyntaxError:
        # Non-Python or broken source: fall back to a text-only signature.
        # The art will be plainer, but generation never crashes.
        return sig

    visitor = _DepthVisitor()
    visitor.visit(tree)

    sig.function_count = visitor.function_count
    sig.class_count = visitor.class_count
    sig.loop_count = visitor.loop_count
    sig.branch_count = visitor.branch_count
    sig.try_count = visitor.try_count
    sig.import_count = visitor.import_count
    sig.return_count = visitor.return_count
    sig.function_lengths = visitor.function_lengths
    sig.max_depth = max(visitor.depths_seen, default=0)
    sig.avg_depth = (
        sum(visitor.depths_seen) / len(visitor.depths_seen)
        if visitor.depths_seen
        else 0.0
    )
    return sig


def analyze_file(path: str) -> CodeSignature:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()
    return analyze_source(source, file_name=path)
