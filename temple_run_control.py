import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
prev_x = None
gesture_cooldown = 0
frame_count = 0

def count_fingers(hand_landmarks):
    fingers = []
    
    # Thumb: Check if thumb is extended (thumb tip higher than thumb base)
    fingers.append(hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y)
    
    # Check for the other fingers (index, middle, ring, pinky)
    for id in [8, 12, 16, 20]:
        fingers.append(hand_landmarks.landmark[id].y < hand_landmarks.landmark[id - 2].y)
    
    return fingers

def is_fist(hand_landmarks):
    # Detect if the hand is a fist (all fingers curled)
    for id in [8, 12, 16, 20]:  # Checking for extended fingers (index, middle, ring, pinky)
        if hand_landmarks.landmark[id].y < hand_landmarks.landmark[id - 2].y:  # Finger tip above its base
            return False  # Finger is not curled, not a fist
    return True  # All fingers are curled (fist)

while True:
    success, frame = cap.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Count the number of extended fingers
            fingers = count_fingers(hand_landmarks)
            finger_count = fingers.count(True)  # Count how many fingers are extended
            
            curr_x = hand_landmarks.landmark[8].x  # Index fingertip position
            
            frame_count += 1
            if frame_count % 5 == 0 and gesture_cooldown == 0:
                # Detect swipe gestures (left/right)
                if prev_x is not None:
                    delta = curr_x - prev_x
                    if delta > 0.1:
                        print("Swipe Right →")
                        pyautogui.press('right')
                        gesture_cooldown = 10
                    elif delta < -0.1:
                        print("Swipe Left ←")
                        pyautogui.press('left')
                        gesture_cooldown = 10
                prev_x = curr_x
                
                # Open Palm (Jump) - All fingers extended
                if finger_count == 5:
                    print("Open Palm → Jump ↑")
                    pyautogui.press('up')
                    gesture_cooldown = 10
                
                # Fist (Slide) - All fingers curled
                elif is_fist(hand_landmarks):
                    print("Fist → Slide ↓")
                    pyautogui.press('down')
                    gesture_cooldown = 10

    if gesture_cooldown > 0:
        gesture_cooldown -= 1

    cv2.imshow("Temple Run Hand Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
