import cv2 
from deepface import DeepFace
import threading
import serial
import speech_recognition
import pyttsx3
import subprocess as sp
import time

recognizer = speech_recognition.Recognizer()
relayData = serial.Serial()
relayData.baudrate = 9600
relayData.port = "/dev/cu.usbmodem1201"
relayData.open()

max_iterations = 3


cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0
face_match = False
reference_img = cv2.imread("unnamed.jpg")

lock = threading.Lock()

exit_program = False

def check_face(frame):
   global face_match
   try:
        if DeepFace.verify(frame, reference_img.copy())['verified']:
           face_match = True
        else:
           face_match = False
   except ValueError:
      pass
   
while True:
  ret, frame = cap.read()

  if ret: 
    if counter % 30 == 0:
      try:
          lock.acquire()
          threading.Thread(target=check_face, args=(frame.copy(),)).start()
      except ValueError:
          pass
      finally: 
         
         lock.release()
    counter += 1

    if face_match:
       cv2.putText(frame, "MASON!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

       sp.call(["say", "Hello Mason!, Would you like to start the car"])
       for _ in range(max_iterations):
              try:
                 with speech_recognition.Microphone() as mic:
                  recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                  audio = recognizer.listen(mic)
                  text = recognizer.recognize_google(audio)
                  text = text.lower()
                  
                  words = text.split()
               

                  if words:
                     first_word = words[0]
                     print(first_word)
            
                     if first_word == "yes":
                        relayData.write("ON".encode('utf-8'))
                        exit_program = True
                        break

              except speech_recognition.UnknownValueError:
                recognizer = speech_recognition.Recognizer()
                sp.call(["say", "Im sorry Mason, could you repeat that ? "])
                continue
    else:
       cv2.putText(frame, "NOT MASON!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
       
       
    cv2.imshow("video",frame)

    if exit_program:
      break

  key = cv2.waitKey(1)
  if key == ord("q"):
     break

cv2.destroyAllWindows()
