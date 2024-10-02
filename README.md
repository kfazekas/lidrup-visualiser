# LDRUP Visualizer

A Python script for visualizing LDRUP (Learned clauses, Deletion, Restoration, and Unit Propagation) patterns in SAT solving.

## Features

- Visualizes LDRUP patterns from solver output
- Supports various graph types for comprehensive analysis
- Option to save generated figures automatically
- Customizable legend display

## Installation

```bash
git clone https://github.com/yourusername/ldrup-visualizer.git
cd ldrup-visualizer
pip install -r requirements.txt
```

## Usage

```bash
python3 ldrup-visualizer.py [OPTIONS] FILENAME
```

### Options

- `--save`: Automatically save the figure as a PNG file (filename derived from input)
- `--no-legend`: Hide the legend for a less cluttered figure

### Examples

1. Generate and display a visualization:
   ```bash
   python3 ldrup-visualizer.py input_file.txt
   ```

2. Generate, display, and save a visualization without legend:
   ```bash
   python3 ldrup-visualizer.py --save --no-legend input_file.txt
   ```

## Graph Explanation

The visualizer generates up to four columns of graphs, each providing different insights into the LDRUP pattern:

1. **Clause Weakening and Restoration** (leftmost column, if applicable)
   - Top: Number of weakened clauses
   - Bottom: Number of restored clauses
   - Color coding indicates the number of queries between operations

2. **Clause Operation Frequency** (second column)
   - Top: Frequency of clause weakening
   - Bottom: Frequency of clause restoration

3. **Clause Addition and Query Results** (third column)
   - Top: Number of clauses added per query (IPASIR inputs vs. solver inputs)
   - Bottom: Query results (SAT/UNSAT) and literal counts (assumed/core)

4. **Variable Usage in Assumptions** (rightmost column)
   - Variables used in query assumptions
   - Color indicates polarity (red: positive, blue: negative)
   - Shade indicates presence in UNSAT core (darker: present)

### Example Visualizations

#### BMC (Bounded Model Checking) Interaction
![BMC example](https://github.com/user-attachments/assets/0c042635-f200-495e-bcdb-6be1009e51de)

#### MaxSAT Solver Interaction
![MaxSAT example](https://github.com/user-attachments/assets/8de79fcc-7115-4e49-9d29-cfeb18e351a8)

Note: The MaxSAT example shows a different pattern in assumptions and query results compared to the BMC example, and does not include weakened or restored clauses.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
