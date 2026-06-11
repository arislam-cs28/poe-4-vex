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
driveTrain = DriveTrain(leftMotor, rightMotor)                  # run both motors simultaneously
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

    brain.screen.set_cursor(1,1)                                    # Setting cursor at location 1, 1
    brain.screen.print("Position: " + str(leftMotor.position()))    # Returning current encoder count

    brain.screen.set_cursor(2,1)                                    # Setting cursor at location 1, 1
    brain.screen.print("Rotation: " + str(inertial_1.rotation()))   # Returning current rotation count

    brain.screen.set_cursor(3,1)                                    # Setting cursor at location 1, 1
    brain.screen.print("Error: " + str(e))                          # Returning current error

def stopMotors():
    """
    Stop both motors at the same time
    """

    driveTrain.stop()
    wait(0.5, SECONDS) # Letting the robot system stabilize with a 0.5 second wait

def driveStraight(distance, setpoint, motorVelocity):
    """
    1. distance  = distance in inches
    2. setpoint = 0-degrees for driving straight
    3. motorVelocity = nominal motor velocity (+) => Forward, (-) => Reverse
    """

    inertial_1.reset_rotation() # Resetting the rotation value to 0 before taking action

    # Setting the stopping mode for the motors
    leftMotor.set_stopping(COAST)
    rightMotor.set_stopping(COAST)


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
            driveTrain.drive(FORWARD)

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
            driveTrain.drive(FORWARD)

            driveStraightData(error) # Display position, rotation, and error

        stopMotors() # Stop both motors once desire distance is reached

def turnData(turnError, derivative):
    brain.screen.set_cursor(1,1) # Setting cursor at location 1, 1
    brain.screen.print("Heading: " + str(inertial_1.heading())) # Returning heading

    brain.screen.set_cursor(2,1) # Setting cursor at location 2, 1
    brain.screen.print("Error: " + str(abs(turnError))) # Returning turnign error

    brain.screen.set_cursor(3,1) # Setting cursor at location 3, 1
    brain.screen.print("Derivative: " + str(abs(derivative))) # Returning the derivative

def pointTurn(setPoint):
    """
    1. Perform a point turn using the inertial sensor heading and proportional derivative control
    2. Argument: Desired heading (setPoint) in degrees
    """

    brain.screen.clear_screen() # Clear the screen

    # Set stopping mode for the left and right motors
    leftMotor.set_stopping(BRAKE)
    rightMotor.set_stopping(BRAKE)

    # Calculate the difference between the setPoint and the current heading
    # to determine the turning direction

    difference = setPoint - inertial_1.heading()

    # Want to turn the smallest amount to reach the desired heading (not the reflex angle)
    if (setPoint > inertial_1.heading()):   # Setpoint
        if (abs(difference) <= 180):
            clockwise = True # Turn CW
        else:
            clockwise = False # Turn CCW
        
    else:
        if (abs(difference) <= 180):
            clockwise = False # Turn CCW
        else:
            clockwise = True # Turn CW
    
    # Define the kP and kD for CW and CCW turns
    if (clockwise):     # Values for a CW turn
        kP = 0.097      # 0.096 looks nice
        kD = 0.001      # 0.001
    else:               # Values for a CCW turn
        kP = 0.095      # 0.099 looks nice
        kD = 0.002     # 0.001
    
    # Define maximum turning velocity and previous error term
    maxVelocity = 50    # Maximum turning velocity
    previousError = 0.0 # Error from the previous loop iteration

    while(True):
        turnError = setPoint - inertial_1.heading() # Calculate error
        derivative = turnError - previousError      # Current error - previous error

        # Break out of the loop and stop turning when the setpoint is reached without oscillation
        if((abs(turnError) < 1) and (abs(derivative) < 0.2)):
           stopMotors()     # Stop motors
           break            # Exit the while loop 

        # Calculate the correction for the motor velocities
        turnCorrection = (kP * turnError) + (kD * derivative)

        # Limit the turnCorrection to be between -1 and 1
        # This will keep the motor velocity <= maximum turn velocity
        if(abs(turnCorrection) > 1):
            turnCorrection = 1
        
        turnVelocity = maxVelocity * turnCorrection

        # Set the motor velocities based on the direction (CW or CCW)
        if (clockwise): # Turn clockwise
            leftMotor.set_velocity(turnVelocity)
            rightMotor.set_velocity(-1 * turnVelocity)
        else: # Turn counterclockwise
            leftMotor.set_velocity(-1 * turnVelocity)
            rightMotor.set_velocity(turnVelocity)
        
        # Spin the motors
        leftMotor.spin(FORWARD)
        rightMotor.spin(FORWARD)

        turnData(turnError, derivative) # Print heading, error, and derivative

        previousError = turnError # Update previous error time
        wait(20, MSEC) # Setting general wait time

def liftArm(motorVelocity, liftAngle):
    # Configure the motor to hold its position once we life the object up, so the robot doesn't drop it
    liftMotor.set_stopping(HOLD)

    liftMotor.set_velocity(motorVelocity, PERCENT)

    gearRatio = 5 # 60T to 12T
    motorAngularDisplacement = liftAngle * gearRatio # Calculate the motor axle's angular displacement

    # Spin the motor forward for the given angular displacement
    liftMotor.spin_for(FORWARD, motorAngularDisplacement, DEGREES)
    wait(0.5, SECONDS) # Letting the system stabilize

#-----------------------------------------------------------------------------


#-------------------------Define main() Function-------------------------------
def main():
    """
    The main() function is the program that is executed by the Brain
    """

    bump()                          # Call the bump() function to begin program execution
    inertialCalibration()           # Calibrate the inertial sensor

    driveStraight(2, 0, 50)
    liftArm(20, 13)
    # liftArm(20, 64)
#-----------------------------------------------------------------------------
main()