import pi_E_709_1C1L
import prior_PureFocus850

piezo = pi_E_709_1C1L.Controller('COM15', 0, 800, verbose=True)
autofocus = prior_PureFocus850.Controller(which_port='COM8', verbose=True)

# Test focusing with serial port commands to the piezo:
for i in range(10):
    piezo.move_um(i)
for i in range(10):
    piezo.move_um(-i)

# Prepare to switch piezo to analogue control mode:
piezo.set_analog_control_limits(                # 0-10V is 0-300um range
    v_min=0, v_max=10, z_min_ai=0, z_max_ai=300)
z_voltage = piezo.get_voltage_for_move_um(0)    # get voltage for ~zero motion
autofocus.set_piezo_range_um(300)               # pass piezo range to autofocus
autofocus.set_piezo_voltage(z_voltage)          # set voltage for ~zero motion

# Switch piezo to analogue control mode and enable autofocus:
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
