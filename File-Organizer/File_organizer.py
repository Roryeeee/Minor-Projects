import os
import shutil
import threading
import time
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox, QHBoxLayout, QProgressBar
from PyQt5.QtGui import QIcon, QFont

# Get the current user's home directory
user_home_dir = os.path.expanduser("~")

# ----- Folder Paths (Modify these as needed) -----
download_fdr = os.path.join(user_home_dir, "Downloads")

destination_fdr = {
    'images': os.path.join(user_home_dir, "Pictures", "Saved Pictures"),
    'installers': os.path.join(user_home_dir, "Downloads", "Software installers"),
    'pdfs': os.path.join(user_home_dir, "Documents", "PDFs"),
    'videos': os.path.join(user_home_dir, "Videos"),
    'MS office': os.path.join(user_home_dir, "Documents", "Office"),
    'wps_files': os.path.join(user_home_dir, "Documents", "WPS Files"),
    'cad_files': os.path.join(user_home_dir, "Documents", "CAD Files"),
    'others': os.path.join(user_home_dir, "Downloads", "Others"),
    'Compressed': os.path.join(user_home_dir, "Downloads", "Compressed")
}

file_type = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    'installers': ['.exe', '.dmg', '.apk', '.msi', '.sh'],
    'pdfs': ['.pdf'],
    'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
    'MS office': ['.doc', '.docx', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'],
    'wps_files': ['.wps'],
    'cad_files': ['.dwg', '.dxf'],
    'Compressed': ['.zip', '.rar', '.7z', '.tar', '.gz']
}

# ----- Core Logic -----
def move_file(sou, dest_folder):
    filename = os.path.basename(sou)
    dest_path = os.path.join(dest_folder, filename)

    # Create the folder if it does not exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # Create folder

    # Skip the file if it already exists in destination
    if os.path.exists(dest_path):
        print(f"Skipped: {dest_path} already exists.")
        return

    try:
        shutil.move(sou, dest_folder)
        print(f"Moved: {sou} -> {dest_folder}")
    except Exception as e:
        print(f"Error moving file {sou} to {dest_folder}: {e}")

def move_files():
    for filename in os.listdir(download_fdr):
        file_path = os.path.join(download_fdr, filename)
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(filename)[1].lower()

            moved = False
            for file_types, extensions in file_type.items():
                if file_extension in extensions:
                    destination_dir = destination_fdr[file_types]
                    move_file(file_path, destination_dir)
                    moved = True
                    break

            if not moved:
                move_file(file_path, destination_fdr['others'])

# ----- PyQt5 GUI -----
class FileOrganizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.running = False
        self.setWindowTitle("File Organizer")
        self.setGeometry(100, 100, 400, 250)
        self.setStyleSheet("background-color: #000000; color: #ffffff;")

        self.init_ui()

    def init_ui(self):
        font = QFont('Arial', 12)

        # Layouts
        main_layout = QVBoxLayout()

        # Header
        header = QLabel("File Organizer", self)
        header.setFont(QFont('Arial', 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Status Layout
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setFont(font)
        self.status_indicator = QLabel("⭕")
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)

        # Buttons with minimalistic black design
        self.start_button = QPushButton("Start Auto Move", self)
        self.start_button.setStyleSheet("background-color: #000000; color: white; border-radius: 15px; padding: 12px 24px; border: 2px solid #ffffff;")
        self.start_button.setFont(font)
        self.start_button.clicked.connect(self.start_auto_move)
        main_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Auto Move", self)
        self.stop_button.setStyleSheet("background-color: #000000; color: white; border-radius: 15px; padding: 12px 24px; border: 2px solid #ffffff;")
        self.stop_button.setFont(font)
        self.stop_button.clicked.connect(self.stop_auto_move)
        main_layout.addWidget(self.stop_button)

        self.move_now_button = QPushButton("Move Now", self)
        self.move_now_button.setStyleSheet("background-color: #000000; color: white; border-radius: 15px; padding: 12px 24px; border: 2px solid #ffffff;")
        self.move_now_button.setFont(font)
        self.move_now_button.clicked.connect(self.move_now)
        main_layout.addWidget(self.move_now_button)

        # Progress bar for feedback
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)

    def start_auto_move(self):
        self.running = True
        self.status_label.setText("Status: Running")
        self.status_indicator.setText("🔄")
        threading.Thread(target=self.auto_move_loop, daemon=True).start()

    def stop_auto_move(self):
        self.running = False
        self.status_label.setText("Status: Stopped")
        self.status_indicator.setText("⭕")

    def auto_move_loop(self):
        while self.running:
            move_files()
            time.sleep(30)
            self.update_progress(50)  # Show progress bar as files are being moved
        self.update_progress(100)  # Finish progress

    def move_now(self):
        move_files()
        QMessageBox.information(self, "Done", "Files moved successfully!")
        self.update_progress(100)  # Finish progress after moving files

    def update_progress(self, value):
        self.progress_bar.setValue(value)

# Main program to run the PyQt app
if __name__ == "__main__":
    app = QApplication([])
    window = FileOrganizerApp()
    window.show()
    app.exec_()
