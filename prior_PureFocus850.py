import time
import serial

class Controller:
    '''
    Basic device adaptor for Prior PureFocus850 Laser Autofocus System. Many
    more commands are available and have not been implemented.
    '''
    def __init__(self,
                 which_port,
                 name='PureFocus850',
                 control_mode='Piezo drive',
                 sensor_mode='Line mode',
                 verbose=True,
                 very_verbose=False):
        self.name = name
        self.verbose = verbose
        self.very_verbose = very_verbose
        if self.verbose: print("%s: opening..."%self.name, end='')
        try:
            self.port = serial.Serial(
                port=which_port, baudrate=460800, timeout=1)
        except serial.serialutil.SerialException:
            raise IOError('%s: unable to connect on %s'%(self.name, which_port))
        if self.verbose: print('done.')        
        self._get_info()
        if self.info[0] != "Prior Scientific Instruments OptiScan LF":
            raise IOError("%s: product not supported"%self.name)
        self._set_config(control_mode, sensor_mode)
        self._get_offset_lens_position() # confirms PF185M head attached
        self._piezo_range_tol_pct = 0.1 # 10%? only certain ranges are accepted
        self._piezo_voltage_tol  = 2 * (10 / 4096) # 2x min voltage step
        self.get_current_objective()
        self.get_servo_enable() # what's the current state of the servo?

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
        if len(response) == 1:
            response = response[0] # avoid list for single line responses
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
        if response =='':
            print('%s: ***ERROR***: No response!'%(self.name))
            raise TypeError(
                '\nIs the PF850 autofocus controller powered up?\n' +
                'Is the PF185M autofocus head connected?')
        if response[0] == 'E':
            error = error_codes[response]
            print('%s: ***ERROR***: %s (%s)'%(self.name, response, error))
        return error

    def _get_info(self):
        if self.verbose:
            print('%s: getting info'%self.name)
        self.info = self._send('DATE', response_lines=2)
        if self.verbose:
            print('%s: -> product = %s'%(self.name, self.info[0]))
            print('%s: -> version = %s'%(self.name, self.info[1]))
        return self.info

    def _get_config(self):
        if self.verbose:
            print('%s: getting config'%self.name)        
        m, s = self._send('CONFIG').split(',')
        m_to_config = {
            'S':'Stepper drive', 'P':'Piezo drive', 'H':'Measure mode'}
        s_to_config = {'S':'Slice mode', 'L':'Line mode'}
        self.control_mode = m_to_config[m]
        self.sensor_mode  = s_to_config[s]
        if self.verbose:
            print('%s: -> control_mode = %s'%(self.name, self.control_mode))
            print('%s: -> sensor_mode  = %s'%(self.name, self.sensor_mode))
        return self.control_mode, self.sensor_mode

    def _set_config(self, control_mode, sensor_mode):
        if self.verbose:
            print('%s: setting config:'%self.name)
            print('%s: -> control_mode = %s'%(self.name, control_mode))
            print('%s: -> sensor_mode  = %s'%(self.name, sensor_mode))
        config_to_m = {'Stepper drive':'S', # Prior (or other) stepper drive
                       'Piezo drive':'P',   # 0-10V analogue output
                       'Measure mode':'H'}  # error is output to DAC
        config_to_s = {'Slice mode':'S',    # PF850  system, PF185  head
                       'Line mode':'L'}     # PF850M system, PF185M head
        self._send('CONFIG' +
                   ',' + config_to_m[control_mode] +
                   ',' + config_to_s[sensor_mode])
        assert self._get_config() == (control_mode, sensor_mode)
        if self.verbose:
            print('%s: done setting config'%self.name)
        return None

    def _get_offset_lens_position(self):
        if self.verbose:
            print('%s: getting offset lens position'%self.name)
        self.offset_lens_position = int(self._send('LENSP'))
        if self.verbose:
            print('%s: -> offset_lens_position = %i'%(
                self.name, self.offset_lens_position))
        return self.offset_lens_position

    def _get_offset_lens_moving(self):
        if self.verbose:
            print('%s: getting offset lens moving'%self.name)
        self.offset_lens_moving = bool(int(self._send('LENS$')))
        if self.verbose:
            print('%s: -> offset_lens_moving = %s'%(
                self.name, self.offset_lens_moving))
        return self.offset_lens_moving

    def get_piezo_range_um(self):
        if self.verbose:
            print('%s: getting piezo range'%self.name)
        assert self.control_mode == 'Piezo drive'
        self.piezo_range_um = int(self._send('UPR'))
        if self.verbose:
            print('%s: -> piezo_range_um = %i'%(
                self.name, self.piezo_range_um))
        return self.piezo_range_um

    def set_piezo_range_um(self, range_um):
        # NOTE: only certain values are accepted!
        # consider setting this range as close as possible to the desired value
        # then setting the actual piezo range (on the piezo controller) to match
        assert isinstance(range_um, int) or isinstance(range_um, float)
        assert 1 <= range_um <= 1000 # 1mm limit?
        if self.verbose:
            print('%s: setting piezo range (um) = %0.2f'%(self.name, range_um))
        self._send('UPR,' + str(range_um))
        self.get_piezo_range_um()
        tol_pct = self._piezo_range_tol_pct
        assert self.piezo_range_um <= range_um + range_um * tol_pct
        assert self.piezo_range_um >= range_um - range_um * tol_pct
        if self.verbose:
            print('%s: -> done setting piezo range'%self.name)
        return None

    def get_piezo_voltage(self):
        if self.verbose:
            print('%s: getting piezo voltage'%self.name)
        DAC_output = int(self._send('PIEZO'))
        self.piezo_voltage = 10 * DAC_output / 4096
        if self.verbose:
            print('%s: -> voltage = %0.2f'%(self.name, self.piezo_voltage))
        return self.piezo_voltage

    def set_piezo_voltage(self, voltage):
        assert isinstance(voltage, int) or isinstance(voltage, float)
        assert 0 <= voltage <= 10
        assert not self.servo_enable, (
            "cannot 'set_piezo_voltage' with servo enabled")
        if self.verbose:
            print('%s: setting piezo voltage = %0.2f'%(self.name, voltage))
        DAC_output = 4096 * (voltage / 10)
        self._send('PIEZO,' + str(DAC_output))
        self.get_piezo_voltage()
        e = "cannot 'set_piezo_voltage' within range, is the servo enabled?"
        assert self.piezo_voltage <= voltage + self._piezo_voltage_tol, e
        assert self.piezo_voltage >= voltage - self._piezo_voltage_tol, e
        if self.verbose:
            print('%s: -> done setting piezo voltage'%self.name)
        return None

    def get_current_objective(self):
        if self.verbose:
            print('%s: getting current objective'%self.name)
        self.current_objective = int(self._send('OBJ'))
        if self.verbose:
            print('%s: -> current_objective = %i'%(
                self.name, self.current_objective))
        return self.current_objective

    def set_current_objective(self, n, polling_wait_s=0.1): # 1 <= n <= 6
        assert isinstance(n, int)
        assert 1 <= n <= 6        
        if self.verbose:
            print('%s: setting current objective = %i\n'%(self.name, n))
        self._send('OBJ,' + str(n))
        assert self.get_current_objective() == n
        verbose = self.verbose
        self.verbose = False
        while self._get_offset_lens_moving(): # blocks method until done!
            print('.', end='')
            time.sleep(polling_wait_s)
        self.verbose = verbose
        if self.verbose:
            print('\n%s: -> current_objective = %i'%(
                self.name, self.current_objective))
        return self.current_objective

    def get_servo_enable(self):
        if self.verbose:
            print('%s: getting servo enable'%self.name)
        self.servo_enable = bool(int(self._send('SERVO')))
        if self.verbose:
            print('%s: -> enable = %s'%(self.name, self.servo_enable))
        return self.servo_enable

    def set_servo_enable(self, enable):
        assert isinstance(enable, bool)
        if self.verbose:
            print('%s: setting servo enable = %s'%(self.name, enable))
        self._send('SERVO,' + str(int(enable)))
        assert self.get_servo_enable() == enable
        if self.verbose:
            print('%s: -> done setting servo enable'%self.name)
        return None

    def get_digipot_mode(self):
        if self.verbose:
            print('%s: getting digipot mode'%self.name)
        n = int(self._send('LENS'))
        if n == 0: self.digipot_mode = 'Focus'
        if n == 1: self.digipot_mode = 'Offset'
        if self.verbose:
            print('%s: -> mode = %s'%(self.name, self.digipot_mode))
        return self.digipot_mode

    def set_digipot_mode(self, mode): # not actually documented but works :)
        assert mode in (
            'Focus',    # the user manually focuses (no autofocus)
            'Offset')   # the user adjusts the offset (autofocus typically on)
        if self.verbose:
            print('%s: setting digipot mode = %s'%(self.name, mode))
        if mode == 'Focus':  n = 0
        if mode == 'Offset': n = 1
        self._send('LENS,' + str(n))
        assert self.get_digipot_mode() == mode
        if self.verbose:
            print('%s: -> done setting digipot mode'%self.name)
        return None

    def get_focus_flag(self):
        if self.verbose:
            print('%s: getting focus flag'%self.name)
        in_focus = bool(int(self._send('FOCUS')))
        if self.verbose:
            print('%s: -> in_focus = %s'%(self.name, in_focus))
        return in_focus

    def close(self):
        if self.verbose: print("%s: closing..."%self.name, end=' ')
        self.port.close()
        if self.verbose: print("done.")
        return None

if __name__ == '__main__':
    autofocus = Controller(which_port='COM8', verbose=True, very_verbose=False)

    import numpy as np
    import random
    iterations = 10
    
    print('\n# Testing piezo range:') # NOTE: only certain values are accepted!
    ranges = np.linspace(1, 1000, iterations)
    for range_um in ranges:
        autofocus.set_piezo_range_um(range_um)

    print('\n# Testing voltage range:')
    voltages = np.linspace(0, 1, iterations)
    for v in voltages:
        autofocus.set_piezo_voltage(v)

    print('\n# Testing random voltages:')
    for i in range(iterations):
        v = random.uniform(0, 1)
        autofocus.set_piezo_voltage(v)

##    print('\n# Testing objectives:')
##    for i in range(6):
##        autofocus.set_current_objective(i + 1)
##    autofocus.set_current_objective(1)

    print('\n# Testing servo:')
    autofocus.set_servo_enable(True)
    autofocus.set_servo_enable(False)

    print('\n# Testing digipot:')
    autofocus.set_digipot_mode('Focus')
    autofocus.set_digipot_mode('Offset')

    print('\n# Testing focus flag:')
    autofocus.get_focus_flag()
    
    autofocus.close()
