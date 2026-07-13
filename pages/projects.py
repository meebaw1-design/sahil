# =====================================================
# Sharp Talk Sport Studio
# STEP 3
# Projects Page
# =====================================================

import customtkinter as ctk
import json
import os

DATABASE = "database/recent_projects.json"


class ProjectsPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        self.configure(fg_color="#2B2B2B")

        # ==========================================
        # Title
        # ==========================================

        title = ctk.CTkLabel(
            self,
            text="📁 Projects",
            font=("Arial", 30, "bold")
        )

        title.pack(pady=(30, 10))

        # ==========================================
        # Subtitle
        # ==========================================

        subtitle = ctk.CTkLabel(
            self,
            text="Recent Projects",
            font=("Arial", 18)
        )

        subtitle.pack(pady=(10, 20))

        # ==========================================
        # Recent Projects Box
        # ==========================================

        self.projects_frame = ctk.CTkFrame(
            self,
            width=700,
            height=350
        )

        self.projects_frame.pack()

        self.projects_frame.pack_propagate(False)

        # ==========================================
        # Load Projects
        # ==========================================

        self.load_recent_projects()

        # ==========================================
        # Button
        # ==========================================

        self.new_project_button = ctk.CTkButton(
            self,
            text="➕ New Project",
            width=250,
            height=45
        )

        self.new_project_button.pack(pady=25)

    # =================================================
    # Load Recent Projects
    # =================================================

    def load_recent_projects(self):

        for widget in self.projects_frame.winfo_children():
            widget.destroy()

        if not os.path.exists(DATABASE):
            return

        with open(DATABASE, "r") as file:
            projects = json.load(file)

        if len(projects) == 0:

            label = ctk.CTkLabel(
                self.projects_frame,
                text="No Projects Yet",
                font=("Arial", 16)
            )

            label.pack(pady=20)
            return

        for project in reversed(projects):

            row = ctk.CTkFrame(
                self.projects_frame
            )

            row.pack(
                fill="x",
                padx=20,
                pady=6
            )

            button = ctk.CTkButton(
                row,
                text="📂  " + project,
                anchor="w",
                font=("Arial", 16),
                fg_color="transparent",
                hover_color="#3A3A3A",
                text_color="white",
                command=lambda p=project: self.open_project(p)
            )

            button.pack(
                fill="x",
                padx=5,
                pady=5
            )

    # =====================================================
    # Open Project
    # =====================================================

    def open_project(self, project_name):

        print(f"Opening Project: {project_name}")

        if hasattr(self, "project_callback"):
            self.project_callback(project_name)
            
# =====================================================
# Test
# =====================================================

if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("1000x700")

    page = ProjectsPage(app)

    page.pack(fill="both", expand=True)

    app.mainloop()