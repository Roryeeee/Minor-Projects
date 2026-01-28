# 🗃️ File Organizer with PyQt5 GUI

This is a desktop file organizing tool built with **Python** and **PyQt5**, designed to **automatically sort your Downloads folder** based on file type into designated folders like Images, PDFs, Videos, MS Office files, and more. It also comes with a minimal, modern GUI for ease of use.

---

## 🚀 Features

- 📂 **Automatically organizes files** from the `Downloads` folder.
- 🖼️ Sorts files into:
  - Images
  - Installers
  - PDFs
  - Videos
  - MS Office documents
  - Compressed files
  - Others
- 🖥️ PyQt5 GUI with:
  - Start Auto Move (every 30 seconds)
  - Stop Auto Move
  - Move Now (manual one-time trigger)
  - Status indicator
  - Progress bar

---

## 📁 Folder Structure

Files are moved to:

| File Type     | Destination Folder (inside user directory) |
|---------------|---------------------------------------------|
| Images        | `Pictures/Saved Pictures/`                  |
| Installers    | `Downloads/Software installers/`            |
| PDFs          | `Documents/PDFs/`                           |
| Videos        | `Videos/`                                   |
| MS Office     | `Documents/Office/`                         |
| Compressed    | `Downloads/Compressed/`                     |
| Others        | `Downloads/Others/`                         |

---

## 🛠️ How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/Roryeeee/file-organizer.git
cd file-organizer
```
###  2. Install Requirements

```
pip install PyQt5 os shutil time
```
### 3. Run the App
```
python File_organizer.py
```


