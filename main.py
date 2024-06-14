import tkinter as tk
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
from sklearn.decomposition import FastICA
import pyaudio
import wave

# Wavefiles application
class BSSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BSS Application")

        self.audio_file_1 = None
        self.audio_file_2 = None
        self.original_signal = None
        self.result_signal_2 = None
        self.result_signal_3 = None

        # flags to check
        # Audio seperation is done - Used when original_signal, result_signal_ are still None
        # Some audio is playing - To prevent play action happening multiple times
        self.audio_seperation_done = False
        self.audio_playing_flag = False

        # Create buttons
        self.play_button_1 = tk.Button(root, text="PLAY ORIGINAL", command=lambda: self.original_audio())
        self.start_button = tk.Button(root, text="START", command=self.run_ica)
        self.play_button_2 = tk.Button(root, text="PLAY AUDIO 1", command=lambda: self.play_audio(self.result_signal_2, duration=5))
        self.play_button_3 = tk.Button(root, text="PLAY AUDIO 2", command=lambda: self.play_audio(self.result_signal_3, duration=5))
        self.plot_button = tk.Button(root, text="PLOT", command=lambda: self.plot_signals(color='red'))
        self.quit_button = tk.Button(root, text="QUIT", command=root.destroy)

        # Create status label
        self.status_label = tk.Label(root, text="READY" if self.original_signal else "CLICK START", fg="green")

        # Audio playing flag
        self.audio_playing_label = tk.Label(root, text="")

        # Place buttons and label on the window
        self.start_button.pack(pady=10)
        self.play_button_1.pack(pady=10)
        self.play_button_2.pack(pady=10)
        self.play_button_3.pack(pady=10)
        self.plot_button.pack(pady=10)
        self.quit_button.pack(pady=10)
        self.status_label.pack(pady=10)
        self.audio_playing_label.pack(pady=10)

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

    def original_audio(self, duration=5):

        # If audio seperation is not done then no original signal is present, return
        if not self.audio_seperation_done:
            return

        # If some audio playing return
        if self.audio_playing_flag:
            return
        
        # If audio not playing, set audio playing flag
        # Change audio playing label
        self.audio_playing_flag = True
        self.audio_playing_label.config(text="Audio playing...", fg="red")
        self.root.update()

        stream = self.p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=48000,
                             output=True)
        stream.write(self.original_signal.tobytes())
        self.root.after(int(duration * 1000), lambda: self.stop_audio(stream))

    def read_wav(self, file_path):
        wf = wave.open(file_path, 'rb')
        frames = wf.readframes(wf.getnframes())
        signal = np.frombuffer(frames, dtype=np.int16)
        sample_rate = wf.getframerate()
        wf.close()
        return signal, sample_rate

    def run_ica(self):
        # Change status label to "Processing..."
        self.status_label.config(text="Processing...", fg="blue")
        self.root.update()

        # Load mixed audio data
        voice_1, fs_1 = self.read_wav("Audio_Files/mix_type_2_1.wav")
        voice_2, fs_2 = self.read_wav("Audio_Files/mix_type_2_2.wav")

        # Reshape the files to have the same size
        m = min(len(voice_1), len(voice_2))
        voice_1 = voice_1[:m]
        voice_2 = voice_2[:m]

        # Mixing data
        voice = np.c_[voice_1, voice_2]
        A = np.array([[1, 1], [0.5, 2]]) 
        X = np.dot(voice, A)

        # Blind source separation using ICA
        ica = FastICA()
        ica.fit(X)
        S_ = ica.transform(X)

        # Save estimated signals to WAV files
        self.write_wav("estimated_voice_1.wav", S_[:, 0], fs_1)
        self.write_wav("estimated_voice_2.wav", S_[:, 1], fs_2)

        # Update result signals for playback
        self.result_signal_2 = S_[:, 0]
        self.result_signal_3 = S_[:, 1]

        # Load original mixed audio data (this is the part you were missing)
        self.original_signal, _ = self.read_wav("Audio_Files/mix_type_2_1.wav")

        # Change status label to "READY"
        self.status_label.config(text="READY", fg="green")

        # Call plot_signals to update the plot
        self.plot_signals()

        # Set audio seperation done flag
        self.audio_seperation_done = True

    def play_audio(self, data, duration):

        # If audio seperation is not done then return
        if not self.audio_seperation_done:
            return

        # If some audio playing return
        if self.audio_playing_flag:
            return
        
        # If audio not playing, set audio playing flag
        # Change audio playing label
        self.audio_playing_flag = True
        self.audio_playing_label.config(text="Audio playing...", fg="red")
        self.root.update()

        stream = self.p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=48000,
                             output=True)

        

        normalized_data = (data * 32767 / np.max(np.abs(data))).astype(np.int16)
        stream.write(normalized_data.tobytes())

        # After the specified duration, stop the stream and close it
        self.root.after(int(duration * 1000), lambda: self.stop_audio(stream))

    def stop_audio(self, stream):

        # Audio playing finished, unset audio playing flag
        # Change audio playing label
        self.audio_playing_flag = False
        self.audio_playing_label.config(text="")
        self.root.update()

        stream.stop_stream()
        stream.close()

    def plot_signals(self, color = 'blue'):
        if self.original_signal is not None and self.result_signal_2 is not None and self.result_signal_3 is not None:
            # Plot original and separated signals
            plt.figure(figsize=(12, 6))

            plt.subplot(3, 1, 1)
            plt.plot(self.original_signal)
            plt.title("Original Signal")

            plt.subplot(3, 1, 2)
            plt.plot(self.result_signal_2, color = 'blue')
            plt.title("Separated Signal 1")

            plt.subplot(3, 1, 3)
            plt.plot(self.result_signal_3, color = 'orange')
            plt.title("Separated Signal 2")

            plt.tight_layout()
            plt.show()

    def write_wav(self, file_path, data, sample_rate):
        normalized_data = (data * 32767 / np.max(np.abs(data))).astype(np.int16)

        wf = wave.open(file_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(normalized_data.tobytes())
        wf.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = BSSApp(root)
    root.mainloop()
