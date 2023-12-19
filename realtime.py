#Realtime/Microphone Application

import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import FastICA
import pyaudio
import wave
import struct
import os


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

        # Create buttons
        
        self.start_button = tk.Button(root, text="START", command=self.run_ica)
        self.play_button_2 = tk.Button(root, text="PLAY AUDIO 1", command=lambda: self.play_audio(self.result_signal_2, duration=5))
        self.play_button_3 = tk.Button(root, text="PLAY AUDIO 2", command=lambda: self.play_audio(self.result_signal_3, duration=5))
        
        self.quit_button = tk.Button(root, text="QUIT", command=root.destroy)

        # Create status label
        self.status_label = tk.Label(root, text="READY", fg="green")

        # Place buttons and label on the window
        self.start_button.pack(pady=10)
        
        self.play_button_2.pack(pady=10)
        self.play_button_3.pack(pady=10)
        
        self.quit_button.pack(pady=10)
        self.status_label.pack(pady=10)

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

    def original_audio(self, duration=5):
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
    
    def recording(self, duration = 5):
        # Open wave files for left and right channels
        left_wf = wave.open("temp_left_channel.wav", 'w')
        right_wf = wave.open("temp_right_channel.wav", 'w')
        left_wf.setnchannels(1)
        right_wf.setnchannels(1)
        left_wf.setsampwidth(2)
        right_wf.setsampwidth(2)
        left_wf.setframerate(48000)
        right_wf.setframerate(48000)

        # Open audio stream
        stream = self.p.open(format=pyaudio.paInt16,
                             channels=2,
                             rate=48000,
                             input=True,
                             output=False)

        # Record to wave files
        for _ in range(int(48000 / 1024 * duration)):
            binary_input_data = stream.read(1024, exception_on_overflow=False)
            input_tuple = struct.unpack('h' * 2 * 1024, binary_input_data)

            left_samples = [input_tuple[n] for n in range(0, 2 * 1024, 2)]
            right_samples = [input_tuple[n + 1] for n in range(0, 2 * 1024, 2)]

            left_binary_output_data = struct.pack('h' * 1024, *left_samples)
            right_binary_output_data = struct.pack('h' * 1024, *right_samples)

            left_wf.writeframes(left_binary_output_data)
            right_wf.writeframes(right_binary_output_data)

        # Close resources
        stream.stop_stream()
        stream.close()
        
        left_wf.close()
        right_wf.close()

    

    def run_ica(self):
        duration = 5 # Recording time
        # Change status label to "Recording..."
        self.status_label.config(text="Recording...", fg="red")
        self.root.update()

        self.recording(duration)

        # Load mixed audio data
        voice_1, fs_1 = self.read_wav("temp_left_channel.wav")
        voice_2, fs_2 = self.read_wav("temp_right_channel.wav")

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
        self.write_wav("estimated_voice_1_realtime.wav", S_[:, 0], fs_1)
        self.write_wav("estimated_voice_2_realtime.wav", S_[:, 1], fs_2)

        # Update result signals for playback
        self.result_signal_2 = S_[:, 0]
        self.result_signal_3 = S_[:, 1]

        # Remove temporary left and right wave files
        os.remove("temp_left_channel.wav")
        os.remove("temp_right_channel.wav")

        # Change status label to "READY"
        self.status_label.config(text="READY", fg="green")

    def play_audio(self, data, duration):
        stream = self.p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=48000,
                             output=True)

        

        normalized_data = (data * 32767 / np.max(np.abs(data))).astype(np.int16)
        stream.write(normalized_data.tobytes())

        # After the specified duration, stop the stream and close it
        self.root.after(int(duration * 1000), lambda: self.stop_audio(stream))

    def stop_audio(self, stream):
        stream.stop_stream()
        stream.close()

    
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