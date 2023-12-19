clear
close all


% STFT Plot of a Wave File

% Specify the path to your wave file
waveFilePath = 'estimated_voice_2_realtime.wav';

% Read the audio file
[x, fs] = audioread(waveFilePath);

% STFT parameters
windowSize = 512;
hopSize = 256;

% Calculate the STFT
[S, F, T] = spectrogram(x, windowSize, hopSize, windowSize, fs);

% Plot the STFT
figure;
surf(T, F, 10 * log10(abs(S)), 'EdgeColor', 'none');
axis tight;
view(0, 90);  % To view the plot from the top
xlabel('Time (s)');
ylabel('Frequency (Hz)');
title('STFT of the Wave File');
colorbar;

% Display the original waveform
figure;
t = (0:length(x)-1) / fs;
plot(t, x);
xlabel('Time (s)');
ylabel('Amplitude');
title('Original Waveform');

