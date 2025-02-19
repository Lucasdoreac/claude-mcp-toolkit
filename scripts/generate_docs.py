#!/usr/bin/env python3
"""
Script para gerar documentação automática do projeto.
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess
import shutil
import re
from typing import List, Dict

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate project documentation')
    parser.add_argument('--source', '-s', default='src',
                      help='Source directory to generate docs from')
    parser.add_argument('--output', '-o', default='docs',
                      help='Output directory for documentation')
    parser.add_argument('--format', '-f', default='markdown',
                      choices=['markdown', 'rst'],
                      help='Documentation format')
    return parser.parse_args()

def extract_docstrings(source_dir: Path) -> Dict[str, str]:
    """Extract docstrings from Python files."""
    docstrings = {}
    for py_file in source_dir.rglob('*.py'):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extrair docstrings usando regex
        matches = re.finditer(r'"""(.*?)"""', content, re.DOTALL)
        if matches:
            docstrings[py_file.relative_to(source_dir)] = [
                m.group(1).strip() for m in matches
            ]
    
    return docstrings

def generate_markdown_docs(docstrings: Dict[str, str], output_dir: Path):
    """Generate Markdown documentation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Gerar index.md
    with open(output_dir / 'index.md', 'w', encoding='utf-8') as f:
        f.write('# API Documentation\n\n')
        for file_path in sorted(docstrings.keys()):
            f.write(f'- [{file_path}]({file_path}.md)\n')
    
    # Gerar páginas individuais
    for file_path, docs in docstrings.items():
        doc_path = output_dir / f'{file_path}.md'
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(f'# {file_path}\n\n')
            for doc in docs:
                f.write(f'{doc}\n\n')

def generate_rst_docs(docstrings: Dict[str, str], output_dir: Path):
    """Generate reStructuredText documentation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Gerar index.rst
    with open(output_dir / 'index.rst', 'w', encoding='utf-8') as f:
        f.write('API Documentation\n')
        f.write('================\n\n')
        f.write('.. toctree::\n')
        f.write('   :maxdepth: 2\n\n')
        for file_path in sorted(docstrings.keys()):
            f.write(f'   {file_path}\n')
    
    # Gerar páginas individuais
    for file_path, docs in docstrings.items():
        doc_path = output_dir / f'{file_path}.rst'
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(f'{file_path}\n')
            f.write('=' * len(str(file_path)) + '\n\n')
            for doc in docs:
                f.write(f'{doc}\n\n')

def build_sphinx_docs(output_dir: Path):
    """Build Sphinx documentation if available."""
    if (output_dir / 'conf.py').exists():
        try:
            subprocess.run(['sphinx-build', '-b', 'html', 
                          str(output_dir), str(output_dir / '_build')],
                         check=True)
            print('Sphinx documentation built successfully')
        except subprocess.CalledProcessError as e:
            print(f'Error building Sphinx docs: {e}')

def main():
    """Main function."""
    args = parse_args()
    
    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f'Source directory {source_dir} not found!')
        sys.exit(1)
    
    output_dir = Path(args.output)
    
    # Extrair docstrings
    print('Extracting docstrings...')
    docstrings = extract_docstrings(source_dir)
    
    # Gerar documentação
    print(f'Generating {args.format} documentation...')
    if args.format == 'markdown':
        generate_markdown_docs(docstrings, output_dir)
    else:
        generate_rst_docs(docstrings, output_dir)
        build_sphinx_docs(output_dir)
    
    print(f'Documentation generated in {output_dir}')

if __name__ == '__main__':
    main()