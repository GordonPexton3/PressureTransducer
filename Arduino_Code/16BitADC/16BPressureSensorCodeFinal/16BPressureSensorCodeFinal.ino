#include <Adafruit_ADS1X15.h>

#define KEY_STRING "ARDU "
#define PRESSURE2 95
#define VAL2 17895
#define PRESSURE1 72
#define VAL1 14420

float slope = (float)(PRESSURE2 - PRESSURE1) / (VAL2 - VAL1);
float intercept = (float)(PRESSURE1 - (slope * VAL1));
String response;

Adafruit_ADS1115 ads;  /* Use this for the 16-bit version */

void setup(void)
{
  Serial.begin(9600);

  // The ADC input range (or gain) can be changed via the following
  // functions, but be careful never to exceed VDD +0.3V max, or to
  // exceed the upper and lower limits if you adjust the input range!
  // Setting these values incorrectly may destroy your ADC!
  //                                                                ADS1015  ADS1115
  //                                                                -------  -------
  // ads.setGain(GAIN_TWOTHIRDS);  // 2/3x gain +/- 6.144V  1 bit = 3mV      0.1875mV (default)
  ads.setGain(GAIN_ONE);        // 1x gain   +/- 4.096V  1 bit = 2mV      0.125mV
  // ads.setGain(GAIN_TWO);        // 2x gain   +/- 2.048V  1 bit = 1mV      0.0625mV
  // ads.setGain(GAIN_FOUR);       // 4x gain   +/- 1.024V  1 bit = 0.5mV    0.03125mV
  // ads.setGain(GAIN_EIGHT);      // 8x gain   +/- 0.512V  1 bit = 0.25mV   0.015625mV
  // ads.setGain(GAIN_SIXTEEN);    // 16x gain  +/- 0.256V  1 bit = 0.125mV  0.0078125mV

  if (!ads.begin()) {
    Serial.println("Failed to initialize ADS.");
    while (1);
  }
  // Serial.println(slope);
  // Serial.println(intercept);
}

void loop(void)
{
  // Serial.println("___________________________");
  // Serial.println(ads.readADC_SingleEnded(0));
  response.concat(KEY_STRING);
  response.concat(slope*ads.readADC_SingleEnded(0) + intercept);
  Serial.println(response);
  response = "";

  delay(1000);
}