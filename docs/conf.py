# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "jarvis"))

# -- Project information -----------------------------------------------------
project = 'Jarvis Enhanced System Integration'
copyright = '2025, Jarvis Development Team'
author = 'Jarvis Development Team'
release = '2.0.0'
version = '2.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
    'sphinx.ext.githubpages',
    'myst_parser',
    'sphinx_copybutton',
    'sphinx.ext.autodoc.typehints'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
source_suffix = {
    '.rst': None,
    '.md': 'myst_parser',
}

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS
html_css_files = [
    'custom.css',
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension ------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Don't show module names in front of class names
add_module_names = False

# -- Options for autosummary extension --------------------------------------
autosummary_generate = True

# -- Options for napoleon extension -----------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for intersphinx extension --------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'langchain': ('https://python.langchain.com/', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
    'pydantic': ('https://docs.pydantic.dev/', None),
}

# -- Options for todo extension ---------------------------------------------
todo_include_todos = True

# -- Options for MyST parser ------------------------------------------------
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# -- Options for copybutton extension ---------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- Custom configuration ---------------------------------------------------

# Mock imports for modules that might not be available during doc build
autodoc_mock_imports = [
    'torch',
    'transformers',
    'sentence_transformers',
    'chromadb',
    'faiss',
    'networkx',
    'sklearn',
    'tree_sitter',
    'rope',
    'jedi',
    'astroid',
    'bandit',
    'vulture',
    'radon'
]

# Custom roles and directives
def setup(app):
    """Custom Sphinx setup function."""
    app.add_css_file('custom.css')
    
    # Add custom roles
    app.add_role('jarvis-component', lambda name, rawtext, text, lineno, inliner, options={}, content=[]: 
                 ([], []))
    
    # Add custom directives for enhanced features
    from docutils.parsers.rst import directives
    from docutils import nodes
    from sphinx.util.docutils import SphinxDirective
    
    class EnhancedFeatureDirective(SphinxDirective):
        """Custom directive for documenting enhanced features."""
        
        has_content = True
        required_arguments = 1
        optional_arguments = 0
        final_argument_whitespace = True
        option_spec = {
            'status': directives.unchanged,
            'version': directives.unchanged,
            'complexity': directives.unchanged,
        }
        
        def run(self):
            feature_name = self.arguments[0]
            status = self.options.get('status', 'In Development')
            version = self.options.get('version', '2.0.0')
            complexity = self.options.get('complexity', 'Medium')
            
            # Create container
            container = nodes.container()
            container['classes'] = ['enhanced-feature']
            
            # Add title
            title = nodes.title(text=f"Enhanced Feature: {feature_name}")
            container += title
            
            # Add metadata
            metadata = nodes.paragraph()
            metadata += nodes.Text(f"Status: {status} | Version: {version} | Complexity: {complexity}")
            container += metadata
            
            # Add content
            if self.content:
                content_node = nodes.container()
                self.state.nested_parse(self.content, self.content_offset, content_node)
                container += content_node
            
            return [container]
    
    app.add_directive('enhanced-feature', EnhancedFeatureDirective)

# -- HTML theme customization -----------------------------------------------
html_title = f"{project} v{version}"
html_short_title = "Jarvis Enhanced"
html_logo = None  # Add logo path if available
html_favicon = None  # Add favicon path if available

# Custom sidebar
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'donate.html',
    ]
}

# -- LaTeX output configuration ---------------------------------------------
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'fncychap': '\\usepackage[Bjornstrup]{fncychap}',
    'printindex': '\\footnotesize\\raggedright\\printindex',
}

latex_documents = [
    (master_doc, 'JarvisEnhanced.tex', 'Jarvis Enhanced System Integration Documentation',
     'Jarvis Development Team', 'manual'),
]

# -- Manual page output configuration ---------------------------------------
man_pages = [
    (master_doc, 'jarvis-enhanced', 'Jarvis Enhanced System Integration Documentation',
     [author], 1)
]

# -- Texinfo output configuration -------------------------------------------
texinfo_documents = [
    (master_doc, 'JarvisEnhanced', 'Jarvis Enhanced System Integration Documentation',
     author, 'JarvisEnhanced', 'AI assistant with enhanced system integration capabilities.',
     'Miscellaneous'),
]

# -- Epub output configuration ----------------------------------------------
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ['search.html']

# -- Custom build configuration ---------------------------------------------
def skip_member(app, what, name, obj, skip, options):
    """Custom function to skip certain members during autodoc."""
    # Skip private methods that start with underscore (except __init__)
    if name.startswith('_') and name != '__init__':
        return True
    
    # Skip test methods
    if name.startswith('test_'):
        return True
    
    return skip

def process_docstring(app, what, name, obj, options, lines):
    """Process docstrings to add custom formatting."""
    # Add enhanced feature markers
    if hasattr(obj, '__enhanced_feature__'):
        lines.insert(0, f".. enhanced-feature:: {obj.__enhanced_feature__}")
        lines.insert(1, "")

# Connect custom functions
def setup_custom_handlers(app):
    """Set up custom event handlers."""
    app.connect('autodoc-skip-member', skip_member)
    app.connect('autodoc-process-docstring', process_docstring)

# Add to setup function
original_setup = setup
def setup(app):
    original_setup(app)
    setup_custom_handlers(app)
