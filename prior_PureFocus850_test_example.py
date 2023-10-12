import pi_E_709_1C1L        # github.com/amsikking/pi_E_709_1C1L
import prior_PureFocus850

piezo = pi_E_709_1C1L.Controller('COM27', 0, 800, verbose=True)
autofocus = prior_PureFocus850.Controller(which_port='COM8', verbose=True)

# Test focusing with serial port commands to the piezo:
z_um = 5
for i in range(z_um):
    piezo.move_um(i)
for i in range(z_um):
    piezo.move_um(-i)

# Prepare to switch piezo to analogue control mode:
# -> consider picking z_range_um < objective working distance
z_range_um = 300
piezo.set_analog_control_limits(                # 0-10V is 'z_range_um'
    v_min=0, v_max=10, z_min_ai=0, z_max_ai=z_range_um)
autofocus.set_piezo_range_um(z_range_um)        # pass 'z_range_um' to autofocus
z0_voltage = piezo.get_voltage_for_move_um(0)    # get voltage for ~zero motion
autofocus.set_piezo_voltage(z0_voltage)          # set voltage for ~zero motion

# Switch piezo to analogue control mode and enable autofocus:
if not autofocus.get_sample_flag():                 # is a sample detected?
    input('\n***WARNING***: sample flag=FALSE\n')
input('\nTest stability (enter to continue)\n')     # gentle press on sample?
piezo.set_analog_control_enable(True)               # switch piezo to analog
autofocus.set_servo_enable(True)                    # enable autofocus
autofocus.set_digipot_mode('Offset')                # set digipot for user
input('\nRe-test stability (enter to continue)\n')  # is it working? (test)
if not autofocus.get_focus_flag():                  # has it found focus?
    print('\n***WARNING***: focus flag=FALSE\n')
autofocus.set_servo_enable(False)                   # disable autofocus
piezo.set_analog_control_enable(False)              # switch piezo to serial

# close:
autofocus.close()
piezo.close()
