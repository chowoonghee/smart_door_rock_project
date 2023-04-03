
// lcd---------------------------------------------------------------
#include <Adafruit_GFX.h>
#include <TouchScreen.h>
#include <Adafruit_TFTLCD.h>

#define YP A3  // must be an analog pin, use "An" notation!
#define XM A2  // must be an analog pin, use "An" notation!
#define YM 9   // can be a digital pin
#define XP 8   // can be a digital pin

#define TS_MINX 210
#define TS_MINY 210
#define TS_MAXX 915
#define TS_MAXY 910

//SPI Communication
#define LCD_CS A3
#define LCD_CD A2
#define LCD_WR A1
#define LCD_RD A0
// optional
#define LCD_RESET A4

//Color Definitons
#define BLACK     0x0000
#define BLUE      0x001F
#define GREY      0xCE79
#define LIGHTGREY 0xDEDB
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF

#define MINPRESSURE 1
#define MAXPRESSURE 1000

TouchScreen ts = TouchScreen(XP, YP, XM, YM, 364);

//Size of key containers 70px
#define BOXSIZE 85

//2.4 = 240 x 320
//Height 319 to fit on screen

Adafruit_TFTLCD tft(LCD_CS, LCD_CD, LCD_WR, LCD_RD, LCD_RESET);

//Container variables for touch coordinates
int X, Y, Z;
int a= 10;
String Pass=""; // 비밀번호 입력 담는 변수
String Open =""; // 입력받은 값을 저장하여 현재 등록된 비밀번호 비교하는 변수
String test = ""; // sql로 값 넣을 거임 
String Pass_change=""; 
int matching = 0;
int login_check = 0;
String serigo="";
String guest_pass ="";
int false_pass = 0;
int husu = 0;
int sound_track = 932;






// 번호판 랜덤 생성
int one ;
int two ;
int three ; 
int four ;
int five ;
int six ;
int seven ;
int eight ;
int nine ;
int zero ;












//Screen height without hidden pixel
double tHeight = tft.height() - 1;
//Centering the mid square
double center = (tft.width() / 2) - (BOXSIZE / 2);
//Space between squares
double padding = 10;
//Position of squares to the left and right of center
double fromCenter = BOXSIZE + padding;
//Second row Y-Axis position
double secondRow = BOXSIZE + padding;
//Third row Y-Axis position
double thirdRow = secondRow + BOXSIZE + padding;
//Fourth row Y-Axis position
double fourthRow = thirdRow + BOXSIZE + padding;
//Y-Axis align for all squares
double verticalAlign = (tHeight - ((BOXSIZE * 4) + (padding * 3))) / 2;
//Left column starting x posision
double leftColPositionX = center - fromCenter;
//Mid column starting x posision
double midColPositionX = center;
//Right column starting x posision
double rightColPositionX = center + fromCenter;

// 솔레노이드-------------------------------------------------------------

#include <Servo.h>
int recvdata; // 시리얼모니터에 작성하는 데이터 값
int value = 0; // 서보모터의 각도 기본값
int solenoid = 12; // 도어락(솔레노이드) 핀을 12번으로 설정

//스피커
int buzzer = 11;
int note[] = {2093,2349,2637,2793,3136,3520,3951,4186}; //문열림
int notes[] = {4186,3951,3520,3136,2793,2637,2349,2093}; // 문닫힘
int false_notes[]={4186,4186,4186};

//스위치
int swich_button = 0; //비밀번호 변경 if조건문


//sd카드
#include <SD.h>
File myFile;
int sensor = 22;                                 // 센서 입력값 7번핀
int Value = 0;                                   // loop에서 사용할 value 변수 설정

//적외선신체감지센서
int sound = 1;

int shoot = 0;
int random_number = 0;

//지문인식센서
#include <Adafruit_Fingerprint.h>
#if (defined(__AVR__) || defined(ESP8266)) && !defined(__AVR_ATmega2560__)
SoftwareSerial mySerial(18, 19);  // 18:노랑, 19:검정
#else
#define mySerial Serial1
#endif
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);
uint8_t id =1; 


void setup() {
  Serial.begin(115200);
  //espserial.begin(115200);
  //지문인식센서
  mySerial.begin(9600);  // 소프트웨어 시리얼 통신 시작
  finger.begin(57600);  // 지문인식 센서 모듈 시작
  // if (finger.verifyPassword()) {
  //   //Serial.println("Found fingerprint sensor!");
  // } else {
  //   //Serial.println("Did not find fingerprint sensor :(");
  // }
  // //finger.emptyDatabase(); //지문 전체삭제

  
  //센서
  pinMode (sensor, INPUT);          //  핀모드 센서 입력값으로 설정
  
  //스위치
  pinMode(10, INPUT_PULLUP);
   
  // //tft lcd
  // tft.reset();
  // uint16_t identifier = tft.readID();
  // tft.begin(identifier);

  // // Background color
  // tft.fillScreen(BLACK);
  // tft.setRotation(2);
  // // draw num pad
  // createButtons();
  // insertNumbers();

  //솔레노이드
  pinMode(solenoid, OUTPUT); // 도어락 출력장치 설정

  //스피커
  pinMode(buzzer, OUTPUT);     //11번핀을 출력으로 설정.

}

//지문인식센서 관련코드
uint8_t getFingerprintEnroll() { //지문인식 등록함수

  int p = -1;
  //Serial.print("Waiting for valid finger to enroll as #"); Serial.println(id);
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image taken");
      break;
    case FINGERPRINT_NOFINGER:
      Serial.println(".");
      break;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      break;
    case FINGERPRINT_IMAGEFAIL:
      Serial.println("Imaging error");
      break;
    default:
      Serial.println("Unknown error");
      break;
    }
  }
   p = finger.image2Tz(1);
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
     Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Could not find fingerprint features");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }
  //Serial.println("Remove finger");
  delay(2000);
  p = 1;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
  }
 Serial.print("ID "); Serial.println(id);
  p = -1;
  Serial.println("Place same finger again");
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image taken");
      break;
    case FINGERPRINT_NOFINGER:
      Serial.print(".");
      break;
    case FINGERPRINT_PACKETRECIEVEERR:
     Serial.println("Communication error");
      break;
    case FINGERPRINT_IMAGEFAIL:
      Serial.println("Imaging error");
      break;
    default:
      Serial.println("Unknown error");
      break;
    }
  }

  // OK success!

  p = finger.image2Tz(2);
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Could not find fingerprint features");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }

  // OK converted!
  Serial.print("Creating model for #");  Serial.println(id);

  p = finger.createModel();
  if (p == FINGERPRINT_OK) {
    Serial.println("Prints matched!");

  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_ENROLLMISMATCH) {
    Serial.println("Fingerprints did not match");
    return p;
  } else {
    Serial.println("Unknown error");
    return p;
  }

  Serial.print("ID "); Serial.println(id);
  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.println("Stored!");
    if (sound ==1){
      tone(buzzer,262);
    delay(200);      
    noTone(buzzer);
    }
    id= id+1;




  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_BADLOCATION) {
    Serial.println("Could not store in that location");
    return p;
  } else if (p == FINGERPRINT_FLASHERR) {
    Serial.println("Error writing to flash");
    return p;
  } else {
    Serial.println("Unknown error");
    return p;
  }

  return true;
}

// fingerprinttt //////////////////////////////////////////////////
uint8_t getFingerprintID() {
  uint8_t p = finger.getImage();
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image taken");
      break;
    case FINGERPRINT_NOFINGER:
      Serial.println("No finger detected");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_IMAGEFAIL:
      Serial.println("Imaging error");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }

  // OK success!

  p = finger.image2Tz();
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Could not find fingerprint features");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }

  // OK converted!
  p = finger.fingerSearch();
  if (p == FINGERPRINT_OK) {
    Serial.println("Found a print match!");
    Serial.println("");
    if (sound ==1){
      tone(buzzer,262);
    delay(200);      
    noTone(buzzer);
    }
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_NOTFOUND) {
    Serial.println("Did not find a match");
    if (sound ==1){
      int elementCount1 = sizeof(false_notes) / sizeof(int);
      for (int i=0; i < elementCount1; i++)    //note를 play
      {
        tone(buzzer,false_notes[i],500);
        delay(500);
      }
    }
    
      matching=0;
    return p;
  } else {
    Serial.println("Unknown error");
    if (sound ==1){
      int elementCount1 = sizeof(false_notes) / sizeof(int);
      for (int i=0; i < elementCount1; i++)    //note를 play
      {
        tone(buzzer,false_notes[i],500);
        delay(500);
      }
    }
    
    return p;
  }

  // found a match!
  Serial.print("Found ID #"); 

  Serial.println(finger.fingerID);
  Serial.print("\n문이 열립니다.");
  digitalWrite(solenoid, HIGH); // 솔레노이드 열리기
  if(sound==1){
      int elementCount = sizeof(note) / sizeof(int);
      for (int i=0; i < elementCount; i++)    //note를 play
      {
        tone(buzzer,note[i],500);
        delay(100);
      }
  }
  


  delay(5000);
  //Serial.print("\n문이 닫힙니다.");
      digitalWrite(solenoid, LOW); // 솔레노이드 닫히기
      delay(1000);
    if(sound==1){
      int elementCount1 = sizeof(notes) / sizeof(int);
      for (int i=0; i < elementCount1; i++)    //note를 play
      {
        tone(buzzer,notes[i],500);
        delay(100);
      }
    }
    

    Open= "";
    matching = 0;
    
  
  return finger.fingerID;
}

// returns -1 if failed, otherwise returns ID #
int getFingerprintIDez() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK)  return -1;

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK)  return -1;

  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK)  return -1;

  // found a match!
  //Serial.print("Found ID/ #");
  // Serial.println(finger.fingerID);
  // Serial.println("getFingerprintIDez");
  // Serial.print(" with confidence of "); Serial.println(finger.confidence);
  return finger.fingerID;
}

// deleteeee //////////////////////////////////////////////////////////
uint8_t deleteFingerprint(uint8_t id) {
  uint8_t p = -1;

  p = finger.deleteModel(id);

  if (p == FINGERPRINT_OK) {
    //Serial.println("Deleted!");
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    //Serial.println("Communication error");
  } else if (p == FINGERPRINT_BADLOCATION) {
    //Serial.println("Could not delete in that location");
  } else if (p == FINGERPRINT_FLASHERR) {
   // Serial.println("Error writing to flash");
  } else {
    //Serial.print("Unknown error: 0x"); Serial.println(p, HEX);
  }
  return p;
}




void door_open(){
  
  //Serial.print("\n문이 열립니다.");
  digitalWrite(solenoid, HIGH); // 솔레노이드 열리기
  delay(1000);

}

void door_close(){
      
      //Serial.print("\n문이 닫힙니다.");
      digitalWrite(solenoid, LOW); // 솔레노이드 닫히기
      delay(1000);
}


void pass_changer(){ //비밀번호변경함수
  int boxHeightRow1 = verticalAlign + BOXSIZE;
  int boxHeightRow2 = secondRow + BOXSIZE;
  int boxHeightRow3 = thirdRow + BOXSIZE;
  int boxHeightRow4 = fourthRow + BOXSIZE;

  if (Z > MINPRESSURE && Z < MAXPRESSURE) {

    //redraw numpad to clear old number
    tft.fillScreen(BLACK);
    createButtons();
    insertNumbers();
    //default text setup for number display on tft
    tft.setCursor(100, 120);
    //tft.setTextColor(RED);
    tft.setTextSize(9);

    //Check if element clicked is in left column
    if (X > leftColPositionX && X < (leftColPositionX + BOXSIZE)) {
      //Check if element clicked is in row 1
      if (Y > verticalAlign) {
        if (Y < boxHeightRow1)
        {
          if(sound==1)
          {
            tone(buzzer,262);
            delay(200);      
            noTone(buzzer);
            delay(200);
          }
          Serial.println("#");
          test = Pass_change;
          Pass_change = "";
          swich_button = 0;
        }

        //Check if element clicked is in row 2
        else if (Y < boxHeightRow2) {
          //Serial.println("9");
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass_change = Pass_change +"9";
          //Serial.println(Pass);
          }

        }
        //Check if element clicked is in row 3
        else if (Y < boxHeightRow3) {
          //Serial.println("6");
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
         if(a >Pass.length()){
            Pass_change = Pass_change +"6";
          //Serial.println(Pass);
          }
          // Pass = Pass +"7";
          // Serial.println(Pass);
        }
        //Check if element clicked is in row 4
        else if (Y < boxHeightRow4) {
          //Serial.println("3");
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass_change = Pass_change +"3";
          //Serial.println(Pass);
          }
        }
      }
      //Check if element clicked is in mid column
    } 
    else if (X > midColPositionX && X < (midColPositionX + BOXSIZE)) {
      //Check if element clicked is in row 1
      if (Y > verticalAlign) {
        if (Y < boxHeightRow1) {
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass_change = Pass_change +"0";
          //Serial.println(Pass);
          }
        }
        
        //Check if element clicked is in row 2
        else if (Y < boxHeightRow2) {
          //Serial.println("8");
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass_change = Pass_change +"8";
          //Serial.println(Pass);
          }
        }

        //Check if element clicked is in row 3
        else if (Y < boxHeightRow3) {
          //Serial.println("5");
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass_change = Pass_change +"5";
          //Serial.println(Pass);
          }
          
        }
        //Check if element clicked is in row 4
        else if (Y < boxHeightRow4) {
         // Serial.println("2");
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass_change = Pass_change +"2";
          //Serial.println(Pass);
          }
          
        }
      }

    } 
    else if (X > rightColPositionX && X < (rightColPositionX + BOXSIZE)) {
      if (Y > verticalAlign) {
        //Check if element clicked is in row 1
        if (Y < boxHeightRow1) {
          Serial.println("*");
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          delay(1000);
          getFingerprintEnroll();
          Pass_change = "";
          
        }
        //Check if element clicked is in row 2
        else if (Y < boxHeightRow2) {
          Serial.println("7");
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass_change = Pass_change +"7";
          //Serial.println(Pass);
          }
          // Pass = Pass +"6";
          // Serial.println(Pass);

        }
        //Check if element clicked is in row 3
        else if (Y < boxHeightRow3) {
          Serial.println("4");
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);

          }
          if(a >Pass.length()){
            Pass_change = Pass_change +"4";//////////////////
          //Serial.println(Pass);
          }
          // Pass = Pass +"9";
          // Serial.println(Pass);
        }
        //Check if element clicked is in row 3
        else if (Y < boxHeightRow4) {
          Serial.println("1");
          if(sound==1){
            tone(buzzer,262);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass_change = Pass_change +"1";//////////////////
          //Serial.println(Pass);
          }
        }
      }
    }
  }
}



void Open_pass(){
  int boxHeightRow1 = verticalAlign + BOXSIZE;
  int boxHeightRow2 = secondRow + BOXSIZE;
  int boxHeightRow3 = thirdRow + BOXSIZE;
  int boxHeightRow4 = fourthRow + BOXSIZE;

  if (Z > MINPRESSURE && Z < MAXPRESSURE) {

    //redraw numpad to clear old number
    tft.fillScreen(BLACK);
    createButtons();
    insertNumbers();
    //default text setup for number display on tft
    tft.setCursor(100, 120);
    //tft.setTextColor(RED);
    tft.setTextSize(9);

    //Check if element clicked is in left column
    if (X > leftColPositionX && X < (leftColPositionX + BOXSIZE)) {
      //Check if element clicked is in row 1
      if (Y > verticalAlign) {
        if (Y < boxHeightRow1) {
          if(sound==1){
          tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          Serial.println("#");
          login_check = 1;
          Open = Pass;
          Pass = "";
          matching = 1;
        }

        //Check if element clicked is in row 2
        else if (Y < boxHeightRow2) {
          //Serial.println("9");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass = Pass +"9";
          //Serial.println(Pass);
          }

        }
        //Check if element clicked is in row 3
        else if (Y < boxHeightRow3) {
         if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
         if(a >Pass.length()){
            Pass = Pass +"6";
          //Serial.println(Pass);
          }
          // Pass = Pass +"7";
          // Serial.println(Pass);
        }
        //Check if element clicked is in row 4
        else if (Y < boxHeightRow4) {
          //Serial.println("3");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass = Pass +"3";
          //Serial.println(Pass);
          }
        }
      }
      //Check if element clicked is in mid column
    } else if (X > midColPositionX && X < (midColPositionX + BOXSIZE)) {
      //Check if element clicked is in row 1
      if (Y > verticalAlign) {
        if (Y < boxHeightRow1) {
         if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass = Pass +"0";
          Serial.println("0");
          }
        }
        
        //Check if element clicked is in row 2
        else if (Y < boxHeightRow2) {
          //Serial.println("8");
         if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass = Pass +"8";
          Serial.println("8");
          }
        }

        //Check if element clicked is in row 3
        else if (Y < boxHeightRow3) {
          //Serial.println("5");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass = Pass +"5";
          //Serial.println(Pass);
          }
          
        }
        //Check if element clicked is in row 4
        else if (Y < boxHeightRow4) {
          //Serial.println("2");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass = Pass +"2";
          //Serial.println(Pass);
          }
          
        }
      }
      //Check if element clicked is in third column
    } else if (X > rightColPositionX && X < (rightColPositionX + BOXSIZE)) {
      if (Y > verticalAlign) {
        //Check if element clicked is in row 1
        if (Y < boxHeightRow1) {
          //Serial.println("*");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          delay(1000);
          getFingerprintID();
//          finger_del();
          // if(a >Pass.length()){
          //   Pass = Pass +"3";
          // Serial.println(Pass);
          // }
          // Pass = Pass +"3";
          // Serial.println(Pass);
        }
        //Check if element clicked is in row 2
        else if (Y < boxHeightRow2) {
          //Serial.println("7");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass = Pass +"7";
          //Serial.println(Pass);
          }
          // Pass = Pass +"6";
          // Serial.println(Pass);

        }
        //Check if element clicked is in row 3
        else if (Y < boxHeightRow3) {
          //Serial.println("4");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass = Pass +"4";//////////////////
          //Serial.println(Pass);
          }
        }

        //Check if element clicked is in row 3
        else if (Y < boxHeightRow4) {
          //Serial.println("1");
         if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass = Pass +"1";//////////////////
          //Serial.println(Pass);
          }
        }
      }
    }
  }
}

//초음파센서 제어

int  cho = 1;

int r = 1;

int choose = 0;

void loop() {
  // 솔레노이드

  //tft lcd
  retrieveTouch();

  if (choose == 0)
  {
    tft.reset();
    uint16_t identifier = tft.readID();
    tft.begin(identifier);

    tft.fillScreen(BLACK);
    tft.setRotation(2);
    createButtons();
    insertNumbers();
    Open_pass();
    choose = 2;
  }
  if (choose == 1)
  {
    tft.reset();
    uint16_t identifier = tft.readID();
    tft.begin(identifier);

    tft.fillScreen(BLACK);
    tft.setRotation(2);
    createButtons();
    randomNumbers();
    randomOpen_pass();
    choose = 3;
  }


  if (random_number == 0)
  {
    if (swich_button == 0)
    {
      Open_pass(); // 비밀번호 입력
    }
  }
  else
  {
    if (swich_button == 0)
    {
      randomOpen_pass(); // 비밀번호 입력
    }
  }



  //스위치
  int Read = digitalRead(10);
  //Read = !Read;
  if (Read == 1)
  {
    tone(buzzer,2349);
    delay(200);
    noTone(buzzer);
    //Serial.println(Open);
    swich_button = 1;
  }

  if (swich_button ==1)
  {
    pass_changer();
    //Serial.println(Open);
    //Serial.println("1111");  
  }
 
  if(Serial.available())
  {
    serigo = Serial.readStringUntil('\n');
    if (serigo == "open")
    {
      Serial.println("Open");  
      door_open();
      if(sound == 1)
      {
        int elementCount = sizeof(note) / sizeof(int);
        for (int i=0; i < elementCount; i++)    //note를 play
        {
         tone(buzzer,note[i],500);
          delay(100);
        }
      }
    delay(5000);
    door_close();
    if(sound == 1)
    {
      int elementCount1 = sizeof(notes) / sizeof(int);
      for (int i=0; i < elementCount1; i++)    //note를 play
      {
        tone(buzzer,notes[i],500);
        delay(100);
      }
    }
    Open= "";
    matching = 0;
    false_pass = 0;
    }

    if (serigo.startsWith("password "))
    {
      String pw = serigo.substring(9);
      test = pw;
      Serial.println(test);
    }
    
    if (serigo.startsWith("passchange ")) // "passchange "으로 시작하는지 확인
    {
      String password = serigo.substring(11); // 11번째 인덱스부터 끝까지 추출
      test = password;
      Serial.print("비밀번호 변경 : ");
      Serial.println(test);
    }
    if(serigo.startsWith("guestpass ")) //guest비밀번호 설정
    {
      String password = serigo.substring(10); // 10번째 인덱스부터 끝까지 추출
      guest_pass = password;
      Serial.print("게스트비밀번호 등록 : ");
      Serial.println(guest_pass);
    }
    if(serigo == "guestclear") //guest 비밀번호 초기화 
    {
      guest_pass = "";
      Serial.println("게스트비밀번호 초기화완료");
    }
    if(serigo.startsWith("finger"))
    {
      getFingerprintEnroll();
    }
    if(serigo.startsWith("solenoid"))
    {
      Serial.println("문열림");
      digitalWrite(solenoid, HIGH); // 솔레노이드 열리기
      delay(1000);
    }

    if(serigo.startsWith("testend"))
    {
      digitalWrite(solenoid, LOW); // 솔레노이드 열리기
      delay(1000);
    }

    if(serigo.startsWith("start"))
    {
      Serial.println(test);
    }
    
    if(serigo.startsWith("지문초기화"))
    {
      finger.emptyDatabase();
      Serial.println("초기화완료");
    }

    if(serigo.startsWith("녹화종료"))
    {
      cho = 1;
    }
    if(serigo.startsWith("etiquette "))      // 에티켓모드
    {
      String sounds = serigo.substring(10);
      if (sounds == "1")
      {
        sound = 2;
        Serial.println("ETIQUETTE ON");
      }
      if (sounds == "0")
      {
        sound = 1;
        Serial.println("ETIQUETTE OFF");
      }
    }

    if (serigo.startsWith("record "))
    {
      String records = serigo.substring(7);
      Serial.println("안전녹화기능");
      delay(500);
      Serial.println(records);
      if (records == "1")
      {
        shoot = 1;
        Serial.println("SAFE RECORD ON");
      }
      else
      {
        shoot = 0;
        Serial.println("SAFE RECORD OFF");
      }
    }

    if (serigo.startsWith("fakenumber "))       // 허수기능
    {
      String fake = serigo.substring(11);
      if (fake == "1")
      {
        husu = 2;
        Serial.println("fake 1");
      }
      if (fake == "0")
      {
        husu = 1;
        Serial.println("fake 0");
      }
    }

    if (serigo.startsWith("random "))
    {
      String randoms = serigo.substring(7);
      if (randoms == "1")
      {
        random_number = 1;
        Serial.println("RANDOM NUMBER ON");
        choose = 1;
      }
      else
      {
        random_number = 0;
        Serial.println("RANDOM NUMBER OFF");
        choose = 0;
      }
    }

    if (serigo.startsWith("sound "))
    {
      int sound_change = serigo.substring(6).toInt();    // 11번째 인덱스부터 끝까지 추출
      sound_track = sound_change;
      tone(buzzer,sound_track);
      delay(200);
      noTone(buzzer);
      delay(200);
    }
  }

  //적외선인체감지센서
  Value = digitalRead(sensor);        // 변수 value에 디지털 센서값 저장

    if(Value == HIGH)                         // value가 high라면
    { 
      if(cho == 1 && shoot == 1)
      {
        Serial.println("모션감지");
        cho =2;
      }
    }
  //tftlcd 비밀번호 매칭

   if(matching == 1)
   {
     if (test == "" && login_check == 1)
     {
       Serial.println("None");
       login_check = 0;
      }
      else
      {
        if (login_check == 1)
        {
          if (husu == 2)
          {
            Open = Open.substring(3);
            if (Open == test || guest_pass == Open)
            {
              door_open();
              int elementCount = sizeof(note) / sizeof(int);
              for (int i = 0; i < elementCount; i++)
              {
                tone(buzzer, note[i],500);
                delay(100);
              }
              Serial.println("Open");
              delay(5000);
              door_close();
              int elementCount1 = sizeof(notes) / sizeof(int);
              for (int i = 0; i < elementCount1; i++)
              {
                tone(buzzer, notes[i],500);
                delay(100);
              }
              Open = "";
              matching = 0;
              false_pass = 0;
            }
            else
            {
              int elementCount1 = sizeof(false_notes) / sizeof(int);
              for (int i = 0; i < elementCount1; i++)
              {
                tone(buzzer,false_notes[i],500);
                delay(500);
              }
              matching = 0;
              false_pass = false_pass + 1;
              if (false_pass >= 3)
              {
                tft.reset();
                delay(5000);
                uint16_t identifier = tft.readID();
                tft.begin(identifier);

                tft.fillScreen(BLACK);
                tft.setRotation(2);
                createButtons();
                insertNumbers();
                Serial.println("Warning");
              }
            }
          }
          if (husu == 1)
          {
            Serial.println(Open);
            if (Open == test || guest_pass == Open)
            {
              door_open();
              int elementCount = sizeof(note) / sizeof(int);
              for (int i = 0; i < elementCount; i++)
              {
                tone(buzzer, note[i],500);
                delay(100);
              }
              Serial.println("Open");
              delay(5000);
              door_close();
              int elementCount1 = sizeof(notes) / sizeof(int);
              for (int i = 0; i < elementCount1; i++)
              {
                tone(buzzer, notes[i],500);
                delay(100);
              }
              Open = "";
              matching = 0;
              false_pass = 0;
            }
            else
            {
              int elementCount1 = sizeof(false_notes) / sizeof(int);
              for (int i = 0; i < elementCount1; i++)
              {
                tone(buzzer,false_notes[i],500);
                delay(500);
              }
              matching = 0;
              false_pass = false_pass + 1;
              if (false_pass >= 3)
              {
                tft.reset();
                delay(5000);
                uint16_t identifier = tft.readID();
                tft.begin(identifier);

                tft.fillScreen(BLACK);
                tft.setRotation(2);
                createButtons();
                insertNumbers();
                Serial.println("Warning");
              }
            }
          }
        }
      }
    }
  }

void retrieveTouch()
{
  //digitalWrite(13, HIGH);
  TSPoint p = ts.getPoint();
  //digitalWrite(13, LOW);

  //If sharing pins, you'll need to fix the directions of the touchscreen pins
  pinMode(XM, OUTPUT);
  pinMode(YP, OUTPUT);


  //Scale from 0->1023 to tft.width
    //X = map(p.x, TS_MAXX, TS_MINX, 0, tft.width());
  //  Y = map(p.y, TS_MAXY, TS_MINY, 0, tft.height());

  // on my tft the numbers are reversed so this is used instead of the above
  X = tft.width() - map(p.x, TS_MAXX, TS_MINX, 0, tft.width());
  Y = map(p.y, TS_MAXY, TS_MINY, 0, tft.height());
  Z = p.z;


}

void createButtons() {
  //(initial x,initial y,width,height,color)
  double secondRowVertialAlign = secondRow + verticalAlign;
  double thirdRowVertialAlign = thirdRow + verticalAlign;
  double fourthRowVertialAlign = fourthRow + verticalAlign;

  /***Draw filled squares with specified dimensions and position***/
  //First Row
  tft.fillRect(leftColPositionX, verticalAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.fillRect(midColPositionX, verticalAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.fillRect(rightColPositionX, verticalAlign, BOXSIZE, BOXSIZE, BLACK);

  //Second Row
  tft.fillRect(leftColPositionX, secondRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.fillRect(midColPositionX, secondRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.fillRect(rightColPositionX, secondRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);

  //Third Row
  tft.fillRect(leftColPositionX, thirdRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.fillRect(midColPositionX, thirdRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.fillRect(rightColPositionX, thirdRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);

  //Fourth Row
  tft.fillRect(leftColPositionX, fourthRowVertialAlign, BOXSIZE , BOXSIZE, BLACK);
  tft.fillRect(rightColPositionX, fourthRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.fillRect(midColPositionX, fourthRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  /***Draw Borders around squares***/
  //First Row
  tft.drawRect(leftColPositionX, verticalAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.drawRect(midColPositionX, verticalAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.drawRect(rightColPositionX, verticalAlign, BOXSIZE, BOXSIZE, BLACK);

  //Second Row
  tft.drawRect(leftColPositionX, secondRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.drawRect(midColPositionX, secondRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.drawRect(rightColPositionX, secondRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);

  //Third Row
  tft.drawRect(leftColPositionX, thirdRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.drawRect(midColPositionX, thirdRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.drawRect(rightColPositionX, thirdRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);

  //Fourth Row
  tft.drawRect(leftColPositionX, fourthRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  //tft.drawRect(leftColPositionX, fourthRowVertialAlign, (BOXSIZE * 2) + padding, BOXSIZE, BLACK);
  tft.drawRect(rightColPositionX, fourthRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
  tft.drawRect(midColPositionX, fourthRowVertialAlign, BOXSIZE, BOXSIZE, BLACK);
}

void insertNumbers()
{
  //Centers text horizontally on all three columns
  double leftColCursorX   = leftColPositionX + (BOXSIZE / 3);
  double midColCursorX    = midColPositionX  + (BOXSIZE / 3);
  double rightColCursorX  = rightColPositionX + (BOXSIZE / 3);
  //Centers text horizontally on all four rows
  double firstRowCursorY  = verticalAlign + (BOXSIZE / 3);
  double secondRowCursorY = secondRow + firstRowCursorY;
  double thirdRowCursorY  = thirdRow  + firstRowCursorY;
  double fourthRowCursorY = fourthRow + firstRowCursorY;

  tft.setTextSize(4);
  tft.setTextColor(WHITE);

  //Insert Number 1
  tft.setCursor(leftColCursorX, firstRowCursorY);
  tft.println("1");
 
  tft.setCursor(midColCursorX, firstRowCursorY);
  tft.println("2");

  //Insert Number 3
  tft.setCursor(rightColCursorX, firstRowCursorY);
  tft.println("3");

  //Insert Number 4
  tft.setCursor(leftColCursorX, secondRowCursorY);
  tft.println("4");

  //Insert Number 5
  tft.setCursor(midColCursorX, secondRowCursorY);
  tft.println("5");

  //Insert Number 6
  tft.setCursor(rightColCursorX, secondRowCursorY);
  tft.println("6");

  //Insert Number 7
  tft.setCursor(leftColCursorX, thirdRowCursorY);
  tft.println("7");

  //Insert Number 8
  tft.setCursor(midColCursorX, thirdRowCursorY);
  tft.println("8");

  //Insert Number 9
  tft.setCursor(rightColCursorX, thirdRowCursorY);
  tft.println("9");

  //Insert Number 0
  tft.setCursor(midColCursorX, fourthRowCursorY);
  tft.println("0");
   
  //Insert Number *
  tft.setCursor(leftColCursorX, fourthRowCursorY);
  tft.println("*");

  //Insert Period Character
  tft.setCursor(rightColCursorX, fourthRowCursorY);
  tft.println("#");
}



void randomNumbers()
{
  //Centers text horizontally on all three columns
  double leftColCursorX   = leftColPositionX + (BOXSIZE / 3);
  double midColCursorX    = midColPositionX  + (BOXSIZE / 3);
  double rightColCursorX  = rightColPositionX + (BOXSIZE / 3);
  //Centers text horizontally on all four rows
  double firstRowCursorY  = verticalAlign + (BOXSIZE / 3);
  double secondRowCursorY = secondRow + firstRowCursorY;
  double thirdRowCursorY  = thirdRow  + firstRowCursorY;
  double fourthRowCursorY = fourthRow + firstRowCursorY;

  // Create an array containing the numbers 0-9
  int numbers[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

  tft.setTextSize(4);
  tft.setTextColor(WHITE);

  // Shuffle the array to get a random order of the numbers
  for (int i = 0; i < 10; i++)
  {
    int randomIndex = random(i, 10);
    int temp = numbers[i];
    numbers[i] = numbers[randomIndex];
    numbers[randomIndex] = temp;
  }

  //Insert Number 1
  tft.setCursor(leftColCursorX, firstRowCursorY);
  one = numbers[0];
  tft.println(numbers[0]);
  
  //Insert Number 2
  tft.setCursor(midColCursorX, firstRowCursorY);
  two = numbers[1];
  tft.println(numbers[1]);

  //Insert Number 3
  tft.setCursor(rightColCursorX, firstRowCursorY);
  three = numbers[2];
  tft.println(numbers[2]);

  //Insert Number 4
  tft.setCursor(leftColCursorX, secondRowCursorY);
  four = numbers[3];
  tft.println(numbers[3]);

  //Insert Number 5
  tft.setCursor(midColCursorX, secondRowCursorY);
  five = numbers[4];
  tft.println(numbers[4]);

  //Insert Number 6
  tft.setCursor(rightColCursorX, secondRowCursorY);
  six = numbers[5];
  tft.println(numbers[5]);

  //Insert Number 7
  tft.setCursor(leftColCursorX, thirdRowCursorY);
  seven = numbers[6];
  tft.println(numbers[6]);

  //Insert Number 8
  tft.setCursor(midColCursorX, thirdRowCursorY);
  eight = numbers[7];
  tft.println(numbers[7]);

  //Insert Number 9
  tft.setCursor(rightColCursorX, thirdRowCursorY);
  nine = numbers[8];
  tft.println(numbers[8]);

 //Insert Number 0
  tft.setCursor(midColCursorX, fourthRowCursorY);
  zero = numbers[9];
  tft.println(numbers[9]);

 //Insert Number *
  tft.setCursor(leftColCursorX, fourthRowCursorY);
  tft.println("*");

  //Insert Period Character
  tft.setCursor(rightColCursorX, fourthRowCursorY);
  tft.println("#");
}




void randomOpen_pass()
{
  int boxHeightRow1 = verticalAlign + BOXSIZE;
  int boxHeightRow2 = secondRow + BOXSIZE;
  int boxHeightRow3 = thirdRow + BOXSIZE;
  int boxHeightRow4 = fourthRow + BOXSIZE;

  if (Z > MINPRESSURE && Z < MAXPRESSURE)
  {
    //redraw numpad to clear old number
    tft.fillScreen(BLACK);
    // createButtons();
    // randomNumbers();
    //default text setup for number display on tft
    tft.setCursor(100, 120);
    //tft.setTextColor(RED);
    tft.setTextSize(9);

    //Check if element clicked is in left column
    if (X > leftColPositionX && X < (leftColPositionX + BOXSIZE))
    {
      //Check if element clicked is in row 1
      if (Y > verticalAlign){
        if (Y < boxHeightRow1) {
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          Serial.println("#");
          Open = Pass;
          Pass = "";
          matching = 1;
          login_check = 1;
        }

        //Check if element clicked is in row 2
        else if (Y < boxHeightRow2) {
          //Serial.println("9");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length())
          {
            Pass += String(nine);
          }
        }
        //Check if element clicked is in row 3
        else if (Y < boxHeightRow3)
        {
          if(sound==1)
          {
            tone(buzzer,sound_track);
            delay(200);      
            noTone(buzzer);
            delay(200);
          }
          if(a >Pass.length())
          {
            Pass += String(six);
          }
        }
        //Check if element clicked is in row 4
        else if (Y < boxHeightRow4) {
          //Serial.println("3");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass += String(three);
          }
        }
      }
      //Check if element clicked is in mid column
    } else if (X > midColPositionX && X < (midColPositionX + BOXSIZE)) {
      //Check if element clicked is in row 1
      if (Y > verticalAlign) {
        if (Y < boxHeightRow1) {
         if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass += String(zero);
          }
        }
        
        //Check if element clicked is in row 2
        else if (Y < boxHeightRow2) {
          //Serial.println("8");
         if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass += String(eight);
          }
        }

        //Check if element clicked is in row 3
        else if (Y < boxHeightRow3) {
          //Serial.println("5");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
           Pass += String(five);
          //Serial.println(Pass);
          }
          
        }
        //Check if element clicked is in row 4
        else if (Y < boxHeightRow4) {
          //Serial.println("2");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass += String(two);
          //Serial.println(Pass);
          }
          
        }
      }
      //Check if element clicked is in third column
    } else if (X > rightColPositionX && X < (rightColPositionX + BOXSIZE)) {
      if (Y > verticalAlign) {
        //Check if element clicked is in row 1
        if (Y < boxHeightRow1) {
          //Serial.println("*");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          delay(1000);
          getFingerprintID();
        }
      
        else if (Y < boxHeightRow2) {
          //Serial.println("7");
          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass += String(seven);
          }
        }
        else if (Y < boxHeightRow3) {

          if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass += String(four);
          }
        }
        //Check if element clicked is in row 3
        else if (Y < boxHeightRow4) {
          //Serial.println("1");
         if(sound==1){
            tone(buzzer,sound_track);
          delay(200);      
          noTone(buzzer);
          delay(200);
          }
          if(a >Pass.length()){
            Pass += String(one);
          }
        }
      }
    }
    createButtons();
    randomNumbers();
  }
}

