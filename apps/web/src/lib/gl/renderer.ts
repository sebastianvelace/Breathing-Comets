import type { Frame, Header } from "../data/types.js";

const vertex = `#version 300 es
out vec2 uv;
void main(){ vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2); uv=p; gl_Position=vec4(p*2.-1.,0.,1.); }`;
const fragment = `#version 300 es
precision highp float; precision highp int;
precision highp sampler2DArray; precision highp usampler2DArray;
uniform sampler2DArray flux; uniform usampler2DArray flags; uniform sampler2D lut;
uniform vec3 view; uniform vec2 size, canvasSize, limits;
uniform uint flagMask;
uniform int frameA, frameB, mode; uniform float blend, sigma;
in vec2 uv; out vec4 color;
vec4 sampleFrame(ivec2 p,int k){
 uint fl=texelFetch(flags,ivec3(p,k),0).r;
 // Saturated samples can also have NaN intensities: saturation has priority.
 if((fl&2u)!=0u) return vec4(1.);
 float value=texelFetch(flux,ivec3(p,k),0).r;
 if(isnan(value)||(fl&8192u)!=0u) return vec4(.043,.043,.039,1.);
 float t;
 if(mode==2) t=clamp(.5+.5*value/(5.*max(sigma,1.e-10)),0.,1.);
 else {float x=clamp((value-limits.x)/max(limits.y-limits.x,1.e-10),0.,1.);t=asinh(20.*x)/asinh(20.);}
 vec4 result=texture(lut,vec2(t,.5));
 if((fl&flagMask)!=0u) result=mix(result,vec4(1.,.42,.34,1.),.55);
 return result;
}
void main(){
 ivec2 p=ivec2(floor((uv-.5)*canvasSize/view.z+view.xy));
 if(any(lessThan(p,ivec2(0)))||any(greaterThanEqual(p,ivec2(size)))){color=vec4(.043,.043,.039,1.);return;}
 vec4 a=sampleFrame(p,frameA);color=mode==1?mix(a,sampleFrame(p,frameB),blend):a;
}`;

export class PlateRenderer {
  readonly gl: WebGL2RenderingContext;
  private program: WebGLProgram;
  private flux: WebGLTexture;
  private flags: WebGLTexture;
  private lut: WebGLTexture;
  private locations = new Map<string, WebGLUniformLocation>();
  constructor(
    readonly canvas: HTMLCanvasElement,
    readonly header: Header,
    difference = false,
  ) {
    const gl = canvas.getContext("webgl2", {
      alpha: false,
      antialias: false,
      preserveDrawingBuffer: false,
    });
    if (!gl) throw new Error("WebGL2 unavailable");
    this.gl = gl;
    const shader = (type: number, source: string) => {
      const s = gl.createShader(type)!;
      gl.shaderSource(s, source);
      gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS))
        throw Error(gl.getShaderInfoLog(s)!);
      return s;
    };
    const vs = shader(gl.VERTEX_SHADER, vertex),
      fs = shader(gl.FRAGMENT_SHADER, fragment),
      program = gl.createProgram()!;
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    gl.deleteShader(vs);
    gl.deleteShader(fs);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS))
      throw Error(gl.getProgramInfoLog(program)!);
    this.program = program;
    gl.useProgram(program);
    for (const name of [
      "flux",
      "flags",
      "lut",
      "view",
      "size",
      "canvasSize",
      "limits",
      "flagMask",
      "frameA",
      "frameB",
      "mode",
      "blend",
      "sigma",
    ])
      this.locations.set(name, gl.getUniformLocation(program, name)!);
    const texture = (unit: number, internal: number) => {
      const t = gl.createTexture()!;
      gl.activeTexture(gl.TEXTURE0 + unit);
      gl.bindTexture(gl.TEXTURE_2D_ARRAY, t);
      gl.texParameteri(gl.TEXTURE_2D_ARRAY, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
      gl.texParameteri(gl.TEXTURE_2D_ARRAY, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
      gl.texParameteri(
        gl.TEXTURE_2D_ARRAY,
        gl.TEXTURE_WRAP_S,
        gl.CLAMP_TO_EDGE,
      );
      gl.texParameteri(
        gl.TEXTURE_2D_ARRAY,
        gl.TEXTURE_WRAP_T,
        gl.CLAMP_TO_EDGE,
      );
      gl.texStorage3D(
        gl.TEXTURE_2D_ARRAY,
        1,
        internal,
        header.grid.nx,
        header.grid.ny,
        header.frames.length,
      );
      return t;
    };
    this.flux = texture(0, gl.R32F);
    this.flags = texture(1, gl.R16UI);
    this.lut = gl.createTexture()!;
    gl.activeTexture(gl.TEXTURE2);
    gl.bindTexture(gl.TEXTURE_2D, this.lut);
    const colors = new Uint8Array(1024),
      dark = [11, 11, 10],
      light = [236, 231, 220];
    for (let i = 0; i < 256; i++) {
      let a = dark,
        b = light,
        t = i / 255;
      if (difference) {
        a = t < 0.5 ? [127, 212, 230] : dark;
        b = t < 0.5 ? dark : [242, 160, 61];
        t = t < 0.5 ? t * 2 : (t - 0.5) * 2;
      }
      for (let c = 0; c < 3; c++)
        colors[i * 4 + c] = Math.round(a[c] + (b[c] - a[c]) * t);
      colors[i * 4 + 3] = 255;
    }
    gl.texImage2D(
      gl.TEXTURE_2D,
      0,
      gl.RGBA8,
      256,
      1,
      0,
      gl.RGBA,
      gl.UNSIGNED_BYTE,
      colors,
    );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.uniform1i(this.u("flux"), 0);
    gl.uniform1i(this.u("flags"), 1);
    gl.uniform1i(this.u("lut"), 2);
    gl.uniform2f(this.u("size"), header.grid.nx, header.grid.ny);
    const limits = header.stretch_hint as { lo: number; hi: number };
    gl.uniform2f(this.u("limits"), limits.lo, limits.hi);
  }
  private u(name: string) {
    return this.locations.get(name)!;
  }
  upload(frame: Frame, i: number) {
    const gl = this.gl,
      { nx, ny } = this.header.grid;
    gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D_ARRAY, this.flux);
    gl.texSubImage3D(
      gl.TEXTURE_2D_ARRAY,
      0,
      0,
      0,
      i,
      nx,
      ny,
      1,
      gl.RED,
      gl.FLOAT,
      frame.flux,
    );
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D_ARRAY, this.flags);
    gl.texSubImage3D(
      gl.TEXTURE_2D_ARRAY,
      0,
      0,
      0,
      i,
      nx,
      ny,
      1,
      gl.RED_INTEGER,
      gl.UNSIGNED_SHORT,
      frame.flags,
    );
  }
  draw(
    a: number,
    b: number,
    mode: number,
    blend: number,
    view: [number, number, number],
    width: number,
    height: number,
    flagMask = 0,
  ) {
    const gl = this.gl,
      ratio = Math.min(devicePixelRatio || 1, 2),
      w = Math.round(width * ratio),
      h = Math.round(height * ratio);
    if (this.canvas.width !== w || this.canvas.height !== h) {
      this.canvas.width = w;
      this.canvas.height = h;
    }
    gl.viewport(0, 0, w, h);
    gl.useProgram(this.program);
    gl.uniform3fv(this.u("view"), view);
    gl.uniform2f(this.u("canvasSize"), width, height);
    gl.uniform1ui(this.u("flagMask"), flagMask);
    gl.uniform1i(this.u("frameA"), a);
    gl.uniform1i(this.u("frameB"), b);
    gl.uniform1i(this.u("mode"), mode);
    gl.uniform1f(this.u("blend"), blend);
    gl.uniform1f(
      this.u("sigma"),
      Number(this.header.frames[a]?.diff_sigma) || 1,
    );
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
  dispose() {
    const gl = this.gl;
    gl.deleteTexture(this.flux);
    gl.deleteTexture(this.flags);
    gl.deleteTexture(this.lut);
    gl.deleteProgram(this.program);
  }
}
