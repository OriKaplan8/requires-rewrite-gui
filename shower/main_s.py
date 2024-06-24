from app_s import AnnotationApp
import tkinter as tk

ant1 = ["lieli", "agent_conv_test"]
ant2 = ["ori", "agent_conv_test"]
ant3 = ["AfikK", "agent_conv_test"]
annotators = [ant1, ant2, ant3]

def main():
    root = tk.Tk()
    app = AnnotationApp(root, annotators)
    root.mainloop()



if __name__ == "__main__":
    main()