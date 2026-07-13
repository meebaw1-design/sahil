import customtkinter as ctk

from pages.dashboard import DashboardPage
from pages.projects import ProjectsPage
from pages.new_project import NewProjectWindow
from pages.project_editor import ProjectEditor
from pages.google_flow import GoogleFlowPage
from pages.api_settings import APISettingsPage

from utils.project_creator import create_project


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SharpTalkStudio(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("⚽ Sharp Talk Sport Studio v1.0")
        self.geometry("1400x800")
        self.minsize(1200, 700)

        self.current_project = "None"
        self.current_page = "Dashboard"

        self.create_sidebar()
        self.create_main_area()
        self.create_status_bar()
        self.load_pages()
        self.connect_buttons()
        self.show_dashboard()

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")

        logo = ctk.CTkLabel(
            self.sidebar,
            text="⚽ Sharp Talk",
            font=("Arial", 24, "bold")
        )
        logo.pack(pady=(30, 40))

        dashboard_button = ctk.CTkButton(
            self.sidebar,
            text="🏠 Dashboard",
            command=self.show_dashboard
        )
        dashboard_button.pack(padx=15, pady=8, fill="x")

        projects_button = ctk.CTkButton(
            self.sidebar,
            text="📁 Projects",
            command=self.show_projects
        )
        projects_button.pack(padx=15, pady=8, fill="x")

        flow_button = ctk.CTkButton(
            self.sidebar,
            text="🌐 Google Flow",
            command=self.show_google_flow
        )
        flow_button.pack(padx=15, pady=8, fill="x")

        api_button = ctk.CTkButton(
            self.sidebar,
            text="🔑 API Settings",
            command=self.show_api_settings
        )
        api_button.pack(padx=15, pady=8, fill="x")

        settings_button = ctk.CTkButton(
            self.sidebar,
            text="⚙ Settings",
            state="disabled"
        )
        settings_button.pack(padx=15, pady=8, fill="x")

        version_label = ctk.CTkLabel(
            self.sidebar,
            text="Version 1.0",
            font=("Arial", 13)
        )
        version_label.pack(side="bottom", pady=20)

    def create_main_area(self):

        self.right_area = ctk.CTkFrame(
            self,
            fg_color="#2B2B2B"
        )
        self.right_area.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.main_area = ctk.CTkFrame(
            self.right_area,
            fg_color="#2B2B2B"
        )
        self.main_area.pack(
            fill="both",
            expand=True
        )

    def create_status_bar(self):

        self.status_bar = ctk.CTkFrame(
            self.right_area,
            height=35,
            corner_radius=0
        )
        self.status_bar.pack(
            side="bottom",
            fill="x"
        )

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready | Page: Dashboard | Project: None | Sharp Talk Sport Studio v1.0",
            font=("Arial", 13)
        )
        self.status_label.pack(side="left", padx=15)

    def update_status(self, page=None, project=None):

        if page is not None:
            self.current_page = page

        if project is not None:
            self.current_project = project

        self.status_label.configure(
            text=f"Ready | Page: {self.current_page} | Project: {self.current_project} | Sharp Talk Sport Studio v1.0"
        )

    def load_pages(self):

        self.dashboard_page = DashboardPage(self.main_area)
        self.projects_page = ProjectsPage(self.main_area)
        self.project_editor_page = ProjectEditor(self.main_area)
        self.google_flow_page = GoogleFlowPage(self.main_area)
        self.api_settings_page = APISettingsPage(self.main_area)

    def connect_buttons(self):

        self.projects_page.new_project_button.configure(
            command=self.open_new_project
        )

        self.projects_page.project_callback = self.open_project_editor

    def open_new_project(self):

        NewProjectWindow(
            self,
            self.create_new_project
        )

    def create_new_project(self, project_name):

        create_project(
            "projects",
            project_name
        )

        self.current_project = project_name

        dialog = ctk.CTkToplevel(self)
        dialog.title("Success")
        dialog.geometry("350x180")
        dialog.grab_set()

        label = ctk.CTkLabel(
            dialog,
            text=f"✅\n\n{project_name}\n\nProject Created Successfully!",
            justify="center",
            font=("Arial", 18)
        )
        label.pack(expand=True)

        self.update_status(
            page="Projects",
            project=project_name
        )

    def hide_pages(self):

        self.dashboard_page.pack_forget()
        self.projects_page.pack_forget()
        self.project_editor_page.pack_forget()
        self.google_flow_page.pack_forget()
        self.api_settings_page.pack_forget()

    def show_dashboard(self):

        self.hide_pages()

        self.dashboard_page.update_stats()
        self.dashboard_page.update_progress()
        self.dashboard_page.update_production_dashboard()

        self.dashboard_page.pack(
            fill="both",
            expand=True
        )

        self.update_status(page="Dashboard")

    def show_projects(self):

        self.hide_pages()

        self.projects_page.load_recent_projects()

        self.projects_page.pack(
            fill="both",
            expand=True
        )

        self.update_status(page="Projects")

    def show_google_flow(self):

        self.hide_pages()

        self.google_flow_page.refresh_status()

        self.google_flow_page.pack(
            fill="both",
            expand=True
        )

        self.update_status(page="Google Flow")

    def show_api_settings(self):

        self.hide_pages()

        self.api_settings_page.refresh_status()

        self.api_settings_page.pack(
            fill="both",
            expand=True
        )

        self.update_status(page="API Settings")

    def open_project_editor(self, project_name):

        self.hide_pages()

        self.project_editor_page.load_project(project_name)

        self.project_editor_page.pack(
            fill="both",
            expand=True
        )

        self.update_status(
            page="Project Editor",
            project=project_name
        )


if __name__ == "__main__":

    app = SharpTalkStudio()
    app.mainloop()