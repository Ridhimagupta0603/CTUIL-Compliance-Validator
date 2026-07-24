from __future__ import annotations
import queue
import traceback


import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from config import default_output_path
from runner import run_validation as execute_validation


class ComplianceValidatorGUI:

    def __init__(self):

        self.root = ttk.Window(themename="flatly")
        self.root.title("CTUIL Compliance Validator")
        self.root.state("zoomed")
        self.root.minsize(950, 700)

        # Variables
        self.workbook_path = tk.StringVar(master=self.root)
        self.output_path = tk.StringVar(master=self.root)

        self.verbose = tk.BooleanVar(master=self.root, value=False)
        self.no_comments = tk.BooleanVar(master=self.root, value=False)
        self.dry_run = tk.BooleanVar(master=self.root, value=False)

        self.search_roots = []
        self.gui_queue = queue.Queue()

        # Check queue every 100 ms
        self.root.after(100, self.process_gui_queue)

        self.create_widgets()

    ####################################################################
    # GUI
    ####################################################################

    def create_widgets(self):

        ###########################################
        # Main Frame
        ###########################################

        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=BOTH, expand=True)

        ###########################################
        # Title
        ###########################################

        ttk.Label(
            main,
            text="CTUIL Compliance Validator",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(0, 15))

        ###########################################
        # Workbook
        ###########################################

        workbook_frame = ttk.Labelframe(
            main,
            text="Compliance Workbook (.xlsx)",
            padding=10,
        )

        workbook_frame.pack(fill=X, pady=5)

        wb_row = ttk.Frame(workbook_frame)
        wb_row.pack(fill=X)

        self.workbook_entry = ttk.Entry(
            wb_row,
            textvariable=self.workbook_path,
        )

        self.workbook_entry.pack(
            side=LEFT,
            fill=X,
            expand=True,
        )

        ttk.Button(
            wb_row,
            text="Browse...",
            width=12,
            bootstyle=PRIMARY,
            command=self.select_workbook,
        ).pack(side=LEFT, padx=(10, 0))

        ###########################################
        # Submission Files
        ###########################################

        submit_frame = ttk.Labelframe(
            main,
            text="Submission Folder(s) / ZIP File(s)",
            padding=10,
        )

        submit_frame.pack(fill=BOTH, expand=True, pady=10)

        tree_frame = ttk.Frame(submit_frame)
        tree_frame.pack(fill=BOTH, expand=True)

        columns = (
            "type",
            "path",
        )

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=10,
        )

        self.tree.heading(
            "type",
            text="Type",
        )

        self.tree.heading(
            "path",
            text="Location",
        )

        self.tree.column(
            "type",
            width=90,
            anchor=CENTER,
            stretch=False,
        )

        self.tree.column(
            "path",
            width=800,
            stretch=True,
        )

        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient=VERTICAL,
            command=self.tree.yview,
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set,
        )

        self.tree.pack(
            side=LEFT,
            fill=BOTH,
            expand=True,
        )

        scrollbar.pack(
            side=RIGHT,
            fill=Y,
        )

        ###########################################
        # Buttons
        ###########################################

        btn_frame = ttk.Frame(submit_frame)
        btn_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Add Folder",
            width=15,
            bootstyle=SUCCESS,
            command=self.add_folder,
        ).pack(side=LEFT)

        ttk.Button(
            btn_frame,
            text="Add ZIP",
            width=15,
            bootstyle=INFO,
            command=self.add_zip,
        ).pack(side=LEFT, padx=10)

        ttk.Button(
            btn_frame,
            text="Remove Selected",
            width=18,
            bootstyle=DANGER,
            command=self.remove_selected,
        ).pack(side=LEFT)

        ###########################################
        # Output
        ###########################################

        output_frame = ttk.Labelframe(
            main,
            text="Output Workbook",
            padding=10,
        )

        output_frame.pack(fill=X)

        out_row = ttk.Frame(output_frame)
        out_row.pack(fill=X)

        self.output_entry = ttk.Entry(
            out_row,
            textvariable=self.output_path,
        )

        self.output_entry.pack(
            side=LEFT,
            fill=X,
            expand=True,
        )

        ttk.Button(
            out_row,
            text="Browse...",
            width=12,
            bootstyle=PRIMARY,
            command=self.select_output,
        ).pack(side=LEFT, padx=(10, 0))

        ###########################################
        # Options
        ###########################################

        option_frame = ttk.Frame(main)
        option_frame.pack(fill=X, pady=10)

        ttk.Checkbutton(
            option_frame,
            text="Dry Run",
            variable=self.dry_run,
        ).pack(side=LEFT)

        ttk.Checkbutton(
            option_frame,
            text="No Comments",
            variable=self.no_comments,
        ).pack(side=LEFT, padx=20)

        ttk.Checkbutton(
            option_frame,
            text="Verbose",
            variable=self.verbose,
        ).pack(side=LEFT)

        ###########################################
        # Progress
        ###########################################

        progress_frame = ttk.Labelframe(
            main,
            text="Progress",
            padding=10,
        )

        progress_frame.pack(fill=X)

        self.progress = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            maximum=100,
        )

        self.progress.pack(fill=X)

        self.status = ttk.Label(
            progress_frame,
            text="Ready",
            font=("Segoe UI", 10),
        )

        self.status.pack(anchor=W, pady=(6, 0))

        ###########################################
        # Start Button
        ###########################################

        self.start_button = ttk.Button(
            main,
            text="START VALIDATION",
            width=30,
            bootstyle="success",
            command=self.start_validation,
        )

        self.start_button.pack(pady=10)
        ###########################################
        # Log Window
        ###########################################

        log_frame = ttk.Labelframe(
            main,
            text="Validation Log",
            padding=10,
        )

        log_frame.pack(
            fill=BOTH,
            expand=True,
            pady=10,
        )

        self.log = tk.Text(
            log_frame,
            height=8,
            wrap="word",
            font=("Consolas", 10),
        )

        self.log.pack(fill=BOTH, expand=True)


        ####################################################################
    # Browse Functions
    ####################################################################

    def select_workbook(self):

        filename = filedialog.askopenfilename(
            title="Select Compliance Workbook",
            filetypes=[
                ("Excel Workbook", "*.xlsx"),
                ("All Files", "*.*"),
            ],
        )

        if not filename:
            return

        self.workbook_path.set(filename)

        # Automatically suggest output file
        if not self.output_path.get():

            output = default_output_path(Path(filename))

            self.output_path.set(str(output))

        self.log_message(f"Workbook Selected : {filename}")

    ###############################################################

    def select_output(self):

        filename = filedialog.asksaveasfilename(
            title="Save Output Workbook",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Workbook", "*.xlsx"),
            ],
        )

        if filename:
            self.output_path.set(filename)

            self.log_message(
                f"Output Workbook : {filename}"
            )

    ###############################################################

    def add_folder(self):

        folder = filedialog.askdirectory(
            title="Select Submission Folder"
        )

        if not folder:
            return

        if folder in self.search_roots:

            messagebox.showwarning(
                "Already Added",
                "Folder already exists."
            )

            return

        self.search_roots.append(folder)

        self.tree.insert(
            "",
            tk.END,
            values=(
                "Folder",
                folder,
            ),
        )

        self.log_message(
            f"Folder Added : {folder}"
        )

    ###############################################################

    def add_zip(self):

        filename = filedialog.askopenfilename(
            title="Select ZIP File",
            filetypes=[
                ("ZIP Files", "*.zip"),
            ],
        )

        if not filename:
            return

        if filename in self.search_roots:

            messagebox.showwarning(
                "Already Added",
                "ZIP file already exists."
            )

            return

        self.search_roots.append(filename)

        self.tree.insert(
            "",
            tk.END,
            values=(
                "ZIP",
                filename,
            ),
        )

        self.log_message(
            f"ZIP Added : {filename}"
        )

    ###############################################################

    def remove_selected(self):

        selected = self.tree.selection()

        if not selected:

            return

        for item in selected:

            values = self.tree.item(item)["values"]

            if len(values) >= 2:

                path = values[1]

                if path in self.search_roots:
                    self.search_roots.remove(path)

            self.tree.delete(item)

        self.log_message(
            "Selected entries removed."
        )

    ####################################################################
    # Logging
    ####################################################################

    def log_message(self, message):

        self.log.insert(
            tk.END,
            message + "\n"
        )

        self.log.see(tk.END)

        self.status.config(
            text=message
        )

        self.root.update_idletasks()

    ####################################################################
    # Progress
    ####################################################################

    def update_progress(self, status, progress):
        """
        Called by runner.py from the worker thread.
        Never touch tkinter widgets here.
        """

        self.gui_queue.put(
            (
                "progress",
                status,
                progress,
            )
        )
    def process_gui_queue(self):

        try:

            while True:

                item = self.gui_queue.get_nowait()

                event = item[0]

                #######################################################

                if event == "progress":

                    _, status, value = item

                    self.progress["value"] = value

                    self.status.config(
                        text=status,
                    )

                    self.log.insert(
                        tk.END,
                        status + "\n",
                    )

                    self.log.see(tk.END)

                #######################################################

                elif event == "success":

                    _, result = item

                    self.progress["value"] = 100

                    self.status.config(
                        text="Completed",
                    )

                    self.start_button.config(
                        state="normal",
                    )

                    self.log.insert(
                        tk.END,
                        "\nValidation Completed Successfully.\n",
                    )

                    self.log.insert(
                        tk.END,
                        f"\nWorkbook : {result['saved']}\n",
                    )

                    self.log.see(tk.END)

                    if result["saved"]:

                        messagebox.showinfo(
                            "Validation Complete",
                            f"Workbook saved to\n\n{result['saved']}"
                        )

                    else:

                        messagebox.showinfo(
                            "Dry Run Complete",
                            "Validation completed."
                        )

                #######################################################

                elif event == "error":

                    _, err = item

                    self.progress["value"] = 0

                    self.status.config(
                        text="Error",
                    )

                    self.start_button.config(
                        state="normal",
                    )

                    self.log.insert(
                        tk.END,
                        "\nERROR\n",
                    )

                    self.log.insert(
                        tk.END,
                        err + "\n",
                    )

                    self.log.see(tk.END)

                    messagebox.showerror(
                        "Validation Failed",
                        err,
                    )

        except queue.Empty:

            pass

        finally:

            self.root.after(
                100,
                self.process_gui_queue,
            )
    ####################################################################
    # Start Button
    ####################################################################

    def start_validation(self):

        if not self.workbook_path.get():

            messagebox.showerror(
                "Missing Workbook",
                "Please select the Compliance Workbook."
            )

            return

        if not self.search_roots:

            messagebox.showerror(
                "Missing Submission Folder",
                "Please add at least one Folder or ZIP."
            )

            return

        self.progress["value"] = 0

        self.log.delete(
            "1.0",
            tk.END,
        )

        self.start_button.config(
            state="disabled"
        )

        threading.Thread(
            target=self.run_validation,
            daemon=True,
        ).start()

        ####################################################################
    # Validation Thread
    ####################################################################

    def run_validation(self):

        try:

            result = execute_validation(

                workbook_path=self.workbook_path.get(),

                search_roots=self.search_roots,

                output_path=self.output_path.get()
                if self.output_path.get()
                else None,

                dry_run=self.dry_run.get(),

                no_comments=self.no_comments.get(),

                verbose=self.verbose.get(),

                progress_callback=self.update_progress,
            )

            self.gui_queue.put(
                (
                    "success",
                    result,
                )
            )

        except Exception:

            self.gui_queue.put(
                (
                    "error",
                    traceback.format_exc(),
                )
            )


if __name__ == "__main__":
    app = ComplianceValidatorGUI()
    app.root.mainloop()