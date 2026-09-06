/* Fark special-die finishes. Painted Lambert colour remains the base.
 * The shared RGB atlas is data, not colour: R = worn/polished patches,
 * G = inclusions that can catch or hold light, B = shallow material depth.
 * Keep all three channels zero over pip ink and the outer ink contour.
 * No new geometry, transparency pass, texture generation or gameplay RNG.
 */
(function (host) {
  'use strict';

  var VERSION = 'fark-dice-finish-v1';
  var time = { value: 1.75 };
  var lastMs = null;
  var media = null;

  /* Powers stay broad enough to read as worn objects in candlelight.
   * Only Starstone has a visible time-varying light; the other materials
   * catch the room light when the die moves. Values are linear-light gains.
   */
  var profiles = {
    amber:     { gloss: .125, power: 17, spec: [1, .79, .43], glow: .006, shimmer: 0,     glowCol: [1, .39, .08], depth: .105, depthCol: [1, .47, .12] },
    jade:      { gloss: .085, power: 13, spec: [.65, .91, .65], glow: 0,    shimmer: 0,     glowCol: [.25, .73, .31], depth: .070, depthCol: [.21, .65, .32] },
    jade2:     { gloss: .105, power: 16, spec: [.75, .97, .74], glow: .003, shimmer: 0,     glowCol: [.29, .78, .39], depth: .085, depthCol: [.28, .74, .40] },
    silver:    { gloss: .205, power: 24, spec: [.86, .91, .94], glow: 0,    shimmer: 0,     glowCol: [.85, .91, 1],   depth: 0,    depthCol: [1, 1, 1] },
    obsidian:  { gloss: .155, power: 28, spec: [.67, .67, .73], glow: 0,    shimmer: 0,     glowCol: [.61, .28, .15], depth: .014, depthCol: [.48, .20, .09] },
    starstone: { gloss: .095, power: 20, spec: [.61, .79, 1],   glow: .010, shimmer: .026,  glowCol: [.31, .58, 1],   depth: .030, depthCol: [.23, .41, .77] },
    vagabond:  { gloss: .037, power: 10, spec: [.86, .62, .43], glow: 0,    shimmer: 0,     glowCol: [.7, .29, .17],  depth: 0,    depthCol: [1, 1, 1] },
    lucky:    { gloss: .135, power: 19, spec: [1, .81, .38],   glow: 0,    shimmer: 0,     glowCol: [1, .72, .24],   depth: 0,    depthCol: [1, 1, 1] }
  };

  var vertexHead = [
    'varying vec3 fkFinishNormal;',
    'varying vec3 fkFinishView;'
  ].join('\n') + '\n';

  var fragmentHead = [
    'varying vec3 fkFinishNormal;',
    'varying vec3 fkFinishView;',
    'uniform sampler2D fkFinishMap;',
    'uniform float fkFinishEnabled;',
    'uniform float fkFinishTime;',
    'uniform vec4 fkFinishAmounts;',
    'uniform float fkFinishPower;',
    'uniform vec3 fkFinishSpecular;',
    'uniform vec3 fkFinishGlowColour;',
    'uniform vec3 fkFinishDepthColour;',
    'uniform vec3 fkFinishTableUp;',
    'uniform float fkFinishFaceShade;'
  ].join('\n') + '\n';

  var fragmentBody = [
    '#ifdef USE_UV',
    'if (fkFinishEnabled > 0.5) {',
    '  vec3 fkM = texture2D(fkFinishMap, vUv).rgb;',
    '  vec3 fkN = normalize(fkFinishNormal);',
    '  vec3 fkV = normalize(fkFinishView);',
    '  vec3 fkL = normalize(vec3(0.0, 0.33, 0.94));',
    '  float fkLamp = 0.0;',
    '  #if NUM_DIR_LIGHTS > 0',
    '    fkL = normalize(directionalLights[0].direction);',
    '    fkLamp = clamp(max(max(directionalLights[0].color.r, directionalLights[0].color.g), directionalLights[0].color.b), 0.0, 1.4);',
    '  #endif',
    '  vec3 fkH = normalize(fkL + fkV);',
    '  float fkNL = max(dot(fkN, fkL), 0.0);',
    '  float fkNV = max(dot(fkN, fkV), 0.0);',
    '  float fkRim = pow(1.0 - fkNV, 2.4);',
    '  float fkFacing = smoothstep(0.05, 0.95, dot(fkN, normalize(fkFinishTableUp)));',
    '  float fkExposure = clamp(dot(diffuse, vec3(0.2126, 0.7152, 0.0722)), 0.0, 1.0);',
    '  fkExposure *= mix(1.0, mix(0.48, 1.0, fkFacing), clamp(fkFinishFaceShade, 0.0, 1.15));',
    '  float fkBrandGuard = 1.0;',
    '  #ifdef USE_EMISSIVEMAP',
    '    fkBrandGuard = 1.0 - smoothstep(0.035, 0.17, dot(totalEmissiveRadiance, vec3(0.2126, 0.7152, 0.0722)));',
    '  #endif',
    '  float fkPolish = smoothstep(0.02, 0.92, fkM.r);',
    '  float fkHighlight = pow(max(dot(fkN, fkH), 0.0), fkFinishPower) * (0.30 + 0.70 * fkNL);',
    '  vec3 fkSurfaceLight = fkFinishSpecular * fkHighlight * fkPolish * fkFinishAmounts.x * fkLamp;',
    '  float fkPhase = dot(vUv, vec2(13.1, 17.7)) + fkM.g * 5.3;',
    '  float fkWave = 0.5 + 0.5 * sin(fkFinishTime * 0.62 + fkPhase);',
    '  fkWave *= 0.72 + 0.28 * sin(fkFinishTime * 0.37 + fkPhase * 1.7);',
    '  float fkInclusion = fkM.g * fkM.g;',
    '  vec3 fkHeldLight = fkFinishGlowColour * fkInclusion * (fkFinishAmounts.y + fkFinishAmounts.z * pow(max(fkWave, 0.0), 3.0));',
    '  float fkDepth = fkM.b * fkFinishAmounts.w * (0.10 + 0.90 * fkRim) * (0.25 + 0.75 * fkNL) * fkLamp;',
    '  vec3 fkUnderLight = fkFinishDepthColour * fkDepth;',
    '  outgoingLight += (fkSurfaceLight + fkHeldLight + fkUnderLight) * fkExposure * fkBrandGuard;',
    '}',
    '#endif'
  ].join('\n');

  function setColour(target, values) {
    target.setRGB(values[0], values[1], values[2]);
  }

  function applyProfile(u, profile, masks) {
    u.enabled.value = 1;
    u.map.value = masks;
    u.amounts.value.set(profile.gloss, profile.glow, profile.shimmer, profile.depth);
    u.power.value = profile.power;
    setColour(u.specular.value, profile.spec);
    setColour(u.glowColour.value, profile.glowCol);
    setColour(u.depthColour.value, profile.depthCol);
  }

  function attach(material, mat, masks) {
    if (!material || !material.isMeshLambertMaterial) return false;
    var data = material.userData || (material.userData = {});
    var current = data.fkDiceFinish;
    var profile = profiles[mat];
    if (!profile || !masks || !masks.isTexture || !material.map) {
      if (current) current.enabled.value = 0;
      return false;
    }
    if (current) {
      applyProfile(current, profile, masks);
      data.fkDiceFinishMaterial = mat;
      return true;
    }
    var T = host.THREE;
    if (!T) return false;
    var u = {
      enabled: { value: 1 }, map: { value: masks }, time: time,
      amounts: { value: new T.Vector4() }, power: { value: 1 },
      specular: { value: new T.Color() }, glowColour: { value: new T.Color() },
      depthColour: { value: new T.Color() },
      tableUp: { value: new T.Vector3(0, 1, 0) }, faceShade: { value: 0 }
    };
    applyProfile(u, profile, masks);
    data.fkDiceFinish = u;
    data.fkDiceFinishMaterial = mat;
    var previous = material.onBeforeCompile;
    /* Snapshot the previous key before wrapping: Three's default key reads
     * onBeforeCompile dynamically. The later face-shade wrapper must append
     * its own key rather than replacing this key (see integration note).
     */
    var previousKey = material.customProgramCacheKey ? material.customProgramCacheKey() : '';
    material.onBeforeCompile = function (shader, renderer) {
      if (previous) previous.call(this, shader, renderer);
      shader.uniforms.fkFinishMap = u.map;
      shader.uniforms.fkFinishEnabled = u.enabled;
      shader.uniforms.fkFinishTime = u.time;
      shader.uniforms.fkFinishAmounts = u.amounts;
      shader.uniforms.fkFinishPower = u.power;
      shader.uniforms.fkFinishSpecular = u.specular;
      shader.uniforms.fkFinishGlowColour = u.glowColour;
      shader.uniforms.fkFinishDepthColour = u.depthColour;
      /* The match shader installs its orientation uniforms after _dress.
       * Reuse those references on compile; offer/shop dice stay unshaded.
       */
      shader.uniforms.fkFinishTableUp = data.fkFaceShade ? data.fkFaceShade.up : u.tableUp;
      shader.uniforms.fkFinishFaceShade = data.fkFaceShade ? data.fkFaceShade.strength : u.faceShade;
      shader.vertexShader = vertexHead + shader.vertexShader
        .replace('#include <defaultnormal_vertex>', '#include <defaultnormal_vertex>\nfkFinishNormal = normalize(transformedNormal);')
        .replace('#include <project_vertex>', '#include <project_vertex>\nfkFinishView = -mvPosition.xyz;');
      shader.fragmentShader = fragmentHead + shader.fragmentShader
        .replace('#include <envmap_fragment>', '#include <envmap_fragment>\n' + fragmentBody);
    };
    material.customProgramCacheKey = function () { return previousKey + '|' + VERSION; };
    material.needsUpdate = true;
    return true;
  }

  function update(nowMs, reduced) {
    if (reduced === undefined) {
      var body = host.document && host.document.body;
      reduced = !!(body && body.classList.contains('reduced-motion'));
      if (!media && host.matchMedia) media = host.matchMedia('(prefers-reduced-motion: reduce)');
      reduced = reduced || !!(media && media.matches);
    }
    if (typeof nowMs !== 'number' || !isFinite(nowMs)) return time.value;
    if (lastMs === null) lastMs = nowMs;
    /* Freeze at the current appearance, including across pause/resume.
     * Capping the elapsed slice avoids a flash after a hidden browser tab.
     * The only per-frame mutation is this one shared number.
     */
    var elapsed = Math.max(0, Math.min(80, nowMs - lastMs));
    lastMs = nowMs;
    if (!reduced) time.value += elapsed * .001;
    return time.value;
  }

  host.FK_DICE_FINISH = {
    version: VERSION,
    profiles: profiles,
    attach: attach,
    update: update
  };
})(typeof window !== 'undefined' ? window : globalThis);
