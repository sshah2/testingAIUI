import tkinter as tk
from tkinter import ttk

# Initialize the main window
root = tk.Tk()
root.title("Tree-like Navigation Menu")

# Create a frame for the navigation menu
nav_frame = tk.Frame(root, padx=10, pady=10)
nav_frame.pack(side=tk.LEFT, fill=tk.Y)

# Create the Treeview widget
tree = ttk.Treeview(nav_frame)

# Define the columns
tree["columns"] = ("Description")
tree.column("#0", width=150, minwidth=150, stretch=tk.NO)
tree.column("Description", width=250, minwidth=200, stretch=tk.NO)

# Define the headings
tree.heading("#0", text="Navigation", anchor=tk.W)
tree.heading("Description", text="Description", anchor=tk.W)

# Insert multiple Parents, Children, and Grandchildren
# Parent 1
parent1 = tree.insert("", "end", text="Parent 1", values=("Parent 1 Description"), open=True)
child1_1 = tree.insert(parent1, "end", text="Child 1.1", values=("Child 1.1 Description"), open=False)
grandchild1_1_1 = tree.insert(child1_1, "end", text="Grandchild 1.1.1", values=("Grandchild 1.1.1 Description"), open=False)
grandchild1_1_2 = tree.insert(child1_1, "end", text="Grandchild 1.1.2", values=("Grandchild 1.1.2 Description"), open=False)

child1_2 = tree.insert(parent1, "end", text="Child 1.2", values=("Child 1.2 Description"), open=False)
grandchild1_2_1 = tree.insert(child1_2, "end", text="Grandchild 1.2.1", values=("Grandchild 1.2.1 Description"), open=False)

# Parent 2
parent2 = tree.insert("", "end", text="Parent 2", values=("Parent 2 Description"), open=True)
child2_1 = tree.insert(parent2, "end", text="Child 2.1", values=("Child 2.1 Description"), open=False)
grandchild2_1_1 = tree.insert(child2_1, "end", text="Grandchild 2.1.1", values=("Grandchild 2.1.1 Description"), open=False)

child2_2 = tree.insert(parent2, "end", text="Child 2.2", values=("Child 2.2 Description"), open=False)
grandchild2_2_1 = tree.insert(child2_2, "end", text="Grandchild 2.2.1", values=("Grandchild 2.2.1 Description"), open=False)
grandchild2_2_2 = tree.insert(child2_2, "end", text="Grandchild 2.2.2", values=("Grandchild 2.2.2 Description"), open=False)

# Parent 3
parent3 = tree.insert("", "end", text="Parent 3", values=("Parent 3 Description"), open=True)
child3_1 = tree.insert(parent3, "end", text="Child 3.1", values=("Child 3.1 Description"), open=False)
grandchild3_1_1 = tree.insert(child3_1, "end", text="Grandchild 3.1.1", values=("Grandchild 3.1.1 Description"), open=False)

child3_2 = tree.insert(parent3, "end", text="Child 3.2", values=("Child 3.2 Description"), open=False)
grandchild3_2_1 = tree.insert(child3_2, "end", text="Grandchild 3.2.1", values=("Grandchild 3.2.1 Description"), open=False)
grandchild3_2_2 = tree.insert(child3_2, "end", text="Grandchild 3.2.2", values=("Grandchild 3.2.2 Description"), open=False)

# Run the main loop
tree.pack(side="top", fill="both", expand=True)
root.mainloop()
