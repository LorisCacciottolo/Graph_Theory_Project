import math
import os


INF = math.inf


def is_int(text):
	if text.startswith("-"):
		return text[1:].isdigit()
	return text.isdigit()


def get_txt_files(graph_dir):
	if not os.path.isdir(graph_dir):
		print(f"Graph directory not found: {graph_dir}")
		return []

	files = sorted(file_name for file_name in os.listdir(graph_dir) if file_name.endswith(".txt"))
	return files


def load_graph(file_path):
	if not os.path.isfile(file_path):
		print(f"File not found: {file_path}")
		return None, None

	with open(file_path, "r") as file:
		lines = [line.strip() for line in file if line.strip()]

	if len(lines) < 2:
		print("Invalid graph file: need at least 2 lines (n and m).")
		return None, None

	if not is_int(lines[0]) or not is_int(lines[1]):
		print("Invalid graph file: n and m must be integers.")
		return None, None

	n = int(lines[0])
	m = int(lines[1])

	if n < 0 or m < 0:
		print("Invalid graph file: n and m must be >= 0.")
		return None, None

	edge_lines = lines[2:]
	if len(edge_lines) != m:
		print(f"Invalid graph file: expected {m} arcs, found {len(edge_lines)}.")
		return None, None

	arcs = []
	index = 0
	while index < len(edge_lines):
		line = edge_lines[index]
		line_number = index + 3
		parts = line.split()
		if len(parts) != 3:
			print(f"Invalid format at line {line_number}: expected 'u v w'.")
			return None, None

		if not is_int(parts[0]) or not is_int(parts[1]) or not is_int(parts[2]):
			print(f"Invalid values at line {line_number}: u, v, w must be integers.")
			return None, None

		u = int(parts[0])
		v = int(parts[1])
		w = int(parts[2])

		if not (0 <= u < n and 0 <= v < n):
			print(f"Invalid vertices at line {line_number}: must be in [0, {n - 1}].")
			return None, None

		arcs.append((u, v, w))
		index += 1
	return n, arcs


def build_matrix(n, arcs):
	matrix = [[INF] * n for _ in range(n)]

	for i in range(n):
		matrix[i][i] = 0

	for u, v, w in arcs:
		matrix[u][v] = w
	return matrix


def display_matrix(matrix, title="Matrix"):
	print(f"\n{title}")
	for row in matrix:
		formatted_row = []
		for value in row:
			formatted_row.append("INF" if value == INF else str(value))
		print(" ".join(f"{cell:>5}" for cell in formatted_row))
