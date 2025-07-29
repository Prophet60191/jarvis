"""
User Help UI

A comprehensive help interface for Jarvis documentation with search,
bookmarking, and voice command integration following the Jarvis UI template.
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget,
    QListWidgetItem, QSplitter, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QScrollArea, QFrame, QComboBox, QCheckBox, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QTextCursor, QTextCharFormat, QColor

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class DocumentationLoader(QThread):
    """Background thread for loading documentation files."""
    
    documentation_loaded = pyqtSignal(dict)
    
    def __init__(self, docs_path: Path):
        super().__init__()
        self.docs_path = docs_path
    
    def run(self):
        """Load all documentation files."""
        try:
            docs = {}
            
            # Documentation files to load
            doc_files = [
                # Essential User Guides
                ("Getting Started", "GETTING_STARTED_COMPLETE.md"),
                ("Voice Commands Reference", "VOICE_COMMANDS_REFERENCE.md"),
                ("User Guide", "USER_GUIDE.md"),
                ("User Help UI Guide", "USER_HELP_UI_GUIDE.md"),
                ("Analytics Dashboard", "ANALYTICS_DASHBOARD_USER_GUIDE.md"),
                ("Troubleshooting", "TROUBLESHOOTING_GUIDE.md"),

                # RAG & Memory System
                ("RAG Memory User Guide", "JARVIS_RAG_MEMORY_USER_GUIDE.md"),

                # Plugin User Guides
                ("Plugin Reference Guide", "PLUGIN_REFERENCE_GUIDE.md"),
                ("Device Time Tool Guide", "jarvis/docs/DEVICE_TIME_TOOL_USER_GUIDE.md"),
                ("Aider Integration Guide", "jarvis/docs/AIDER_INTEGRATION_USER_GUIDE.md"),
                ("LaVague Web Automation Guide", "jarvis/docs/LAVAGUE_WEB_AUTOMATION_USER_GUIDE.md"),
                ("Log Terminal Tools Guide", "jarvis/docs/LOG_TERMINAL_TOOLS_USER_GUIDE.md"),
                ("Open Interpreter User Guide", "jarvis/docs/OPEN_INTERPRETER_USER_GUIDE.md"),
                ("Robot Framework User Guide", "jarvis/docs/ROBOT_FRAMEWORK_USER_GUIDE.md"),

                # System & Architecture
                ("Architecture", "ARCHITECTURE.md"),
                ("System Integration", "SYSTEM_INTEGRATION_PLAN.md"),
                ("Performance Optimization", "PERFORMANCE_OPTIMIZATION_GUIDE.md"),
                ("Migration Guide", "MIGRATION_GUIDE.md"),

                # Integration Guides
                ("Open Interpreter Integration", "OPEN_INTERPRETER_INTEGRATION.md"),
                ("Open Interpreter MCP Guide", "OPEN_INTERPRETER_MCP_GUIDE.md"),

                # Reference Materials
                ("Documentation Index", "DOCUMENTATION_INDEX.md"),
                ("README", "README.md"),
                ("Web UI Guide", "jarvis/WEB_UI_GUIDE.md"),
                ("FAQ", "jarvis/docs/FAQ.md"),
                ("Installation Guide", "jarvis/docs/installation.md")
            ]
            
            for title, filename in doc_files:
                file_path = self.docs_path / filename
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        docs[title] = {
                            'content': content,
                            'file_path': str(file_path),
                            'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                        }
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
                else:
                    print(f"Documentation file not found: {filename}")
            
            self.documentation_loaded.emit(docs)
            
        except Exception as e:
            print(f"Error loading documentation: {e}")
            self.documentation_loaded.emit({})

class UserHelpUI(QMainWindow):
    """
    User Help UI for Jarvis documentation.
    
    Features:
    - Searchable documentation
    - Bookmarking system
    - Voice command integration
    - Clean, accessible interface
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis User Help")
        self.setGeometry(100, 100, 1200, 800)
        
        # Data storage
        self.documentation = {}
        self.bookmarks = self.load_bookmarks()
        self.search_history = []
        self.current_doc = None
        
        # Apply Jarvis UI theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }
            QTreeWidget {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #ffffff;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
        """)
        
        # Initialize UI
        self.init_ui()
        
        # Load documentation
        self.load_documentation()
    
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Navigation and search
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Content display
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
    
    def create_left_panel(self) -> QWidget:
        """Create the left navigation panel."""
        panel = QWidget()
        panel.setMaximumWidth(350)
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Jarvis Help")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(header_label)

        # Search section
        search_layout = QVBoxLayout()

        search_label = QLabel("Search Documentation")
        search_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for help topics...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Documentation list
        docs_label = QLabel("Documentation")
        docs_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(docs_label)

        self.docs_list = QListWidget()
        self.docs_list.itemClicked.connect(self.on_doc_selected)
        layout.addWidget(self.docs_list)

        # Bookmarks section
        bookmarks_label = QLabel("Bookmarks")
        bookmarks_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(bookmarks_label)
        
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemClicked.connect(self.on_bookmark_selected)
        layout.addWidget(self.bookmarks_list)
        
        # Bookmark controls
        bookmark_controls = QHBoxLayout()
        
        add_bookmark_btn = QPushButton("Add Bookmark")
        add_bookmark_btn.clicked.connect(self.add_bookmark)
        bookmark_controls.addWidget(add_bookmark_btn)
        
        remove_bookmark_btn = QPushButton("Remove")
        remove_bookmark_btn.clicked.connect(self.remove_bookmark)
        bookmark_controls.addWidget(remove_bookmark_btn)
        
        layout.addLayout(bookmark_controls)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right content panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Content header
        header_layout = QHBoxLayout()
        
        self.content_title = QLabel("Welcome to Jarvis Help")
        self.content_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(self.content_title)
        
        header_layout.addStretch()
        
        # Navigation buttons
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        header_layout.addWidget(self.back_btn)

        self.forward_btn = QPushButton("Forward")
        self.forward_btn.clicked.connect(self.go_forward)
        self.forward_btn.setEnabled(False)
        header_layout.addWidget(self.forward_btn)
        
        layout.addLayout(header_layout)
        
        # Content display
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setHtml(self.get_welcome_content())
        layout.addWidget(self.content_display)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888888; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.word_count_label = QLabel("")
        self.word_count_label.setStyleSheet("color: #888888; font-size: 12px;")
        status_layout.addWidget(self.word_count_label)
        
        layout.addLayout(status_layout)
        
        panel.setLayout(layout)
        return panel
    
    def load_documentation(self):
        """Load documentation files in background."""
        self.status_label.setText("Loading documentation...")
        
        # Start documentation loader thread
        self.doc_loader = DocumentationLoader(project_root)
        self.doc_loader.documentation_loaded.connect(self.on_documentation_loaded)
        self.doc_loader.start()
    
    def on_documentation_loaded(self, docs: Dict):
        """Handle loaded documentation."""
        self.documentation = docs
        
        # Populate documentation list
        self.docs_list.clear()
        for title in sorted(self.documentation.keys()):
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, title)
            self.docs_list.addItem(item)
        
        # Update bookmarks list
        self.update_bookmarks_list()
        
        self.status_label.setText(f"Loaded {len(docs)} documentation files")
    
    def on_doc_selected(self, item: QListWidgetItem):
        """Handle documentation selection."""
        doc_title = item.data(Qt.ItemDataRole.UserRole)
        self.display_documentation(doc_title)
    
    def display_documentation(self, doc_title: str):
        """Display selected documentation."""
        if doc_title not in self.documentation:
            return
        
        doc = self.documentation[doc_title]
        self.current_doc = doc_title
        
        # Update title
        self.content_title.setText(doc_title)
        
        # Convert markdown to HTML (basic conversion)
        html_content = self.markdown_to_html(doc['content'])
        self.content_display.setHtml(html_content)
        
        # Update status
        word_count = len(doc['content'].split())
        self.word_count_label.setText(f"{word_count} words")
        self.status_label.setText(f"Viewing: {doc_title} (Modified: {doc['last_modified']})")
    
    def markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown to HTML (basic implementation)."""
        html = markdown_content
        
        # Headers
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Code blocks
        html = re.sub(r'```(.*?)```', r'<pre style="background-color: #333; padding: 10px; border-radius: 4px;"><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.*?)`', r'<code style="background-color: #333; padding: 2px 4px; border-radius: 2px;">\1</code>', html)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color: #0078d4;">\1</a>', html)
        
        # Line breaks
        html = html.replace('\n', '<br>')
        
        # Wrap in HTML structure
        return f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #ffffff;
                    background-color: #2b2b2b;
                }}
                h1, h2, h3 {{ color: #0078d4; margin-top: 20px; }}
                h1 {{ font-size: 24px; }}
                h2 {{ font-size: 20px; }}
                h3 {{ font-size: 16px; }}
                pre {{ overflow-x: auto; }}
                code {{ font-family: 'Consolas', 'Monaco', monospace; }}
                a {{ text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
    
    def perform_search(self):
        """Perform documentation search."""
        query = self.search_input.text().strip().lower()
        if not query:
            return
        
        # Add to search history
        if query not in self.search_history:
            self.search_history.append(query)
        
        # Search through documentation
        results = []
        for title, doc in self.documentation.items():
            content = doc['content'].lower()
            if query in content:
                # Count occurrences
                count = content.count(query)
                results.append((title, count))
        
        # Sort by relevance (occurrence count)
        results.sort(key=lambda x: x[1], reverse=True)
        
        if results:
            # Display search results
            self.display_search_results(query, results)
        else:
            self.status_label.setText(f"No results found for '{query}'")
    
    def display_search_results(self, query: str, results: List):
        """Display search results."""
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    color: #ffffff;
                    background-color: #2b2b2b;
                }}
                .result {{ 
                    margin: 10px 0; 
                    padding: 10px; 
                    background-color: #333; 
                    border-radius: 4px; 
                }}
                .result-title {{ 
                    color: #0078d4; 
                    font-weight: bold; 
                    font-size: 16px; 
                }}
                .result-count {{ 
                    color: #888; 
                    font-size: 12px; 
                }}
            </style>
        </head>
        <body>
            <h2>Search Results for "{query}"</h2>
            <p>Found {len(results)} documents containing your search term.</p>
        """
        
        for title, count in results:
            html_content += f"""
            <div class="result">
                <div class="result-title">{title}</div>
                <div class="result-count">{count} occurrence{'s' if count != 1 else ''}</div>
            </div>
            """
        
        html_content += "</body></html>"
        
        self.content_title.setText(f"Search Results: {query}")
        self.content_display.setHtml(html_content)
        self.status_label.setText(f"Found {len(results)} results for '{query}'")
    
    def on_search_changed(self):
        """Handle search input changes (for live search)."""
        # Could implement live search here if desired
        pass
    
    def add_bookmark(self):
        """Add current document to bookmarks."""
        if not self.current_doc:
            QMessageBox.information(self, "No Document", "Please select a document to bookmark.")
            return
        
        if self.current_doc not in self.bookmarks:
            self.bookmarks.append(self.current_doc)
            self.save_bookmarks()
            self.update_bookmarks_list()
            self.status_label.setText(f"Added '{self.current_doc}' to bookmarks")
        else:
            QMessageBox.information(self, "Already Bookmarked", "This document is already in your bookmarks.")
    
    def remove_bookmark(self):
        """Remove selected bookmark."""
        current_item = self.bookmarks_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a bookmark to remove.")
            return
        
        bookmark_title = current_item.data(Qt.ItemDataRole.UserRole)
        if bookmark_title in self.bookmarks:
            self.bookmarks.remove(bookmark_title)
            self.save_bookmarks()
            self.update_bookmarks_list()
            self.status_label.setText(f"Removed '{bookmark_title}' from bookmarks")
    
    def on_bookmark_selected(self, item: QListWidgetItem):
        """Handle bookmark selection."""
        bookmark_title = item.data(Qt.ItemDataRole.UserRole)
        self.display_documentation(bookmark_title)
    
    def update_bookmarks_list(self):
        """Update the bookmarks list widget."""
        self.bookmarks_list.clear()
        for bookmark in self.bookmarks:
            if bookmark in self.documentation:
                item = QListWidgetItem(bookmark)
                item.setData(Qt.ItemDataRole.UserRole, bookmark)
                self.bookmarks_list.addItem(item)
    
    def load_bookmarks(self) -> List[str]:
        """Load bookmarks from file."""
        bookmarks_file = project_root / "data" / "user_help_bookmarks.json"
        try:
            if bookmarks_file.exists():
                with open(bookmarks_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading bookmarks: {e}")
        return []
    
    def save_bookmarks(self):
        """Save bookmarks to file."""
        bookmarks_file = project_root / "data" / "user_help_bookmarks.json"
        try:
            bookmarks_file.parent.mkdir(exist_ok=True)
            with open(bookmarks_file, 'w') as f:
                json.dump(self.bookmarks, f, indent=2)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")
    
    def get_welcome_content(self) -> str:
        """Get welcome content HTML."""
        return """
        <html>
        <head>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #ffffff;
                    background-color: #2b2b2b;
                    padding: 20px;
                }
                h1 { color: #0078d4; }
                .feature {
                    margin: 15px 0;
                    padding: 10px;
                    background-color: #333;
                    border-radius: 4px;
                }
                .doc-category {
                    margin: 10px 0;
                    padding: 8px;
                    background-color: #404040;
                    border-radius: 3px;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to Jarvis User Help</h1>
            <p>Your comprehensive guide to using Jarvis Voice Assistant with enhanced features and complete plugin documentation!</p>

            <div class="feature">
                <h3>Search Documentation</h3>
                <p>Use the search box to find specific topics, commands, or features across all documentation.</p>
            </div>

            <div class="feature">
                <h3>Browse Documentation</h3>
                <p>Select from the comprehensive documentation list including:</p>
                <div class="doc-category"><strong>Essential Guides:</strong> Getting Started, Voice Commands, User Guide, Troubleshooting</div>
                <div class="doc-category"><strong>Plugin Guides:</strong> Device Time, Aider Integration, LaVague Web Automation, Log Terminal Tools, Open Interpreter, Robot Framework</div>
                <div class="doc-category"><strong>RAG & Memory:</strong> Complete RAG Memory system documentation</div>
                <div class="doc-category"><strong>System Guides:</strong> Architecture, Performance Optimization, Integration</div>
            </div>

            <div class="feature">
                <h3>Bookmark Important Pages</h3>
                <p>Save frequently accessed documentation for quick reference and easy return access.</p>
            </div>

            <div class="feature">
                <h3>Voice Commands</h3>
                <p>Say "Hey Jarvis, open user help" to launch this interface.<br>
                Say "Hey Jarvis, close user help" to close it properly.<br>
                Say "Hey Jarvis, search help for [topic]" to search documentation.</p>
            </div>

            <p><strong>Get Started:</strong> Select a document from the left panel or search for a specific topic. All plugin documentation and RAG guides are now available!</p>
        </body>
        </html>
        """
    
    def go_back(self):
        """Navigate back (placeholder for navigation history)."""
        # Could implement navigation history here
        pass
    
    def go_forward(self):
        """Navigate forward (placeholder for navigation history)."""
        # Could implement navigation history here
        pass
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save bookmarks before closing
        self.save_bookmarks()
        event.accept()

def main():
    """Main function to run the User Help UI."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Jarvis User Help")
    app.setApplicationVersion("1.0.0")
    
    # Create and show help UI
    help_ui = UserHelpUI()
    help_ui.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
