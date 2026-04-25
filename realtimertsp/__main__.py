import argparse
import time

import cv2

from realtimertsp import RealtimeStream

parser = argparse.ArgumentParser()
parser.add_argument("url", nargs="?")
args = parser.parse_args()

with RealtimeStream(args.url) as stream:
    fps, count, t0 = 0.0, 0, time.perf_counter()

    while True:
        frame = stream.read_latest_frame()
        if frame is None:
            print("Stream ended.")
            break

        frame = frame.copy()

        count += 1
        now = time.perf_counter()
        if now - t0 >= 1.0:
            fps = count / (now - t0)
            count, t0 = 0, now

        cv2.putText(frame, f"{fps:.1f} fps", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow(args.url, frame)

        if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q"), 27):
            break
    cv2.destroyAllWindows()