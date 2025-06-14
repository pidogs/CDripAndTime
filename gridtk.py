import tkinter as tk
from ttkbootstrap import ttk

# ==============================================================================
# == CUSTOMIZE THIS FUNCTION with your desired formula.
# ==============================================================================
def calculate_output(row_input, col_input):
  if not row_input or not col_input:
    return "..." # Return a placeholder if an input is empty
  return f"{row_input} & {col_input}"


class GridApplication:
  """
  A class to create and manage the dynamic grid GUI.
  """
  def __init__(self, root, num_rows=6, num_cols=3):
    self.root = root
    self.root.title("Dynamic Input/Output Grid")
    self.num_rows = num_rows
    self.num_cols = num_cols

    # Store references to Tkinter variables and widgets
    self.row_input_vars = []
    self.col_input_vars = []
    self.output_labels = []

    # Create a main frame for content
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    self._create_widgets(main_frame)
    self._update_all_outputs()

  def _create_widgets(self, parent_frame):
    """Creates and arranges all the widgets in the grid."""
    # Create column input entries (the top row)
    ttk.Label(parent_frame, text="").grid(row=0, column=0) # Placeholder top-left corner
    for j in range(self.num_cols):
      var = tk.StringVar(value=f"other input {j + 1}")
      # When the variable's value changes, call the update function
      var.trace_add("write", self._update_all_outputs)
      self.col_input_vars.append(var)

      entry = ttk.Entry(parent_frame, textvariable=var, width=20, justify='center')
      entry.grid(row=0, column=j + 1, padx=5, pady=5, sticky="ew")

    # Create row input entries (the first column) and the output labels
    for i in range(self.num_rows):
      # Row Input Entry
      var = tk.StringVar(value=f"Input {i + 1}")
      var.trace_add("write", self._update_all_outputs)
      self.row_input_vars.append(var)

      entry = ttk.Entry(parent_frame, textvariable=var, width=15)
      entry.grid(row=i + 1, column=0, padx=5, pady=5, sticky="ew")

      # Output Labels for this row
      output_row = []
      for j in range(self.num_cols):
        label = ttk.Label(parent_frame, text="...", width=20, anchor='center', relief="groove", padding=5)
        label.grid(row=i + 1, column=j + 1, padx=5, pady=5, sticky="ew")
        output_row.append(label)
      self.output_labels.append(output_row)

  def _update_all_outputs(self, *args):
    """
    Recalculates and updates the text of every output label in the grid.
    This method is triggered automatically when any input value changes.
    """
    for i in range(self.num_rows):
      for j in range(self.num_cols):
        # Get the current input values from their associated variables
        row_val = self.row_input_vars[i].get()
        col_val = self.col_input_vars[j].get()

        # Calculate the new output using the user-defined function
        output_text = calculate_output(row_val, col_val)

        # Update the corresponding output label
        self.output_labels[i][j].config(text=output_text)


if __name__ == "__main__":
  # Create the main window
  root = tk.Tk()
  
  # You can easily change the size of the grid here
  # For example, to create a 10x5 grid: GridApplication(root, num_rows=10, num_cols=5)
  app = GridApplication(root, num_rows=6, num_cols=3)

  # Start the GUI event loop
  root.mainloop()