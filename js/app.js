const CONNECTIONS = [
  [0,1],[1,2],[2,3],[3,4],
  [0,5],[5,6],[6,7],[7,8],
  [0,9],[9,10],[10,11],[11,12],
  [0,13],[13,14],[14,15],[15,16],
  [0,17],[17,18],[18,19],[19,20],
  [5,9],[9,13],[13,17]
];

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const statusEl = document.getElementById('status');
const gestureEl = document.getElementById('gesture');
const legendToggle = document.getElementById('legendToggle');
const legend = document.getElementById('legend');
const ctx = canvas.getContext('2d');

legendToggle.addEventListener('click', () => legend.classList.toggle('open'));

function dist(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function isExtended(lm, tip, pip) {
  const wrist = lm[0];
  return dist(lm[tip], wrist) > dist(lm[pip], wrist);
}

function getGesture(lm) {
  const thumbEx  = isExtended(lm, 4, 3);
  const indexEx  = isExtended(lm, 8, 6);
  const middleEx = isExtended(lm, 12, 10);
  const ringEx   = isExtended(lm, 16, 14);
  const pinkyEx  = isExtended(lm, 20, 18);

  const ext = [thumbEx, indexEx, middleEx, ringEx, pinkyEx];
  const count = ext.filter(Boolean).length;

  const thumbIndexDist = dist(lm[4], lm[8]);

  if (thumbIndexDist < 0.05 && !indexEx && thumbEx) return { name: 'OK', emoji: '👌', count };

  if (ext.every(f => f)) return { name: 'Open Palm', emoji: '✋', count };
  if (ext.every(f => !f)) return { name: 'Fist', emoji: '✊', count };

  if (thumbEx && indexEx && !middleEx && !ringEx && pinkyEx) return { name: 'ILY', emoji: '🤟', count };
  if (indexEx && !middleEx && !ringEx && pinkyEx && !thumbEx) return { name: 'Rock On', emoji: '🤘', count };
  if (thumbEx && pinkyEx && !indexEx && !middleEx && !ringEx) return { name: 'Call Me', emoji: '🤙', count };
  if (indexEx && middleEx && ringEx && !thumbEx && !pinkyEx) return { name: 'Three', emoji: '3️⃣', count };
  if (indexEx && middleEx && !thumbEx && !ringEx && !pinkyEx) return { name: 'Peace', emoji: '✌️', count };

  if (indexEx && middleEx && ringEx && pinkyEx && !thumbEx) return { name: 'Four', emoji: '4️⃣', count };

  if (thumbEx && !indexEx && !middleEx && !ringEx && !pinkyEx) return { name: 'Thumbs Up', emoji: '👍', count };
  if (indexEx && !thumbEx && !middleEx && !ringEx && !pinkyEx) return { name: 'Pointing', emoji: '☝️', count };

  return null;
}

function onResults(results) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
    const n = results.multiHandLandmarks.length;
    statusEl.textContent = `${n} hand${n > 1 ? 's' : ''} detected`;

    for (const landmarks of results.multiHandLandmarks) {
      const w = canvas.width;
      const h = canvas.height;

      ctx.lineWidth = 2;
      ctx.lineCap = 'round';

      for (const [i, j] of CONNECTIONS) {
        const a = landmarks[i];
        const b = landmarks[j];
        ctx.beginPath();
        ctx.moveTo(a.x * w, a.y * h);
        ctx.lineTo(b.x * w, b.y * h);
        ctx.strokeStyle = 'rgba(66, 165, 245, 0.5)';
        ctx.stroke();
      }

      for (const lm of landmarks) {
        const x = lm.x * w;
        const y = lm.y * h;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = 'rgba(255, 64, 129, 0.8)';
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      const gesture = getGesture(landmarks);
      if (gesture) {
        gestureEl.textContent = `${gesture.emoji}  ${gesture.name}`;
        gestureEl.classList.add('visible');
      } else {
        gestureEl.classList.remove('visible');
      }
    }
  } else {
    statusEl.textContent = 'No hands detected';
    gestureEl.classList.remove('visible');
  }
}

async function init() {
  try {
    const hands = new Hands({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4/${file}`
    });

    hands.setOptions({
      maxNumHands: 2,
      modelComplexity: 1,
      minDetectionConfidence: 0.7,
      minTrackingConfidence: 0.6
    });

    hands.onResults(onResults);

    const camera = new Camera(video, {
      onFrame: async () => {
        await hands.send({ image: video });
      },
      width: 720,
      height: 540
    });

    await camera.start();
    canvas.width = 720;
    canvas.height = 540;
    statusEl.textContent = 'Camera active';
  } catch (err) {
    statusEl.textContent = 'Error: ' + err.message;
    console.error(err);
  }
}

init();
