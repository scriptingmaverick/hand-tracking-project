import cv2
import math
import mediapipe as mp

mp_hands = mp.solutions.hands

SKELETON_CONNECTIONS = [
    [0, 1], [1, 2], [2, 3], [3, 4],
    [0, 5], [5, 6], [6, 7], [7, 8],
    [0, 9], [9, 10], [10, 11], [11, 12],
    [0, 13], [13, 14], [14, 15], [15, 16],
    [0, 17], [17, 18], [18, 19], [19, 20],
    [5, 9], [9, 13], [13, 17],
]

THUMB_TIP = 4
THUMB_IP = 3
INDEX_TIP = 8
INDEX_PIP = 6
MIDDLE_TIP = 12
MIDDLE_PIP = 10
RING_TIP = 16
RING_PIP = 14
PINKY_TIP = 20
PINKY_PIP = 18
WRIST = 0


def calculate_distance(point_a, point_b):
    return math.hypot(point_a.x - point_b.x, point_a.y - point_b.y)


def is_finger_extended(landmarks, tip_index, pip_index):
    wrist = landmarks[WRIST]
    tip_distance = calculate_distance(landmarks[tip_index], wrist)
    pip_distance = calculate_distance(landmarks[pip_index], wrist)
    return tip_distance > pip_distance


def recognize_gesture(landmarks):
    thumb_extended = is_finger_extended(landmarks, THUMB_TIP, THUMB_IP)
    index_extended = is_finger_extended(landmarks, INDEX_TIP, INDEX_PIP)
    middle_extended = is_finger_extended(landmarks, MIDDLE_TIP, MIDDLE_PIP)
    ring_extended = is_finger_extended(landmarks, RING_TIP, RING_PIP)
    pinky_extended = is_finger_extended(landmarks, PINKY_TIP, PINKY_PIP)

    extended_flags = [
        thumb_extended, index_extended,
        middle_extended, ring_extended, pinky_extended
    ]
    extended_count = sum(extended_flags)

    thumb_index_distance = calculate_distance(landmarks[THUMB_TIP], landmarks[INDEX_TIP])

    if thumb_index_distance < 0.05 and not index_extended and thumb_extended:
        return "👌  OK", extended_count

    if all(extended_flags):
        return "✋  Open Palm", extended_count
    if not any(extended_flags):
        return "✊  Fist", extended_count

    if thumb_extended and index_extended and not middle_extended and not ring_extended and pinky_extended:
        return "🤟  ILY", extended_count
    if index_extended and not middle_extended and not ring_extended and pinky_extended and not thumb_extended:
        return "🤘  Rock On", extended_count
    if thumb_extended and pinky_extended and not index_extended and not middle_extended and not ring_extended:
        return "🤙  Call Me", extended_count
    if index_extended and middle_extended and ring_extended and not thumb_extended and not pinky_extended:
        return "3️⃣  Three", extended_count
    if index_extended and middle_extended and not thumb_extended and not ring_extended and not pinky_extended:
        return "✌️  Peace", extended_count

    if index_extended and middle_extended and ring_extended and pinky_extended and not thumb_extended:
        return "4️⃣  Four", extended_count

    if thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        return "👍  Thumbs Up", extended_count
    if index_extended and not thumb_extended and not middle_extended and not ring_extended and not pinky_extended:
        return "☝️  Pointing", extended_count

    return None, extended_count


camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

with mp_hands.Hands(
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6,
) as hands:
    while camera.isOpened():
        success, frame = camera.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            num_hands = len(results.multi_hand_landmarks)
            status_text = f"{num_hands} hand{'s' if num_hands > 1 else ''} detected"

            current_gesture = None

            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark

                for start_index, end_index in SKELETON_CONNECTIONS:
                    point_a = landmarks[start_index]
                    point_b = landmarks[end_index]
                    x1, y1 = int(point_a.x * width), int(point_a.y * height)
                    x2, y2 = int(point_b.x * width), int(point_b.y * height)
                    cv2.line(frame, (x1, y1), (x2, y2),
                             (66, 165, 245, 128), 2)

                for landmark in landmarks:
                    x, y = int(landmark.x * width), int(landmark.y * height)
                    cv2.circle(frame, (x, y), 5, (255, 64, 129), -1)
                    cv2.circle(frame, (x, y), 5, (255, 255, 255), 1)

                gesture_name, _ = recognize_gesture(landmarks)
                if gesture_name:
                    current_gesture = gesture_name

            if current_gesture:
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, height - 95), (width, height - 35),
                              (10, 10, 15), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                cv2.rectangle(frame, (0, height - 95), (width, height - 35),
                              (201, 168, 76), 1)

                text_size = cv2.getTextSize(current_gesture,
                                            cv2.FONT_HERSHEY_DUPLEX,
                                            1.2, 2)[0]
                text_x = (width - text_size[0]) // 2
                text_y = height - 55
                cv2.putText(frame, current_gesture, (text_x, text_y),
                            cv2.FONT_HERSHEY_DUPLEX, 1.2,
                            (245, 240, 232), 2)

        else:
            status_text = "No hands detected"

        cv2.putText(frame, status_text, (16, 30),
                    cv2.FONT_HERSHEY_DUPLEX, 0.5,
                    (245, 240, 232, 128), 1)

        cv2.imshow("Gesture — Hand Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()
