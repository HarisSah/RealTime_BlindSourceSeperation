clear
close all


% STFT Plot of a Wave File

% Specify the path to your wave file
waveFilePath = 'estimated_voice_2.wav';

% Read the audio file
[x, fs] = audioread(waveFilePath);

% STFT parameters
windowSize = 512;
hopSize = 128;

% Calculate the STFT
[S, F, T] = spectrogram(x, windowSize, hopSize, windowSize, fs);

% Plot the STFT with enhanced color contrast
figure;
surf(T, F, 10 * log10(abs(S)),'EdgeColor','none');
axis tight;
view(0, 90);  % To view the plot from the top
xlabel('Time (s)');
ylabel('Frequency (Hz)');
title('STFT of the Wave File');
colorbar;


% Choose a colormap with high contrast
colormap(jet);

% Adjust the color axis scaling for better contrast
clim([max(10 * log10(abs(S(:)))) - 50, max(10 * log10(abs(S(:))))]);



% Display the original waveform
figure;
t = (0:length(x)-1) / fs;
plot(t, x);
xlabel('Time (s)');
ylabel('Amplitude');
title('Original Waveform');

