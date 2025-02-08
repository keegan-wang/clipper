import os
import json
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QGridLayout,
    QFileDialog, QListWidget, QTabWidget, QLineEdit, QListWidgetItem, QProgressBar, QCheckBox, QStackedWidget
)
from PyQt5.QtWidgets import QListWidgetItem, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSlot
from moviepy.editor import AudioFileClip
from moviepy.editor import VideoFileClip
import subprocess


class VideoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Processing App")
        self.resize(1000, 600)

        # Create the tab widget
        self.tabs = QTabWidget()

        # Initialize each tab
        self.uploadTab = QWidget()
        self.searchTab = QWidget()
        self.editTab = QWidget()

        # Add tabs to the tab widget
        self.tabs.addTab(self.uploadTab, "Upload Videos")
        self.tabs.addTab(self.searchTab, "Search Metadata")
        self.tabs.addTab(self.editTab, "Edit Video")

        # Set up each tab's layout
        self.initUploadTab()
        self.initSearchTab()
        self.initEditTab()

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def initUploadTab(self):
        layout = QVBoxLayout()

        self.toggleButton = QPushButton("Switch to Gallery View")
        self.toggleButton.clicked.connect(self.toggleView)

        self.uploadButton = QPushButton("Upload Videos")
        self.uploadButton.clicked.connect(self.uploadVideos)

        # Stacked widget to hold list and gallery views
        self.viewStack = QStackedWidget()

        # List view (default)
        self.videoList = QListWidget()
        self.viewStack.addWidget(self.videoList)

        # Gallery view
        self.galleryWidget = QWidget()
        self.galleryLayout = QGridLayout()
        self.galleryWidget.setLayout(self.galleryLayout)
        self.viewStack.addWidget(self.galleryWidget)

        # Add widgets to layout
        layout.addWidget(self.uploadButton)
        layout.addWidget(self.toggleButton)
        layout.addWidget(self.viewStack)

        self.uploadTab.setLayout(layout)
        self.currentView = "list"  # Start with list view
        self.populateUploadedVideos()

    def toggleView(self):
        """Switch between list view and gallery view."""
        if self.currentView == "list":
            self.currentView = "gallery"
            self.viewStack.setCurrentWidget(self.galleryWidget)
            self.toggleButton.setText("Switch to List View")
        else:
            self.currentView = "list"
            self.viewStack.setCurrentWidget(self.videoList)
            self.toggleButton.setText("Switch to Gallery View")

    def uploadVideos(self):
        """Upload videos and refresh the views."""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Videos", "", "Video Files (*.mp4 *.mov)")
        clips_folder = "data/clips"

        if files:
            for file in files:
                destination = os.path.join(clips_folder, os.path.basename(file))
                shutil.copy(file, destination)
            self.populateUploadedVideos()

    def populateUploadedVideos(self):
        """Populate the list and gallery views with uploaded videos."""
        self.videoList.clear()
        self.clearGalleryView()

        clips_folder = "data/clips"
        row, col = 0, 0

        for filename in os.listdir(clips_folder):
            if filename.endswith((".mp4", ".mov")):
                video_path = os.path.join(clips_folder, filename)

                # ---- List View ----
                self.addListItem(filename)

                # ---- Gallery View ----
                thumbnail_path = self.generateThumbnail(video_path)
                self.addGalleryItem(filename, thumbnail_path, row, col)

                # Update grid position
                col += 1
                if col == 4:  # 4 columns per row
                    col = 0
                    row += 1

    def addListItem(self, filename):
        """Add a video item to the list view."""
        item_widget = QWidget()
        layout = QHBoxLayout()

        video_label = QLabel(filename)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.deleteVideo(filename))

        layout.addWidget(video_label)
        layout.addWidget(delete_button)
        item_widget.setLayout(layout)

        list_item = QListWidgetItem(self.videoList)
        list_item.setSizeHint(item_widget.sizeHint())
        self.videoList.addItem(list_item)
        self.videoList.setItemWidget(list_item, item_widget)

    def addGalleryItem(self, filename, thumbnail_path, row, col):
        """Add a video item to the gallery view."""
        item_widget = QWidget()
        layout = QVBoxLayout()

        thumbnail_label = QLabel()
        pixmap = QPixmap(thumbnail_path)
        thumbnail_label.setPixmap(pixmap.scaled(150, 100, Qt.KeepAspectRatio))

        name_label = QLabel(filename)
        name_label.setAlignment(Qt.AlignCenter)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.deleteVideo(filename))

        layout.addWidget(thumbnail_label)
        layout.addWidget(name_label)
        layout.addWidget(delete_button)
        item_widget.setLayout(layout)

        self.galleryLayout.addWidget(item_widget, row, col)

    def clearGalleryView(self):
        """Clear all items from the gallery view."""
        while self.galleryLayout.count():
            item = self.galleryLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def generateThumbnail(self, video_path):
        """Generate a thumbnail image for a video."""
        thumbnail_folder = "data/thumbnails"
        os.makedirs(thumbnail_folder, exist_ok=True)

        thumbnail_path = os.path.join(thumbnail_folder, os.path.basename(video_path) + ".png")

        if not os.path.exists(thumbnail_path):
            try:
                with VideoFileClip(video_path) as video:
                    frame = video.get_frame(1.0)
                    thumbnail = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                    thumbnail.save(thumbnail_path)
            except Exception as e:
                print(f"Error generating thumbnail for {video_path}: {e}")

        return thumbnail_path

    def deleteVideo(self, filename):
        """Delete the video and remove it from both views."""
        clips_folder = "data/clips"
        file_path = os.path.join(clips_folder, filename)

        if os.path.exists(file_path):
            os.remove(file_path)
            self.populateUploadedVideos()

    # ------------------- Tab 2: Search Metadata -------------------

    def initSearchTab(self):
        layout = QVBoxLayout()

        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("Enter keywords to search for...")
        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.searchMetadata)

        self.searchResults = QListWidget()

        layout.addWidget(QLabel("Search Metadata"))
        layout.addWidget(self.searchInput)
        layout.addWidget(self.searchButton)
        layout.addWidget(self.searchResults)

        self.searchTab.setLayout(layout)

    def searchMetadata(self):
        """Search metadata for videos containing the entered keywords."""
        keyword = self.searchInput.text().lower()
        metadata_folder = "data/metadata"

        self.searchResults.clear()

        for metadata_file in os.listdir(metadata_folder):
            if metadata_file.endswith("_objects.json"):
                with open(os.path.join(metadata_folder, metadata_file), "r") as file:
                    metadata = json.load(file)

                for entry in metadata:
                    detected_objects = [obj.lower() for obj in entry["objects"]]
                    if keyword in detected_objects:
                        result = f"Video: {metadata_file.replace('_objects.json', '.mp4')}, Timestamp: {entry['timestamp']}s"
                        self.searchResults.addItem(result)

    # ------------------- Tab 3: Edit Video -------------------

    def initEditTab(self):
        layout = QVBoxLayout()

        self.scriptTextEdit = QTextEdit()
        self.scriptTextEdit.setPlaceholderText("Enter script...")

        self.videoCheckboxList = QListWidget()

        self.startProcessingButton = QPushButton("Start Processing")
        self.startProcessingButton.clicked.connect(self.startProcessing)

        self.progressBar = QProgressBar()

        layout.addWidget(QLabel("Script"))
        layout.addWidget(self.scriptTextEdit)
        layout.addWidget(QLabel("Select Videos"))
        layout.addWidget(self.videoCheckboxList)
        layout.addWidget(self.startProcessingButton)
        layout.addWidget(self.progressBar)

        self.editTab.setLayout(layout)
        self.populateVideoCheckboxList()

    def populateVideoCheckboxList(self):
        clips_folder = "data/clips"
        self.videoCheckboxList.clear()

        for filename in os.listdir(clips_folder):
            if filename.endswith((".mp4", ".mov")):
                item = QListWidgetItem(filename)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.videoCheckboxList.addItem(item)

    def startProcessing(self):
        """Start the video processing workflow with progress updates."""
        script_text = self.scriptTextEdit.toPlainText().strip()
        selected_videos = [
            item.text() for item in self.videoCheckboxList.findItems("", Qt.MatchContains)
            if item.checkState() == Qt.Checked
        ]

        if not script_text or not selected_videos:
            print("Please provide a script and select videos.")
            self.progressBar.setValue(0)
            return

        # Save the script text
        script_path = "data/script/narration_script.txt"
        os.makedirs("data/script", exist_ok=True)
        with open(script_path, "w") as script_file:
            script_file.write(script_text)

        # Update progress and execute subprocess
        self.progressBar.setValue(10)

        try:
            process = subprocess.run(
                ["python3", "src/main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            self.progressBar.setValue(100)
            print("Processing completed:", process.stdout)

        except subprocess.CalledProcessError as e:
            self.progressBar.setValue(0)
            print(f"Error during processing: {e}")

    def checkAndUpdateMetadata(self):
        """Check if each video has metadata and process missing ones."""
        clips_folder = "data/clips"
        metadata_folder = "data/metadata"
        
        # Ensure folders exist
        os.makedirs(clips_folder, exist_ok=True)
        os.makedirs(metadata_folder, exist_ok=True)

        # Collect videos that are missing metadata
        videos_to_process = []
        
        for video_file in os.listdir(clips_folder):
            if video_file.endswith((".mp4", ".mov")):
                # Define expected metadata filename
                metadata_file = os.path.splitext(video_file)[0] + "_objects.json"
                metadata_path = os.path.join(metadata_folder, metadata_file)

                # Check if metadata exists
                if not os.path.exists(metadata_path):
                    print(f"Metadata missing for: {video_file}")
                    videos_to_process.append(os.path.join(clips_folder, video_file))

        if not videos_to_process:
            print("All videos already have metadata.")
            return

        # Process videos missing metadata
        print(f"Processing {len(videos_to_process)} videos without metadata...")

        try:
            for video in videos_to_process:
                print(f"Running scene detection on {video}...")
                # Call scene detection with the video path
                subprocess.run(["python3", "src/sceneDetection.py", video], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"Completed scene detection for {video}")

        except subprocess.CalledProcessError as e:
            print(f"Error during scene detection: {e}")
            print(f"Standard Output: {e.stdout}")
            print(f"Standard Error: {e.stderr}")

    # ------------------- Cleanup on Close -------------------

    def closeEvent(self, event):
        """Handle cleanup when the app is closed."""
        self.cleanup_data()
        event.accept()

    def cleanup_data(self):
        """Delete the matched_clips.json file on app close."""
        matches_file = "data/matches/matched_clips.json"
        if os.path.exists(matches_file):
            os.remove(matches_file)


if __name__ == "__main__":
    app = QApplication([])
    window = VideoApp()
    window.show()
    app.exec_()
