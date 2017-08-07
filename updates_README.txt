Updates:

change "Use Joystick" checkbox into "Sync Joystick"
STATUS: COMPLETE

ensure joystick sync rate (update_refresh_rate) is distinct from 
    auto query update rate (update_rate)
STATUS: COMPLETE

add a new "Use Joystick" checkbox to initiate joystick motor control
STATUS: COMPLETE

auto-uncheck "Use Joystick" cb if "Sync Joystick" cb is deselected
STATUS: COMPLETE

add a new timer for motor controll transmission rate (red box 
    currently)
STATUS: COMPLETE

add color to text boxes to indicate whether their related functions 
    are active
STATUS: COMPLETE

update the target marker on the gui dials whenever joystick motor 
    control is halted
STATUS: COMPLETE

add a safety button (joystick trigger) to prevent unwanted motor 
    control transmission
STATUS: COMPLETE

add motor control hex code transmission
STATUS: COMPLETE

when sync box gets unchecked, the motor event still runs
STATUS: FIXED






when sync joystick is unchecked, the motors return to zero position
STATUS:

add limits of movement
STATUS: COMPLETE

add text labels to sync rate and motor control rate text boxes
STATUS: unnecessary?

add a "zero" button to calibrate az/el
STATUS: 

track the dish orientation using the az/el dials
STATUS:

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Joystick fine adjustment code
--using the hat and adjustable degree amounts (one button to switch)
--degree increments of .1, 1, 5, 10, or user input?


add "fine tune" checkbox to switch from joy control to hat control
STATUS: COMPLETE

use same motor control speed as useJoystick?
ANSWER:

add button (button 2 of the saitek joystick) to switch degree increments
STATUS: COMPLETE

add a text display or label to indicate which degree increment is active
STATUS: COMPLETE

add a text box for degree increment input?
ANSWER: NO

"fine tune" checkbox should only be checkable when both "sync joystick" and "use joystick" are checked
STATUS: 



7-16-17
display degree increment for fine tune control                                      |   COMPLETE
faster hat and deg inc button refresh rate                                          |   
add time delay for hat input                                                        |
unchecking "sync" needs to uncheck "fine tune"                                      |
unchecking "sync" needs to NOT return motor to calibrated zero                      |
add calibration feature                                                             |
add motor angle tracking on the gui dials during all levels of joystick control     |

degree increment for fine-tune hat control
current: .1, 1, 5, 10
proposed: .1, .5, 1, 5, (10?)


7-21-17
hat abandoned due to ease of mistakes in input (user too easily accidentally flicks up/down when only trying to go left/right, and vice versa)
need to fix joystick code so when you uncheck "sync joystick" and "use joystick," the motor doesn't return to home or some other position.
need to allow the fine gui input alongside with the joystick input


7-25-17

