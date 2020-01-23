import sys, os, vlc, time
from PyQt5.QtWidgets import  QStyleFactory, QApplication, QMainWindow, QFileDialog, QMessageBox, QFrame
from PyQt5.QtGui import QPalette, QColor, QPixmap, QIcon
from PyQt5.QtCore import Qt, QDir, QTimer
from hydra_ui import Ui_hydraMainWindow


class Hydra(QMainWindow):
    """
    This is the hydra video player class
    """

    def __init__(self):
        super().__init__()
        self.ui = Ui_hydraMainWindow()
        self.ui.setupUi(self)
        # create a timer for updating the user interface
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update)
        # load  icons
        self.play_icon = QIcon(QPixmap(self.resource_path('play.png')))
        self.pause_icon = QIcon(QPixmap(self.resource_path('pause.gif')))
        self.repeat_on_icon = QIcon(QPixmap(self.resource_path('repeat_on.png')))
        self.repeat_off_icon = QIcon(QPixmap(self.resource_path('repeat_off.png')))
        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()
        # set the video to play on when opened and create a checker if a video is opened
        # and set stop button click checker
        self.isPaused = False
        self.video_opened = False
        self.stop_clicked = False
        # initialize playlist and its selected index
        self.playlist = []
        self.playlist_current_index = 0
        # connect buttons to actions
        self.ui.openMediaButton.clicked.connect(self.open_file)
        self.ui.playPauseButton.clicked.connect(self.play_pause)
        self.ui.stopButton.clicked.connect(self.manual_stop)
        self.ui.volumeSlider.valueChanged.connect(self.set_volume)
        self.ui.progressSlider.sliderMoved.connect(self.set_position)
        self.ui.repeatButton.toggled.connect(self.visualize_repeat_state)
        self.ui.openPlaylistButton.clicked.connect(self.open_playlist)
        self.ui.previousMediaButton.clicked.connect(self.previous_media)
        self.ui.nextMediaButton.clicked.connect(self.next_media)

    def play(self):
        """
        This method plays the media
        """
        self.stop_clicked = False
        self.mediaplayer.play()
        self.ui.playPauseButton.setIcon(self.pause_icon)
        self.ui.playPauseButton.setToolTip('Pause (SPACE BAR)')
        self.timer.start()
        self.isPaused = False

    def pause(self):
        """
        This method pauses playback
        """
        self.mediaplayer.pause()
        self.ui.playPauseButton.setIcon(self.play_icon)
        self.ui.playPauseButton.setToolTip('Play (SPACE BAR)')
        self.isPaused = True

    def play_pause(self):
        """
        This method pauses or plays playback as appropriate
        """
        if self.video_opened:
            if self.mediaplayer.is_playing():
                self.pause()
            else:
                self.play()

    def forward(self):
        """
        This method moves the video forward by 5 secs
        """
        try:
            # if the current time is equal to 5 secs less than the total duration,
            # ignore action else increase the time by 5 secs
            if self.mediaplayer.get_time() >= self.media.get_duration() - 5000:
                return
            else:
                self.mediaplayer.set_time(self.mediaplayer.get_time() + 5000)
        except:
            pass

    def backward(self):
        """
        This method moves the video backward by 5 secs
        """
        try:
            # if the current time is less than 5 secs set the time to 0
            # else reduce the current time by 5 secs
            if self.mediaplayer.get_time() < 5000:
                self.mediaplayer.set_time(0)
            else:
                self.mediaplayer.set_time(self.mediaplayer.get_time() - 5000)
        except:
            pass

    def open_file(self):
        """
        This method opens a media file
        """
        try:
            options = QFileDialog.Options()
            filename = QFileDialog.getOpenFileName(self, "Open File", QDir.homePath(), options=options)[0]
            if filename:
                # clear the playlist if any
                self.clear_playlist()
                # create the media
                if sys.version < '3':
                    filename = unicode(filename)
                self.media = self.instance.media_new(filename)
                # put the media in the media player
                self.mediaplayer.set_media(self.media)
                # parse the metadata of the file
                self.media.parse()
                # set the title of the track as window title
                self.setWindowTitle(self.media.get_meta(0))
                # set the duration of the media into the duration label
                self.ui.totalDurationLabel.setText(time.strftime('%H:%M:%S', time.localtime(self.media.get_duration() / 1000)))
                # give the id of the QFrame (or similar object) to vlc, different platforms
                # have different functions for this
                if sys.platform.startswith('linux'): # for Linux using the X Server
                    self.mediaplayer.set_xwindow(self.ui.videoFrame.winId())
                    self.mediaplayer.get_xwindow()
                elif sys.platform == "win32": # for Windows
                    self.mediaplayer.set_hwnd(self.ui.videoFrame.winId())
                elif sys.platform == "darwin": # for MacOS
                    self.mediaplayer.set_nsobject(int(self.videoFrame.winId()))
                # notify that a video file is loaded
                self.video_opened = True
                # start playing the media file
                self.play()
        except:
            QMessageBox.critical(self, 'Error', 'Unable to load file')

    def open_playlist(self):
        """
        This method opens a playlist
        """
        try:
            options = QFileDialog.Options()
            filenames = QFileDialog.getOpenFileNames(self, "Select media files", QDir.homePath(), options=options)[0]
            if filenames:
                if len(filenames) > 1:
                    # clear the playlist before adding new one
                    self.clear_playlist()
                    self.playlist = filenames
                    # create the media
                    filename = self.playlist[self.playlist_current_index]
                    if sys.version < '3':
                        filename = unicode(filename)
                    self.media = self.instance.media_new(filename)
                    # put the media in the media player
                    self.mediaplayer.set_media(self.media)
                    # parse the metadata of the file
                    self.media.parse()
                    # set the title of the track as window title
                    self.setWindowTitle(self.media.get_meta(0))
                    # set the duration of the media into the duration label
                    self.ui.totalDurationLabel.setText(time.strftime('%H:%M:%S', time.localtime(self.media.get_duration() / 1000)))
                    # give the id of the QFrame (or similar object) to vlc, different platforms
                    # have different functions for this
                    if sys.platform.startswith('linux'): # for Linux using the X Server
                        self.mediaplayer.set_xwindow(self.ui.videoFrame.winId())
                    elif sys.platform == "win32": # for Windows
                        self.mediaplayer.set_hwnd(self.ui.videoFrame.winId())
                    elif sys.platform == "darwin": # for MacOS
                        self.mediaplayer.set_nsobject(int(self.videoFrame.winId()))
                    # notify that a video file is loaded
                    self.video_opened = True
                    # start playing the media file
                    self.play()
                else:
                    QMessageBox.information(self, 'Notification', 'Playlist must contain more than one media file')
        except:
            QMessageBox.critical(self, 'Error', 'Unable to load file')

    def next_media(self):
        """
        This method plays the next video on the playlist
        """
        if len(self.playlist) > 0:
            # if there are more videos on the playlist, select the next else play the current video
            if self.playlist_current_index < len(self.playlist) - 1:
                # get the next media index
                self.playlist_current_index += 1
                # create the media
                filename = self.playlist[self.playlist_current_index]
                if sys.version < '3':
                    filename = unicode(filename)
                self.media = self.instance.media_new(filename)
                # put the media in the media player
                self.mediaplayer.set_media(self.media)
                # parse the metadata of the file
                self.media.parse()
                # set the title of the track as window title
                self.setWindowTitle(self.media.get_meta(0))
                # set the duration of the media into the duration label
                self.ui.totalDurationLabel.setText(time.strftime('%H:%M:%S', time.localtime(self.media.get_duration() / 1000)))
                # give the id of the QFrame (or similar object) to vlc, different platforms
                # have different functions for this
                if sys.platform.startswith('linux'): # for Linux using the X Server
                    self.mediaplayer.set_xwindow(self.ui.videoFrame.winId())
                elif sys.platform == "win32": # for Windows
                    self.mediaplayer.set_hwnd(self.ui.videoFrame.winId())
                elif sys.platform == "darwin": # for MacOS
                    self.mediaplayer.set_nsobject(int(self.videoFrame.winId()))
                # start playing the media file
                self.play()

    def previous_media(self):
        """
        This method plays the previous video on the playlist
        """
        if len(self.playlist) > 0:
            if self.playlist_current_index > 0:
                # get the previous media index
                self.playlist_current_index -= 1
                # create the media
                filename = self.playlist[self.playlist_current_index]
                if sys.version < '3':
                    filename = unicode(filename)
                self.media = self.instance.media_new(filename)
                # put the media in the media player
                self.mediaplayer.set_media(self.media)
                # parse the metadata of the file
                self.media.parse()
                # set the title of the track as window title
                self.setWindowTitle(self.media.get_meta(0))
                # set the duration of the media into the duration label
                self.ui.totalDurationLabel.setText(time.strftime('%H:%M:%S', time.localtime(self.media.get_duration() / 1000)))
                # give the id of the QFrame (or similar object) to vlc, different
                # platforms have different functions for this
                if sys.platform.startswith('linux'): # for Linux using the X Server
                    self.mediaplayer.set_xwindow(self.ui.videoFrame.winId())
                elif sys.platform == "win32": # for Windows
                    self.mediaplayer.set_hwnd(self.ui.videoFrame.winId())
                elif sys.platform == "darwin": # for MacOS
                    self.mediaplayer.set_nsobject(int(self.videoFrame.winId()))
                # start playing the media file
                self.play()

    def clear_playlist(self):
        """
        This method clears the playlist
        """
        self.playlist.clear()
        self.playlist_current_index = 0

    def stop(self):
        """
        This method stops the player
        """
        self.mediaplayer.stop()
        self.ui.playPauseButton.setIcon(self.play_icon)
        self.ui.playPauseButton.setToolTip('Play (SPACE BAR)')
        try:
            self.ui.currentTimeLabel.setText(time.strftime('%H:%M:%S', time.localtime(self.media.get_duration() / 1000)))
        except:
            pass

    def manual_stop(self):
        """
        This method stops the player when the button is clicked
        """
        self.stop_clicked = True
        self.stop()

    def set_volume(self, volume):
        """
        This method sets the volume of the player
        """
        self.mediaplayer.audio_set_volume(volume)

    def volume_up(self):
        """
        This method increases the volume by 5
        """
        self.ui.volumeSlider.setValue(self.ui.volumeSlider.value() + 5)

    def volume_down(self):
        """
        This method decreases the volume by 5
        """
        self.ui.volumeSlider.setValue(self.ui.volumeSlider.value() - 5)

    def set_position(self, position):
        """
        This method sets the position of the player
        """
        self.mediaplayer.set_position(position / 1000.0)

    def update(self):
        """
        This method updates the progress slider, handles replays and stops playback
        """
        # set the current time into the current time label
        self.ui.currentTimeLabel.setText(time.strftime('%H:%M:%S', time.localtime(self.mediaplayer.get_time() / 1000)))
        # set the slider to the desired position
        self.ui.progressSlider.setValue(self.mediaplayer.get_position() * 1000.0)
        
        if not self.mediaplayer.is_playing():
            # if nothing is playing, stop the timer
            self.timer.stop()
            if not self.isPaused:
                # stop the video video and set reset the play-pause button when the video ends
                self.stop()
                # if stop action was done manually with the button click, then stop the video
                # and do not replay or move to next if it is a playlist
                if not self.stop_clicked:
                    # if the repeat button is checked start playing the again
                    if self.ui.repeatButton.isChecked():
                        self.play()
                    elif len(self.playlist) > 1:
                        # if it is a playlist with more media, move on to the next
                        self.next_media()

    def visualize_repeat_state(self):
        """
        This method changes the icon and tooltip of the repeat button when modes are switched
        """
        if self.ui.repeatButton.isChecked():
            self.ui.repeatButton.setIcon(self.repeat_on_icon)
            self.ui.repeatButton.setToolTip('Repeat ON (R)')
        else:
            self.ui.repeatButton.setIcon(self.repeat_off_icon)
            self.ui.repeatButton.setToolTip('Repeat OFF (R)')

    def get_media_properties(self):
        """
        This method gets the properties of the media file
        """
        # get the resolution
        resolution_tuple = self.mediaplayer.video_get_size(0)
        resolution = str(resolution_tuple[0]) + ' x ' + str(resolution_tuple[1])
        # get the video duration
        duration = time.strftime('%H:%M:%S', time.localtime(self.media.get_duration() / 1000))
        # get fps
        fps = str(self.mediaplayer.get_fps())
        # get rate
        rate = str(self.mediaplayer.get_rate())
        # get aspect ration
        aspect_ratio = str(self.mediaplayer.video_get_aspect_ratio())
        # get scale
        scale = str(self.mediaplayer.video_get_scale())
        # get track
        track = str(self.mediaplayer.video_get_track())
        # get track count
        track_count = str(self.mediaplayer.video_get_track_count())
        

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def keyPressEvent(self, event):
        key_pressed = event.key()
        # press F key to open a media file
        if key_pressed == Qt.Key_F:
            self.open_file()
        # press the A key to open a playlist
        elif key_pressed == Qt.Key_A:
            self.open_playlist()
        # press the B key to select previous media in a playlist if any
        elif key_pressed == Qt.Key_B:
            self.previous_media()
        # press the Space Bar to toggle pause and play
        elif key_pressed == Qt.Key_Space:
            self.play_pause()
        # press the S key to stop the media playback
        elif key_pressed == Qt.Key_S:
            self.manual_stop()
        # press the R key to toggle the repeat button
        elif key_pressed == Qt.Key_R:
            self.ui.repeatButton.toggle()
        # press the N key to select next media in a playlist if any
        elif key_pressed == Qt.Key_N:
            self.next_media()
        # press the Down arrow key to decrease the volume
        elif key_pressed == Qt.Key_Down:
            self.volume_down()
        # press the Up arrow key to increase the volume
        elif key_pressed == Qt.Key_Up:
            self.volume_up()
        # press the right arrow key to move forward by 5 seconds
        elif key_pressed == Qt.Key_Right:
            self.forward()
        # press the left arrow key to move backwarrd by 5 seconds
        elif key_pressed == Qt.Key_Left:
            self.backward()

    def closeEvent(self, event):
        self.stop()
        sys.exit(0)


if __name__ == '__main__':
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    app = QApplication(sys.argv)
    player = Hydra()
    player.show()
    sys.exit(app.exec_())
