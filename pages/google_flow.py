import customtkinter as ctk

from utils.google_flow_manager import (
    open_google_flow,
    verify_connection,
    disconnect_flow,
    load_status
)

from utils.project_list import get_projects
from utils.prompt_generator import create_prompt_package


class GoogleFlowPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        self.configure(fg_color="#2B2B2B")

        title = ctk.CTkLabel(
            self,
            text="🌐 Google Flow",
            font=("Arial", 32, "bold")
        )
        title.pack(pady=(25, 10))

        subtitle = ctk.CTkLabel(
            self,
            text="Generate Google Flow prompt packages for your football videos",
            font=("Arial", 17)
        )
        subtitle.pack(pady=5)

        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Checking...",
            font=("Arial", 20, "bold")
        )
        self.status_label.pack(pady=15)

        # -----------------------------
        # Prompt Generator Box
        # -----------------------------

        prompt_box = ctk.CTkFrame(self, width=650, height=260)
        prompt_box.pack(pady=15)
        prompt_box.pack_propagate(False)

        prompt_title = ctk.CTkLabel(
            prompt_box,
            text="🎬 Prompt Package Generator",
            font=("Arial", 20, "bold")
        )
        prompt_title.pack(pady=(15, 10))

        projects = get_projects()

        if len(projects) == 0:
            projects = ["No Projects Found"]

        self.project_menu = ctk.CTkOptionMenu(
            prompt_box,
            values=projects,
            width=350
        )
        self.project_menu.pack(pady=8)

        self.video_title_entry = ctk.CTkEntry(
            prompt_box,
            width=350,
            placeholder_text="Video title, e.g. Premier League Final Tactical Prediction"
        )
        self.video_title_entry.pack(pady=8)

        self.duration_menu = ctk.CTkOptionMenu(
            prompt_box,
            values=["40 seconds", "60 seconds", "90 seconds", "3 minutes"],
            width=350
        )
        self.duration_menu.pack(pady=8)

        generate_button = ctk.CTkButton(
            prompt_box,
            text="✨ Generate Prompt Package",
            width=260,
            height=40,
            command=self.generate_prompt_package
        )
        generate_button.pack(pady=12)

        self.prompt_result_label = ctk.CTkLabel(
            self,
            text="Prompt Status: Waiting",
            font=("Arial", 15)
        )
        self.prompt_result_label.pack(pady=8)

        # -----------------------------
        # Google Flow Connection Buttons
        # -----------------------------

        open_button = ctk.CTkButton(
            self,
            text="🌐 Open Google Flow",
            width=260,
            height=40,
            command=self.open_flow
        )
        open_button.pack(pady=8)

        verify_button = ctk.CTkButton(
            self,
            text="✅ I Have Logged In",
            width=260,
            height=40,
            command=self.verify
        )
        verify_button.pack(pady=8)

        disconnect_button = ctk.CTkButton(
            self,
            text="Disconnect",
            width=260,
            height=38,
            command=self.disconnect
        )
        disconnect_button.pack(pady=8)

        self.info_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 15),
            justify="left"
        )
        self.info_label.pack(pady=18)

        self.refresh_status()

    def open_flow(self):
        open_google_flow()

    def verify(self):
        verify_connection()
        self.refresh_status()

    def disconnect(self):
        disconnect_flow()
        self.refresh_status()

    def refresh_status(self):
        status = load_status()

        if status["connected"]:
            self.status_label.configure(
                text="🟢 Connected to Google Flow"
            )
        else:
            self.status_label.configure(
                text="🔴 Not Connected"
            )

        self.info_label.configure(
            text=(
                f"Service: {status['service']}\n\n"
                f"Credits: {status['credits']}\n\n"
                f"Queue: {status['queue']}"
            )
        )

    def generate_prompt_package(self):

        project_name = self.project_menu.get()
        video_title = self.video_title_entry.get().strip()
        duration = self.duration_menu.get()

        if project_name == "No Projects Found":
            self.prompt_result_label.configure(
                text="❌ No project selected"
            )
            return

        if video_title == "":
            video_title = project_name + " Football Analysis"

        folder = create_prompt_package(
            project_name,
            video_title,
            duration
        )

        self.prompt_result_label.configure(
            text=f"✅ Prompt package created:\n{folder}"
        )