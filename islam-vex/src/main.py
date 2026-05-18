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
    inertial_1.calibrate() # Calibrate the inertial sensor

    wait(2, SECONDS)
    brain.screen.set_cursor(1,1)
    brain.screen.clear_line(1)
    brain.screen.print("Inertial calibration complete")

def testInertial():
    """
    1. Test the inertial sensor by having it display heading and rotational data
    2. Press the button to end the test
    """

    brain.screen.clear_screen()
    while(bumpSwitch.pressing() == False):
        wait(10, MSEC) # Debouncing the button
        brain.screen.set_cursor(5, 1)
        brain.screen.print("Heading:  " + str(inertial_1.heading()))
        brain.screen.set_cursor(6, 1)
        brain.screen.print("Rotation:  " + str(inertial_1.rotation()))
        brain.screen.set_cursor(8, 1)
        brain.screen.print("Press the button to end the test")

def driveStraightData(e):
    """
    1. Report position, rotation, and the error
    2. Parameter: e is equal to our error value (setpoint - rotation)
    """

    brain.screen.set_cursor(1,1) # Setting cursor at location 1, 1
    brain.screen.print("Position: " + str(leftMotor.position())) # Returning current encoder count

    brain.screen.set_cursor(1,1) # Setting cursor at location 1, 1
    brain.screen.print("Rotation: " + str(inertial_1.rotation())) # Returning current rotation count

    brain.screen.set_cursor(1,1) # Setting cursor at location 1, 1
    brain.screen.print("Error: " + str(e)) # Returning current error

def stopMotors():
    """
    Stop both motors at the same time
    """

    rightMotor.stop()
    leftMotor.stop()
    wait(0.5, SECONDS) # Letting the robot system stabilize with a 0.5 second wait

def driveStraight(distance, setpoint, motorVelocity):
    """
    1. distance  = distance in inches
    2. setpoint = 0-degrees for driving straight
    3. motorVelocity = nominal motor velocity (+) => Forward, (-) => Reverse
    """

    inertial_1.reset_rotation() # Resetting the rotation value to 0 before taking action

    kP = 0.60   # Proportional constant for driving straight
                # Used calculate the correction to maintain course
                # If too small, correction will occur too slowly
                # If too large, over-correction will occur
                # Determine best value by iteratively testing

    wheelDiameter = 4 # 4" wheel diameter
    wheelCircumference = wheelDiameter * math.pi   # wheel circumference

    # Convert the distance in inches to distance in "ticks"
    # distance (ticks) = (distance in inches / Wheel Circumference) * 360

    distance = (distance / wheelCircumference) * 360

    # Reset the motor encoders 
    leftMotor.set_position(0, DEGREES)
    rightMotor.set_position(0, DEGREES)

    # Drive forward if motor velocity > 0
    if (motorVelocity > 0):
        # While loop to track the distance traveled
        while(leftMotor.position() < distance):
            error = (setpoint - inertial_1.rotation()) # error
            correction = kP * error # Motor velocity correction

            # Correct motor velocities
            # If error > 0 (Setpoint is greater than the rotation) => drifting left
            # If error < 0 (Setpoint is less than the rotation) => drifting right

            leftMotor.set_velocity((motorVelocity + correction), PERCENT)
            rightMotor.set_velocity((motorVelocity - correction), PERCENT)


            # Spin the motors
            leftMotor.spin(FORWARD)
            rightMotor.spin(FORWARD)

            driveStraightData(error) # Display position, rotation, and error

        stopMotors() # Stop both motors once desire distance is reached

    else:
        # While loop to track the distance traveled
        distance *= -1 # distance = distance * -1
        while(leftMotor.position() > distance):
            error = (setpoint - inertial_1.rotation()) # error
            correction = kP * error # Motor velocity correction

            # Correct motor velocities
            # If error > 0 (Setpoint is greater than the rotation) => drifting left
            # If error < 0 (Setpoint is less than the rotation) => drifting right

            leftMotor.set_velocity((motorVelocity + correction), PERCENT)
            rightMotor.set_velocity((motorVelocity - correction), PERCENT)


            # Spin the motors
            leftMotor.spin(FORWARD)
            rightMotor.spin(FORWARD)

            driveStraightData(error) # Display position, rotation, and error

        stopMotors() # Stop both motors once desire distance is reached

#-----------------------------------------------------------------------------


#-------------------------Define main() Function-------------------------------
def main():
    """
    The main() function is the program that is executed by the Brain
    """

    bump()                          # Call the bump() function to begin program execution
    leftMotor.set_stopping(BRAKE)   # This mode will help reduce the "lurch" effect
    rightMotor.set_stopping(BRAKE) 
    inertialCalibration()           # Calibrate the inertial sensor

    driveStraight(87, 0, 50)        # Call driveStraight with the necessary distance
    wait(2, SECONDS)
    driveStraight(87, 0, -50)
#-----------------------------------------------------------------------------
main()