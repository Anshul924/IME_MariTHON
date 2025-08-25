/* ============ UI: basic handling ============ */
const uploadBtn = document.getElementById("submitUpload");
const calcBtn   = document.getElementById("calculateBtn");
const exportBtn = document.getElementById("exportCsv");
const clearBtn  = document.getElementById("clearTbl");

uploadBtn.addEventListener("click", () => {
  Velocity(document.querySelector(".upload-section"),
    { opacity:[1,0], translateY:[0,30] }, { duration:600 });
  document.querySelector(".form-section").scrollIntoView({ behavior:"smooth" });
});

calcBtn.addEventListener("click", () => {
  const tableSec = document.querySelector(".table-section");
  tableSec.classList.remove("hidden");
  Velocity(tableSec, { opacity:[1,0], translateY:[0,40] }, { duration:700 });
  // keep empty; user will add real events later
  document.querySelector(".totals").textContent = "Total Time: 0h 00m";
});

exportBtn.addEventListener("click", () => {
  const rows = Array.from(document.querySelectorAll("#resultTable tr"))
    .map(row => Array.from(row.querySelectorAll("th,td"))
      .map(cell => `"${cell.innerText}"`).join(","));
  const csv = rows.join("\n");
  const blob = new Blob([csv], { type:"text/csv" });
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement("a"), { href:url, download:"results.csv" });
  a.click(); URL.revokeObjectURL(url);
});

clearBtn.addEventListener("click", () => {
  document.querySelector("#resultTable tbody").innerHTML = "";
  document.querySelector(".totals").textContent = "Total Time: 0h 00m";
});

/* ============ THREE: scene setup ============ */
const canvas   = document.getElementById("bg-canvas");
const scene    = new THREE.Scene();
const camera   = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 0.1, 3000);
camera.position.set(0, 1.4, 9);

const renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
renderer.setSize(window.innerWidth, window.innerHeight);

/* Lights (subtle) */
const hemi = new THREE.HemisphereLight(0x88cfff, 0x0b1a2a, 0.9);
scene.add(hemi);

/* ===== Ocean (wavy plane) ===== */
const oceanW = 80, oceanH = 80, seg = 200;
const oceanGeo = new THREE.PlaneGeometry(oceanW, oceanH, seg, seg);
oceanGeo.rotateX(-Math.PI/2);
const oceanMat = new THREE.MeshPhongMaterial({
  color:0x0b3560, emissive:0x001222, shininess:10, transparent:true, opacity:0.95
});
const ocean = new THREE.Mesh(oceanGeo, oceanMat);
ocean.position.y = -1.2;
scene.add(ocean);
const oceanBase = oceanGeo.attributes.position.array.slice();

/* ===== Low-poly Cargo Ship ===== */
const ship = new THREE.Group();

// hull
const hull = new THREE.Mesh(
  new THREE.BoxGeometry(4.8, 0.6, 1.2),
  new THREE.MeshStandardMaterial({ color:0x0a4aa7, metalness:0.1, roughness:0.6 })
);
hull.position.y = -0.3;
ship.add(hull);

// deck
const deck = new THREE.Mesh(
  new THREE.BoxGeometry(4.5, 0.2, 1.0),
  new THREE.MeshStandardMaterial({ color:0x1674d1, metalness:0.1, roughness:0.8 })
);
deck.position.y = 0;
ship.add(deck);

// bridge
const bridge = new THREE.Mesh(
  new THREE.BoxGeometry(0.9, 0.5, 0.8),
  new THREE.MeshStandardMaterial({ color:0xcfd8dc, roughness:0.9 })
);
bridge.position.set(-1.6, 0.45, 0);
ship.add(bridge);

// containers
for(let i=0;i<6;i++){
  const c = new THREE.Mesh(
    new THREE.BoxGeometry(0.9, 0.35, 0.8),
    new THREE.MeshStandardMaterial({ color:[0x18c99a,0x22d3ee,0x34d399,0x0ea5e9][i%4], roughness:0.7 })
  );
  c.position.set(-0.9 + i*0.7, 0.3, 0);
  ship.add(c);
}

// simple mast
const mast = new THREE.Mesh(
  new THREE.CylinderGeometry(0.05, 0.05, 0.9, 12),
  new THREE.MeshStandardMaterial({ color:0xffd166 })
);
mast.position.set(1.8, 0.65, 0);
ship.add(mast);

ship.position.set(-10, 0, 0);
scene.add(ship);

/* ===== Spark Particles ===== */
const pCount = 300;
const pGeo = new THREE.BufferGeometry();
const pPos = new Float32Array(pCount*3);
const pVel = new Float32Array(pCount*3);
const pTTL = new Float32Array(pCount);
for(let i=0;i<pCount;i++){
  pPos[i*3]   = (Math.random()-0.5)*30;
  pPos[i*3+1] = Math.random()*5;
  pPos[i*3+2] = (Math.random()-0.5)*10;
}
pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
const pMat = new THREE.PointsMaterial({ size:0.06, color:0x00ffcc, transparent:true, opacity:0.7, blending:THREE.AdditiveBlending });
const particles = new THREE.Points(pGeo, pMat);
scene.add(particles);

/* ===== Horizontal scanning beams (no diagonals) ===== */
function makeBeam(opacity){
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(40, 0.4),
    new THREE.MeshBasicMaterial({ color:0x00ffff, transparent:true, opacity, blending:THREE.AdditiveBlending, depthWrite:false })
  );
  mesh.rotation.x = -Math.PI/2; // lay flat near ocean then seen as glow
  mesh.position.y = -0.1;
  return mesh;
}
const beams = [makeBeam(0.28), makeBeam(0.22), makeBeam(0.18)];
beams.forEach(b=>scene.add(b));

/* ===== Mouse & Click ===== */
const mouse = { x:0, y:0 };
window.addEventListener("mousemove", e=>{
  mouse.x = (e.clientX/window.innerWidth)*2-1;
  mouse.y = -(e.clientY/window.innerHeight)*2+1;
});
window.addEventListener("click", ()=>{
  for(let k=0;k<20;k++){
    const i = Math.floor(Math.random()*pCount);
    pVel[i*3]   = (Math.random()-0.5)*8;
    pVel[i*3+1] = (Math.random())*6;
    pVel[i*3+2] = (Math.random()-0.5)*8;
    pTTL[i] = 60;
  }
});

/* ============ Animate ============ */
function animate(t=0){
  requestAnimationFrame(animate);
  const time = t*0.001;

  // camera subtle parallax
  camera.position.x = mouse.x*0.6;
  camera.position.y = 1.4 + mouse.y*0.3;
  camera.lookAt(0,0,0);

  // ocean waves
  const arr = oceanGeo.attributes.position.array;
  for(let i=0;i<arr.length;i+=3){
    const ox = oceanBase[i], oy = oceanBase[i+1], oz = oceanBase[i+2];
    const wave = Math.sin((ox+time*2)*0.35)*0.25 + Math.cos((oz+time*1.8)*0.45)*0.2;
    arr[i]   = ox;
    arr[i+1] = oy + wave;
    arr[i+2] = oz;
  }
  oceanGeo.attributes.position.needsUpdate = true;

  // ship cruise + bob
  ship.position.x += 0.02;
  if(ship.position.x > 12) ship.position.x = -12;
  ship.position.y = Math.sin(time*2)*0.2;
  ship.rotation.z = Math.sin(time*1.5)*0.03;
  ship.rotation.y = Math.sin(time*0.5)*0.02;

  // particles drift + burst decay
  const pA = pGeo.attributes.position.array;
  for(let i=0;i<pCount;i++){
    const idx=i*3;
    pA[idx]   += Math.sin(time+i)*0.004;
    pA[idx+1] += Math.cos(time*1.1+i)*0.003;

    if(pTTL[i]>0){
      pA[idx]   += pVel[idx]*0.02;
      pA[idx+1] += pVel[idx+1]*0.02;
      pA[idx+2] += pVel[idx+2]*0.02;
      pVel[idx]*=0.94; pVel[idx+1]*=0.94; pVel[idx+2]*=0.94;
      pTTL[i]--;
    }
  }
  pGeo.attributes.position.needsUpdate = true;

  // beams sweep (horizontal only)
  beams[0].position.z = (time*6)%20-10;
  beams[1].position.z = (time*4.5)%20-10;
  beams[2].position.z = (time*3.2)%20-10;

  renderer.render(scene, camera);
}
animate();

/* Resize */
window.addEventListener("resize", ()=>{
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
