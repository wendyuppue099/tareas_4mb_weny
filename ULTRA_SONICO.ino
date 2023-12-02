const int trigPin = 9;   // Pin de activación del sensor ultrasónico
const int echoPin = 10;  // Pin de eco del sensor ultrasónico
long duracion;           // Variable para almacenar la duración del pulso ultrasónico
int distancia;           // Variable para almacenar la distancia calculada

void setup() {
  pinMode(trigPin, OUTPUT);  // Configura el pin de activación como salida
  pinMode(echoPin, INPUT);   // Configura el pin de eco como entrada
  
  Serial.begin(9600);        // Inicia la comunicación serial a 9600 baudios
  
  while (!Serial) {
    delay(10);               // Espera a que se establezca la comunicación serial
  }

  // Limpia la pantalla de la consola
  Serial.write(27);
  Serial.print("[2J");
  Serial.write(27);
  Serial.print("[H");

  // Imprime un encabezado en el Monitor Serie
  Serial.println("Medición de Distancia");
  Serial.println("_____________________");
  Serial.println("Distancia (cm)");
  Serial.println();
}

void loop() {
  digitalWrite(trigPin, LOW);         // Apaga el pin de activación
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);        // Envía un pulso de activación
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);         // Apaga el pulso de activación
  
  duracion = pulseIn(echoPin, HIGH);   // Mide la duración del pulso de eco
  
  // Calcula la distancia en centímetros usando la fórmula de velocidad
  distancia = (duracion * 0.034) / 2;

  // Imprime la distancia en centímetros en el Monitor Serie
  Serial.print(distancia);

  // Imprime una línea en blanco para mejorar la visualización
  Serial.println();

  delay(300);  // Espera 300 milisegundos antes de la próxima medición
}
