import os

from graph import get_txt_files, load_graph, build_matrix, display_matrix


def main():
	print("Graph test program")

	files = get_txt_files(".")
	if len(files) == 0:
		print("No .txt graph files found in this folder.")
		return

	print("\nAvailable graph files:")
	index = 0
	while index < len(files):
		print(f"{index} - {files[index]}")
		index += 1

	choice = input("\nChoose file number: ").strip()
	if not choice.isdigit():
		print("Please enter a number.")
		return

	file_index = int(choice)
	if file_index < 0 or file_index >= len(files):
		print("Invalid file number.")
		return

	file_path = os.path.join(".", files[file_index])
	n, arcs = load_graph(file_path)

	if n is None:
		print("Graph loading failed.")
		return

	print(f"\nLoaded file: {files[file_index]}")
	print(f"Number of vertices: {n}")
	print(f"Number of arcs: {len(arcs)}")

	matrix = build_matrix(n, arcs)
	display_matrix(matrix, "Initial matrix")


if __name__ == "__main__":
	main()
