# =====================================================
# Sharp Talk Sport Studio
# API Settings Page
# Phase 3 Step 3C
# =====================================================

import customtkinter as ctk

from utils.api_key_manager import (
    save_api_key,
    get_status
)

from utils.gemini_connection import test_gemini_connection


class APISettingsPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        self.configure(fg_color="#2B2B2B")

        title = ctk.CTkLabel(
            self,
            text="🔑 Gemini API Settings",
            font=("Arial", 32, "bold")
        )
        title.pack(pady=(45, 15))

        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Checking...",
            font=("Arial", 20, "bold")
        )
        self.status_label.pack(pady=15)

        self.api_entry = ctk.CTkEntry(
            self,
            width=500,
            show="*",
            placeholder_text="Paste your Gemini API key here"
        )
        self.api_entry.pack(pady=12)

        save_button = ctk.CTkButton(
            self,
            text="💾 Save API Key",
            width=250,
            height=42,
            command=self.save_key
        )
        save_button.pack(pady=10)

        test_button = ctk.CTkButton(
            self,
            text="🧪 Test Gemini Connection",
            width=250,
            height=42,
            command=self.test_connection
        )
        test_button.pack(pady=10)

        self.test_result_label = ctk.CTkLabel(
            self,
            text="Connection Test: Not tested yet",
            font=("Arial", 16)
        )
        self.test_result_label.pack(pady=18)

        note = ctk.CTkLabel(
            self,
            text="Your API key is saved locally on your computer.\nDo not share it in chat.",
            font=("Arial", 15),
            justify="center"
        )
        note.pack(pady=20)

        self.refresh_status()

    def save_key(self):

        key = self.api_entry.get().strip()

        save_api_key(key)

        self.api_entry.delete(0, "end")

        self.refresh_status()

        self.test_result_label.configure(
            text="Connection Test: Not tested yet"
        )

    def refresh_status(self):

        status = get_status()

        if status == "Configured":
            self.status_label.configure(
                text="🟢 Status: Configured"
            )
        else:
            self.status_label.configure(
                text="🔴 Status: Not Configured"
            )

    def test_connection(self):

        self.test_result_label.configure(
            text="Testing Gemini connection..."
        )

        success, message = test_gemini_connection()

        if success:
            self.test_result_label.configure(
                text=f"🟢 {message}"
            )
        else:
            self.test_result_label.configure(
                text=f"🔴 {message}"
            )