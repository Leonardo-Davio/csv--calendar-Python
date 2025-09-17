import customtkinter as ctk
from tkinter import filedialog, messagebox
from logic import LessonManager
import re

def to_camel_case(s):
    parts = re.split(r"\s+", s.strip())
    return ''.join(word.capitalize() for word in parts)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

manager = LessonManager()
courses = []
selected_subject = ""
room_vars = {}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🗓️  Crea calendario da CSV")
        self.geometry("600x550")
        self.resizable(False, False)

        # Frame centrale (card look)
        self.card = ctk.CTkFrame(self, corner_radius=20)
        self.card.pack(padx=20, pady=10, fill="both", expand=True)

        # Titolo
        title_label = ctk.CTkLabel(self.card, text="Crea calendario da CSV", font=("Segoe UI Bold", 22))
        title_label.pack(pady=(20, 5))

        # Seleziona CSV
        self.csv_button = ctk.CTkButton(self.card, text="Seleziona CSV delle lezioni", command=self.load_csv_dialog,
                                        width=220, height=38, font=("Segoe UI", 14))
        self.csv_button.pack(pady=(16, 12))

        # ComboBox Materia
        self.subject_combo = ctk.CTkComboBox(self.card, values=[], state="disabled", command=self.subject_selected,
                                             width=220, font=("Segoe UI", 13))
        self.subject_combo.pack(pady=8)

        # Nome corso personalizzato
        self.custom_course_name = ctk.StringVar(value="")
        name_label = ctk.CTkLabel(self.card, text="Nome corso personalizzato:", font=("Segoe UI", 12))
        name_label.pack(pady=(20, 2))
        self.custom_name_entry = ctk.CTkEntry(self.card, textvariable=self.custom_course_name, width=320,
                                              font=("Segoe UI", 13))
        self.custom_name_entry.pack(pady=(0, 12))

        # Frame sedi
        self.venues_frame = ctk.CTkFrame(self.card, fg_color="#232323", corner_radius=15)
        self.venues_frame.pack(fill="x", padx=8, pady=8)

        # Frame bottoni affiancati
        btn_row = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_row.pack(pady=(18, 0))

        self.ics_button = ctk.CTkButton(btn_row, text="Esporta calendario (.ics)", command=self.export_ics_dialog,
                                        width=190, height=38, font=("Segoe UI", 14))
        self.ics_button.pack(side="left", padx=10)

        self.save_map_button = ctk.CTkButton(btn_row, text="Salva mappa sedi", command=self.save_room_map,
                                             width=190, height=38, font=("Segoe UI", 14))
        self.save_map_button.pack(side="left", padx=10)

        # Label feedback
        self.feedback_label = ctk.CTkLabel(self.card, text="", font=("Segoe UI", 12), text_color="lightgray")
        self.feedback_label.pack(pady=(18, 0))

        # Frame separato per pulsante Esci, ben distanziato
        self.exit_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.exit_frame.pack(fill="x", pady=(32, 0))

        self.exit_button = None

    def show_message(self, msg, title="Messaggio"):
        messagebox.showinfo(title, msg)

    def load_csv_dialog(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            manager.load_csv(file_path)
            global courses
            courses = manager.get_courses()
            self.subject_combo.configure(values=courses, state="normal")
            if courses:
                self.subject_combo.set(courses[0])
                self.subject_selected(courses[0])
        except Exception as e:
            self.show_message(f"Errore nel caricamento del file: {e}", title="Errore")

    def update_venues(self):
        global room_vars
        for widget in self.venues_frame.winfo_children():
            widget.destroy()
        venues = manager.get_rooms_for_subject(selected_subject)
        room_vars.clear()
        for venue in venues:
            saved_name = manager.get_display_room_name(venue)
            var = ctk.StringVar(value=saved_name)
            room_vars[venue] = var

            card_row = ctk.CTkFrame(self.venues_frame, fg_color="transparent")
            card_row.pack(fill="x", pady=4, padx=6)

            label = ctk.CTkLabel(card_row, text=venue, font=("Segoe UI", 11))
            label.pack(side="left", padx=(0, 10))

            entry = ctk.CTkEntry(card_row, textvariable=var, width=150, font=("Segoe UI", 11))
            entry.pack(side="left", padx=3)

    def export_ics_dialog(self):
        room_map = {venue: var.get() for venue, var in room_vars.items()}
        manager.set_room_map(room_map)
        if hasattr(manager, "set_course_map"):
            manager.set_course_map({selected_subject: self.custom_course_name.get()})
        suggested_name = to_camel_case(self.custom_course_name.get()) + ".ics"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ics",
            filetypes=[("ICS files", "*.ics")],
            initialfile=suggested_name
        )
        if not file_path:
            self.feedback_label.configure(text="Nessun file di destinazione selezionato", text_color="#e85353")
            self.hide_exit_button()
            return
        out_path = manager.generate_ics_for_subject(selected_subject, file_path)
        if out_path:
            self.feedback_label.configure(text=f"File calendario esportato in: {out_path}", text_color="#53e853")
            self.show_exit_button()
        else:
            self.feedback_label.configure(text="Errore nell'esportazione del calendario.", text_color="#e85353")
            self.hide_exit_button()

    def save_room_map(self):
        room_map = {venue: var.get() for venue, var in room_vars.items()}
        manager.set_room_map(room_map)
        if hasattr(manager, "set_course_map"):
            manager.set_course_map({selected_subject: self.custom_course_name.get()})
        out_path = manager.save_room_map()
        if out_path:
            self.feedback_label.configure(text=f"Mappa aule salvata.", text_color="#53e853")
        else:
            self.feedback_label.configure(text="Errore nel salvataggio della mappa aule.", text_color="#e85353")

    def show_exit_button(self):
        if self.exit_button is None:
            self.exit_button = ctk.CTkButton(self.exit_frame, text="Esci", command=self.destroy, width=120,
                                             fg_color="#e85353", font=("Segoe UI", 14))
            self.exit_button.pack(pady=(0, 0))
        else:
            self.exit_button.pack(pady=(0, 0))

    def hide_exit_button(self):
        if self.exit_button is not None:
            self.exit_button.pack_forget()

    def subject_selected(self, value):
        global selected_subject
        selected_subject = value
        self.custom_course_name.set(value)
        self.update_venues()
        self.feedback_label.configure(text="")
        self.hide_exit_button()

if __name__ == "__main__":
    app = App()
    app.mainloop()