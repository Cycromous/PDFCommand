# PDF Commander

> A clean, lightweight desktop toolkit for everything you need to do with PDF files.

PDF Commander is a local desktop application that brings together the most common PDF workflows — editing, merging, splitting, converting, and viewing — into a single unified interface. No subscriptions, no uploads, no internet connection required. Everything runs on your machine.

---

## Features

### Editor
- Add text anywhere on a page with a click, using an adjustable font size slider (2–50pt)
- Draw filled shapes — rectangles and ovals — with a built-in color picker
- Insert and resize images and signatures by dragging the corner handles
- Drag any element to reposition it freely on the page
- Right-click any element to delete it
- Autosaves changes to the original file in the background as you work
- Save a clean copy at any time with Save As

### Merger
- Add multiple PDF files and preview a thumbnail of the first page of each
- Reorder files by selecting and using Move Up / Move Down before merging
- Remove individual files from the queue
- Merge all files in order into a single saved PDF

### Splitter
- Load any PDF and see its total page count
- Enter a custom page range to extract (e.g. `1-3, 5, 8-10`)
- Save the selected pages as a new standalone PDF

### Converter
- Convert Word documents (`.docx`) to PDF
- Convert images (`.png`, `.jpg`, `.jpeg`, `.bmp`) to PDF
- Add multiple files of mixed types in one batch and convert them all at once to a chosen destination folder

### Viewer
- Open and read any PDF with smooth page-by-page navigation
- Launch directly into the Editor from the Viewer with the current page preserved using the Edit This PDF button
- Open a PDF directly from the command line or by setting PDF Commander as your default `.pdf` handler in Windows

---

## Getting Started

### Requirements

- Python 3.8 or higher
- Windows (DPI awareness is configured automatically)
- All module files must be in the same directory:

```
PDFCommander.py
PDFEditor.py
PDFMerger.py
PDFSplitter.py
PDFConverter.py
PDFViewer.py
Commander.ico       ← optional, window icon
```

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-commander.git
cd pdf-commander

# Install dependencies
pip install -r requirements.txt

# Launch the app
python PDFCommander.py
```

### DOCX Conversion

DOCX to PDF conversion requires Microsoft Word to be installed on the machine. The `docx2pdf` library uses Word in the background to perform the conversion. If Word is not installed, DOCX files will be skipped and an error will be shown. Image conversion works without Word.

### Opening a PDF Directly

PDF Commander supports opening a file directly from the command line. When launched with a `.pdf` path as an argument, it skips the dashboard and opens the file immediately in the Viewer.

```bash
python PDFCommander.py "C:\path\to\your\file.pdf"
```

You can also associate `.pdf` files with PDF Commander in Windows so that double-clicking any PDF opens it directly in the Viewer.

---

## Usage

Launch `PDFCommander.py` to open the Tools Dashboard. Click any tool card to open it. Each tool runs in its own window. Closing a tool window returns you to the dashboard.

| Tool | Input | Output |
|---|---|---|
| Editor | Any PDF | Edited PDF saved in place or downloaded |
| Merger | 2+ PDF files | Single merged PDF |
| Splitter | Any PDF + page range | New PDF with selected pages |
| Converter | DOCX and/or image files | One PDF per file, saved to chosen folder |
| Viewer | Any PDF | Read-only view with direct handoff to Editor |

---

## Project Structure

```
pdf-commander/
├── PDFCommander.py     # Main launcher and dashboard
├── PDFEditor.py        # PDF editing module
├── PDFMerger.py        # PDF merging module
├── PDFSplitter.py      # PDF splitting module
├── PDFConverter.py     # PDF conversion module
├── PDFViewer.py        # PDF viewer module
├── Commander.ico       # Application icon
├── requirements.txt    # Python dependencies
└── setup.py            # Executable build configuration
```

---

## Built With

- [Tkinter](https://docs.python.org/3/library/tkinter.html) — GUI framework (Python standard library)
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) — PDF rendering, editing, merging, splitting, and image conversion
- [docx2pdf](https://github.com/AlJohri/docx2pdf) — DOCX to PDF conversion (requires Microsoft Word)

---

## License

MIT License. See `LICENSE` for details.
