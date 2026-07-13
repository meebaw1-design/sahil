# =====================================================
# Sharp Talk Sport Studio
# STEP 2
# New Project Window
# =====================================================

import customtkinter as ctk


class NewProjectWindow(ctk.CTkToplevel):

    def __init__(self, parent, callback):

        super().__init__(parent)

        self.callback = callback

        self.title("Create New Project")

        self.geometry("500x250")

        self.resizable(False, False)

        self.grab_set()

        title = ctk.CTkLabel(
            self,
            text="Create New Football Project",
            font=("Arial",22,"bold")
        )

        title.pack(pady=(20,10))

        self.project_name = ctk.CTkEntry(
            self,
            width=350,
            placeholder_text="Example: Argentina vs France 2026"
        )

        self.project_name.pack(pady=20)

        create_button = ctk.CTkButton(
            self,
            text="Create Project",
            command=self.create_project
        )

        create_button.pack(pady=20)

    def create_project(self):

        project_name = self.project_name.get().strip()

        if project_name:

            self.callback(project_name)

            self.destroy()