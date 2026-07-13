# =====================================================
# Sharp Talk Sport Studio
# Dashboard Page
# Version 1.0 - Step 4D Task 3
# =====================================================

import customtkinter as ctk
import json
import os

from utils.progress_tracker import get_project_progress
from utils.dashboard_manager import get_dashboard_data


class DashboardPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        self.configure(fg_color="#2B2B2B")

        self.header = ctk.CTkFrame(
            self,
            fg_color="#2B2B2B"
        )
        self.header.pack(fill="x", pady=(18, 5))

        title = ctk.CTkLabel(
            self.header,
            text="⚽ Sharp Talk Sport Studio",
            font=("Arial", 32, "bold")
        )
        title.pack()

        version = ctk.CTkLabel(
            self.header,
            text="Version 1.0  |  Status: Ready for Production",
            font=("Arial", 15, "bold")
        )
        version.pack(pady=(4, 8))

        welcome = ctk.CTkLabel(
            self.header,
            text="Welcome Sahil!",
            font=("Arial", 20)
        )
        welcome.pack(pady=3)

        subtitle = ctk.CTkLabel(
            self.header,
            text="Football AI Production Studio",
            font=("Arial", 15)
        )
        subtitle.pack(pady=(0, 8))

        self.stats_label = ctk.CTkLabel(
            self.header,
            text="Projects Created: 0",
            font=("Arial", 18, "bold")
        )
        self.stats_label.pack(pady=4)

        self.progress_label = ctk.CTkLabel(
            self.header,
            text="Latest Project Progress\nLoading...",
            font=("Arial", 15)
        )
        self.progress_label.pack(pady=5)

        dashboard_title = ctk.CTkLabel(
            self,
            text="📊 Production Dashboard",
            font=("Arial", 22, "bold")
        )
        dashboard_title.pack(pady=(10, 8))

        self.projects_box = ctk.CTkScrollableFrame(
            self,
            width=850,
            height=360
        )
        self.projects_box.pack(
            fill="both",
            expand=True,
            padx=80,
            pady=(5, 20)
        )

        self.update_stats()
        self.update_progress()
        self.update_production_dashboard()

    def update_stats(self):

        database = "database/recent_projects.json"

        if not os.path.exists(database):
            total_projects = 0
        else:
            with open(database, "r") as file:
                projects = json.load(file)
            total_projects = len(projects)

        self.stats_label.configure(
            text=f"Projects Created: {total_projects}"
        )

    def update_progress(self):

        database = "database/recent_projects.json"

        if not os.path.exists(database):
            self.progress_label.configure(text="No Projects")
            return

        with open(database, "r") as file:
            projects = json.load(file)

        if len(projects) == 0:
            self.progress_label.configure(text="No Projects")
            return

        latest = projects[-1]
        progress = get_project_progress(latest)

        self.progress_label.configure(
            text=(
                f"Latest Project: {latest}\n"
                f"{progress['completed']} / {progress['total']} Scenes  |  "
                f"{progress['percent']}% Complete"
            )
        )

    def update_production_dashboard(self):

        for widget in self.projects_box.winfo_children():
            widget.destroy()

        data = get_dashboard_data()

        if len(data) == 0:

            empty = ctk.CTkLabel(
                self.projects_box,
                text="No projects found.",
                font=("Arial", 16)
            )
            empty.pack(pady=20)
            return

        for project in data:

            card = ctk.CTkFrame(
                self.projects_box
            )
            card.pack(
                fill="x",
                padx=20,
                pady=10
            )

            name = ctk.CTkLabel(
                card,
                text=f"📂 {project['name']}",
                font=("Arial", 17, "bold"),
                anchor="w"
            )
            name.pack(
                fill="x",
                padx=18,
                pady=(12, 3)
            )

            info = ctk.CTkLabel(
                card,
                text=f"{project['completed']} / {project['total']} Scenes — {project['percent']}% Complete",
                font=("Arial", 14),
                anchor="w"
            )
            info.pack(
                fill="x",
                padx=18,
                pady=(0, 6)
            )

            bar = ctk.CTkProgressBar(card)
            bar.pack(
                fill="x",
                padx=18,
                pady=(0, 14)
            )

            bar.set(project["percent"] / 100)


if __name__ == "__main__":

    app = ctk.CTk()
    app.geometry("1000x750")

    dashboard = DashboardPage(app)
    dashboard.pack(fill="both", expand=True)

    app.mainloop()