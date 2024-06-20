from app import AnnotationApp
import tkinter as tk

dev = ["lieli", "agent_conv_test"]
dev1 = ["ori", "asi-23_4"]
def main():
    root = tk.Tk()
    app = AnnotationApp(root)
    root.mainloop()



if __name__ == "__main__":
    main()