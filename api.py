# vim:ts=4:sts=4:sw=4:expandtab

import logging
import uuid

class Frame:
    """Abstract frame class"""

    def __init__(self, length, first_tick):
        self._id = uuid.uuid4()
        self._length = length
        self._first_tick = first_tick

    @property
    def id(self):
        """Returns globally unique id of the frame"""
        return self._id

    @property
    def length(self):
        """Returns length, in ticks, of the frame"""
        return self._length

    @property
    def first_tick(self):
        """Returns the first tick number of the frame"""
        return self._first_tick

class Channel:
    """Abstract channel class"""

    def transmit_part(self, frame, part):
        """Transmits part of the frame"""
        pass

    @property
    def transmit_status(self):
        """Checks if the last transmission was acknowledged"""
        pass

    @property
    def carrier_sense(self):
        """Checks if channel was active in the last tick"""
        pass

class Algorithm:
    """Abstract MAC algorithm"""

    def __init__(self, channel, max_length): 
        if not isinstance(channel, Channel):
            raise ValueError
        self.channel = channel
        self.frame = None
        self.part = None
        self.transmitted = False
        self._max_length = max_length

    @property
    def max_length(self):
        return self._max_length

    def __call__(self, tick, frame=None):
        self.tick_count = tick
        if self.transmitted:
            self.part += 1
        else:
            self.part = 0
        self.transmitted = False
        if self.frame and self.part == self.frame.length:
            if self.channel.transmit_status:
                #SUCCESS
                self.frame = None
                self.part = 0
            else:
                #FAILURE
                self.part = 0
        if frame is not None and not isinstance(frame, Frame):
            raise ValueError
        if frame is not None and self.frame is not None:
            raise ValueError
        if frame is not None:
            self.frame = frame
            self.part = 0
        self.tick()

    def transmit(self):
        self.channel.transmit_part(self.frame, self.part)
        self.transmitted = True

    def tick(self):
        """ALGORITHM"""
        pass
