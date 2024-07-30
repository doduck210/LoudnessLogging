from queue import Queue
import gi
import time

gi.require_version("Gst", "1.0")
from gi.repository import Gst

Gst.init(None)


class Decklink:
    def __init__(self, dev_index):
        self.framequeue = Queue()
        self.keep_going = True
        self.dev_index = dev_index
        self.list_roi = []

    def play(self):
        audiosrc = Gst.ElementFactory.make("decklinkaudiosrc", "audiosrc")
        audioconvert = Gst.ElementFactory.make("audioconvert", "audioconvert")
        audioresample = Gst.ElementFactory.make("audioresample", "audioresample")
        wavenc = Gst.ElementFactory.make("wavenc", "wavenc")
        audiosink = Gst.ElementFactory.make("filesink", "audiosink")

        videosrc = Gst.ElementFactory.make("decklinkvideosrc", "videosrc")
        videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
        videosink = Gst.ElementFactory.make("fakevideosink", "videosink")

        audiosrc.set_property("device-number", self.dev_index)
        videosrc.set_property("device-number", self.dev_index)

        audiosink.set_property("location", "test.wav")

        self.pipeline = Gst.Pipeline.new("pipeline")

        self.pipeline.add(audiosrc)
        self.pipeline.add(audioconvert)
        self.pipeline.add(audioresample)
        self.pipeline.add(wavenc)
        self.pipeline.add(audiosink)
        self.pipeline.add(videosrc)
        self.pipeline.add(videoconvert)
        self.pipeline.add(videosink)

        print(Gst.Element.link(audiosrc, audioconvert))
        print(Gst.Element.link(audioconvert, audioresample))
        print(Gst.Element.link(audioresample, wavenc))
        print(Gst.Element.link(wavenc, audiosink))
        print(Gst.Element.link(videosrc, videoconvert))
        print(Gst.Element.link(videoconvert, videosink))

        if self.pipeline.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
            print("Unable to set the pipeline to the playing state.")
            exit(-1)

        self.bus = self.pipeline.get_bus()

        while self.keep_going:
            message = self.bus.timed_pop_filtered(10000, Gst.MessageType.ANY)

            if message:
                if message.type == Gst.MessageType.ERROR:
                    err, debug = message.parse_error()
                    print(
                        (
                            "Error received from element %s: %s"
                            % (message.src.get_name(), err)
                        ),
                        f"  index = {self.dev_index}",
                    )
                    print(
                        ("Debugging information: %s" % debug),
                        f"  index = {self.dev_index}",
                    )
                    break
                elif message.type == Gst.MessageType.EOS:
                    print("End-Of-Stream reached.", f"  index = {self.dev_index}")
                    break
                elif message.type == Gst.MessageType.STATE_CHANGED:
                    if isinstance(message.src, Gst.Pipeline):
                        old_state, new_state, pending_state = (
                            message.parse_state_changed()
                        )
                        print(
                            (
                                "Pipeline state changed from %s to %s."
                                % (old_state.value_nick, new_state.value_nick)
                            ),
                            f"  index = {self.dev_index}",
                        )
                else:
                    print("Unexpected message received.", f"  index = {self.dev_index}")
            time.sleep(0.0001)
