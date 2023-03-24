import serial

class Controller:
    '''
    Basic device adaptor for Prior PureFocus850 Laser Autofocus System. Many
    more commands are available and have not been implemented.
    '''
    def __init__(self,
                 which_port,
                 name='PureFocus850',
                 verbose=True,
                 very_verbose=False):
        self.name = name
        self.verbose = verbose
        self.very_verbose = very_verbose
        if self.verbose: print("%s: opening..."%self.name, end='')
        try:
            self.port = serial.Serial(
                port=which_port, baudrate=460800, timeout=5)
        except serial.serialutil.SerialException:
            raise IOError('%s: unable to connect on %s'%(self.name, which_port))
        if self.verbose: print('done.')        
        self.info = self._get_info()
        if self.info[0] != "Prior Scientific Instruments OptiScan LF":
            raise IOError("%s: product not supported"%self.name)

    def _send(self, cmd, response_lines=1):
        if self.very_verbose:
            print('%s: sending cmd ='%self.name, cmd)
        cmd = bytes(cmd + '\r', 'ascii')
        self.port.write(cmd)
        response = []
        for line in range(response_lines):
            response_line = (
                self.port.read_until(b'\r').decode('ascii').strip('\r\n'))
            response.append(response_line)
            if self.very_verbose:
                print('%s: -> response = '%self.name, response_line)
            self._check_error(response_line)
        assert self.port.inWaiting() == 0
        return response

    def _check_error(self, response):
        error_codes = {
            'E,2' :'Not idle',
            'E,3' :'No drive',
            'E,4' :'String parse',
            'E,5' :'Command not found',
            'E,8' :'Value out of range',
            'E,10':'Argument 1 out of range',
            'E,11':'Argument 2 out of range',
            'E,12':'Argument 3 out of range',
            'E,13':'Argument 4 out of range',
            'E,14':'Argument 5 out of range',
            'E,15':'Argument 6 out of range',
            }
        error = None
        if response[0] == 'E':
            error = error_codes[response]
            print('%s: ***ERROR***: %s (%s)'%(self.name, response, error))
        return error

    def _get_info(self):
        if self.verbose:
            print('%s: getting info'%self.name)
        response = self._send('DATE', response_lines=2)
        if self.verbose:
            print('%s: -> product = %s'%(self.name, response[0]))
            print('%s: -> version = %s'%(self.name, response[1]))
        return response

    def close(self):
        if self.verbose: print("%s: closing..."%self.name, end=' ')
        self.port.close()
        if self.verbose: print("done.")
        return None

if __name__ == '__main__':
    autofocus = Controller(which_port='COM8', verbose=True, very_verbose=True)

    autofocus.close()
