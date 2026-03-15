"""
LaTeX source file parser for astronomical papers.

Extracts structured content from LaTeX source files, preserving math notation
and expanding custom commands.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pylatexenc
from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode

from .bbl_parser import parse_bbl
from .models import Author, ExtractionInfo, ExtractedPaper, Reference, Section

logger = logging.getLogger(__name__)


def extract_from_latex(tex_path: Path, arxiv_id: str) -> ExtractedPaper:
    """
    Extract structured content from a LaTeX source file.

    Args:
        tex_path: Path to main .tex file
        arxiv_id: arXiv paper identifier

    Returns:
        ExtractedPaper with all parsed content

    Raises:
        FileNotFoundError: If .tex file does not exist
        OSError: If file cannot be read
    """
    # AI NOTE: This function parses the main .tex file and associated .bbl file.
    # It extracts title, authors, abstract, sections, and references. Custom
    # commands from the preamble are expanded in body text.

    tex_path = Path(tex_path)

    if not tex_path.exists():
        raise FileNotFoundError(f".tex file not found: {tex_path}")

    logger.info(f"Extracting from LaTeX file: {tex_path}")

    # Read LaTeX file
    try:
        with open(tex_path, "r", encoding="utf-8", errors="strict") as f:
            tex_content = f.read()
    except UnicodeDecodeError as e:
        logger.warning(f"Encoding issue in {tex_path}: {e}")
        with open(tex_path, "r", encoding="utf-8", errors="replace") as f:
            tex_content = f.read()

    # Parse LaTeX using pylatexenc
    walker = LatexWalker(tex_content)
    nodes, pos, _ = walker.get_latex_nodes()

    # Initialize extraction info
    extraction_info = ExtractionInfo(
        method="latex",
        source_file=str(tex_path),
        timestamp=datetime.now(timezone.utc).isoformat(),
        warnings=[],
        pylatexenc_version=pylatexenc.__version__,
    )

    # Extract custom commands from preamble
    custom_commands = _extract_custom_commands(tex_content)
    logger.info(f"Found {len(custom_commands)} custom commands")

    # Extract metadata
    title = _extract_title(tex_content)
    authors = _extract_authors(tex_content)
    abstract = _extract_abstract(tex_content, custom_commands)

    # Expand custom commands in abstract, then strip residual \xspace
    # AI NOTE: _clean_section_content strips \xspace, but _expand_custom_commands
    # may reintroduce it from command definitions (e.g., \hMpc -> Mpc h$^{-1}$\xspace).
    # The strip here catches any \xspace introduced by expansion.
    abstract = _expand_custom_commands(abstract, custom_commands, extraction_info)
    abstract = abstract.replace("\\xspace", "")

    # Extract sections
    sections = _extract_sections(tex_content, custom_commands, extraction_info)
    logger.info(f"Extracted {len(sections)} sections")

    # Parse references from .bbl file if it exists
    bbl_path = tex_path.with_suffix(".bbl")
    references: Dict[str, Reference] = {}
    if bbl_path.exists():
        references = parse_bbl(bbl_path)
        logger.info(f"Loaded {len(references)} references from .bbl file")
    else:
        logger.warning(f".bbl file not found: {bbl_path}")
        extraction_info.warnings.append(f".bbl file not found: {bbl_path}")

    return ExtractedPaper(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors,
        abstract=abstract,
        custom_commands=custom_commands,
        sections=sections,
        references=references,
        extraction_info=extraction_info,
    )


def _extract_custom_commands(tex_content: str) -> Dict[str, str]:
    """
    Extract custom command definitions from LaTeX preamble.

    Uses brace-balanced matching to correctly handle definitions containing
    nested braces, e.g., ``\\newcommand{\\hMpc}{Mpc h$^{-1}$\\xspace}``.

    Args:
        tex_content: Full LaTeX source

    Returns:
        Dictionary mapping command names to their expansions
    """
    # AI NOTE: The previous regex-based approach used [^}]* which broke on
    # nested braces (e.g., $^{-1}$ inside a definition). This brace-balanced
    # approach handles arbitrary nesting depth. It does not skip LaTeX comments,
    # so a % } in a definition could truncate early — acceptable for well-formed
    # papers but noted as a known limitation.
    custom_commands: Dict[str, str] = {}

    # Find \newcommand{\name} or \newcommand{\name}[n] patterns, then
    # extract the balanced-brace definition that follows
    for match in re.finditer(r"\\newcommand\{\\(\w+)\}(?:\[\d+\])?", tex_content):
        cmd_name = match.group(1)
        start = match.end()

        if start < len(tex_content) and tex_content[start] == "{":
            depth = 0
            for i in range(start, len(tex_content)):
                if tex_content[i] == "{":
                    depth += 1
                elif tex_content[i] == "}":
                    depth -= 1
                    if depth == 0:
                        definition = tex_content[start + 1:i].strip()
                        custom_commands[cmd_name] = definition
                        break

    return custom_commands


def _expand_custom_commands(
    text: str, custom_commands: Dict[str, str], extraction_info: ExtractionInfo
) -> str:
    """
    Expand custom commands in text.

    Args:
        text: Text with potential custom commands
        custom_commands: Mapping of command names to expansions
        extraction_info: Extraction info for warning logging

    Returns:
        Text with custom commands expanded
    """
    # AI NOTE: Custom commands are expanded recursively to handle nested definitions.
    # This is a simple approach - complex arguments are not fully supported.

    if not custom_commands:
        return text

    result = text
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        previous = result
        for cmd_name, cmd_expansion in custom_commands.items():
            # Match \cmdname with optional arguments
            pattern = re.compile(rf"\\{re.escape(cmd_name)}(?:\[[^\]]*\])?")
            result = pattern.sub(lambda m: cmd_expansion, result)

        if result == previous:
            break
        iteration += 1

    return result


def _extract_title(tex_content: str) -> str:
    """
    Extract paper title from LaTeX source.

    Args:
        tex_content: Full LaTeX source

    Returns:
        Paper title
    """
    # Match \title{...}
    title_match = re.search(
        r"\\title\{([^}]*(?:\{[^}]*\}[^}]*)*)\}", tex_content, re.DOTALL
    )

    if title_match:
        title = title_match.group(1).strip()
        # Remove LaTeX formatting commands from title
        title = _strip_latex_commands(title)
        return title

    return ""


def _extract_authors(tex_content: str) -> List[Author]:
    """
    Extract authors from LaTeX source.

    Args:
        tex_content: Full LaTeX source

    Returns:
        List of Author objects
    """
    authors: List[Author] = []

    # Match \author[orcid]{name}\email{email} or \author[orcid]{name}
    # Pattern captures: optional ORCID, author name, optional email
    author_pattern = re.compile(
        r"\\author(?:\[([^\]]+)\])?\{([^}]+)\}(?:\\email\{([^}]+)\})?", re.DOTALL
    )

    for match in author_pattern.finditer(tex_content):
        orcid = match.group(1)
        name = match.group(2).strip()
        email = match.group(3)

        # Clean up name (remove LaTeX commands)
        name = _strip_latex_commands(name)

        authors.append(
            Author(
                name=name,
                orcid=orcid,
                affiliations=[],
                email=email,
            )
        )

    # Extract affiliations separately
    # \affiliation{...}
    affiliation_pattern = re.compile(r"\\affiliation\{([^}]*)\}", re.DOTALL)

    affiliations = [aff.strip() for aff in affiliation_pattern.findall(tex_content)]

    # Assign affiliations to authors (simple 1:1 mapping)
    for i, author in enumerate(authors):
        if i < len(affiliations):
            author.affiliations = [_strip_latex_commands(affiliations[i])]

    return authors


def _extract_abstract(tex_content: str, custom_commands: Dict[str, str]) -> str:
    """
    Extract abstract from LaTeX source.

    Args:
        tex_content: Full LaTeX source
        custom_commands: Custom commands to expand during cleaning

    Returns:
        Abstract text
    """
    # Match \begin{abstract}...\end{abstract}
    abstract_match = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex_content, re.DOTALL
    )

    if abstract_match:
        abstract = abstract_match.group(1).strip()
        abstract = _clean_section_content(abstract, custom_commands)
        return abstract

    return ""


def _extract_sections(
    tex_content: str, custom_commands: Dict[str, str], extraction_info: ExtractionInfo
) -> List[Section]:
    """
    Extract sections from LaTeX document body.

    Args:
        tex_content: Full LaTeX source
        custom_commands: Custom commands to expand
        extraction_info: Extraction info for warning logging

    Returns:
        List of Section objects
    """
    sections: List[Section] = []

    # Find the document body (between \begin{document} and \end{document})
    doc_match = re.search(
        r"\\begin\{document\}(.*?)\\end\{document\}", tex_content, re.DOTALL
    )

    if not doc_match:
        logger.warning("Could not find document body in LaTeX source")
        extraction_info.warnings.append("Could not find document body")
        return sections

    body = doc_match.group(1)

    # Track section hierarchy
    section_stack: List[Dict[str, Any]] = []

    # Pattern for sections: \section, \subsection, \subsubsection
    section_patterns = [
        (r"\\section\*?\{([^}]*)\}", 1),
        (r"\\subsection\*?\{([^}]*)\}", 2),
        (r"\\subsubsection\*?\{([^}]*)\}", 3),
    ]

    # Find all section starts with their positions
    section_matches = []
    for pattern, level in section_patterns:
        for match in re.finditer(pattern, body):
            section_matches.append((match.start(), level, match.group(1)))

    # Sort by position
    section_matches.sort(key=lambda x: x[0])

    # Extract content between sections
    for i, (pos, level, title) in enumerate(section_matches):
        # Determine content end (next section start or end of document)
        if i + 1 < len(section_matches):
            end_pos = section_matches[i + 1][0]
        else:
            end_pos = len(body)

        content = body[pos:end_pos]

        # Extract section label if present
        label_match = re.search(r"\\label\{([^}]*)\}", content)
        label = label_match.group(1) if label_match else None

        # Clean content
        clean_content = _clean_section_content(content, custom_commands)

        # Build section path
        path = title.strip()
        current_stack = section_stack.copy()

        # Update section stack based on level
        while section_stack and section_stack[-1]["level"] >= level:
            section_stack.pop()

        if section_stack:
            path = section_stack[-1]["path"] + " > " + path

        section_stack.append({"level": level, "path": path})

        sections.append(
            Section(
                title=title.strip(),
                path=path,
                level=level,
                content=clean_content,
                label=label,
            )
        )

    return sections


def _clean_section_content(content: str, custom_commands: Dict[str, str]) -> str:
    """
    Clean and normalize section content.

    Args:
        content: Raw section content
        custom_commands: Custom commands to expand

    Returns:
        Cleaned content with math preserved, formatting stripped
    """
    # Remove section header line
    content = re.sub(r"\\section\*?\{[^}]*\}", "", content)
    content = re.sub(r"\\subsection\*?\{[^}]*\}", "", content)
    content = re.sub(r"\\subsubsection\*?\{[^}]*\}", "", content)

    # Remove figure and table environments
    content = re.sub(
        r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", "", content, flags=re.DOTALL
    )
    content = re.sub(
        r"\\begin\{table\*?\}.*?\\end\{table\*?\}", "", content, flags=re.DOTALL
    )
    content = re.sub(
        r"\\begin\{figure\}.*?\\end\{figure\}", "", content, flags=re.DOTALL
    )
    content = re.sub(r"\\begin\{table\}.*?\\end\{table\}", "", content, flags=re.DOTALL)

    # Remove \label commands
    content = re.sub(r"\\label\{[^}]*\}", "", content)

    # Remove \cite, \citep, \citet commands but keep the citation keys
    content = re.sub(r"\\citep?\{([^}]*)\}", r"[\1]", content)
    content = re.sub(r"\\citet?\{([^}]*)\}", r"[\1]", content)

    # Preserve math notation - protect math environments
    # AI NOTE: Order matters here. Display math ($$...$$) must be protected
    # BEFORE inline math ($...$), otherwise the inline regex matches the inner
    # content of $$...$$ first, stripping the outer delimiters.
    math_preservations: List[str] = []

    def protect_math(match: re.Match) -> str:
        math_preservations.append(match.group(0))
        return f"__MATH_{len(math_preservations) - 1}__"

    # Protect display math first (greedy patterns before narrow ones)
    content = re.sub(r"\$\$[^$]+\$\$", protect_math, content)
    content = re.sub(r"\\\[.*?\\\]", protect_math, content, flags=re.DOTALL)
    content = re.sub(
        r"\\begin\{equation\}.*?\\end\{equation\}",
        protect_math,
        content,
        flags=re.DOTALL,
    )

    # Then protect inline math
    # AI NOTE: \(...\) uses .*? not [^)]* so that expressions containing
    # literal ) like \(f(x)\) are matched correctly up to the \) delimiter.
    content = re.sub(r"\$[^$]+\$", protect_math, content)
    content = re.sub(r"\\\(.*?\\\)", protect_math, content)

    # Strip formatting commands but keep content
    formatting_commands = [r"\\textbf", r"\\emph", r"\\textit", r"\\underline"]
    for cmd in formatting_commands:
        content = re.sub(rf"{cmd}\s*\{{([^}}]*)\}}", r"\1", content)

    # Expand custom commands
    if custom_commands:
        for cmd_name, cmd_expansion in custom_commands.items():
            content = content.replace(f"\\{cmd_name}", cmd_expansion)

    # Strip \xspace (LaTeX conditional whitespace, meaningless in plain text)
    content = content.replace("\\xspace", "")

    # Restore math notation
    for i, math_text in enumerate(math_preservations):
        content = content.replace(f"__MATH_{i}__", math_text)

    # Clean up whitespace
    content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)
    content = content.strip()

    return content


def _strip_latex_commands(text: str) -> str:
    """
    Strip LaTeX formatting commands from text.

    Args:
        text: Text with LaTeX commands

    Returns:
        Plain text without formatting commands
    """
    # Remove common formatting commands
    text = re.sub(r"\\textbf\s*\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textit\s*\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\emph\s*\{([^}]*)\}", r"\1", text)

    # Remove special characters
    text = text.replace("~", " ")
    text = text.replace("\\&", "&")
    text = text.replace("\\%", "%")
    text = text.replace("\\$", "$")
    text = text.replace("\\#", "#")
    text = text.replace("\\_", "_")

    # Clean up
    text = text.strip()

    return text
