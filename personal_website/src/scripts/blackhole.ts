import * as THREE from 'three';

let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let accretionDisk: THREE.Points;
let relativisticJet: THREE.Points;
let dustMotes: THREE.Points;
let clock: THREE.Clock;

export function initBlackHole() {
  const canvas = document.getElementById('wormhole-canvas') as HTMLCanvasElement;
  if (!canvas) return;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020204);
  scene.fog = new THREE.FogExp2(0x020204, 0.0015);

  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
  camera.position.set(0, 150, 400);
  camera.lookAt(0, 0, 0);

  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  clock = new THREE.Clock();

  // Create soft glowing circle texture procedurally
  const textureCanvas = document.createElement('canvas');
  textureCanvas.width = 64;
  textureCanvas.height = 64;
  const ctx = textureCanvas.getContext('2d');
  if (ctx) {
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(255,255,255,1)');
    gradient.addColorStop(0.3, 'rgba(255,255,255,0.8)');
    gradient.addColorStop(0.8, 'rgba(255,255,255,0.1)');
    gradient.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 64, 64);
  }
  const circleTexture = new THREE.CanvasTexture(textureCanvas);

  // 2. Create Accretion Disk (The Black Hole Swirl)
  const diskGeo = new THREE.BufferGeometry();
  const diskCount = 20000;
  const diskPos = new Float32Array(diskCount * 3);
  const diskColors = new Float32Array(diskCount * 3);
  
  const colorCyan = new THREE.Color(0x00f0ff);
  const colorBlue = new THREE.Color(0x0a44ff);

  for (let i = 0; i < diskCount; i++) {
    const radius = Math.random() * 250 + 20; 
    const angle = Math.random() * Math.PI * 2;
    const dip = Math.exp(-radius / 50) * 100;
    
    diskPos[i * 3] = Math.cos(angle) * radius;
    diskPos[i * 3 + 1] = (Math.random() - 0.5) * 10 - dip; 
    diskPos[i * 3 + 2] = Math.sin(angle) * radius;

    const mixed = colorCyan.clone().lerp(colorBlue, radius / 270);
    diskColors[i * 3] = mixed.r;
    diskColors[i * 3 + 1] = mixed.g;
    diskColors[i * 3 + 2] = mixed.b;
  }

  diskGeo.setAttribute('position', new THREE.BufferAttribute(diskPos, 3));
  diskGeo.setAttribute('color', new THREE.BufferAttribute(diskColors, 3));

  const diskMat = new THREE.PointsMaterial({
    size: 2.5,
    map: circleTexture,
    vertexColors: true,
    transparent: true,
    opacity: 0.8,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });

  accretionDisk = new THREE.Points(diskGeo, diskMat);
  scene.add(accretionDisk);

  // 3. Create Relativistic Jet (Trailing Light)
  const jetGeo = new THREE.BufferGeometry();
  const jetCount = 10000;
  const jetPos = new Float32Array(jetCount * 3);
  const jetColors = new Float32Array(jetCount * 3);

  for(let i=0; i < jetCount; i++) {
    const y = (Math.random() - 0.5) * 1500; 
    const radius = Math.random() * (10 + Math.abs(y) * 0.05);
    const angle = Math.random() * Math.PI * 2;
    
    jetPos[i*3] = Math.cos(angle) * radius;
    jetPos[i*3+1] = y;
    jetPos[i*3+2] = Math.sin(angle) * radius;

    jetColors[i*3] = colorCyan.r * 1.5;
    jetColors[i*3+1] = colorCyan.g * 1.5;
    jetColors[i*3+2] = colorCyan.b * 1.5;
  }

  jetGeo.setAttribute('position', new THREE.BufferAttribute(jetPos, 3));
  jetGeo.setAttribute('color', new THREE.BufferAttribute(jetColors, 3));

  const jetMat = new THREE.PointsMaterial({
    size: 3.5,
    map: circleTexture,
    vertexColors: true,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });

  relativisticJet = new THREE.Points(jetGeo, jetMat);
  scene.add(relativisticJet);

  // 4. Create Ambient Golden Dust Motes
  const dustGeo = new THREE.BufferGeometry();
  const dustCount = 1000;
  const dustPos = new Float32Array(dustCount * 3);
  const colorGold = new THREE.Color(0xffb84d);

  for(let i=0; i<dustCount; i++) {
    dustPos[i*3] = (Math.random() - 0.5) * 800;
    dustPos[i*3+1] = (Math.random() - 0.5) * 800;
    dustPos[i*3+2] = (Math.random() - 0.5) * 800;
  }
  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  const dustMat = new THREE.PointsMaterial({
    size: 5.0,
    map: circleTexture,
    color: colorGold,
    transparent: true,
    opacity: 0.5,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  dustMotes = new THREE.Points(dustGeo, dustMat);
  scene.add(dustMotes);

  // Event Listeners
  window.addEventListener('resize', onWindowResize);

  // Animation Loop
  animate();
}

function onWindowResize() {
  if(!camera || !renderer) return;
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
  requestAnimationFrame(animate);
  if(!clock) return;
  const time = clock.getElapsedTime();

  // Spin the accretion disk
  if(accretionDisk) {
    accretionDisk.rotation.y = time * 0.2;
  }

  // Spin and pulse the relativistic jet
  if(relativisticJet) {
    relativisticJet.rotation.y = time * -0.5;
    (relativisticJet.material as THREE.PointsMaterial).opacity = 0.5 + Math.sin(time * 2) * 0.2;
  }

  // Drift the dust motes
  if(dustMotes) {
    dustMotes.rotation.y = time * 0.05;
    dustMotes.position.y = Math.sin(time * 0.5) * 10;
  }

  renderer.render(scene, camera);
}

// Export the camera so GSAP in main.ts can fly it through space!
export const getCamera = () => camera;
