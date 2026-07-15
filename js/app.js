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
const ctx = canvas.getContext('2d');

function onResults(results) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
    statusEl.textContent = `${results.multiHandLandmarks.length} hand(s) detected`;

    for (const landmarks of results.multiHandLandmarks) {
      const w = canvas.width;
      const h = canvas.height;

      ctx.lineWidth = 3;
      ctx.lineCap = 'round';

      for (const [i, j] of CONNECTIONS) {
        const a = landmarks[i];
        const b = landmarks[j];
        ctx.beginPath();
        ctx.moveTo(a.x * w, a.y * h);
        ctx.lineTo(b.x * w, b.y * h);
        ctx.strokeStyle = '#42a5f5';
        ctx.stroke();
      }

      for (const lm of landmarks) {
        const x = lm.x * w;
        const y = lm.y * h;
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, 2 * Math.PI);
        ctx.fillStyle = '#ff4081';
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      ctx.fillStyle = '#fff';
      ctx.font = '12px monospace';
      ctx.fillText(`Fingers: ${countFingers(landmarks)}`, 16, 24);
    }
  } else {
    statusEl.textContent = 'No hands detected';
  }
}

function countFingers(lm) {
  const tips = [4, 8, 12, 16, 20];
  const bases = [2, 5, 9, 13, 17];
  let count = 0;
  for (let i = 0; i < 5; i++) {
    if (lm[tips[i]].y < lm[bases[i]].y) count++;
  }
  return count;
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
