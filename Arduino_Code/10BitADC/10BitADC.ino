#define VIN_PIN A6
#define KEY_STRING "ARDU "
#define SLOPE 0.2441406
#define INTERCEPT -18.0
#define ADC_RES 12

void setup(void) {
  Serial.begin(9600);
  analogReadResolution(ADC_RES);
}

float pressure;
String response;
void loop() {
  response.concat(KEY_STRING);
  pressure = SLOPE*analogRead(VIN_PIN) + INTERCEPT;
  response.concat(pressure); 
  Serial.println(response); 
  response = "";
  delay(500);
}

