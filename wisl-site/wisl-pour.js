/* WISL scroll pour — needs three.js r147 + GLTFLoader + RoundedBoxGeometry loaded first */
(async function(){
const statusEl = document.getElementById('status');
const fail = m => { statusEl.textContent = m; };
if (!window.THREE || !THREE.GLTFLoader) { fail("The 3D library didn't load. Check your connection and reload."); return; }
THREE.ColorManagement.legacyMode = false;

// ---------------- settings (tweak these) ----------------
const CFG = {
  liquid: '#EE4459', liquidTop: '#D9374C', ink: '#0A0A0A',
  pour:   { tiltStart: 0.04, tiltEnd: 0.30, streamOn: 0.30, fillStart: 0.34, fillEnd: 0.86, streamOff: 0.86, tiltBack: 0.95 },
  tilt: 118,           // degrees the bottle tips over to pour
  bottleScale: 1.15,
  maxFill: 0.80,       // fraction of glass height when full
};

const canvas = document.getElementById('wislCanvas');
let renderer;
try { renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true}); }
catch(e){ fail("Your browser can't show 3D here (WebGL is off or unsupported)."); return; }
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.setClearColor(0, 0);

const scene = new THREE.Scene();
const sun = new THREE.DirectionalLight(0xffffff, 0.75); sun.position.set(-3, 4, 5); scene.add(sun);
scene.add(new THREE.AmbientLight(0xffffff, 0.25));
const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
camera.position.set(0, 0.9, 14); camera.lookAt(0, 0, 0);

const ramp = new THREE.DataTexture(new Uint8Array([150, 255]), 2, 1, THREE.RedFormat);
ramp.minFilter = ramp.magFilter = THREE.NearestFilter; ramp.needsUpdate = true;
const toon = (c, o = {}) => new THREE.MeshToonMaterial(Object.assign({color:c, gradientMap:ramp}, o));
const INK = new THREE.MeshBasicMaterial({color:CFG.ink});
const INK_BACK = new THREE.MeshBasicMaterial({color:CFG.ink, side:THREE.BackSide});
const WHITE = new THREE.MeshBasicMaterial({color:'#ffffff'});

// ---------------- bottle (the rigged toon bottle) ----------------
const MODEL_URL = document.getElementById('wislPour').dataset.model || 'wisl-pour/wisl-bottle.glb';
let gltf;
try { gltf = await new Promise((res, rej) => new THREE.GLTFLoader().load(MODEL_URL, res, undefined, rej)); }
catch(e){ fail("The bottle couldn't load from " + MODEL_URL + ". Check the file path, then reload."); return; }
const bottle = new THREE.Group(); scene.add(bottle);
const model = gltf.scene; bottle.add(model);
const bodyMat = toon('#EE4459'); const cache = {};
model.traverse(o => {
  if (!o.isMesh) return;
  o.frustumCulled = false;
  const n = o.material.name;
  if (n === 'WISL_Body') o.material = bodyMat;
  else if (n === 'WISL_Ink' || n === 'WISL_Black') o.material = INK;
  else if (n === 'WISL_Outline') o.material = new THREE.MeshBasicMaterial({color:CFG.ink});
  else if (n === 'WISL_Highlight') o.material = WHITE;
  else o.material = cache[n] || (cache[n] = toon(o.material.color.clone()));
});
const mixer = new THREE.AnimationMixer(model);
const clip = n => gltf.animations.find(a => a.name === n);
mixer.clipAction(clip('Idle')).play();
const faceWhistle = mixer.clipAction(clip('Expr_Whistle')); faceWhistle.play();
const faceGrin = mixer.clipAction(clip('Expr_Grin')); faceGrin.play(); faceGrin.setEffectiveWeight(0);
const capBone = model.getObjectByName('cap');
const capMesh = model.getObjectByName('WISL_Cap');
const shadowMesh = model.getObjectByName('WISL_Shadow');
const fizz = [1,2,3].map(i => model.getObjectByName('WISL_Bubble_' + i)).filter(Boolean);

// ---------------- glass ----------------
const G = { H: 1.75, r0: 0.52, r1: 0.67, base: 0.14 };
const rAt = y => G.r0 + (G.r1 - G.r0) * (y / G.H);
const glass = new THREE.Group(); scene.add(glass);
const prof = (dr, y0, y1) => { const p = []; for (let i = 0; i <= 12; i++) { const y = y0 + (y1 - y0) * i / 12; p.push(new THREE.Vector2(rAt(Math.max(0, y)) + dr, y)); } return p; };
// interior seen through the glass (white, like the drawing)
const inner = new THREE.Mesh(new THREE.LatheGeometry(prof(0, G.base, G.H), 64), toon('#ffffff', {side:THREE.BackSide}));
glass.add(inner);
const floor = new THREE.Mesh(new THREE.CircleGeometry(rAt(G.base), 64), toon('#ffffff'));
floor.rotation.x = -Math.PI / 2; floor.position.y = G.base; glass.add(floor);
// thick black outline (inverted hull) + rim
const hullProf = [new THREE.Vector2(0, -0.05), ...prof(0.05, -0.05, G.H)];
glass.add(new THREE.Mesh(new THREE.LatheGeometry(hullProf, 64), INK_BACK));
const rim = new THREE.Mesh(new THREE.TorusGeometry(G.r1 + 0.012, 0.042, 12, 72), INK);
rim.rotation.x = Math.PI / 2; rim.position.y = G.H; glass.add(rim);
// front wall: barely-there glass so the liquid shows through
const front = new THREE.Mesh(new THREE.LatheGeometry(prof(0.004, 0, G.H), 64),
  new THREE.MeshBasicMaterial({color:'#ffffff', transparent:true, opacity:0.12, depthWrite:false}));
front.renderOrder = 3; glass.add(front);
// white highlight streak on the front-left
const streakGeo = new THREE.CapsuleGeometry ? new THREE.CapsuleGeometry(0.03, 0.95, 4, 8) : new THREE.CylinderGeometry(0.03, 0.03, 0.95, 8);
const streak = new THREE.Mesh(streakGeo, WHITE);
{ const y = 0.95, ang = THREE.MathUtils.degToRad(-38), r = rAt(y) + 0.01;
  streak.position.set(Math.sin(ang) * r, y, Math.cos(ang) * r); streak.rotation.z = -0.08; streak.renderOrder = 4; glass.add(streak); }

// liquid (rebuilt as it rises)
const liqMat = toon(CFG.liquid);
const liquid = new THREE.Mesh(new THREE.BufferGeometry(), liqMat); glass.add(liquid);
const surface = new THREE.Mesh(new THREE.CircleGeometry(1, 64), toon(CFG.liquidTop));
surface.rotation.x = -Math.PI / 2; glass.add(surface);
let builtLevel = -1;
function buildLiquid(level){
  if (Math.abs(level - builtLevel) < 0.002) return;
  builtLevel = level;
  const h = Math.max(level, 0.001), y0 = G.base, r = y => rAt(y) - 0.012;
  liquid.geometry.dispose();
  liquid.geometry = new THREE.CylinderGeometry(r(y0 + h), r(y0), h, 64, 1, true);
  liquid.position.y = y0 + h / 2;
  surface.scale.setScalar(r(y0 + h)); surface.position.y = y0 + h;
  liquid.visible = surface.visible = level > 0.003;
}

// ice cubes: white, black outline
function iceCube(){
  const g = new THREE.Group();
  const geo = new THREE.RoundedBoxGeometry(0.34, 0.34, 0.34, 4, 0.07);
  g.add(new THREE.Mesh(geo, toon('#ffffff')));
  const o = new THREE.Mesh(geo, INK_BACK); o.scale.setScalar(1.17); g.add(o);
  return g;
}
const ice = [ {m: iceCube(), x:-0.17, z:0.12, rot:[0.25, 0.5, 0.18], ph:0},
              {m: iceCube(), x: 0.20, z:0.02, rot:[-0.2, 0.9, -0.25], ph:1.7} ];
ice.forEach(c => glass.add(c.m));

// bubbles inside the liquid (rings, like the icons)
const bubbleGeo = new THREE.TorusGeometry(1, 0.26, 8, 24);
const bubbles = [[-0.3, 0.07, 0.2], [0.26, 0.055, 0.7], [-0.05, 0.04, 1.3], [0.12, 0.065, 2.1], [-0.22, 0.04, 2.8]]
  .map(([x, s, ph]) => { const m = new THREE.Mesh(bubbleGeo, INK); m.scale.setScalar(s); m.renderOrder = 2; glass.add(m); return {m, x, ph}; });

// pour stream + splash
const stream = new THREE.Group(); scene.add(stream);
const sCore = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, 1, 16, 1, true), toon(CFG.liquid));
const sHull = new THREE.Mesh(new THREE.CylinderGeometry(0.115, 0.115, 1, 16, 1, true), INK_BACK);
stream.add(sCore, sHull);
const splash = new THREE.Mesh(new THREE.TorusGeometry(1, 0.2, 8, 32), INK);
splash.rotation.x = Math.PI / 2; scene.add(splash);

// ---------------- layout ----------------
let view = {w: 10, h: 8};
function layout(){
  const w = canvas.clientWidth, h = canvas.clientHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h;
  camera.fov = w < h ? 40 : 32; camera.updateProjectionMatrix();
  const vh = 2 * camera.position.z * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  view = {w: vh * camera.aspect, h: vh};
  const gs = Math.min(1, view.w / 4.2);                  // shrink the glass on very narrow screens
  glass.scale.setScalar(gs * 1.05);
  glass.position.set(0, -view.h / 2 + 1.35, 0);
  glass.updateMatrixWorld(true);
}
addEventListener('resize', layout); layout();

// ---------------- scroll progress ----------------
const section = document.getElementById('wislPour');
const hint = document.getElementById('hint');
let target = 0, prog = 0, prev = 0, vel = 0;
function readScroll(){
  const r = section.getBoundingClientRect();
  const span = r.height - innerHeight;
  target = THREE.MathUtils.clamp(-r.top / Math.max(span, 1), 0, 1);
}
addEventListener('scroll', readScroll, {passive:true}); readScroll();
window.WISLPour = { setProgress(p){ target = THREE.MathUtils.clamp(p, 0, 1); } };   // drive it yourself if you like

const ss = (a, b, x) => { const t = THREE.MathUtils.clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
const up = new THREE.Vector3(), mouth = new THREE.Vector3(), tmp = new THREE.Vector3();

function update(p, time){
  const P = CFG.pour, s = CFG.bottleScale;
  bottle.scale.setScalar(s);
  // tilt: tip over to pour, ease back a touch at the end
  const tiltK = ss(P.tiltStart, P.tiltEnd, p) - 0.18 * ss(P.streamOff, P.tiltBack, p);
  const theta = THREE.MathUtils.degToRad(CFG.tilt) * tiltK;
  // where the mouth should be while pouring: just above the glass rim
  const gTop = glass.position.y + G.H * glass.scale.y;
  const pourMouth = new THREE.Vector3(0.12, gTop + 2.1, 0);
  const pourBase = pourMouth.clone().add(new THREE.Vector3(Math.sin(theta), -Math.cos(theta), 0).multiplyScalar(2 * s));
  const startBase = new THREE.Vector3(Math.min(view.w / 2 - 0.9, 2.7), gTop + 0.35, 0);
  bottle.position.lerpVectors(startBase, pourBase, ss(P.tiltStart, P.tiltEnd, p));
  bottle.rotation.set(0, -0.25 * (1 - tiltK), theta);
  bottle.updateMatrixWorld(true);

  // cap pops off and flies away as the bottle tips
  const capK = ss(P.tiltStart, P.tiltStart + 0.14, p);
  if (capBone) { capBone.position.y += capK * 6; capBone.rotation.x += capK * 9; }
  if (capMesh) capMesh.visible = capK < 0.98;
  if (shadowMesh) shadowMesh.visible = tiltK < 0.04;
  fizz.forEach(b => b.visible = tiltK < 0.2);

  // face: whistling while it pours, grins when the glass is full
  const happy = ss(P.fillEnd - 0.04, P.fillEnd + 0.04, p);
  faceWhistle.setEffectiveWeight(1 - happy); faceGrin.setEffectiveWeight(happy);

  // fill
  const fill = ss(P.fillStart, P.fillEnd, p);
  const level = fill * CFG.maxFill * (G.H - G.base);
  buildLiquid(level);
  const wob = THREE.MathUtils.clamp(vel * 4, -0.18, 0.18) * (level > 0.01 ? 1 : 0);
  surface.rotation.set(-Math.PI / 2 + wob * 0.6, 0, Math.sin(time * 3) * 0.03 + wob);
  const surfY = G.base + level;
  ice.forEach((c, i) => {
    const restY = G.base + 0.2 + i * 0.03;
    const floatY = surfY - 0.12 + Math.sin(time * 1.6 + c.ph) * 0.025;
    const y = Math.max(restY, floatY);
    const r = rAt(y) - 0.25;
    c.m.position.set(THREE.MathUtils.clamp(c.x, -r, r), y, c.z);
    c.m.rotation.set(c.rot[0] + (y - restY) * 0.4, c.rot[1] + Math.sin(time + c.ph) * 0.05 * fill, c.rot[2]);
  });
  bubbles.forEach(b => {
    const span = Math.max(level - 0.12, 0.001);
    const y = G.base + 0.08 + ((time * 0.18 + b.ph * 0.37) % 1) * span;
    const r = rAt(y);
    b.m.position.set(b.x, y, Math.sqrt(Math.max(r * r - b.x * b.x, 0)) - 0.004);
    b.m.visible = level > 0.25 && y < surfY - 0.06;
  });

  // stream: falls from the mouth to the liquid surface, then detaches at the end
  bottle.localToWorld(mouth.set(0, 1.86, 0));
  const surfWorld = glass.localToWorld(tmp.set(0, surfY, 0)).y;
  const head = ss(P.streamOn, P.streamOn + 0.05, p);                 // stream reaching down
  const tail = ss(P.streamOff, P.streamOff + 0.05, p);               // stream letting go
  const yTop = THREE.MathUtils.lerp(mouth.y, surfWorld, tail);
  const yBot = THREE.MathUtils.lerp(mouth.y, surfWorld, head);
  const len = yTop - yBot;
  stream.visible = len > 0.02 && tiltK > 0.5;
  if (stream.visible) {
    const thin = 1 - 0.35 * tail;
    stream.position.set(mouth.x, (yTop + yBot) / 2, 0.05);
    stream.scale.set(thin, len, thin);
  }
  const splashOn = stream.visible && head > 0.98 && tail < 0.95;
  splash.visible = splashOn;
  if (splashOn) {
    const pulse = 0.16 + 0.05 * Math.sin(time * 14);
    splash.position.set(mouth.x, surfWorld + 0.02, 0.05);
    splash.scale.set(pulse * 1.4, pulse, pulse);
  }
  hint.style.opacity = p < 0.03 ? 1 : 0;
}

statusEl.remove();
const clock = new THREE.Clock(); let time = 0;
renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), 0.05); time += dt;
  prog += (target - prog) * Math.min(1, dt * 7);        // smooth the scroll
  vel += ((prog - prev) / Math.max(dt, 1e-3) - vel) * 0.15; prev = prog;
  mixer.update(dt);
  update(prog, time);
  renderer.render(scene, camera);
});
})();
