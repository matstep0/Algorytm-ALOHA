# vim:ts=4:sts=4:sw=4:expandtab

import random
import uuid

import api
import algorithm
import logging

class Simulator:
    """Simulator sandbox for MAC algorithm experiments"""

    class Channel(api.Channel):
        def __init__(self, simulator):
            self.id = uuid.uuid4()
            self._transmit_frame_id = None
            self._transmit_part = None
            self._transmit_status = None
            self._carrier_sense=None
            super().__init__()
        def transmit_part(self, frame, part):
            if not isinstance(frame, Simulator.Frame):
                raise ValueError
            if not isinstance(part, int):
                raise ValueError
            logging.debug("Channel %s : Transmission of part %d/%d of frame %s"%(self.id, part, frame.length, frame.id))
            self._transmit_frame_id = frame.id
            self._transmit_part = part
        @property
        def transmit_status(self):
            return self._transmit_status
        @property
        def carrier_sense(self):
            return self._carrier_sense

    class Frame(api.Frame):
        def __init__(self, length, first_tick):
            super().__init__(length, first_tick)

    class Client:
        def __init__(self, simulator, channel, algorithm, max_length, frame_probability):
            self.id = uuid.uuid4()
            self.simulator = simulator
            self.channel = channel
            self.channel.client = self
            self.algorithm = algorithm(self.channel, max_length)
            self.max_length = max_length
            self.frame_probability = frame_probability
            self.frame = None
            self.next_part = 0
            logging.debug("Client %s : using algorithm %s on channel %s"%(self.id, self.algorithm.__class__.__name__, self.channel.id))

        def tick(self, tick):
            if self.frame is None:
                if random.random() < self.frame_probability:
                    length = random.randrange(1, self.max_length+1)
                    self.frame = Simulator.Frame(length, tick)
                    logging.info("Client %s: new frame %s of length %d" % (self.id, self.frame.id, self.frame.length))
                    self.next_part = 0
                    self.algorithm(tick, self.frame)
                else:
                    self.algorithm(tick, None)
            else:
                self.algorithm(tick, None)
        def tack(self, transfers):
            if len(transfers) == 1 and self.id in transfers and self.channel._transmit_part is not None:
                if self.channel._transmit_part == self.next_part:
                    self.next_part += 1
                    if self.frame is not None and self.next_part == self.frame.length:
                        #SUCCESS
                        logging.debug("Client %s: transmitted frame %s" % (self.id, self.frame.id))
                        self.channel._transmit_status = True
                        self.frame = None
                        self.next_part = 0
                    return
            if len(transfers)>1 and self.id in transfers:
                self.channel._carrier_sense=True #ktos nadawal
            if self.channel._transmit_part is not None and self.frame is not None and self.channel._transmit_part == self.frame.length-1:
                self.channel._transmit_status = False
            self.next_part = 0

    def __init__(self):
        self.channels = dict()
        self.clients = dict()
        self.tick_count = 0
        self.success_count=0

    def add_client(self, algorithm, max_length, frame_probability):
        channel = Simulator.Channel(self)
        client = Simulator.Client(self, channel, algorithm, max_length, frame_probability)
        self.clients[client.id] = client
        self.channels[channel.id] = channel

    def tick(self):
        for id, client in self.clients.items():
            client.tick(self.tick_count)
            client.channel._transmit_status = None
            client.channel._carrier_sense= None
        transfers = set()
        for id, client in self.clients.items():
            if client.channel._transmit_frame_id is not None:
                transfers.add(id)
        logging.debug("Simulator: Tick %d transfer count %d" % (self.tick_count, len(transfers)))
        for id, client in self.clients.items():
            client.tack(transfers)
            if client.channel._transmit_status==True:
                self.success_count+=1
            client.channel._transmit_frame_id = None
            client.channel._transmit_part = None
        self.tick_count += 1

    @property
    def stats(self):
        result = dict()
        result['ticks'] = self.tick_count
        result['success']=self.success_count
        return result
