# vim:ts=4:sts=4:sw=4:expandtab

import api
import logging
import random
rconst=10
class SimpleAlgorithm(api.Algorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self):
        logging.debug("Algorithm tick : %s"%(repr([
            self.tick_count,
            (self.frame and str(self.frame.id)),
            (self.frame and self.frame.first_tick),
            (self.frame and self.frame.length),
            self.part,
            self.channel.transmit_status,
            self.max_length,
        ]),))
        #print(self.channel._transmit_status)
        if self.frame is not None:
            self.transmit()
class aloha2n(api.Algorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_const=rconst
        self.wait=random.randrange(1,self.wait_const) #mozna zrobic testy jaka stala jest ok
        self.wait_counter=self.wait
    def tick(self):
        if self.frame is not None:
            if(self.wait-self.wait_counter==0):
                self.transmit()
            if(self.channel._transmit_status==False):
                self.wait=self.wait*2+random.randrange(1,self.wait_const)
                self.wait_const*=2
                self.wait_counter=0
class slotted(api.Algorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started=0
        self.wait_const=rconst
        self.wait=random.randrange(1,self.wait_const) #mozna zrobic testy jaka stala jest ok
        self.wait_counter=self.wait
    def tick(self):
        if self.frame is not None:
            if(self.wait-self.wait_counter==0):
                if self.started==1:
                    self.transmit()
                else: #started = 0
                    if self.tick_count%self.max_length==0:
                        self.transmit()
                        self.started=1
            if(self.channel._transmit_status==False):
                self.wait=self.wait*2+random.randrange(1,self.wait_const)
                self.wait_const*=2 #rosnie z czasem
                self.wait_counter=0
                self.started=0
class CSMA(api.Algorithm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started=0
        self.wait_const=rconst
        self.wait=random.randrange(1,self.wait_const)
        self.wait_counter=self.wait
    def tick(self):
        if self.frame is not None:
            if(self.wait-self.wait_counter==0):
                if self.started==1:
                    self.transmit()
                else: #started = 0
                    if self.channel._carrier_sense==None:
                        self.transmit()
                        self.started=1
                        self.wait_const=rconst
            if(self.channel._transmit_status==False):
                self.wait=random.randrange(1,self.wait_const)
                self.wait_counter=0
                self.wait_const*=2
                self.started=0
