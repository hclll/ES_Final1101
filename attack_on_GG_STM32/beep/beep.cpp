#include "beep.h"
#include "ThisThread.h"
#include "Thread.h"
#include "mbed.h"
#include <cstdint>

/** class to make sound with a buzzer, based on a PwmOut
 *   The class use a timeout to switch off the sound  - it is not blocking while making noise
 *
 * Example:
 * @code
 * // Beep with 1Khz for 0.5 seconds
 * #include "mbed.h"
 * #include "beep.h"
 * 
 * Beep buzzer(p21);
 * 
 * int main() {
 *       ...
 *   buzzer.beep(1000,0.5);    
 *       ...
 * }
 * @endcode
 */

using namespace mbed;
 // constructor
 /** Create a Beep object connected to the specified PwmOut pin
  *
  * @param pin PwmOut pin to connect to 
  */
    
Beep::Beep(PinName pin) : _digitalOut(pin) {
    _digitalOut.write(0);     // after creating it have to be off
}

 /** stop the beep instantaneous 
  * usually not used 
  */
void Beep::nobeep() {
    _digitalOut.write(0);
}

/** Beep with given frequency and duration.
 *
 * @param frequency - the frequency of the tone in Hz
 * @param time - the duration of the tone in seconds
 */
     
void Beep::beep(float time) {

    _digitalOut.write(1);
    printf("beep %d\n", (uint32_t)time);
    ThisThread::sleep_for((uint32_t)time);
    Beep::nobeep();
    

    // toff.attach(&Beep::nobeep, time);   // time to off
}




