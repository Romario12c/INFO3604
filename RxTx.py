

import time
import RPi.GPIO as GPIO

RECEIVE_PIN = 11
TRANSMIT_PIN = 7

class RxTx:
    def __init__(self, codes={}):
      
        self._codes = codes

        channel = 21
        #GPIO.setmode(GPIO.BCM)
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(channel, GPIO.IN)
        GPIO.setup(RECEIVE_PIN, GPIO.IN)
        GPIO.setup(TRANSMIT_PIN, GPIO.OUT)

   
 
    def _createBuffer(self, start_time, mode=GPIO.HIGH):
        
        if mode != GPIO.HIGH and mode != GPIO.LOW:
            raise(Exception('Mode must be either GPIO.HIGH or GPIO.LOW'))

        buffer_limit = 200
        dt = -1
        t = 0
        buffer = []
        while len(buffer) < buffer_limit:
            dt = time.time() - start_time
            bit = GPIO.input(RECEIVE_PIN)

            if bit == mode:
                t += dt
            else:
                if t != 0:
                    buffer.append(t)
                t = 0

        return buffer

    def _processBuffer(self, buffer, mode=GPIO.HIGH):
        
        if mode != GPIO.HIGH and mode != GPIO.LOW:
            raise(Exception('Mode must be either GPIO.HIGH or GPIO.LOW'))

        codes = []
        if mode == GPIO.HIGH:
            for i in range(len(buffer) - 25):
                l_max = max(buffer[i:i+25])
                l_min = min(buffer[i:i+25])
                thresh = (l_max - l_min)/3 + l_min
                out = ''
                for j in range(25):
                    if buffer[i+j] < thresh:
                        out += '1'
                    else:
                        out += '0'

                
                if out not in codes:
                    codes.append(out)
        else:
            for i in range(len(buffer) - 25):
                
                l_max = max(buffer[i:i+25])
                l_min = min(buffer[i:i+25])
                idx = buffer.index(l_max)
                # We want to pass until idx == i
                if idx == i:
                    # Reset the local max value
                    l_max = max(buffer[i+1:i+25])
                    thresh = (l_max - l_min)/3 + l_min
                    out = ''
                    for j in range(24):
                        if buffer[i+1+j] < thresh:
                            out += '0'
                        else:
                            out += '1'
                   
                    if out not in codes:
                        codes.append(out)
        return codes

    def _sniffTiming(self, start_time):
        
        buffer_limit = 1000
        buffer = []
        temp_bit = -1

        one_high = -1
        one_low = -1
        zero_high = -1
        zero_low = -1
        interval = -1

       
        while len(buffer) < buffer_limit:
            dt = time.time() - start_time
            bit = GPIO.input(RECEIVE_PIN)

            if len(buffer) == 0:
                buffer.append(dt)
                temp_bit = bit
            elif bit != temp_bit:
                buffer.append(dt)
                temp_bit = bit
                start_time = time.time()

        POWER = 1e5
        simplified = [int(POWER*b) for b in buffer]

        # The interval between codes is the largest number
        interval = max(simplified)
        idx = simplified.index(interval)
        interval /= POWER

        while idx < len(simplified) - 1:
            first = simplified[idx+1]
            second = simplified[idx+2]
            idx += 2

            if first < second:
                one_high = first/POWER
                one_low = second/POWER
            else:
                zero_high = first/POWER
                zero_low = second/POWER

            if(one_high != -1 and one_low != -1 and
               zero_high != -1 and zero_low != -1):
                break

        return one_high, one_low, zero_high, zero_low, interval

    
    def rxCode(self, runTime=None):
        
        start_time = time.time()

        try:
            while True:
                
                if(runTime is not None and
                   (time.time() - start_time) > runTime):
                    break

               
                buffer = self._createBuffer(start_time)

                
                codes = self._processBuffer(buffer)

                
                key = ''
                for i, l_key in enumerate(self._codes):
                    for j, l_code in enumerate(codes):
                        if l_code == self._codes[l_key]:
                            key = l_key
                            break
                if key:
                    return key

        except Exception as e:
            raise(Exception(e))

    def txCode(self, code, one_high, one_low, zero_high, zero_low,
               interval):
       
        for i in range(10):
            for bit in code:
                if int(bit) == GPIO.HIGH:
                    GPIO.output(TRANSMIT_PIN, GPIO.HIGH)
                    time.sleep(one_high)
                    GPIO.output(TRANSMIT_PIN, GPIO.LOW)
                    time.sleep(one_low)
                else:
                    GPIO.output(TRANSMIT_PIN, GPIO.HIGH)
                    time.sleep(zero_high)
                    GPIO.output(TRANSMIT_PIN, GPIO.LOW)
                    time.sleep(zero_low)
            GPIO.output(TRANSMIT_PIN, GPIO.LOW)
            time.sleep(interval)

    def sniffCode(self, seekTime=2):
       
        
        start_time = time.time()

        # Run the sniffer for the allocated amount of time
        while time.time() - start_time < seekTime:
            # Get the unique codes corresponding to pulse down-time 
            buffer = self._createBuffer(start_time, mode=GPIO.LOW)
            low_codes = self._processBuffer(buffer, mode=GPIO.LOW)

            # Get the unique codes corresponding to pulse up-time
            buffer = self._createBuffer(start_time)
            high_codes = self._processBuffer(buffer)

            # Get the delay times
            o_h, o_l, z_h, z_l, _i = self._sniffTiming(time.time())

           
            for high_code in high_codes:
                for low_code in low_codes:
                    # Our low code collection ignores the last bit due
                    # to ambiguity as it its length (blank between
                    # pulses)
                    if low_code == high_code[:-1]:
                        return high_code, o_h, o_l, z_h, z_l, _i

    def cleanup(self):
       
      
        GPIO.output(TRANSMIT_PIN, GPIO.LOW)
        GPIO.cleanup()
