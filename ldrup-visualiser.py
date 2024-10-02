#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from collections import Counter
    from argparse import ArgumentParser
except ImportError as e:
    print(f'Error: {e}')
    print('Please install the required modules with "pip install matplotlib numpy"')
    print('Make sure the pip used is the one associated with the python interpreter you are using.')
    exit(1)

args = ArgumentParser()
args.add_argument('filename', type=str, help='Path to the lidrup file.')
args.add_argument('--save', action='store_true', help='Save the plot as a PNG file.')
args.add_argument('--no-legend', action='store_true', help='Do not show the legend in the plot.')
args = args.parse_args()


queries = []
vacated = dict()
weakens = dict()
restores = dict()
index = 0
queried = False
query = {'index': index, 'weakened': dict(), 'restored': dict(), 'learned_clauses': 0, 'input_clauses': 0, 'deleted_clauses': 0}
for line in open(args.filename):
    if line.startswith('i'):
        query['input_clauses'] += 1
        if queried:
            query['input_after_query'] = query.get('input_after_query', 0) + 1
    elif line.startswith('l'):
        query['learned_clauses'] += 1
    elif line.startswith('d'):
        query['deleted_clauses'] += 1
    elif line.startswith('q'):
        queried = True
        query['asserted_vars'] = [int(x) for x in line.split()[1:-1]]
    elif line.startswith('w'):
        clauses = line.split()[1:-1]
        for x in clauses:
            weakens[int(x)] = weakens.get(int(x), 0) + 1
            diff = (index - vacated.get(int(x), index))
            query['weakened'][diff] = query['weakened'].get(diff, 0) + 1
            vacated[int(x)] = index
    elif line.startswith('r'):
        clauses = line.split()[1:-1]
        for x in clauses:
            diff = index - vacated.pop(int(x))
            query['restored'][diff] = query['restored'].get(diff, 0) + 1
            restores[int(x)] = restores.get(int(x), 0) + 1
            vacated[int(x)] = index
    elif line.startswith('s'):
        # check SAT or UNSAT
        query["result"] = line.split()[1]
    elif line.startswith('u'):
        # check UNSAT core
        first_zero = line.find('0')
        query["unsat_core"] = [int(x) for x in line[:first_zero].split()[1:]]
        queries.append(query)
        queried = False
        index += 1
        query = {'index': index, 'weakened': dict(), 'restored': dict(), 'learned_clauses': 0, 'input_clauses': 0, 'deleted_clauses': 0}
    elif line.startswith('m'):
        # check model
        query["model"] = [int(x) for x in line.split()[1:-1]]
        queries.append(query)
        queried = False
        index += 1
        query = {'index': index, 'weakened': dict(), 'restored': dict(), 'learned_clauses': 0, 'input_clauses': 0, 'deleted_clauses': 0}
        

indices = [query['index'] for query in queries]

# Get unique durations for weakened and restored separately
weaken_durations = set()
restore_durations = set()
for query in queries:
    weaken_durations.update(query['weakened'].keys())
    restore_durations.update(query['restored'].keys())

# Check if there are any weakened or restored clauses
has_weakened = any(sum(query['weakened'].values()) > 0 for query in queries)
has_restored = any(sum(query['restored'].values()) > 0 for query in queries)
    

# Set x-axis labels for all plots
num_labels = 10
step = max(len(indices) // (num_labels - 1), 1)
label_indices = list(range(0, len(indices), step))
if len(indices) - 1 not in label_indices:
    label_indices[-1] = len(indices) - 1


# Modify the figure layout
fig = plt.figure(figsize=(40, 30))
gs = fig.add_gridspec(2, 4, height_ratios=[1, 1], width_ratios=[1, 1, 1, 1])

plot_index = 0

if has_weakened or has_restored:
    weaken_durations = sorted(weaken_durations)
    restore_durations = sorted(restore_durations)

    weaken_colors = plt.cm.rainbow(np.linspace(0, 1, len(weaken_durations) if len(weaken_durations) <= 15 else 15))
    restore_colors = plt.cm.rainbow(np.linspace(0, 1, len(restore_durations) if len(restore_durations) <= 15 else 15))

    ax1 = fig.add_subplot(gs[0, plot_index])
    ax2 = fig.add_subplot(gs[1, plot_index], sharex=ax1)
    plot_index += 1
    grouped_heights = []
    # Plot weakened clauses
    bottom = np.zeros(len(indices))
    for i, duration in enumerate(weaken_durations):
        heights = [query['weakened'].get(duration, 0) for query in queries]
        if any(heights):
            if i >= 15:
                grouped_heights.append(heights)
            else:
                ax1.bar(indices, heights, bottom=bottom, color=weaken_colors[i], 
                        label=f'After {duration} queries')
                bottom += heights
    if grouped_heights:
        ax1.bar(indices, np.sum(grouped_heights, axis=0), bottom=bottom, color=weaken_colors[-1], 
                label=f'More than {weaken_durations[15]} queries')
        
    ax1.set_ylabel('Number of Weakened Clauses')
    ax1.set_title('Weakened Clauses per Query')
    if not args.no_legend:
        ax1.legend(title="Weakening Interval", loc='upper left', fontsize="small", borderaxespad=0., framealpha=0.5)


    grouped_heights = []
    # Plot restored clauses
    bottom = np.zeros(len(indices))
    for i, duration in enumerate(restore_durations):
        if i >= 15:
            grouped_heights.append(heights)
            continue
        heights = [query['restored'].get(duration, 0) for query in queries]
        if any(heights):
            ax2.bar(indices, heights, bottom=bottom, color=restore_colors[i], 
                    label=f'After {duration} queries')
            bottom += heights

    if grouped_heights:
        ax2.bar(indices, np.sum(grouped_heights, axis=0), bottom=bottom, color=restore_colors[-1], 
                label=f'More than {restore_durations[15]} queries')
        
    ax2.set_xlabel('Query')
    ax2.set_ylabel('Number of Restored Clauses')
    ax2.set_title('Restored Clauses per Query')
    if not args.no_legend:
        ax2.legend(title="Restoration Interval", loc='upper left', fontsize="small", borderaxespad=0., framealpha=0.5)
    ax2.set_xticks(label_indices)
    ax2.set_xticklabels([indices[i] for i in label_indices])

    ax3 = fig.add_subplot(gs[0, plot_index])
    ax4 = fig.add_subplot(gs[1, plot_index])
    plot_index += 1

    # Histogram of total weakenings with logarithmic y-axis
    weaken_counts = Counter(weakens.values())
    max_count = max(weaken_counts.keys())
    counts = [weaken_counts.get(i, 0) for i in range(1, max_count + 1)]
    ax3.bar(range(1, max_count + 1), counts, color='skyblue', edgecolor='black')
    ax3.set_yscale('log')
    ax3.set_xlabel('Number of Times Weakened')
    ax3.set_ylabel('Number of Clauses (log scale)')
    ax3.set_title('Distribution of Clause Weakenings')
    ax3.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # Histogram of total restorations with logarithmic y-axis
    restore_counts = Counter(restores.values())
    max_count = max(restore_counts.keys())
    counts = [restore_counts.get(i, 0) for i in range(1, max_count + 1)]
    ax4.bar(range(1, max_count + 1), counts, color='lightgreen', edgecolor='black')
    ax4.set_yscale('log')
    ax4.set_xlabel('Number of Times Restored')
    ax4.set_ylabel('Number of Clauses (log scale)')
    ax4.set_title('Distribution of Clause Restorations')
    ax4.xaxis.set_major_locator(plt.MaxNLocator(integer=True))  


# New plot for input, learned, deleted, weakened, restored clauses, and inputs after query
input_clauses = [query['input_clauses'] - query.get('input_after_query', 0) for query in queries]
learned_clauses = [query['learned_clauses'] for query in queries]
deleted_clauses = [query['deleted_clauses'] for query in queries]
weakened_clauses = [sum(query['weakened'].values()) for query in queries]
restored_clauses = [sum(query['restored'].values()) for query in queries]
inputs_after_query = [query.get('input_after_query', 0) for query in queries]

ax5 = fig.add_subplot(gs[0, plot_index])
ax5.plot(indices, input_clauses, label='Input Clauses', color='blue')
ax5.plot(indices, learned_clauses, label='Learned Clauses', color='green')
ax5.plot(indices, deleted_clauses, label='Deleted Clauses', color='red')
ax5.plot(indices, weakened_clauses, label='Weakened Clauses', color='purple')
ax5.plot(indices, restored_clauses, label='Restored Clauses', color='cyan')
ax5.plot(indices, inputs_after_query, label='Inputs After Query', color='orange')

ax5.set_xlabel('Query')
ax5.set_ylabel('Number of Clauses')
ax5.set_title('Clause Counts per Query')
if not args.no_legend:
    ax5.legend(loc='upper left', fontsize='small', borderaxespad=0., framealpha=0.5)

# Adjust the layout to make room for the legend
plt.tight_layout()
ax5.set_position([ax5.get_position().x0, ax5.get_position().y0, ax5.get_position().width * 0.75, ax5.get_position().height])


# New plot for query results
bar_width = 0.8
colors_bottom = []
colors_top = []
heights_bottom = []
heights_top = []
labels = []

for query in queries:
    if query['result'] == 'UNSATISFIABLE':
        colors_bottom.append('#FF0000')  # Red
        colors_top.append('#8B0000')     # Dark Red
        core_size = len(query.get('unsat_core', []))
        heights_bottom.append(core_size)
        heights_top.append(len(query['asserted_vars']))
    elif query['result'] == 'SATISFIABLE':
        colors_top.append('#00FF00')     # Green
        heights_bottom.append(0)
        heights_top.append(len(query['asserted_vars']))
    else:
        colors_bottom.append('gray')
        colors_top.append('darkgray')
        heights_bottom.append(1)
        heights_top.append(1)
# Create the stacked bar plot
ax6 = fig.add_subplot(gs[1, plot_index])

bottom_bars = ax6.bar(indices, heights_bottom, color=colors_bottom, width=bar_width)
top_bars = ax6.bar(indices, heights_top, bottom=heights_bottom, color=colors_top, width=bar_width)

ax6.set_xlabel('Query')
ax6.set_ylabel('Size of Core and Number of Assumptions')
ax6.set_title('Query Results: Core Size (Bottom) and Number of Assumptions (Top)')

# Add text annotations
for i, (height_bottom, height_top, label) in enumerate(zip(heights_bottom, heights_top, labels)):
    total_height = height_bottom + height_top
    ax6.text(i, total_height, label, ha='center', va='bottom', rotation=90, fontsize=8)

# Create custom legend elements
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#FF0000', edgecolor='#FF0000', label='UNSAT Core'),
    Patch(facecolor='#8B0000', edgecolor='#8B0000', label='UNSAT Assumptions'),
    Patch(facecolor='#00FF00', edgecolor='#00FF00', label='SAT Assumptions')
]

# Add the custom legend
if not args.no_legend:
    ax6.legend(handles=legend_elements, loc='upper left', borderaxespad=0., framealpha=0.5, fontsize='small')


for ax in [ax5, ax6]:
    ax.set_xticks(label_indices)
    ax.set_xticklabels([indices[i] for i in label_indices])


plot_index += 1
# New plot for assumption variables usage
ax7 = fig.add_subplot(gs[0, plot_index])

# New plot for assumption variables usage
all_vars = set()
for query in queries:
    all_vars.update(abs(var) for var in query['asserted_vars'])
all_vars = sorted(all_vars)

y_positions = range(len(all_vars))
ax7.set_yticks(y_positions)
ax7.set_yticklabels(all_vars)
ax7.set_xlabel('Query Index')
ax7.set_ylabel('Assumption Variables')
ax7.set_title('Assumption Variables Usage')

# Create custom legend elements
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Positive', markerfacecolor='red', markersize=6),
    Line2D([0], [0], marker='o', color='w', label='Negative', markerfacecolor='blue', markersize=6),
    Line2D([0], [0], marker='o', color='w', label='Pos in UNSAT Core', markerfacecolor='darkred', markersize=6),
    Line2D([0], [0], marker='o', color='w', label='Neg in UNSAT Core', markerfacecolor='darkblue', markersize=6)
]

for i, query in enumerate(queries):
    for var in query['asserted_vars']:
        abs_var = abs(var)
        y = all_vars.index(abs_var)
        color = 'red' if var > 0 else 'blue'
        if query['result'] == 'UNSATISFIABLE' and abs_var in [abs(x) for x in query.get('unsat_core', [])]:
            color = 'darkred' if var > 0 else 'darkblue'
        ax7.scatter(i, y, c=color, s=20)

# Add the legend inside the plot
if not args.no_legend:
    ax7.legend(handles=legend_elements, loc='upper left', fontsize='small', framealpha=0.5)

# Statistics table
total_clauses = sum(query['input_clauses'] + query['learned_clauses'] for query in queries)
total_deletions = sum(query['deleted_clauses'] for query in queries)
total_learned = sum(query['learned_clauses'] for query in queries)
total_weakens = sum(sum(query['weakened'].values()) for query in queries)
total_restores = sum(sum(query['restored'].values()) for query in queries)
percent_weakened_not_restored = (total_weakens - total_restores) / total_weakens * 100 if total_weakens > 0 else 0
num_sat = sum(1 for query in queries if query['result'] == 'SATISFIABLE')
num_unsat = sum(1 for query in queries if query['result'] == 'UNSATISFIABLE')

stats = [
    ['Total Clauses', f'{total_clauses:,}'],
    ['Total Deletions', f'{total_deletions:,}'],
    ['Total Learned', f'{total_learned:,}'],
    ['Total Weakens', f'{total_weakens:,}'],
    ['Total Restores', f'{total_restores:,}'],
    ['% Weakened Not Restored', f'{percent_weakened_not_restored:.2f}%'],
    ['Satisfied Results', f'{num_sat:,}'],
    ['Unsatisfied Results', f'{num_unsat:,}']
]
ax8 = fig.add_subplot(gs[1, plot_index])
ax8.axis('tight')
ax8.axis('off')
table = ax8.table(cellText=stats, loc='center', cellLoc='left', colWidths=[0.5, 0.5])
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(1, 2)  # Increase vertical scale to make cells taller
for key, cell in table.get_celld().items():
    cell.set_text_props(wrap=True)
    cell.set_height(0.1)  # Increase cell height
    cell.set_linewidth(0.5)  # Reduce line width for better appearance

plt.tight_layout()
if args.save:
    # remove the extension
    filename = args.filename.split('.')[0]
    plt.savefig(f'{filename}.png')
else:
    plt.show()
