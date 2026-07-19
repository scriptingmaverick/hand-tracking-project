import cv2
import math
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
mp_draw_styles = mp.solutions.drawing_styles

CONNECTIONS = [
    [0, 1], [1, 2], [2, 3], [3, 4],
    [0, 5], [5, 6], [6, 7], [7, 8],
    [0, 9], [9, 10], [10, 11], [11, 12],
    [0, 13], [13, 14], [14, 15], [15, 16],
    [0, 17], [17, 18], [18, 19], [19, 20],
    [5, 9], [9, 13], [13, 17],
]


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def is_extended(hand, tip, pip):
    wrist = hand[0]
    return dist(hand[tip], wrist) > dist(hand[pip], wrist)


def get_gesture(hand):
    thumb_ex = is_extended(hand, 4, 3)
    index_ex = is_extended(hand, 8, 6)
    middle_ex = is_extended(hand, 12, 10)
    ring_ex = is_extended(hand, 16, 14)
    pinky_ex = is_extended(hand, 20, 18)

    ext = [thumb_ex, index_ex, middle_ex, ring_ex, pinky_ex]
    count = sum(ext)

    thumb_index_dist = dist(hand[4], hand[8])

    if thumb_index_dist < 0.05 and not index_ex and thumb_ex:
        return "👌  OK", count

    if all(ext):
        return "✋  Open Palm", count
    if not any(ext):
        return "✊  Fist", count

    if thumb_ex and index_ex and not middle_ex and not ring_ex and pinky_ex:
        return "🤟  ILY", count
    if index_ex and not middle_ex and not ring_ex and pinky_ex and not thumb_ex:
        return "🤘  Rock On", count
    if thumb_ex and pinky_ex and not index_ex and not middle_ex and not ring_ex:
        return "🤙  Call Me", count
    if index_ex and middle_ex and ring_ex and not thumb_ex and not pinky_ex:
        return "3️⃣  Three", count
    if index_ex and middle_ex and not thumb_ex and not ring_ex and not pinky_ex:
        return "✌️  Peace", count

    if index_ex and middle_ex and ring_ex and pinky_ex and not thumb_ex:
        return "4️⃣  Four", count

    if thumb_ex and not index_ex and not middle_ex and not ring_ex and not pinky_ex:
        return "👍  Thumbs Up", count
    if index_ex and not thumb_ex and not middle_ex and not ring_ex and not pinky_ex:
        return "☝️  Pointing", count

    return None, count


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

with mp_hands.Hands(
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6,
) as hands:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            n = len(results.multi_hand_landmarks)
            status = f"{n} hand{'s' if n > 1 else ''} detected"

            gesture_text = None

            for hand_landmarks in results.multi_hand_landmarks:
                hand = hand_landmarks.landmark

                for i, j in CONNECTIONS:
                    a = hand[i]
                    b = hand[j]
                    x1, y1 = int(a.x * w), int(a.y * h)
                    x2, y2 = int(b.x * w), int(b.y * h)
                    cv2.line(frame, (x1, y1), (x2, y2),
                             (66, 165, 245, 128), 2)

                for lm in hand:
                    x, y = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (x, y), 5, (255, 64, 129), -1)
                    cv2.circle(frame, (x, y), 5, (255, 255, 255), 1)

                name, _ = get_gesture(hand)
                if name:
                    gesture_text = name

            if gesture_text:
                label_bg = frame[h - 90: h - 40, 0:w]
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, h - 95), (w, h - 35),
                              (10, 10, 15), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                cv2.rectangle(frame, (0, h - 95), (w, h - 35),
                              (201, 168, 76), 1)

                text_size = cv2.getTextSize(gesture_text,
                                            cv2.FONT_HERSHEY_DUPLEX,
                                            1.2, 2)[0]
                text_x = (w - text_size[0]) // 2
                text_y = h - 55
                cv2.putText(frame, gesture_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_DUPLEX, 1.2,
                            (245, 240, 232), 2)

        else:
            status = "No hands detected"

        cv2.putText(frame, status, (16, 30),
                    cv2.FONT_HERSHEY_DUPLEX, 0.5,
                    (245, 240, 232, 128), 1)

        cv2.imshow("Gesture — Hand Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
