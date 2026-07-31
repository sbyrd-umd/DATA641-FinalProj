import threading

import pyaudio


class MicStreamer:
    """
    Streams microphone audio on a background thread and forwards each raw
    PCM16 chunk to `send_media` (which breaks the stream if it errors, since
    that's the upstream connection).
    """

    def __init__(self, format, channels, rate, chunk, ready_event: threading.Event):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.ready_event = ready_event  # set once the upstream connection is ready to receive audio
        self.stop_event = threading.Event()

    def start(self, send_media, *other_consumers):
        """Launch the mic stream on a background (daemon) thread."""
        thread = threading.Thread(
            target=self._run, args=(send_media, other_consumers), daemon=True
        )
        thread.start()
        return thread

    def stop(self):
        """Signal the background thread to stop and close out the mic stream."""
        self.stop_event.set()

    def _run(self, send_media, other_consumers):
        self.ready_event.wait()  # pause until connection is OPEN
        audio = pyaudio.PyAudio()
        mic = audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )
        print("Listening... Press Ctrl+C to stop.")

        try:
            while not self.stop_event.is_set():
                data = mic.read(self.chunk, exception_on_overflow=False)

                try:
                    send_media(data)
                except Exception as e:
                    print(f"Error sending media: {e}")
                    break  # stop the stream if the upstream connection fails
                
                # feed data to consumers
                for consumer in other_consumers:
                    try:
                        consumer(data)
                    except Exception as e:
                        print(f"Error in audio consumer: {e}")
        finally:
            mic.stop_stream()
            mic.close()
            audio.terminate()
