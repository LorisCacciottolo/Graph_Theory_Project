import os
import sys


class Tee:
	"""Writes all output to both the terminal and a log file."""
	def __init__(self, filepath):
		self._terminal = sys.stdout
		self._log = open(filepath, "w", encoding="utf-8")
		sys.stdout = self

	def write(self, message):
		self._terminal.write(message)
		self._log.write(message)

	def flush(self):
		self._terminal.flush()
		self._log.flush()

	def stop(self):
		sys.stdout = self._terminal
		self._log.close()


from graph import (
	get_txt_files,
	load_graph,
	build_matrix,
	display_matrix,
	display_pred_matrix,
	floyd_warshall,
	has_absorbing_circuit,
	reconstruct_path,
	INF,
)


def ask_path(L, P, n):
	"""Interactive loop: let the user query shortest paths until they stop."""
	while True:
		answer = input("\nFind a shortest path? (y/n): ").strip().lower()
		if answer != "y":
			break

		src = input("  Starting vertex: ").strip()
		dst = input("  Ending vertex:   ").strip()

		if not src.isdigit() or not dst.isdigit():
			print("  Please enter valid vertex numbers.")
			continue

		s, t = int(src), int(dst)
		if not (0 <= s < n and 0 <= t < n):
			print(f"  Vertices must be in [0, {n - 1}].")
			continue

		if s == t:
			print(f"  Path: {s}   (distance: 0)")
			continue

		if L[s][t] == INF:
			print(f"  No path from {s} to {t}.")
			continue

		path = reconstruct_path(P, s, t)
		if path is None:
			print(f"  No path from {s} to {t}.")
		else:
			path_str = " -> ".join(str(v) for v in path)
			print(f"  Path:     {path_str}")
			print(f"  Distance: {int(L[s][t])}")


def process_graph(files):
	"""Load one graph chosen by the user, run Floyd-Warshall, handle results."""

	# step 1 and 2: choose and load the graph
	print("\nAvailable graphs:")
	for i, f in enumerate(files):
		print(f"  {i:>3} — {f}")

	choice = input("\nChoose graph number: ").strip()
	if not choice.isdigit():
		print("Please enter a valid number.")
		return

	idx = int(choice)
	if idx < 0 or idx >= len(files):
		print("Invalid number.")
		return

	file_path = os.path.join(BASE_DIR, files[idx])

	# step 3: load into memory
	n, arcs = load_graph(file_path)
	if n is None:
		return

	print(f"\nLoaded : {files[idx]}")
	print(f"Vertices: {n}   |   Arcs: {len(arcs)}")

	# step 4: display the graph as a weight matrix
	matrix = build_matrix(n, arcs)
	display_matrix(matrix, "Initial weight matrix")

	# step 5: run floyd-warshall and display intermediate L and P
	L, P = floyd_warshall(matrix)

	# step 6: absorbing-circuit detection
	print("\n" + "=" * 60)
	if has_absorbing_circuit(L):
		print("  RESULT: The graph contains at least one absorbing circuit")
		print("          (negative cycle detected — shortest paths undefined).")
		print("=" * 60)
		return

	print("  RESULT: No absorbing circuit detected.")
	print("=" * 60)

	# step 7: display final matrices and let user query paths
	display_matrix(L, "L*  [final shortest-path distances]")
	display_pred_matrix(P, "P*  [final predecessor matrix]")

	ask_path(L, P, n)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
	print("╔══════════════════════════════════════════════╗")
	print("║     Floyd-Warshall Shortest Path Program     ║")
	print("╚══════════════════════════════════════════════╝")

	while True:
		files = get_txt_files(BASE_DIR)
		if not files:
			print("No .txt graph files found in the current directory.")
			break

		process_graph(files)

		again = input("\nProcess another graph? (y/n): ").strip().lower()
		if again != "y":
			print("Goodbye.")
			break


if __name__ == "__main__":
	tee = Tee(os.path.join(BASE_DIR, "traces.txt"))
	try:
		main()
	finally:
		tee.stop()
