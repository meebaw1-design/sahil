# =====================================================
# Sharp Talk Sport Studio
# Project Editor
# STEP 3
# =====================================================

import customtkinter as ctk

from utils.scene_loader import SceneLoader


class ProjectEditor(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent)

        self.loader = None
        self.current_scene = 1

        self.configure(fg_color="#2B2B2B")

        # ------------------------------------------
        # Project Name
        # ------------------------------------------

        self.project_title = ctk.CTkLabel(
            self,
            text="No Project Open",
            font=("Arial", 28, "bold")
        )

        self.project_title.pack(pady=20)

        # ------------------------------------------

        self.content = ctk.CTkFrame(self)

        self.content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # ------------------------------------------
        # Scene Panel
        # ------------------------------------------

        self.left = ctk.CTkFrame(
            self.content,
            width=220
        )

        self.left.pack(
            side="left",
            fill="y",
            padx=10,
            pady=10
        )

        self.left.pack_propagate(False)

        title = ctk.CTkLabel(
            self.left,
            text="Scenes",
            font=("Arial",20,"bold")
        )

        title.pack(pady=15)

        self.scene_buttons = []

        for i in range(1,11):

            btn = ctk.CTkButton(

                self.left,

                text=f"Scene {i:02}",

                command=lambda n=i: self.open_scene(n)

            )

            btn.pack(
                pady=4,
                padx=10
            )

            self.scene_buttons.append(btn)

        # ------------------------------------------
        # Editor
        # ------------------------------------------

        self.right = ctk.CTkFrame(self.content)

        self.right.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        label = ctk.CTkLabel(

            self.right,

            text="Scene Editor",

            font=("Arial",20,"bold")

        )

        label.pack(pady=15)

        self.editor = ctk.CTkTextbox(

            self.right,

            font=("Consolas",15)

        )

        self.editor.pack(

            fill="both",

            expand=True,

            padx=15,

            pady=10

        )

        self.save_button = ctk.CTkButton(

            self.right,

            text="💾 Save Scene",

            command=self.save_scene

        )

        self.save_button.pack(pady=15)

    # =================================================

    def load_project(self, project_name):

        self.project_title.configure(

            text=project_name

        )

        folder = f"projects/{project_name}"

        self.loader = SceneLoader(folder)

        self.open_scene(1)

    # =================================================

    def open_scene(self, scene):

        if self.loader is None:

            return

        self.current_scene = scene

        text = self.loader.load_scene(scene)

        self.editor.delete("1.0","end")

        self.editor.insert("1.0",text)

    # =================================================

    def save_scene(self):

        if self.loader is None:

            return

        text = self.editor.get("1.0","end")

        self.loader.save_scene(

            self.current_scene,

            text

        )