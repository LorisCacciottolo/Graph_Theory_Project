import copy
import math
import os


INF = math.inf # use math.inf for infinite distances, to show there is no known path between vertices


def is_int(text):  # check if a string represents an integer (including negatives)
	if text.startswith("-"):
		return text[1:].isdigit()
	return text.isdigit()


def get_txt_files(graph_dir):  # return graph .txt files sorted by embedded numeric index
	def numeric_key(name):
		stem = os.path.splitext(name)[0]  # remove extension txt (ex: graph12.txt -> graph12)
		digits = "".join(c for c in stem if c.isdigit())  # keep only digits from the filename
		return int(digits) if digits else 0  # use 0 when no digits are present

	files = sorted(
		(file_name for file_name in os.listdir(graph_dir)  # scan files in the target directory
		 if file_name.endswith(".txt") and file_name != "traces.txt"),
		key=numeric_key,  # numeric ordering: graph2 before graph10
	)
	return files


def load_graph(file_path):
	if not os.path.isfile(file_path): # validate that the target file exists
		print(f"File not found: {file_path}")
		return None, None

	with open(file_path, "r") as file:  # read file content
		lines = [line.strip() for line in file if line.strip()]

	if len(lines) < 2:  # at least n and m must be present
		print("Invalid graph file: need at least 2 lines (n and m).")
		return None, None

	if not is_int(lines[0]) or not is_int(lines[1]):  # check numeric format before int conversion
		print("Invalid graph file: n and m must be integers.")
		return None, None

	n = int(lines[0])
	m = int(lines[1])

	if n < 0 or m < 0:  # graph size values must be non-negative
		print("Invalid graph file: n and m must be >= 0.")
		return None, None

	edge_lines = lines[2:]
	if len(edge_lines) != m:  # the number of arc lines must match m
		print(f"Invalid graph file: expected {m} arcs, found {len(edge_lines)}.")
		return None, None

	arcs = []
	index = 0
	while index < len(edge_lines):  # parse each expected arc line: u v w
		line = edge_lines[index]
		line_number = index + 3
		parts = line.split()
		if len(parts) != 3:  # each arc line must have exactly 3 values
			print(f"Invalid format at line {line_number}: expected 'u v w'.")
			return None, None

		if not is_int(parts[0]) or not is_int(parts[1]) or not is_int(parts[2]):  # u, v, w must be integers
			print(f"Invalid values at line {line_number}: u, v, w must be integers.")
			return None, None

		u = int(parts[0])
		v = int(parts[1])
		w = int(parts[2])

		if not (0 <= u < n and 0 <= v < n):  # vertex indices must be in [0, n-1]
			print(f"Invalid vertices at line {line_number}: must be in [0, {n - 1}].")
			return None, None

		arcs.append((u, v, w))  # store one validated directed weighted arc
		index += 1

	return n, arcs  # return graph size and validated arc list


def build_matrix(n, arcs):
	matrix = [[INF] * n for _ in range(n)]  # initialize with INF (unreachable by default)

	for i in range(n):
		matrix[i][i] = 0  # zero cost from a vertex to itself

	for u, v, w in arcs:
		matrix[u][v] = min(matrix[u][v], w)  # keep minimal weight when duplicate arcs exist
        
	return matrix  # return initial adjacency/weight matrix


def _cell_width(n):
	# compute a column width that fits vertex indices and common values
	return max(6, len(str(n - 1)) + 2)


def _display_table(rows, title):
	# print a generic indexed square table from pre-formatted string cells
	n = len(rows)  # number of rows and columns
	cw = _cell_width(n)  # width of each data column
	label_w = cw  # width of the row index label column

	print(f"\n{title}")  # table title
	header = " " * (label_w + 3) + "".join(f"{j:>{cw}}" for j in range(n))  # top header with column indices
	print(header)
	print(" " * (label_w + 3) + "-" * (cw * n))  # visual separator below header

	# each printed line starts with row index i, then all cells in that row
	for i, cells in enumerate(rows):
		print(f"{i:>{label_w}} |  " + "".join(f"{c:>{cw}}" for c in cells))


def display_matrix(matrix, title="Matrix"):
	# convert numeric matrix values to printable cells then display
	rows = []
	for row in matrix:
		cells = []
		for val in row:
			if val == INF:
				cells.append("INF")  # show unreachable entries explicitly
			else:
				cells.append(str(int(val)))  # display finite distances as integers
		rows.append(cells)
	_display_table(rows, title)


def display_pred_matrix(P, title="Predecessors P"):
	# convert predecessor values to printable cells then display
	rows = [["-" if v is None else str(v) for v in row] for row in P]  # '-' means no predecessor known
	_display_table(rows, title)


def floyd_warshall(matrix):
	# run floyd-warshall on the weight matrix
	# display L(k) and P(k) at each step
	# return final shortest-path matrix L and predecessor matrix P
	n = len(matrix)
	L = copy.deepcopy(matrix)  # l stores current shortest distances

	# p[i][j] = direct predecessor of j on the shortest known path from i to j
	P = [[None] * n for _ in range(n)]
	for i in range(n):
		for j in range(n):
			if i != j and L[i][j] < INF:  # if direct arc i->j exists, predecessor is i
				P[i][j] = i

	print("\n" + "=" * 60)
	print("  Floyd-Warshall execution")
	print("=" * 60)

	display_matrix(L, "L(0)  [initial weight matrix]")
	display_pred_matrix(P, "P(0)  [initial predecessors]")

	for k in range(n):  # main loop: try each vertex k as intermediate pivot
		for i in range(n):
			for j in range(n):
				if L[i][k] != INF and L[k][j] != INF:  # combine only reachable subpaths
					candidate = L[i][k] + L[k][j]
					if candidate < L[i][j]:  # check if new path is shorter and update predecessor
						L[i][j] = candidate
						P[i][j] = P[k][j]

		display_matrix(L, f"L({k + 1})  [after pivot vertex {k}]")
		display_pred_matrix(P, f"P({k + 1})  [after pivot vertex {k}]")

	return L, P


def has_absorbing_circuit(L):
	# return True if at least one diagonal value is negative
	for i in range(len(L)):
		if L[i][i] < 0:  # negative value on diagonal => negative cycle detected
			return True
	return False


def reconstruct_path(P, i, j):
	# rebuild shortest path from i to j using predecessor matrix P
	# return vertex list or None if no path exists
	if i == j:  # trivial case: source and destination are the same
		return [i]
	if P[i][j] is None:  # no predecessor means no reconstructible path
		return None

	path = [j]  # start from destination and backtrack through predecessors
	while path[0] != i:
		pred = P[i][path[0]]
		if pred is None:
			return None
		if pred in path:   # safety guard against malformed P
			return None
		path.insert(0, pred)
	return path