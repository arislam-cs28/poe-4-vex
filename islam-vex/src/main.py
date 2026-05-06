# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       Arisha I, Amy W                                              #
# 	Created:      5/4/2026, 2:15:03 PM                                         #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# Brain should be defined by default
brain=Brain()

#--------------------------Robot Configuration--------------------------------

rightMotor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)  # the right drive train motor
leftMotor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)    # the left drive train motor
liftMotor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)   # the lift motor
inertial_1 = Inertial(Ports.PORT5)                              # setting inertial sensor
liftArmRotation = Rotation(Ports.PORT6, False)                  # LiftArmRotation sensor
bumpSwitch = Bumper(brain.three_wire_port.a)                    # Bumper switch set
#-----------------------------------------------------------------------------


#-------------------------Helper Functions------------------------------------
def bump():
    """
    Hold the program's execution until the button is pressed
    """

    while(bumpSwitch.pressing() == False):
        wait(10, MSEC) # Debouncing the button

        brain.screen.set_cursor(1, 1) # Placing cursor into row 1, column 1 position
        brain.screen.print("Press the button to start the program") 

        pass

    brain.screen.clear_line(1) # Clearing the first line of the LCD screen
    brain.screen.set_cursor(1,1)
    brain.screen.print("Program executed")
    wait (1, SECONDS)

def inertialCalibration():
    """
    1. Calibrate the inertial sensor.
    2. Include a 2 second wait time for calibration
    3. Call this function at the start of the program's execution
    """

    brain.screen.clear_screen()
    brain.screen.set_cursor(1,1)
    brain.screen.print("Calibrating the inertial sensor")
    brain.screen.set_cursor(2,1)
    brain.screen.print("Don't move the robot!")
    inertial_1.calibrate() # calibrate the inertial sensor

    wait(2, SECONDS)
    brain.screen.set_cursor(1,1)
    brain.screen.clear_line(1)
    brain.screen.print("Inertial calibration complete")

#-----------------------------------------------------------------------------


#-------------------------Define main() Function-------------------------------
def main():
    """
    The main() function is the program that is executed by the Brain
    """

    bump() # call the bump() function to begin program execution

#-----------------------------------------------------------------------------
main()


