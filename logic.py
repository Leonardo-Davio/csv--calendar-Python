import json
import re
import uuid
from datetime import datetime
import os
import csv

class LessonManager:
    def __init__(self, csv_path=None):
        self.csv_data = []
        self.room_map = {}
        self.course_map = {}
        self.file_path = csv_path
        self.load_room_map()

    def load_csv(self, path):
        with open(path, newline='', encoding='utf-8') as csvfile:
            self.csv_data = list(csv.reader(csvfile, delimiter=';'))
        self.file_path = path
        self.load_room_map()
        self.load_course_map()

    def load_room_map(self):
        local_dir = os.path.dirname(os.path.abspath(__file__))
        out_path = os.path.join(local_dir, "room_map.json")
        if os.path.exists(out_path):
            try:
                with open(out_path, "r", encoding="utf-8") as f:
                    self.room_map = json.load(f)
            except Exception:
                self.room_map = {}
        else:
            self.room_map = {}

    def load_course_map(self):
        if self.file_path:
            map_path = os.path.splitext(self.file_path)[0] + "_course_map.json"
            if os.path.exists(map_path):
                with open(map_path, "r", encoding="utf-8") as f:
                    self.course_map = json.load(f)
            else:
                self.course_map = {}

    def get_courses(self):
        courses = set()
        for row in self.csv_data[6:]:
            if len(row) > 2:
                course = row[2].split('-')[0].strip() if row[2] else None
                if course and course.lower() != "insegnamento":
                    course = course.title()
                    courses.add(course)
        return sorted(courses)

    def extract_location_abbreviation(self, raw_loc):
        # Extract location abbreviation from room_map.json or fallback to full name
        # Extract location part (inside [...]), e.g., [C.Didat.Morgagni (Piano Terra)]
        location_abbr = ""
        m = re.search(r"\[([^]]+)]", raw_loc)
        if m:
            full_location = m.group(1).split('(')[0].strip()
            location_abbr = self.room_map.get(full_location, full_location)
        return location_abbr

    def extract_aula_abbreviation(self, raw_loc):
        # Auditorium A/B
        if "Auditorium A" in raw_loc:
            return self.room_map.get("Auditorium A", "Aud A")
        elif "Auditorium B" in raw_loc:
            return self.room_map.get("Auditorium B", "Aud B")
        # Aula number
        n = re.search(r"Aula\s*([0-9]+)", raw_loc)
        if n:
            return n.group(1)
        # Other room types? Add more custom logic here if needed
        return ""

    def extract_full_room_string(self, raw_loc):
        # Returns a string with location abbreviation + aula abbreviation (e.g., "CDm 001" or "CDm Aud A")
        location_abbr = self.extract_location_abbreviation(raw_loc)
        aula_abbr = self.extract_aula_abbreviation(raw_loc)
        if location_abbr and aula_abbr:
            return f"{location_abbr} {aula_abbr}"
        elif location_abbr:
            return location_abbr
        elif aula_abbr:
            return aula_abbr
        else:
            # Fallback: try to get something meaningful
            m = re.search(r"Aula\s*([0-9]+)", raw_loc)
            if m:
                return m.group(1)
            return raw_loc

    def get_rooms_for_subject(self, subject):
        rooms = set()
        for row in self.csv_data[6:]:
            if len(row) > 5:
                course = row[2].split('-')[0].strip() if row[2] else None
                course = course.title()
                if course == subject:
                    venue = self.extract_full_room_string(row[5])
                    rooms.add(venue)
        return sorted(rooms)

    def set_room_map(self, room_map):
        self.room_map.update(room_map)
        self.save_room_map()

    def set_course_map(self, course_map):
        self.course_map = dict(course_map)
        self.save_course_map()

    def save_room_map(self):
        local_dir = os.path.dirname(os.path.abspath(__file__))
        out_path = os.path.join(local_dir, "room_map.json")
        if os.path.exists(out_path):
            try:
                with open(out_path, "r", encoding="utf-8") as f:
                    existing_map = json.load(f)
            except Exception:
                existing_map = {}
        else:
            existing_map = {}

        for key, value in self.room_map.items():
            existing_map[key] = value

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(existing_map, f, indent=2, ensure_ascii=False)
        self.room_map = existing_map
        return out_path

    def save_course_map(self):
        if self.file_path:
            out_path = os.path.splitext(self.file_path)[0] + "_course_map.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(self.course_map, f, indent=2, ensure_ascii=False)
            return out_path
        return None

    def get_display_room_name(self, room):
        return self.room_map.get(room, room)

    def generate_ics_for_subject(self, subject, dest_path=None):
        events = []
        for row in self.csv_data[6:]:
            if len(row) > 5:
                course_orig = row[2].split('-')[0].strip() if row[2] else None
                course = course_orig.title()
                if course != subject:
                    continue
                date = row[0].strip()
                time_range = row[1].strip()
                room_raw = row[5].strip()
                venue = self.extract_full_room_string(room_raw)
                course_name = self.course_map.get(venue, course)
                times = [t.strip() for t in time_range.split("-")]
                start_t = times[0]
                end_t = times[1] if len(times) > 1 else ""
                try:
                    dt_start = datetime.strptime(f"{date} {start_t}", "%d-%m-%Y %H:%M")
                    dt_end = datetime.strptime(f"{date} {end_t}", "%d-%m-%Y %H:%M")
                except ValueError:
                    # Skip rows with invalid dates/times
                    continue
                dtstart_ics = dt_start.strftime("%Y%m%dT%H%M%S")
                dtend_ics = dt_end.strftime("%Y%m%dT%H%M%S")
                summary = f"{course_name} - {venue}".strip()
                event = [
                    "BEGIN:VEVENT",
                    f"UID:{str(uuid.uuid4())}@roomrenamer.local",
                    f"SUMMARY:{summary}",
                    f"DTSTART:{dtstart_ics}",
                    f"DTEND:{dtend_ics}",
                    "END:VEVENT"
                ]
                events.extend(event)
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//RoomRenamerApp//IT"
        ]
        ics_lines.extend(events)
        ics_lines.append("END:VCALENDAR")
        if dest_path:
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write("\n".join(ics_lines))
            return dest_path
        if self.file_path:
            out_path = os.path.splitext(self.file_path)[0] + f"_{subject.replace(' ', '_')}.ics"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(ics_lines))
            return out_path
        return None