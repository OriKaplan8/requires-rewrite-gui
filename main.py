from requiresRerwrite import RequiresRewriteApp
from scoringRewrite import ScoringRewritesApp
import tkinter as tk
from tkinter import simpledialog


class FileDialog(simpledialog.Dialog):
    """
    A dialog window for choosing a file.

    Inherits from simpledialog.Dialog class.

    Attributes:
        field1 (tk.Entry): The entry field for the username.
        field2 (tk.Entry): The entry field for the filename.
        result (tuple): A tuple containing the values entered in the entry fields.

    Methods:
        body(master): Creates the body of the dialog window.
        apply(): Applies the changes made in the dialog window.
    """

    def __init__(self, root, dev_mode=False):
        self.dev_mode = dev_mode
        self.root = root
        # Call the parent class constructor
        super().__init__(root)

    def body(self, master):
        self.title("Choose File")

        tk.Label(master, text="username").grid(row=0)
        tk.Label(master, text="filename").grid(row=1)

        self.field1 = tk.Entry(master)
        self.field2 = tk.Entry(master)

        self.field1.grid(row=0, column=1)
        self.field2.grid(row=1, column=1)

        # Prefill fields if in dev_mode
        if isinstance(self.dev_mode, list) and len(self.dev_mode) == 2:
            self.field1.insert(0, self.dev_mode[0])
            self.field2.insert(0, self.dev_mode[1])

        return self.field1  # Initial focus on the first field

    def apply(self):
        self.result = (self.field1.get(), self.field2.get())



dev = ["lieli", "agent_conv_test"]
dev1 = ["ori", "asi-23_4"]
toy = ["test-user", "toy-dataset-2" ]
test= ["ori2" , "old-dataset"]
new = ["test-user", "rewrite-scoring-1"]

def main(dev = None):
    root = tk.Tk()
    app = None
    login = None
    version = 4.0
    if dev is None:
        dialog = FileDialog(root)

        if dialog.result:
            username, filename = dialog.result
            login = {"username": username, "filename": filename}

            if filename in ["agent_conv_complete", "agent_conv_test", "asi-14_4", "asi-23_4"]:
                app = RequiresRewriteApp
            else:
                app = ScoringRewritesApp

        else:
            root.destroy()
    
    else:
        login = {"username": dev[0], "filename": dev[1]}
        if dev[1] in ["agent_conv_complete", "agent_conv_test", "asi-14_4", "asi-23_4"]:
            app = RequiresRewriteApp
        else:
            app = ScoringRewritesApp


    app(root, version, login)
    root.mainloop()



if __name__ == "__main__":
    main()