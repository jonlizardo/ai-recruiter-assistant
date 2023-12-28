from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

import numpy as np
import cv2  # Import OpenCV for video writing
import av

import time
import os

from firebase_admin import credentials, storage

# from init import initialize_app


# initialize_app()


def webcam(participant_id):
    class VideoProcessor:
        def __init__(self, target_fps=10, output_file='recording.mp4'):
            # Target frames per second (FPS)
            self.target_fps = target_fps
            # Interval in seconds between frames
            self.interval = 1 / target_fps
            # Time of the last processed frame
            self.last_time = 0
            # Output video file name
            self.output_file = output_file
            # Initialize the video writer
            self.out = None

        def recv(self, frame):
            current_time = time.time()
            # Check if the interval since the last frame is less than the target interval
            if current_time - self.last_time < self.interval:
                return None  # Skip this frame

            self.last_time = current_time
            img = frame.to_ndarray(format="bgr24")

            # Initialize the video writer when receiving the first frame
            if self.out is None:
                self.out = cv2.VideoWriter(self.output_file, cv2.VideoWriter_fourcc(
                    *'mp4v'), self.target_fps, (img.shape[1], img.shape[0]))

            # Write the frame to the video file
            self.out.write(img)

            return av.VideoFrame.from_ndarray(img, format="bgr24")

        def close(self):
            # Close the video writer
            if self.out:
                self.out.release()
                self.out = None

                # Upload to Firebase Storage
                bucket = storage.bucket()
                blob = bucket.blob(self.output_file)
                blob.upload_from_filename(self.output_file)

                # Optionally, delete the local file after upload
                # os.remove(self.output_file)


    RTC_CONFIGURATION = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    # Instantiate the video processor
    video_processor = VideoProcessor()

    webrtc_ctx = webrtc_streamer(
        key="WYH",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        video_processor_factory=lambda: video_processor,
        async_processing=True,
    )

    # Handle the stream end to close the video writer
    if webrtc_ctx.video_processor:
        webrtc_ctx.video_processor.close()
