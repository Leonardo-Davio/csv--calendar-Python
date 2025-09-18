# csv--calendar-Python (Windows Executable)

A graphical tool to create calendar files (.ics) from CSV exports of lessons/events from Kairos Unifi (University of Florence).

## Download

Download the Windows executable (`gui.exe`) from the [v1.0 Release page](https://github.com/Leonardo-Davio/csv--calendar-Python/releases/tag/v1.0).

No installation or Python required.  
Just double-click `gui.exe` to start the application.

## How to Use

1. **Open** `gui.exe`.
2. **Select** your CSV file exported from Kairos Unifi.
3. **Choose** the subject/course to export.
4. **Optionally**, customize course and room names.
5. **Click** **Export calendar (.ics)** to save your calendar file.

## Supported CSV Format (Kairos Unifi Export)

Your CSV should follow the structure exported by the Kairos Unifi website. The file has several header rows and then a table of lessons/events.  
**Typical Example:**
The firts 5 rows are:
```csv
Anno accademico: 2025/2026,,,,,,
Corso di Studio: INGEGNERIA INFORMATICA (Laurea),,,,,,
Anno di Studio: 1 - TECNICO SCIENTIFICO,,,,,,
,,,,,,
,,,,,,
```
From the 6 row:  
```
| Giorno    | Ora    | Insegnamento    | Docente    | Percorso didattico    | Aula e sede    | Note    |
```
Where the **Column Meaning:**

| Column                | Example Value                       | Description                                           |
|-----------------------|-------------------------------------|-------------------------------------------------------|
| Giorno                | 15-09-2025                          | Date of the lesson/event (DD-MM-YYYY)                 |
| Ora                   | 11:15 - 13:15                       | Time range (start - end, HH:MM - HH:MM)               |
| Insegnamento          | ANALISI MATEMATICA I - B******      | Subject name and code                                 |
| Docente               | MARIO ROSSI                         | Teacher name (ignored by the application)             |
| Percorso didattico    | INGEGNERIA INFORMATICA [...]        | Degree program, year, study path                      |
| Aula e sede           | Aula 001 [C.Didat.Morgagni (...)]   | Room and location                                     |
| Note                  | (empty or text)                     | Additional notes                                      |

**How to Export from Kairos Unifi:**
1. Go to your course calendar on Kairos Unifi.
2. Use the export option to download the CSV.
3. Use this file directly with the application.

## Frequently Asked Questions

**Q:** Do I need Python installed?  
**A:** No. This executable works out-of-the-box on Windows.

**Q:** Where is my exported calendar?  
**A:** You choose the save location when exporting. The result is a `.ics` file.

**Q:** What if my CSV format is different?  
**A:** The application is designed for the default Kairos Unifi export (see example above).

## Credits

Developed by Leonardo Davio  
Original repository: [csv--calendar-Python](https://github.com/Leonardo-Davio/csv--calendar-Python)

## License

MIT License

---

If you have problems, open an issue on the [GitHub repository](https://github.com/Leonardo-Davio/csv--calendar-Python/issues).
