# Multi-Document Graph Visualizer for Humanities and Social Sciences

A powerful tool for researchers in humanities and social sciences to discover and visualize connections across multiple texts, documents, and research materials.

## What This Tool Does

This application helps you:
- Discover hidden connections between your research documents
- Visualize relationships between concepts, people, places, and ideas
- Explore your corpus through an interactive network graph
- Generate data that can support your qualitative analysis

Perfect for researchers working with:
- Historical documents
- Interview transcripts
- Policy documents
- Literary texts
- Archival materials
- Field notes
- And more!

## Getting Started (No Technical Experience Required)

1. **Install Required Tools**
   - You'll need two tools installed on your computer:
     - `pyenv` (for managing Python versions)
     - `poetry` (for managing Python packages)
     - `npm` (for the visualization interface)
   - If you don't have these installed, please ask for help or check the troubleshooting section

2. **Prepare Your Documents**
   - Create a folder called `txt_data` on your computer
   - Replace any existing contents in the `txt_data` folder with your research materials
   - **Compatible formats**: 
     - PDF files (`.pdf`)
     - Plain text files (`.txt`)
     - Other formats are not currently supported
   - You can organize your files in subfolders within `txt_data`
   - Example structure:
     ```
     txt_data/
     ├── interviews/
     │   ├── interview1.pdf
     │   └── interview2.txt
     ├── historical_docs/
     │   └── archive1.pdf
     └── field_notes.txt
     ```

3. **Set Up and Run**
   First time setup (installs Python $(PYTHON_VERSION) and all dependencies):
   ```bash
   make setup
   ```

   Then run the analysis:
   ```bash
   make run
   ```

   Finally, start the visualization interface:
   ```bash
   make serve-frontend
   ```

   Note: If you need to restart the visualization with a fresh install:
   ```bash
   make viz
   ```

4. **Access Your Visualization**
   - Open your web browser
   - Go to http://localhost (or http://localhost:8080)
   - Your document network will appear automatically

## Research Applications

### For Qualitative Research
- Identify emerging themes across multiple documents
- Track the evolution of concepts through your corpus
- Discover unexpected connections between sources
- Support your close reading with distant reading methods

### For Historical Research
- Map relationships between historical figures
- Trace the spread of ideas across documents
- Identify key events and their connections
- Visualize temporal and spatial relationships

### For Literary Analysis
- Map character relationships
- Track motifs across texts
- Analyze intertextual connections
- Explore narrative networks

## Understanding Your Visualization

The interactive graph shows:
- **Nodes**: Represent documents, concepts, or entities
- **Edges**: Show connections between nodes
- **Size**: Reflects importance or frequency

You can:
- Click and drag nodes to explore
- Zoom in/out for different levels of detail
- Filter by relationship types
- Search for specific elements
- Export data for further analysis

## Working with Your Data

### Input
- Place your documents in the `txt_data` folder
- Files should be in PDF or plain text format
- No size limit, but processing time increases with corpus size

### Output
- Interactive visualization in your web browser
- Exportable JSON data for further analysis
- Network data compatible with other tools

## Testing the Tool

Before processing your full dataset, you can test the tool with a smaller sample:

```bash
make test
```

This will process just 5 files to help you understand how it works.

## Need Help?

- For questions about using the tool: [Create an Issue]
- For technical problems: Check the Troubleshooting section below
- For research collaboration: [Contact Information]

## Troubleshooting

Common solutions:
- If you need to install `pyenv`:
  - [Instructions for installing pyenv]
- If you need to install `poetry`:
  - [Instructions for installing poetry]
- If you need to install `npm`:
  - [Instructions for installing npm]
- If the visualization doesn't appear, try:
  ```bash
  make viz  # This will do a clean reinstall of the visualization dependencies
  ```
- If documents aren't processing, check they're in the correct folder (`txt_data`)
- For memory issues with large corpora, try processing in smaller batches
- To clean up and start fresh:
  ```bash
  make clean  # Removes all generated files and dependencies
  ```

## Contributing

We welcome contributions from both technical and non-technical backgrounds:
- Suggestions for new features
- Documentation improvements
- Bug reports
- Use case studies

## Citation

If you use this tool in your research, please cite:
```
@mastersthesis{barreda2024graphviz,
    author = {Barreda, Atilio},
    title = {Multi-Document Graph Visualizer: A Tool for Humanities and Social Sciences Research},
    school = {CUNY Graduate Center},
    program = {Data Analysis and Visualization},
    year = {2024},
    type = {MS Thesis}
}
```

## License

MIT License

Copyright (c) 2024 Atilio Barreda

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 