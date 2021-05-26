import cv2
import time
import datetime
import edgeiq
"""
Use object detection to count the number of each type of object in
the frame. The types of objects detected can be changed by selecting
different models. The list of object types that are counted can be
changed by modifying `OBJECTS`.

To change the computer vision model, the engine and accelerator,
and add additional dependencies read this guide:
https://alwaysai.co/docs/application_development/configuration_and_packaging.html
"""


###################################################
# Choose objects to count from the following list #
###################################################
"""
background, aeroplane, bicycle, bird, boat,
bottle, bus, car, cat, chair, cow, diningtable,
dog, horse, motorbike, person, pottedplant, sheep,
sofa, train, tvmonitor
"""


OBJECTS = ["person", "chair", "sofa", "pottedplant"]


def main():
    obj_detect = edgeiq.ObjectDetection("alwaysai/mobilenet_ssd")
    obj_detect.load(engine=edgeiq.Engine.DNN)

    print("Engine: {}".format(obj_detect.engine))
    print("Accelerator: {}\n".format(obj_detect.accelerator))
    print("Model:\n{}\n".format(obj_detect.model_id))
    print("Labels:\n{}\n".format(obj_detect.labels))
    print("Detecting:\n{}\n".format(OBJECTS))

    fps = edgeiq.FPS()

    try:
        with edgeiq.WebcamVideoStream(cam=0) as video_stream, \
                edgeiq.Streamer() as streamer:
            # Allow Webcam to warm up
            time.sleep(2.0)
            fps.start()

            # loop detection
            while True:
                frame = video_stream.read()
                results = obj_detect.detect_objects(frame, confidence_level=.5)
                predictions = edgeiq.filter_predictions_by_label(
                        results.predictions, OBJECTS)
                frame = edgeiq.markup_image(
                        frame, predictions, show_confidences=False,
                        colors=obj_detect.colors)

                # Print date and time on frame
                current_time_date = str(datetime.datetime.now())
                (h, w) = frame.shape[:2]
                cv2.putText(
                        frame, current_time_date, (10, h - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Count objects
                counter = {obj: 0 for obj in OBJECTS}

                for prediction in predictions:
                    # increment the counter of the detected object
                    counter[prediction.label] += 1

                # Generate text to display on streamer
                text = ["Model: {}".format(obj_detect.model_id)]
                text.append(
                        "Inference time: {:1.3f} s".format(results.duration))
                text.append("Object counts:")

                for label, count in counter.items():
                    text.append("{}: {}".format(label, count))

                streamer.send_data(frame, text)

                fps.update()

                if streamer.check_exit():
                    break

    finally:
        fps.stop()
        print("elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("approx. FPS: {:.2f}".format(fps.compute_fps()))

        print("Program Ending")


if __name__ == "__main__":
    main()
