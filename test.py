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
    fingers.append(hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x)
    for id in [8, 12, 16, 20]:
        fingers.append(hand_landmarks.landmark[id].y < hand_landmarks.landmark[id - 2].y)
    return fingers.count(True)

while True:
    success, frame = cap.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            curr_x = hand_landmarks.landmark[8].x
            finger_count = count_fingers(hand_landmarks)

            frame_count += 1
            if frame_count % 5 == 0 and gesture_cooldown == 0:
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

                if finger_count == 5:
                    print("Jump ↑")
                    pyautogui.press('up')
                    gesture_cooldown = 10
                elif finger_count == 0:
                    print("Slide ↓")
                    pyautogui.press('down')
                    gesture_cooldown = 10

    if gesture_cooldown > 0:
        gesture_cooldown -= 1

    cv2.imshow("Temple Run Hand Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
