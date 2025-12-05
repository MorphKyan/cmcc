/**
* @vue/shared v3.5.22
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
// @__NO_SIDE_EFFECTS__
function wt(e) {
  const t = /* @__PURE__ */ Object.create(null);
  for (const n of e.split(",")) t[n] = 1;
  return (n) => n in t;
}
const me = process.env.NODE_ENV !== "production" ? Object.freeze({}) : {}, tn = process.env.NODE_ENV !== "production" ? Object.freeze([]) : [], Re = () => {
}, gs = () => !1, Tn = (e) => e.charCodeAt(0) === 111 && e.charCodeAt(1) === 110 && // uppercase letter
(e.charCodeAt(2) > 122 || e.charCodeAt(2) < 97), Xn = (e) => e.startsWith("onUpdate:"), Ve = Object.assign, Qr = (e, t) => {
  const n = e.indexOf(t);
  n > -1 && e.splice(n, 1);
}, $i = Object.prototype.hasOwnProperty, le = (e, t) => $i.call(e, t), K = Array.isArray, Bt = (e) => fr(e) === "[object Map]", vs = (e) => fr(e) === "[object Set]", q = (e) => typeof e == "function", Se = (e) => typeof e == "string", Rt = (e) => typeof e == "symbol", he = (e) => e !== null && typeof e == "object", Zr = (e) => (he(e) || q(e)) && q(e.then) && q(e.catch), ms = Object.prototype.toString, fr = (e) => ms.call(e), eo = (e) => fr(e).slice(8, -1), _s = (e) => fr(e) === "[object Object]", to = (e) => Se(e) && e !== "NaN" && e[0] !== "-" && "" + parseInt(e, 10) === e, vn = /* @__PURE__ */ wt(
  // the leading comma is intentional so empty string "" is also included
  ",key,ref,ref_for,ref_key,onVnodeBeforeMount,onVnodeMounted,onVnodeBeforeUpdate,onVnodeUpdated,onVnodeBeforeUnmount,onVnodeUnmounted"
), Fi = /* @__PURE__ */ wt(
  "bind,cloak,else-if,else,for,html,if,model,on,once,pre,show,slot,text,memo"
), ur = (e) => {
  const t = /* @__PURE__ */ Object.create(null);
  return ((n) => t[n] || (t[n] = e(n)));
}, ji = /-\w/g, ot = ur(
  (e) => e.replace(ji, (t) => t.slice(1).toUpperCase())
), Ui = /\B([A-Z])/g, Mt = ur(
  (e) => e.replace(Ui, "-$1").toLowerCase()
), dr = ur((e) => e.charAt(0).toUpperCase() + e.slice(1)), jt = ur(
  (e) => e ? `on${dr(e)}` : ""
), Wt = (e, t) => !Object.is(e, t), an = (e, ...t) => {
  for (let n = 0; n < e.length; n++)
    e[n](...t);
}, Qn = (e, t, n, r = !1) => {
  Object.defineProperty(e, t, {
    configurable: !0,
    enumerable: !1,
    writable: r,
    value: n
  });
}, Hi = (e) => {
  const t = parseFloat(e);
  return isNaN(t) ? e : t;
}, Bi = (e) => {
  const t = Se(e) ? Number(e) : NaN;
  return isNaN(t) ? e : t;
};
let No;
const Vn = () => No || (No = typeof globalThis < "u" ? globalThis : typeof self < "u" ? self : typeof window < "u" ? window : typeof global < "u" ? global : {});
function pr(e) {
  if (K(e)) {
    const t = {};
    for (let n = 0; n < e.length; n++) {
      const r = e[n], o = Se(r) ? Ki(r) : pr(r);
      if (o)
        for (const s in o)
          t[s] = o[s];
    }
    return t;
  } else if (Se(e) || he(e))
    return e;
}
const Wi = /;(?![^(]*\))/g, zi = /:([^]+)/, Gi = /\/\*[^]*?\*\//g;
function Ki(e) {
  const t = {};
  return e.replace(Gi, "").split(Wi).forEach((n) => {
    if (n) {
      const r = n.split(zi);
      r.length > 1 && (t[r[0].trim()] = r[1].trim());
    }
  }), t;
}
function hr(e) {
  let t = "";
  if (Se(e))
    t = e;
  else if (K(e))
    for (let n = 0; n < e.length; n++) {
      const r = hr(e[n]);
      r && (t += r + " ");
    }
  else if (he(e))
    for (const n in e)
      e[n] && (t += n + " ");
  return t.trim();
}
const Yi = "html,body,base,head,link,meta,style,title,address,article,aside,footer,header,hgroup,h1,h2,h3,h4,h5,h6,nav,section,div,dd,dl,dt,figcaption,figure,picture,hr,img,li,main,ol,p,pre,ul,a,b,abbr,bdi,bdo,br,cite,code,data,dfn,em,i,kbd,mark,q,rp,rt,ruby,s,samp,small,span,strong,sub,sup,time,u,var,wbr,area,audio,map,track,video,embed,object,param,source,canvas,script,noscript,del,ins,caption,col,colgroup,table,thead,tbody,td,th,tr,button,datalist,fieldset,form,input,label,legend,meter,optgroup,option,output,progress,select,textarea,details,dialog,menu,summary,template,blockquote,iframe,tfoot", Ji = "svg,animate,animateMotion,animateTransform,circle,clipPath,color-profile,defs,desc,discard,ellipse,feBlend,feColorMatrix,feComponentTransfer,feComposite,feConvolveMatrix,feDiffuseLighting,feDisplacementMap,feDistantLight,feDropShadow,feFlood,feFuncA,feFuncB,feFuncG,feFuncR,feGaussianBlur,feImage,feMerge,feMergeNode,feMorphology,feOffset,fePointLight,feSpecularLighting,feSpotLight,feTile,feTurbulence,filter,foreignObject,g,hatch,hatchpath,image,line,linearGradient,marker,mask,mesh,meshgradient,meshpatch,meshrow,metadata,mpath,path,pattern,polygon,polyline,radialGradient,rect,set,solidcolor,stop,switch,symbol,text,textPath,title,tspan,unknown,use,view", qi = "annotation,annotation-xml,maction,maligngroup,malignmark,math,menclose,merror,mfenced,mfrac,mfraction,mglyph,mi,mlabeledtr,mlongdiv,mmultiscripts,mn,mo,mover,mpadded,mphantom,mprescripts,mroot,mrow,ms,mscarries,mscarry,msgroup,msline,mspace,msqrt,msrow,mstack,mstyle,msub,msubsup,msup,mtable,mtd,mtext,mtr,munder,munderover,none,semantics", Xi = /* @__PURE__ */ wt(Yi), Qi = /* @__PURE__ */ wt(Ji), Zi = /* @__PURE__ */ wt(qi), ec = "itemscope,allowfullscreen,formnovalidate,ismap,nomodule,novalidate,readonly", tc = /* @__PURE__ */ wt(ec);
function bs(e) {
  return !!e || e === "";
}
const Es = (e) => !!(e && e.__v_isRef === !0), pn = (e) => Se(e) ? e : e == null ? "" : K(e) || he(e) && (e.toString === ms || !q(e.toString)) ? Es(e) ? pn(e.value) : JSON.stringify(e, ys, 2) : String(e), ys = (e, t) => Es(t) ? ys(e, t.value) : Bt(t) ? {
  [`Map(${t.size})`]: [...t.entries()].reduce(
    (n, [r, o], s) => (n[yr(r, s) + " =>"] = o, n),
    {}
  )
} : vs(t) ? {
  [`Set(${t.size})`]: [...t.values()].map((n) => yr(n))
} : Rt(t) ? yr(t) : he(t) && !K(t) && !_s(t) ? String(t) : t, yr = (e, t = "") => {
  var n;
  return (
    // Symbol.description in es2019+ so we need to cast here to pass
    // the lib: es2016 check
    Rt(e) ? `Symbol(${(n = e.description) != null ? n : t})` : e
  );
};
/**
* @vue/reactivity v3.5.22
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
function it(e, ...t) {
  console.warn(`[Vue warn] ${e}`, ...t);
}
let We;
class nc {
  constructor(t = !1) {
    this.detached = t, this._active = !0, this._on = 0, this.effects = [], this.cleanups = [], this._isPaused = !1, this.parent = We, !t && We && (this.index = (We.scopes || (We.scopes = [])).push(
      this
    ) - 1);
  }
  get active() {
    return this._active;
  }
  pause() {
    if (this._active) {
      this._isPaused = !0;
      let t, n;
      if (this.scopes)
        for (t = 0, n = this.scopes.length; t < n; t++)
          this.scopes[t].pause();
      for (t = 0, n = this.effects.length; t < n; t++)
        this.effects[t].pause();
    }
  }
  /**
   * Resumes the effect scope, including all child scopes and effects.
   */
  resume() {
    if (this._active && this._isPaused) {
      this._isPaused = !1;
      let t, n;
      if (this.scopes)
        for (t = 0, n = this.scopes.length; t < n; t++)
          this.scopes[t].resume();
      for (t = 0, n = this.effects.length; t < n; t++)
        this.effects[t].resume();
    }
  }
  run(t) {
    if (this._active) {
      const n = We;
      try {
        return We = this, t();
      } finally {
        We = n;
      }
    } else process.env.NODE_ENV !== "production" && it("cannot run an inactive effect scope.");
  }
  /**
   * This should only be called on non-detached scopes
   * @internal
   */
  on() {
    ++this._on === 1 && (this.prevScope = We, We = this);
  }
  /**
   * This should only be called on non-detached scopes
   * @internal
   */
  off() {
    this._on > 0 && --this._on === 0 && (We = this.prevScope, this.prevScope = void 0);
  }
  stop(t) {
    if (this._active) {
      this._active = !1;
      let n, r;
      for (n = 0, r = this.effects.length; n < r; n++)
        this.effects[n].stop();
      for (this.effects.length = 0, n = 0, r = this.cleanups.length; n < r; n++)
        this.cleanups[n]();
      if (this.cleanups.length = 0, this.scopes) {
        for (n = 0, r = this.scopes.length; n < r; n++)
          this.scopes[n].stop(!0);
        this.scopes.length = 0;
      }
      if (!this.detached && this.parent && !t) {
        const o = this.parent.scopes.pop();
        o && o !== this && (this.parent.scopes[this.index] = o, o.index = this.index);
      }
      this.parent = void 0;
    }
  }
}
function rc() {
  return We;
}
let pe;
const Nr = /* @__PURE__ */ new WeakSet();
class Ns {
  constructor(t) {
    this.fn = t, this.deps = void 0, this.depsTail = void 0, this.flags = 5, this.next = void 0, this.cleanup = void 0, this.scheduler = void 0, We && We.active && We.effects.push(this);
  }
  pause() {
    this.flags |= 64;
  }
  resume() {
    this.flags & 64 && (this.flags &= -65, Nr.has(this) && (Nr.delete(this), this.trigger()));
  }
  /**
   * @internal
   */
  notify() {
    this.flags & 2 && !(this.flags & 32) || this.flags & 8 || ws(this);
  }
  run() {
    if (!(this.flags & 1))
      return this.fn();
    this.flags |= 2, xo(this), Os(this);
    const t = pe, n = st;
    pe = this, st = !0;
    try {
      return this.fn();
    } finally {
      process.env.NODE_ENV !== "production" && pe !== this && it(
        "Active effect was not restored correctly - this is likely a Vue internal bug."
      ), Cs(this), pe = t, st = n, this.flags &= -3;
    }
  }
  stop() {
    if (this.flags & 1) {
      for (let t = this.deps; t; t = t.nextDep)
        oo(t);
      this.deps = this.depsTail = void 0, xo(this), this.onStop && this.onStop(), this.flags &= -2;
    }
  }
  trigger() {
    this.flags & 64 ? Nr.add(this) : this.scheduler ? this.scheduler() : this.runIfDirty();
  }
  /**
   * @internal
   */
  runIfDirty() {
    Lr(this) && this.run();
  }
  get dirty() {
    return Lr(this);
  }
}
let xs = 0, mn, _n;
function ws(e, t = !1) {
  if (e.flags |= 8, t) {
    e.next = _n, _n = e;
    return;
  }
  e.next = mn, mn = e;
}
function no() {
  xs++;
}
function ro() {
  if (--xs > 0)
    return;
  if (_n) {
    let t = _n;
    for (_n = void 0; t; ) {
      const n = t.next;
      t.next = void 0, t.flags &= -9, t = n;
    }
  }
  let e;
  for (; mn; ) {
    let t = mn;
    for (mn = void 0; t; ) {
      const n = t.next;
      if (t.next = void 0, t.flags &= -9, t.flags & 1)
        try {
          t.trigger();
        } catch (r) {
          e || (e = r);
        }
      t = n;
    }
  }
  if (e) throw e;
}
function Os(e) {
  for (let t = e.deps; t; t = t.nextDep)
    t.version = -1, t.prevActiveLink = t.dep.activeLink, t.dep.activeLink = t;
}
function Cs(e) {
  let t, n = e.depsTail, r = n;
  for (; r; ) {
    const o = r.prevDep;
    r.version === -1 ? (r === n && (n = o), oo(r), oc(r)) : t = r, r.dep.activeLink = r.prevActiveLink, r.prevActiveLink = void 0, r = o;
  }
  e.deps = t, e.depsTail = n;
}
function Lr(e) {
  for (let t = e.deps; t; t = t.nextDep)
    if (t.dep.version !== t.version || t.dep.computed && (Ss(t.dep.computed) || t.dep.version !== t.version))
      return !0;
  return !!e._dirty;
}
function Ss(e) {
  if (e.flags & 4 && !(e.flags & 16) || (e.flags &= -17, e.globalVersion === Nn) || (e.globalVersion = Nn, !e.isSSR && e.flags & 128 && (!e.deps && !e._dirty || !Lr(e))))
    return;
  e.flags |= 2;
  const t = e.dep, n = pe, r = st;
  pe = e, st = !0;
  try {
    Os(e);
    const o = e.fn(e._value);
    (t.version === 0 || Wt(o, e._value)) && (e.flags |= 128, e._value = o, t.version++);
  } catch (o) {
    throw t.version++, o;
  } finally {
    pe = n, st = r, Cs(e), e.flags &= -3;
  }
}
function oo(e, t = !1) {
  const { dep: n, prevSub: r, nextSub: o } = e;
  if (r && (r.nextSub = o, e.prevSub = void 0), o && (o.prevSub = r, e.nextSub = void 0), process.env.NODE_ENV !== "production" && n.subsHead === e && (n.subsHead = o), n.subs === e && (n.subs = r, !r && n.computed)) {
    n.computed.flags &= -5;
    for (let s = n.computed.deps; s; s = s.nextDep)
      oo(s, !0);
  }
  !t && !--n.sc && n.map && n.map.delete(n.key);
}
function oc(e) {
  const { prevDep: t, nextDep: n } = e;
  t && (t.nextDep = n, e.prevDep = void 0), n && (n.prevDep = t, e.nextDep = void 0);
}
let st = !0;
const Ds = [];
function ct() {
  Ds.push(st), st = !1;
}
function lt() {
  const e = Ds.pop();
  st = e === void 0 ? !0 : e;
}
function xo(e) {
  const { cleanup: t } = e;
  if (e.cleanup = void 0, t) {
    const n = pe;
    pe = void 0;
    try {
      t();
    } finally {
      pe = n;
    }
  }
}
let Nn = 0;
class sc {
  constructor(t, n) {
    this.sub = t, this.dep = n, this.version = n.version, this.nextDep = this.prevDep = this.nextSub = this.prevSub = this.prevActiveLink = void 0;
  }
}
class Ts {
  // TODO isolatedDeclarations "__v_skip"
  constructor(t) {
    this.computed = t, this.version = 0, this.activeLink = void 0, this.subs = void 0, this.map = void 0, this.key = void 0, this.sc = 0, this.__v_skip = !0, process.env.NODE_ENV !== "production" && (this.subsHead = void 0);
  }
  track(t) {
    if (!pe || !st || pe === this.computed)
      return;
    let n = this.activeLink;
    if (n === void 0 || n.sub !== pe)
      n = this.activeLink = new sc(pe, this), pe.deps ? (n.prevDep = pe.depsTail, pe.depsTail.nextDep = n, pe.depsTail = n) : pe.deps = pe.depsTail = n, Vs(n);
    else if (n.version === -1 && (n.version = this.version, n.nextDep)) {
      const r = n.nextDep;
      r.prevDep = n.prevDep, n.prevDep && (n.prevDep.nextDep = r), n.prevDep = pe.depsTail, n.nextDep = void 0, pe.depsTail.nextDep = n, pe.depsTail = n, pe.deps === n && (pe.deps = r);
    }
    return process.env.NODE_ENV !== "production" && pe.onTrack && pe.onTrack(
      Ve(
        {
          effect: pe
        },
        t
      )
    ), n;
  }
  trigger(t) {
    this.version++, Nn++, this.notify(t);
  }
  notify(t) {
    no();
    try {
      if (process.env.NODE_ENV !== "production")
        for (let n = this.subsHead; n; n = n.nextSub)
          n.sub.onTrigger && !(n.sub.flags & 8) && n.sub.onTrigger(
            Ve(
              {
                effect: n.sub
              },
              t
            )
          );
      for (let n = this.subs; n; n = n.prevSub)
        n.sub.notify() && n.sub.dep.notify();
    } finally {
      ro();
    }
  }
}
function Vs(e) {
  if (e.dep.sc++, e.sub.flags & 4) {
    const t = e.dep.computed;
    if (t && !e.dep.subs) {
      t.flags |= 20;
      for (let r = t.deps; r; r = r.nextDep)
        Vs(r);
    }
    const n = e.dep.subs;
    n !== e && (e.prevSub = n, n && (n.nextSub = e)), process.env.NODE_ENV !== "production" && e.dep.subsHead === void 0 && (e.dep.subsHead = e), e.dep.subs = e;
  }
}
const kr = /* @__PURE__ */ new WeakMap(), zt = Symbol(
  process.env.NODE_ENV !== "production" ? "Object iterate" : ""
), Pr = Symbol(
  process.env.NODE_ENV !== "production" ? "Map keys iterate" : ""
), xn = Symbol(
  process.env.NODE_ENV !== "production" ? "Array iterate" : ""
);
function Ie(e, t, n) {
  if (st && pe) {
    let r = kr.get(e);
    r || kr.set(e, r = /* @__PURE__ */ new Map());
    let o = r.get(n);
    o || (r.set(n, o = new Ts()), o.map = r, o.key = n), process.env.NODE_ENV !== "production" ? o.track({
      target: e,
      type: t,
      key: n
    }) : o.track();
  }
}
function pt(e, t, n, r, o, s) {
  const i = kr.get(e);
  if (!i) {
    Nn++;
    return;
  }
  const c = (u) => {
    u && (process.env.NODE_ENV !== "production" ? u.trigger({
      target: e,
      type: t,
      key: n,
      newValue: r,
      oldValue: o,
      oldTarget: s
    }) : u.trigger());
  };
  if (no(), t === "clear")
    i.forEach(c);
  else {
    const u = K(e), m = u && to(n);
    if (u && n === "length") {
      const h = Number(r);
      i.forEach((p, E) => {
        (E === "length" || E === xn || !Rt(E) && E >= h) && c(p);
      });
    } else
      switch ((n !== void 0 || i.has(void 0)) && c(i.get(n)), m && c(i.get(xn)), t) {
        case "add":
          u ? m && c(i.get("length")) : (c(i.get(zt)), Bt(e) && c(i.get(Pr)));
          break;
        case "delete":
          u || (c(i.get(zt)), Bt(e) && c(i.get(Pr)));
          break;
        case "set":
          Bt(e) && c(i.get(zt));
          break;
      }
  }
  ro();
}
function Xt(e) {
  const t = re(e);
  return t === e ? t : (Ie(t, "iterate", xn), Xe(e) ? t : t.map(Ye));
}
function so(e) {
  return Ie(e = re(e), "iterate", xn), e;
}
const ic = {
  __proto__: null,
  [Symbol.iterator]() {
    return xr(this, Symbol.iterator, Ye);
  },
  concat(...e) {
    return Xt(this).concat(
      ...e.map((t) => K(t) ? Xt(t) : t)
    );
  },
  entries() {
    return xr(this, "entries", (e) => (e[1] = Ye(e[1]), e));
  },
  every(e, t) {
    return _t(this, "every", e, t, void 0, arguments);
  },
  filter(e, t) {
    return _t(this, "filter", e, t, (n) => n.map(Ye), arguments);
  },
  find(e, t) {
    return _t(this, "find", e, t, Ye, arguments);
  },
  findIndex(e, t) {
    return _t(this, "findIndex", e, t, void 0, arguments);
  },
  findLast(e, t) {
    return _t(this, "findLast", e, t, Ye, arguments);
  },
  findLastIndex(e, t) {
    return _t(this, "findLastIndex", e, t, void 0, arguments);
  },
  // flat, flatMap could benefit from ARRAY_ITERATE but are not straight-forward to implement
  forEach(e, t) {
    return _t(this, "forEach", e, t, void 0, arguments);
  },
  includes(...e) {
    return wr(this, "includes", e);
  },
  indexOf(...e) {
    return wr(this, "indexOf", e);
  },
  join(e) {
    return Xt(this).join(e);
  },
  // keys() iterator only reads `length`, no optimization required
  lastIndexOf(...e) {
    return wr(this, "lastIndexOf", e);
  },
  map(e, t) {
    return _t(this, "map", e, t, void 0, arguments);
  },
  pop() {
    return fn(this, "pop");
  },
  push(...e) {
    return fn(this, "push", e);
  },
  reduce(e, ...t) {
    return wo(this, "reduce", e, t);
  },
  reduceRight(e, ...t) {
    return wo(this, "reduceRight", e, t);
  },
  shift() {
    return fn(this, "shift");
  },
  // slice could use ARRAY_ITERATE but also seems to beg for range tracking
  some(e, t) {
    return _t(this, "some", e, t, void 0, arguments);
  },
  splice(...e) {
    return fn(this, "splice", e);
  },
  toReversed() {
    return Xt(this).toReversed();
  },
  toSorted(e) {
    return Xt(this).toSorted(e);
  },
  toSpliced(...e) {
    return Xt(this).toSpliced(...e);
  },
  unshift(...e) {
    return fn(this, "unshift", e);
  },
  values() {
    return xr(this, "values", Ye);
  }
};
function xr(e, t, n) {
  const r = so(e), o = r[t]();
  return r !== e && !Xe(e) && (o._next = o.next, o.next = () => {
    const s = o._next();
    return s.done || (s.value = n(s.value)), s;
  }), o;
}
const cc = Array.prototype;
function _t(e, t, n, r, o, s) {
  const i = so(e), c = i !== e && !Xe(e), u = i[t];
  if (u !== cc[t]) {
    const p = u.apply(e, s);
    return c ? Ye(p) : p;
  }
  let m = n;
  i !== e && (c ? m = function(p, E) {
    return n.call(this, Ye(p), E, e);
  } : n.length > 2 && (m = function(p, E) {
    return n.call(this, p, E, e);
  }));
  const h = u.call(i, m, r);
  return c && o ? o(h) : h;
}
function wo(e, t, n, r) {
  const o = so(e);
  let s = n;
  return o !== e && (Xe(e) ? n.length > 3 && (s = function(i, c, u) {
    return n.call(this, i, c, u, e);
  }) : s = function(i, c, u) {
    return n.call(this, i, Ye(c), u, e);
  }), o[t](s, ...r);
}
function wr(e, t, n) {
  const r = re(e);
  Ie(r, "iterate", xn);
  const o = r[t](...n);
  return (o === -1 || o === !1) && Zn(n[0]) ? (n[0] = re(n[0]), r[t](...n)) : o;
}
function fn(e, t, n = []) {
  ct(), no();
  const r = re(e)[t].apply(e, n);
  return ro(), lt(), r;
}
const lc = /* @__PURE__ */ wt("__proto__,__v_isRef,__isVue"), As = new Set(
  /* @__PURE__ */ Object.getOwnPropertyNames(Symbol).filter((e) => e !== "arguments" && e !== "caller").map((e) => Symbol[e]).filter(Rt)
);
function ac(e) {
  Rt(e) || (e = String(e));
  const t = re(this);
  return Ie(t, "has", e), t.hasOwnProperty(e);
}
class Ms {
  constructor(t = !1, n = !1) {
    this._isReadonly = t, this._isShallow = n;
  }
  get(t, n, r) {
    if (n === "__v_skip") return t.__v_skip;
    const o = this._isReadonly, s = this._isShallow;
    if (n === "__v_isReactive")
      return !o;
    if (n === "__v_isReadonly")
      return o;
    if (n === "__v_isShallow")
      return s;
    if (n === "__v_raw")
      return r === (o ? s ? $s : Ps : s ? ks : Ls).get(t) || // receiver is not the reactive proxy, but has the same prototype
      // this means the receiver is a user proxy of the reactive proxy
      Object.getPrototypeOf(t) === Object.getPrototypeOf(r) ? t : void 0;
    const i = K(t);
    if (!o) {
      let u;
      if (i && (u = ic[n]))
        return u;
      if (n === "hasOwnProperty")
        return ac;
    }
    const c = Reflect.get(
      t,
      n,
      // if this is a proxy wrapping a ref, return methods using the raw ref
      // as receiver so that we don't have to call `toRaw` on the ref in all
      // its class methods
      Le(t) ? t : r
    );
    if ((Rt(n) ? As.has(n) : lc(n)) || (o || Ie(t, "get", n), s))
      return c;
    if (Le(c)) {
      const u = i && to(n) ? c : c.value;
      return o && he(u) ? Fr(u) : u;
    }
    return he(c) ? o ? Fr(c) : io(c) : c;
  }
}
class Is extends Ms {
  constructor(t = !1) {
    super(!1, t);
  }
  set(t, n, r, o) {
    let s = t[n];
    if (!this._isShallow) {
      const u = It(s);
      if (!Xe(r) && !It(r) && (s = re(s), r = re(r)), !K(t) && Le(s) && !Le(r))
        return u ? (process.env.NODE_ENV !== "production" && it(
          `Set operation on key "${String(n)}" failed: target is readonly.`,
          t[n]
        ), !0) : (s.value = r, !0);
    }
    const i = K(t) && to(n) ? Number(n) < t.length : le(t, n), c = Reflect.set(
      t,
      n,
      r,
      Le(t) ? t : o
    );
    return t === re(o) && (i ? Wt(r, s) && pt(t, "set", n, r, s) : pt(t, "add", n, r)), c;
  }
  deleteProperty(t, n) {
    const r = le(t, n), o = t[n], s = Reflect.deleteProperty(t, n);
    return s && r && pt(t, "delete", n, void 0, o), s;
  }
  has(t, n) {
    const r = Reflect.has(t, n);
    return (!Rt(n) || !As.has(n)) && Ie(t, "has", n), r;
  }
  ownKeys(t) {
    return Ie(
      t,
      "iterate",
      K(t) ? "length" : zt
    ), Reflect.ownKeys(t);
  }
}
class Rs extends Ms {
  constructor(t = !1) {
    super(!0, t);
  }
  set(t, n) {
    return process.env.NODE_ENV !== "production" && it(
      `Set operation on key "${String(n)}" failed: target is readonly.`,
      t
    ), !0;
  }
  deleteProperty(t, n) {
    return process.env.NODE_ENV !== "production" && it(
      `Delete operation on key "${String(n)}" failed: target is readonly.`,
      t
    ), !0;
  }
}
const fc = /* @__PURE__ */ new Is(), uc = /* @__PURE__ */ new Rs(), dc = /* @__PURE__ */ new Is(!0), pc = /* @__PURE__ */ new Rs(!0), $r = (e) => e, $n = (e) => Reflect.getPrototypeOf(e);
function hc(e, t, n) {
  return function(...r) {
    const o = this.__v_raw, s = re(o), i = Bt(s), c = e === "entries" || e === Symbol.iterator && i, u = e === "keys" && i, m = o[e](...r), h = n ? $r : t ? jr : Ye;
    return !t && Ie(
      s,
      "iterate",
      u ? Pr : zt
    ), {
      // iterator protocol
      next() {
        const { value: p, done: E } = m.next();
        return E ? { value: p, done: E } : {
          value: c ? [h(p[0]), h(p[1])] : h(p),
          done: E
        };
      },
      // iterable protocol
      [Symbol.iterator]() {
        return this;
      }
    };
  };
}
function Fn(e) {
  return function(...t) {
    if (process.env.NODE_ENV !== "production") {
      const n = t[0] ? `on key "${t[0]}" ` : "";
      it(
        `${dr(e)} operation ${n}failed: target is readonly.`,
        re(this)
      );
    }
    return e === "delete" ? !1 : e === "clear" ? void 0 : this;
  };
}
function gc(e, t) {
  const n = {
    get(o) {
      const s = this.__v_raw, i = re(s), c = re(o);
      e || (Wt(o, c) && Ie(i, "get", o), Ie(i, "get", c));
      const { has: u } = $n(i), m = t ? $r : e ? jr : Ye;
      if (u.call(i, o))
        return m(s.get(o));
      if (u.call(i, c))
        return m(s.get(c));
      s !== i && s.get(o);
    },
    get size() {
      const o = this.__v_raw;
      return !e && Ie(re(o), "iterate", zt), o.size;
    },
    has(o) {
      const s = this.__v_raw, i = re(s), c = re(o);
      return e || (Wt(o, c) && Ie(i, "has", o), Ie(i, "has", c)), o === c ? s.has(o) : s.has(o) || s.has(c);
    },
    forEach(o, s) {
      const i = this, c = i.__v_raw, u = re(c), m = t ? $r : e ? jr : Ye;
      return !e && Ie(u, "iterate", zt), c.forEach((h, p) => o.call(s, m(h), m(p), i));
    }
  };
  return Ve(
    n,
    e ? {
      add: Fn("add"),
      set: Fn("set"),
      delete: Fn("delete"),
      clear: Fn("clear")
    } : {
      add(o) {
        !t && !Xe(o) && !It(o) && (o = re(o));
        const s = re(this);
        return $n(s).has.call(s, o) || (s.add(o), pt(s, "add", o, o)), this;
      },
      set(o, s) {
        !t && !Xe(s) && !It(s) && (s = re(s));
        const i = re(this), { has: c, get: u } = $n(i);
        let m = c.call(i, o);
        m ? process.env.NODE_ENV !== "production" && Oo(i, c, o) : (o = re(o), m = c.call(i, o));
        const h = u.call(i, o);
        return i.set(o, s), m ? Wt(s, h) && pt(i, "set", o, s, h) : pt(i, "add", o, s), this;
      },
      delete(o) {
        const s = re(this), { has: i, get: c } = $n(s);
        let u = i.call(s, o);
        u ? process.env.NODE_ENV !== "production" && Oo(s, i, o) : (o = re(o), u = i.call(s, o));
        const m = c ? c.call(s, o) : void 0, h = s.delete(o);
        return u && pt(s, "delete", o, void 0, m), h;
      },
      clear() {
        const o = re(this), s = o.size !== 0, i = process.env.NODE_ENV !== "production" ? Bt(o) ? new Map(o) : new Set(o) : void 0, c = o.clear();
        return s && pt(
          o,
          "clear",
          void 0,
          void 0,
          i
        ), c;
      }
    }
  ), [
    "keys",
    "values",
    "entries",
    Symbol.iterator
  ].forEach((o) => {
    n[o] = hc(o, e, t);
  }), n;
}
function gr(e, t) {
  const n = gc(e, t);
  return (r, o, s) => o === "__v_isReactive" ? !e : o === "__v_isReadonly" ? e : o === "__v_raw" ? r : Reflect.get(
    le(n, o) && o in r ? n : r,
    o,
    s
  );
}
const vc = {
  get: /* @__PURE__ */ gr(!1, !1)
}, mc = {
  get: /* @__PURE__ */ gr(!1, !0)
}, _c = {
  get: /* @__PURE__ */ gr(!0, !1)
}, bc = {
  get: /* @__PURE__ */ gr(!0, !0)
};
function Oo(e, t, n) {
  const r = re(n);
  if (r !== n && t.call(e, r)) {
    const o = eo(e);
    it(
      `Reactive ${o} contains both the raw and reactive versions of the same object${o === "Map" ? " as keys" : ""}, which can lead to inconsistencies. Avoid differentiating between the raw and reactive versions of an object and only use the reactive version if possible.`
    );
  }
}
const Ls = /* @__PURE__ */ new WeakMap(), ks = /* @__PURE__ */ new WeakMap(), Ps = /* @__PURE__ */ new WeakMap(), $s = /* @__PURE__ */ new WeakMap();
function Ec(e) {
  switch (e) {
    case "Object":
    case "Array":
      return 1;
    case "Map":
    case "Set":
    case "WeakMap":
    case "WeakSet":
      return 2;
    default:
      return 0;
  }
}
function yc(e) {
  return e.__v_skip || !Object.isExtensible(e) ? 0 : Ec(eo(e));
}
function io(e) {
  return It(e) ? e : vr(
    e,
    !1,
    fc,
    vc,
    Ls
  );
}
function Nc(e) {
  return vr(
    e,
    !1,
    dc,
    mc,
    ks
  );
}
function Fr(e) {
  return vr(
    e,
    !0,
    uc,
    _c,
    Ps
  );
}
function ht(e) {
  return vr(
    e,
    !0,
    pc,
    bc,
    $s
  );
}
function vr(e, t, n, r, o) {
  if (!he(e))
    return process.env.NODE_ENV !== "production" && it(
      `value cannot be made ${t ? "readonly" : "reactive"}: ${String(
        e
      )}`
    ), e;
  if (e.__v_raw && !(t && e.__v_isReactive))
    return e;
  const s = yc(e);
  if (s === 0)
    return e;
  const i = o.get(e);
  if (i)
    return i;
  const c = new Proxy(
    e,
    s === 2 ? r : n
  );
  return o.set(e, c), c;
}
function nn(e) {
  return It(e) ? nn(e.__v_raw) : !!(e && e.__v_isReactive);
}
function It(e) {
  return !!(e && e.__v_isReadonly);
}
function Xe(e) {
  return !!(e && e.__v_isShallow);
}
function Zn(e) {
  return e ? !!e.__v_raw : !1;
}
function re(e) {
  const t = e && e.__v_raw;
  return t ? re(t) : e;
}
function xc(e) {
  return !le(e, "__v_skip") && Object.isExtensible(e) && Qn(e, "__v_skip", !0), e;
}
const Ye = (e) => he(e) ? io(e) : e, jr = (e) => he(e) ? Fr(e) : e;
function Le(e) {
  return e ? e.__v_isRef === !0 : !1;
}
function wc(e) {
  return Le(e) ? e.value : e;
}
const Oc = {
  get: (e, t, n) => t === "__v_raw" ? e : wc(Reflect.get(e, t, n)),
  set: (e, t, n, r) => {
    const o = e[t];
    return Le(o) && !Le(n) ? (o.value = n, !0) : Reflect.set(e, t, n, r);
  }
};
function Fs(e) {
  return nn(e) ? e : new Proxy(e, Oc);
}
class Cc {
  constructor(t, n, r) {
    this.fn = t, this.setter = n, this._value = void 0, this.dep = new Ts(this), this.__v_isRef = !0, this.deps = void 0, this.depsTail = void 0, this.flags = 16, this.globalVersion = Nn - 1, this.next = void 0, this.effect = this, this.__v_isReadonly = !n, this.isSSR = r;
  }
  /**
   * @internal
   */
  notify() {
    if (this.flags |= 16, !(this.flags & 8) && // avoid infinite self recursion
    pe !== this)
      return ws(this, !0), !0;
    process.env.NODE_ENV;
  }
  get value() {
    const t = process.env.NODE_ENV !== "production" ? this.dep.track({
      target: this,
      type: "get",
      key: "value"
    }) : this.dep.track();
    return Ss(this), t && (t.version = this.dep.version), this._value;
  }
  set value(t) {
    this.setter ? this.setter(t) : process.env.NODE_ENV !== "production" && it("Write operation failed: computed value is readonly");
  }
}
function Sc(e, t, n = !1) {
  let r, o;
  q(e) ? r = e : (r = e.get, o = e.set);
  const s = new Cc(r, o, n);
  return process.env.NODE_ENV, s;
}
const jn = {}, er = /* @__PURE__ */ new WeakMap();
let Ut;
function Dc(e, t = !1, n = Ut) {
  if (n) {
    let r = er.get(n);
    r || er.set(n, r = []), r.push(e);
  } else process.env.NODE_ENV !== "production" && !t && it(
    "onWatcherCleanup() was called when there was no active watcher to associate with."
  );
}
function Tc(e, t, n = me) {
  const { immediate: r, deep: o, once: s, scheduler: i, augmentJob: c, call: u } = n, m = (B) => {
    (n.onWarn || it)(
      "Invalid watch source: ",
      B,
      "A watch source can only be a getter/effect function, a ref, a reactive object, or an array of these types."
    );
  }, h = (B) => o ? B : Xe(B) || o === !1 || o === 0 ? At(B, 1) : At(B);
  let p, E, A, H, j = !1, _e = !1;
  if (Le(e) ? (E = () => e.value, j = Xe(e)) : nn(e) ? (E = () => h(e), j = !0) : K(e) ? (_e = !0, j = e.some((B) => nn(B) || Xe(B)), E = () => e.map((B) => {
    if (Le(B))
      return B.value;
    if (nn(B))
      return h(B);
    if (q(B))
      return u ? u(B, 2) : B();
    process.env.NODE_ENV !== "production" && m(B);
  })) : q(e) ? t ? E = u ? () => u(e, 2) : e : E = () => {
    if (A) {
      ct();
      try {
        A();
      } finally {
        lt();
      }
    }
    const B = Ut;
    Ut = p;
    try {
      return u ? u(e, 3, [H]) : e(H);
    } finally {
      Ut = B;
    }
  } : (E = Re, process.env.NODE_ENV !== "production" && m(e)), t && o) {
    const B = E, ce = o === !0 ? 1 / 0 : o;
    E = () => At(B(), ce);
  }
  const ne = rc(), Z = () => {
    p.stop(), ne && ne.active && Qr(ne.effects, p);
  };
  if (s && t) {
    const B = t;
    t = (...ce) => {
      B(...ce), Z();
    };
  }
  let Q = _e ? new Array(e.length).fill(jn) : jn;
  const Oe = (B) => {
    if (!(!(p.flags & 1) || !p.dirty && !B))
      if (t) {
        const ce = p.run();
        if (o || j || (_e ? ce.some((De, we) => Wt(De, Q[we])) : Wt(ce, Q))) {
          A && A();
          const De = Ut;
          Ut = p;
          try {
            const we = [
              ce,
              // pass undefined as the old value when it's changed for the first time
              Q === jn ? void 0 : _e && Q[0] === jn ? [] : Q,
              H
            ];
            Q = ce, u ? u(t, 3, we) : (
              // @ts-expect-error
              t(...we)
            );
          } finally {
            Ut = De;
          }
        }
      } else
        p.run();
  };
  return c && c(Oe), p = new Ns(E), p.scheduler = i ? () => i(Oe, !1) : Oe, H = (B) => Dc(B, !1, p), A = p.onStop = () => {
    const B = er.get(p);
    if (B) {
      if (u)
        u(B, 4);
      else
        for (const ce of B) ce();
      er.delete(p);
    }
  }, process.env.NODE_ENV !== "production" && (p.onTrack = n.onTrack, p.onTrigger = n.onTrigger), t ? r ? Oe(!0) : Q = p.run() : i ? i(Oe.bind(null, !0), !0) : p.run(), Z.pause = p.pause.bind(p), Z.resume = p.resume.bind(p), Z.stop = Z, Z;
}
function At(e, t = 1 / 0, n) {
  if (t <= 0 || !he(e) || e.__v_skip || (n = n || /* @__PURE__ */ new Map(), (n.get(e) || 0) >= t))
    return e;
  if (n.set(e, t), t--, Le(e))
    At(e.value, t, n);
  else if (K(e))
    for (let r = 0; r < e.length; r++)
      At(e[r], t, n);
  else if (vs(e) || Bt(e))
    e.forEach((r) => {
      At(r, t, n);
    });
  else if (_s(e)) {
    for (const r in e)
      At(e[r], t, n);
    for (const r of Object.getOwnPropertySymbols(e))
      Object.prototype.propertyIsEnumerable.call(e, r) && At(e[r], t, n);
  }
  return e;
}
/**
* @vue/runtime-core v3.5.22
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
const Gt = [];
function Bn(e) {
  Gt.push(e);
}
function Wn() {
  Gt.pop();
}
let Or = !1;
function R(e, ...t) {
  if (Or) return;
  Or = !0, ct();
  const n = Gt.length ? Gt[Gt.length - 1].component : null, r = n && n.appContext.config.warnHandler, o = Vc();
  if (r)
    ln(
      r,
      n,
      11,
      [
        // eslint-disable-next-line no-restricted-syntax
        e + t.map((s) => {
          var i, c;
          return (c = (i = s.toString) == null ? void 0 : i.call(s)) != null ? c : JSON.stringify(s);
        }).join(""),
        n && n.proxy,
        o.map(
          ({ vnode: s }) => `at <${Er(n, s.type)}>`
        ).join(`
`),
        o
      ]
    );
  else {
    const s = [`[Vue warn]: ${e}`, ...t];
    o.length && s.push(`
`, ...Ac(o)), console.warn(...s);
  }
  lt(), Or = !1;
}
function Vc() {
  let e = Gt[Gt.length - 1];
  if (!e)
    return [];
  const t = [];
  for (; e; ) {
    const n = t[0];
    n && n.vnode === e ? n.recurseCount++ : t.push({
      vnode: e,
      recurseCount: 0
    });
    const r = e.component && e.component.parent;
    e = r && r.vnode;
  }
  return t;
}
function Ac(e) {
  const t = [];
  return e.forEach((n, r) => {
    t.push(...r === 0 ? [] : [`
`], ...Mc(n));
  }), t;
}
function Mc({ vnode: e, recurseCount: t }) {
  const n = t > 0 ? `... (${t} recursive calls)` : "", r = e.component ? e.component.parent == null : !1, o = ` at <${Er(
    e.component,
    e.type,
    r
  )}`, s = ">" + n;
  return e.props ? [o, ...Ic(e.props), s] : [o + s];
}
function Ic(e) {
  const t = [], n = Object.keys(e);
  return n.slice(0, 3).forEach((r) => {
    t.push(...js(r, e[r]));
  }), n.length > 3 && t.push(" ..."), t;
}
function js(e, t, n) {
  return Se(t) ? (t = JSON.stringify(t), n ? t : [`${e}=${t}`]) : typeof t == "number" || typeof t == "boolean" || t == null ? n ? t : [`${e}=${t}`] : Le(t) ? (t = js(e, re(t.value), !0), n ? t : [`${e}=Ref<`, t, ">"]) : q(t) ? [`${e}=fn${t.name ? `<${t.name}>` : ""}`] : (t = re(t), n ? t : [`${e}=`, t]);
}
function Rc(e, t) {
  process.env.NODE_ENV !== "production" && e !== void 0 && (typeof e != "number" ? R(`${t} is not a valid number - got ${JSON.stringify(e)}.`) : isNaN(e) && R(`${t} is NaN - the duration expression might be incorrect.`));
}
const co = {
  sp: "serverPrefetch hook",
  bc: "beforeCreate hook",
  c: "created hook",
  bm: "beforeMount hook",
  m: "mounted hook",
  bu: "beforeUpdate hook",
  u: "updated",
  bum: "beforeUnmount hook",
  um: "unmounted hook",
  a: "activated hook",
  da: "deactivated hook",
  ec: "errorCaptured hook",
  rtc: "renderTracked hook",
  rtg: "renderTriggered hook",
  0: "setup function",
  1: "render function",
  2: "watcher getter",
  3: "watcher callback",
  4: "watcher cleanup function",
  5: "native event handler",
  6: "component event handler",
  7: "vnode hook",
  8: "directive hook",
  9: "transition hook",
  10: "app errorHandler",
  11: "app warnHandler",
  12: "ref function",
  13: "async component loader",
  14: "scheduler flush",
  15: "component update",
  16: "app unmount cleanup function"
};
function ln(e, t, n, r) {
  try {
    return r ? e(...r) : e();
  } catch (o) {
    An(o, t, n);
  }
}
function at(e, t, n, r) {
  if (q(e)) {
    const o = ln(e, t, n, r);
    return o && Zr(o) && o.catch((s) => {
      An(s, t, n);
    }), o;
  }
  if (K(e)) {
    const o = [];
    for (let s = 0; s < e.length; s++)
      o.push(at(e[s], t, n, r));
    return o;
  } else process.env.NODE_ENV !== "production" && R(
    `Invalid value type passed to callWithAsyncErrorHandling(): ${typeof e}`
  );
}
function An(e, t, n, r = !0) {
  const o = t ? t.vnode : null, { errorHandler: s, throwUnhandledErrorInProduction: i } = t && t.appContext.config || me;
  if (t) {
    let c = t.parent;
    const u = t.proxy, m = process.env.NODE_ENV !== "production" ? co[n] : `https://vuejs.org/error-reference/#runtime-${n}`;
    for (; c; ) {
      const h = c.ec;
      if (h) {
        for (let p = 0; p < h.length; p++)
          if (h[p](e, u, m) === !1)
            return;
      }
      c = c.parent;
    }
    if (s) {
      ct(), ln(s, null, 10, [
        e,
        u,
        m
      ]), lt();
      return;
    }
  }
  Lc(e, n, o, r, i);
}
function Lc(e, t, n, r = !0, o = !1) {
  if (process.env.NODE_ENV !== "production") {
    const s = co[t];
    if (n && Bn(n), R(`Unhandled error${s ? ` during execution of ${s}` : ""}`), n && Wn(), r)
      throw e;
    console.error(e);
  } else {
    if (o)
      throw e;
    console.error(e);
  }
}
const Be = [];
let dt = -1;
const rn = [];
let Tt = null, en = 0;
const Us = /* @__PURE__ */ Promise.resolve();
let tr = null;
const kc = 100;
function Pc(e) {
  const t = tr || Us;
  return e ? t.then(this ? e.bind(this) : e) : t;
}
function $c(e) {
  let t = dt + 1, n = Be.length;
  for (; t < n; ) {
    const r = t + n >>> 1, o = Be[r], s = wn(o);
    s < e || s === e && o.flags & 2 ? t = r + 1 : n = r;
  }
  return t;
}
function mr(e) {
  if (!(e.flags & 1)) {
    const t = wn(e), n = Be[Be.length - 1];
    !n || // fast path when the job id is larger than the tail
    !(e.flags & 2) && t >= wn(n) ? Be.push(e) : Be.splice($c(t), 0, e), e.flags |= 1, Hs();
  }
}
function Hs() {
  tr || (tr = Us.then(zs));
}
function Bs(e) {
  K(e) ? rn.push(...e) : Tt && e.id === -1 ? Tt.splice(en + 1, 0, e) : e.flags & 1 || (rn.push(e), e.flags |= 1), Hs();
}
function Co(e, t, n = dt + 1) {
  for (process.env.NODE_ENV !== "production" && (t = t || /* @__PURE__ */ new Map()); n < Be.length; n++) {
    const r = Be[n];
    if (r && r.flags & 2) {
      if (e && r.id !== e.uid || process.env.NODE_ENV !== "production" && lo(t, r))
        continue;
      Be.splice(n, 1), n--, r.flags & 4 && (r.flags &= -2), r(), r.flags & 4 || (r.flags &= -2);
    }
  }
}
function Ws(e) {
  if (rn.length) {
    const t = [...new Set(rn)].sort(
      (n, r) => wn(n) - wn(r)
    );
    if (rn.length = 0, Tt) {
      Tt.push(...t);
      return;
    }
    for (Tt = t, process.env.NODE_ENV !== "production" && (e = e || /* @__PURE__ */ new Map()), en = 0; en < Tt.length; en++) {
      const n = Tt[en];
      process.env.NODE_ENV !== "production" && lo(e, n) || (n.flags & 4 && (n.flags &= -2), n.flags & 8 || n(), n.flags &= -2);
    }
    Tt = null, en = 0;
  }
}
const wn = (e) => e.id == null ? e.flags & 2 ? -1 : 1 / 0 : e.id;
function zs(e) {
  process.env.NODE_ENV !== "production" && (e = e || /* @__PURE__ */ new Map());
  const t = process.env.NODE_ENV !== "production" ? (n) => lo(e, n) : Re;
  try {
    for (dt = 0; dt < Be.length; dt++) {
      const n = Be[dt];
      if (n && !(n.flags & 8)) {
        if (process.env.NODE_ENV !== "production" && t(n))
          continue;
        n.flags & 4 && (n.flags &= -2), ln(
          n,
          n.i,
          n.i ? 15 : 14
        ), n.flags & 4 || (n.flags &= -2);
      }
    }
  } finally {
    for (; dt < Be.length; dt++) {
      const n = Be[dt];
      n && (n.flags &= -2);
    }
    dt = -1, Be.length = 0, Ws(e), tr = null, (Be.length || rn.length) && zs(e);
  }
}
function lo(e, t) {
  const n = e.get(t) || 0;
  if (n > kc) {
    const r = t.i, o = r && Ii(r.type);
    return An(
      `Maximum recursive updates exceeded${o ? ` in component <${o}>` : ""}. This means you have a reactive effect that is mutating its own dependencies and thus recursively triggering itself. Possible sources include component template, render function, updated hook or watcher source function.`,
      null,
      10
    ), !0;
  }
  return e.set(t, n + 1), !1;
}
let gt = !1;
const zn = /* @__PURE__ */ new Map();
process.env.NODE_ENV !== "production" && (Vn().__VUE_HMR_RUNTIME__ = {
  createRecord: Cr(Gs),
  rerender: Cr(Uc),
  reload: Cr(Hc)
});
const Yt = /* @__PURE__ */ new Map();
function Fc(e) {
  const t = e.type.__hmrId;
  let n = Yt.get(t);
  n || (Gs(t, e.type), n = Yt.get(t)), n.instances.add(e);
}
function jc(e) {
  Yt.get(e.type.__hmrId).instances.delete(e);
}
function Gs(e, t) {
  return Yt.has(e) ? !1 : (Yt.set(e, {
    initialDef: nr(t),
    instances: /* @__PURE__ */ new Set()
  }), !0);
}
function nr(e) {
  return Ri(e) ? e.__vccOpts : e;
}
function Uc(e, t) {
  const n = Yt.get(e);
  n && (n.initialDef.render = t, [...n.instances].forEach((r) => {
    t && (r.render = t, nr(r.type).render = t), r.renderCache = [], gt = !0, r.job.flags & 8 || r.update(), gt = !1;
  }));
}
function Hc(e, t) {
  const n = Yt.get(e);
  if (!n) return;
  t = nr(t), So(n.initialDef, t);
  const r = [...n.instances];
  for (let o = 0; o < r.length; o++) {
    const s = r[o], i = nr(s.type);
    let c = zn.get(i);
    c || (i !== n.initialDef && So(i, t), zn.set(i, c = /* @__PURE__ */ new Set())), c.add(s), s.appContext.propsCache.delete(s.type), s.appContext.emitsCache.delete(s.type), s.appContext.optionsCache.delete(s.type), s.ceReload ? (c.add(s), s.ceReload(t.styles), c.delete(s)) : s.parent ? mr(() => {
      s.job.flags & 8 || (gt = !0, s.parent.update(), gt = !1, c.delete(s));
    }) : s.appContext.reload ? s.appContext.reload() : typeof window < "u" ? window.location.reload() : console.warn(
      "[HMR] Root or manually mounted instance modified. Full reload required."
    ), s.root.ce && s !== s.root && s.root.ce._removeChildStyle(i);
  }
  Bs(() => {
    zn.clear();
  });
}
function So(e, t) {
  Ve(e, t);
  for (const n in e)
    n !== "__file" && !(n in t) && delete e[n];
}
function Cr(e) {
  return (t, n) => {
    try {
      return e(t, n);
    } catch (r) {
      console.error(r), console.warn(
        "[HMR] Something went wrong during Vue component hot-reload. Full reload required."
      );
    }
  };
}
let rt, hn = [], Ur = !1;
function Mn(e, ...t) {
  rt ? rt.emit(e, ...t) : Ur || hn.push({ event: e, args: t });
}
function ao(e, t) {
  var n, r;
  rt = e, rt ? (rt.enabled = !0, hn.forEach(({ event: o, args: s }) => rt.emit(o, ...s)), hn = []) : /* handle late devtools injection - only do this if we are in an actual */ /* browser environment to avoid the timer handle stalling test runner exit */ /* (#4815) */ typeof window < "u" && // some envs mock window but not fully
  window.HTMLElement && // also exclude jsdom
  // eslint-disable-next-line no-restricted-syntax
  !((r = (n = window.navigator) == null ? void 0 : n.userAgent) != null && r.includes("jsdom")) ? ((t.__VUE_DEVTOOLS_HOOK_REPLAY__ = t.__VUE_DEVTOOLS_HOOK_REPLAY__ || []).push((s) => {
    ao(s, t);
  }), setTimeout(() => {
    rt || (t.__VUE_DEVTOOLS_HOOK_REPLAY__ = null, Ur = !0, hn = []);
  }, 3e3)) : (Ur = !0, hn = []);
}
function Bc(e, t) {
  Mn("app:init", e, t, {
    Fragment: tt,
    Text: Rn,
    Comment: Ae,
    Static: Yn
  });
}
function Wc(e) {
  Mn("app:unmount", e);
}
const zc = /* @__PURE__ */ fo(
  "component:added"
  /* COMPONENT_ADDED */
), Ks = /* @__PURE__ */ fo(
  "component:updated"
  /* COMPONENT_UPDATED */
), Gc = /* @__PURE__ */ fo(
  "component:removed"
  /* COMPONENT_REMOVED */
), Kc = (e) => {
  rt && typeof rt.cleanupBuffer == "function" && // remove the component if it wasn't buffered
  !rt.cleanupBuffer(e) && Gc(e);
};
// @__NO_SIDE_EFFECTS__
function fo(e) {
  return (t) => {
    Mn(
      e,
      t.appContext.app,
      t.uid,
      t.parent ? t.parent.uid : void 0,
      t
    );
  };
}
const Yc = /* @__PURE__ */ Ys(
  "perf:start"
  /* PERFORMANCE_START */
), Jc = /* @__PURE__ */ Ys(
  "perf:end"
  /* PERFORMANCE_END */
);
function Ys(e) {
  return (t, n, r) => {
    Mn(e, t.appContext.app, t.uid, t, n, r);
  };
}
function qc(e, t, n) {
  Mn(
    "component:emit",
    e.appContext.app,
    e,
    t,
    n
  );
}
let Je = null, Js = null;
function rr(e) {
  const t = Je;
  return Je = e, Js = e && e.type.__scopeId || null, t;
}
function qs(e, t = Je, n) {
  if (!t || e._n)
    return e;
  const r = (...o) => {
    r._d && lr(-1);
    const s = rr(t);
    let i;
    try {
      i = e(...o);
    } finally {
      rr(s), r._d && lr(1);
    }
    return process.env.NODE_ENV !== "production" && Ks(t), i;
  };
  return r._n = !0, r._c = !0, r._d = !0, r;
}
function Xs(e) {
  Fi(e) && R("Do not use built-in directive ids as custom directive id: " + e);
}
function kt(e, t, n, r) {
  const o = e.dirs, s = t && t.dirs;
  for (let i = 0; i < o.length; i++) {
    const c = o[i];
    s && (c.oldValue = s[i].value);
    let u = c.dir[r];
    u && (ct(), at(u, n, 8, [
      e.el,
      c,
      e,
      t
    ]), lt());
  }
}
const Xc = Symbol("_vte"), Qs = (e) => e.__isTeleport, yt = Symbol("_leaveCb"), Un = Symbol("_enterCb");
function Qc() {
  const e = {
    isMounted: !1,
    isLeaving: !1,
    isUnmounting: !1,
    leavingVNodes: /* @__PURE__ */ new Map()
  };
  return ii(() => {
    e.isMounted = !0;
  }), ci(() => {
    e.isUnmounting = !0;
  }), e;
}
const Qe = [Function, Array], Zs = {
  mode: String,
  appear: Boolean,
  persisted: Boolean,
  // enter
  onBeforeEnter: Qe,
  onEnter: Qe,
  onAfterEnter: Qe,
  onEnterCancelled: Qe,
  // leave
  onBeforeLeave: Qe,
  onLeave: Qe,
  onAfterLeave: Qe,
  onLeaveCancelled: Qe,
  // appear
  onBeforeAppear: Qe,
  onAppear: Qe,
  onAfterAppear: Qe,
  onAppearCancelled: Qe
}, ei = (e) => {
  const t = e.subTree;
  return t.component ? ei(t.component) : t;
}, Zc = {
  name: "BaseTransition",
  props: Zs,
  setup(e, { slots: t }) {
    const n = mo(), r = Qc();
    return () => {
      const o = t.default && ri(t.default(), !0);
      if (!o || !o.length)
        return;
      const s = ti(o), i = re(e), { mode: c } = i;
      if (process.env.NODE_ENV !== "production" && c && c !== "in-out" && c !== "out-in" && c !== "default" && R(`invalid <transition> mode: ${c}`), r.isLeaving)
        return Sr(s);
      const u = Do(s);
      if (!u)
        return Sr(s);
      let m = Hr(
        u,
        i,
        r,
        n,
        // #11061, ensure enterHooks is fresh after clone
        (p) => m = p
      );
      u.type !== Ae && On(u, m);
      let h = n.subTree && Do(n.subTree);
      if (h && h.type !== Ae && !Ht(h, u) && ei(n).type !== Ae) {
        let p = Hr(
          h,
          i,
          r,
          n
        );
        if (On(h, p), c === "out-in" && u.type !== Ae)
          return r.isLeaving = !0, p.afterLeave = () => {
            r.isLeaving = !1, n.job.flags & 8 || n.update(), delete p.afterLeave, h = void 0;
          }, Sr(s);
        c === "in-out" && u.type !== Ae ? p.delayLeave = (E, A, H) => {
          const j = ni(
            r,
            h
          );
          j[String(h.key)] = h, E[yt] = () => {
            A(), E[yt] = void 0, delete m.delayedLeave, h = void 0;
          }, m.delayedLeave = () => {
            H(), delete m.delayedLeave, h = void 0;
          };
        } : h = void 0;
      } else h && (h = void 0);
      return s;
    };
  }
};
function ti(e) {
  let t = e[0];
  if (e.length > 1) {
    let n = !1;
    for (const r of e)
      if (r.type !== Ae) {
        if (process.env.NODE_ENV !== "production" && n) {
          R(
            "<transition> can only be used on a single element or component. Use <transition-group> for lists."
          );
          break;
        }
        if (t = r, n = !0, process.env.NODE_ENV === "production") break;
      }
  }
  return t;
}
const el = Zc;
function ni(e, t) {
  const { leavingVNodes: n } = e;
  let r = n.get(t.type);
  return r || (r = /* @__PURE__ */ Object.create(null), n.set(t.type, r)), r;
}
function Hr(e, t, n, r, o) {
  const {
    appear: s,
    mode: i,
    persisted: c = !1,
    onBeforeEnter: u,
    onEnter: m,
    onAfterEnter: h,
    onEnterCancelled: p,
    onBeforeLeave: E,
    onLeave: A,
    onAfterLeave: H,
    onLeaveCancelled: j,
    onBeforeAppear: _e,
    onAppear: ne,
    onAfterAppear: Z,
    onAppearCancelled: Q
  } = t, Oe = String(e.key), B = ni(n, e), ce = (Y, ae) => {
    Y && at(
      Y,
      r,
      9,
      ae
    );
  }, De = (Y, ae) => {
    const ue = ae[1];
    ce(Y, ae), K(Y) ? Y.every(($) => $.length <= 1) && ue() : Y.length <= 1 && ue();
  }, we = {
    mode: i,
    persisted: c,
    beforeEnter(Y) {
      let ae = u;
      if (!n.isMounted)
        if (s)
          ae = _e || u;
        else
          return;
      Y[yt] && Y[yt](
        !0
        /* cancelled */
      );
      const ue = B[Oe];
      ue && Ht(e, ue) && ue.el[yt] && ue.el[yt](), ce(ae, [Y]);
    },
    enter(Y) {
      let ae = m, ue = h, $ = p;
      if (!n.isMounted)
        if (s)
          ae = ne || m, ue = Z || h, $ = Q || p;
        else
          return;
      let be = !1;
      const X = Y[Un] = (ke) => {
        be || (be = !0, ke ? ce($, [Y]) : ce(ue, [Y]), we.delayedLeave && we.delayedLeave(), Y[Un] = void 0);
      };
      ae ? De(ae, [Y, X]) : X();
    },
    leave(Y, ae) {
      const ue = String(e.key);
      if (Y[Un] && Y[Un](
        !0
        /* cancelled */
      ), n.isUnmounting)
        return ae();
      ce(E, [Y]);
      let $ = !1;
      const be = Y[yt] = (X) => {
        $ || ($ = !0, ae(), X ? ce(j, [Y]) : ce(H, [Y]), Y[yt] = void 0, B[ue] === e && delete B[ue]);
      };
      B[ue] = e, A ? De(A, [Y, be]) : be();
    },
    clone(Y) {
      const ae = Hr(
        Y,
        t,
        n,
        r,
        o
      );
      return o && o(ae), ae;
    }
  };
  return we;
}
function Sr(e) {
  if (In(e))
    return e = vt(e), e.children = null, e;
}
function Do(e) {
  if (!In(e))
    return Qs(e.type) && e.children ? ti(e.children) : e;
  if (e.component)
    return e.component.subTree;
  const { shapeFlag: t, children: n } = e;
  if (n) {
    if (t & 16)
      return n[0];
    if (t & 32 && q(n.default))
      return n.default();
  }
}
function On(e, t) {
  e.shapeFlag & 6 && e.component ? (e.transition = t, On(e.component.subTree, t)) : e.shapeFlag & 128 ? (e.ssContent.transition = t.clone(e.ssContent), e.ssFallback.transition = t.clone(e.ssFallback)) : e.transition = t;
}
function ri(e, t = !1, n) {
  let r = [], o = 0;
  for (let s = 0; s < e.length; s++) {
    let i = e[s];
    const c = n == null ? i.key : String(n) + String(i.key != null ? i.key : s);
    i.type === tt ? (i.patchFlag & 128 && o++, r = r.concat(
      ri(i.children, t, c)
    )) : (t || i.type !== Ae) && r.push(c != null ? vt(i, { key: c }) : i);
  }
  if (o > 1)
    for (let s = 0; s < r.length; s++)
      r[s].patchFlag = -2;
  return r;
}
function oi(e) {
  e.ids = [e.ids[0] + e.ids[2]++ + "-", 0, 0];
}
const To = /* @__PURE__ */ new WeakSet(), or = /* @__PURE__ */ new WeakMap();
function bn(e, t, n, r, o = !1) {
  if (K(e)) {
    e.forEach(
      (j, _e) => bn(
        j,
        t && (K(t) ? t[_e] : t),
        n,
        r,
        o
      )
    );
    return;
  }
  if (En(r) && !o) {
    r.shapeFlag & 512 && r.type.__asyncResolved && r.component.subTree.component && bn(e, t, n, r.component.subTree);
    return;
  }
  const s = r.shapeFlag & 4 ? _o(r.component) : r.el, i = o ? null : s, { i: c, r: u } = e;
  if (process.env.NODE_ENV !== "production" && !c) {
    R(
      "Missing ref owner context. ref cannot be used on hoisted vnodes. A vnode with ref must be created inside the render function."
    );
    return;
  }
  const m = t && t.r, h = c.refs === me ? c.refs = {} : c.refs, p = c.setupState, E = re(p), A = p === me ? gs : (j) => process.env.NODE_ENV !== "production" && (le(E, j) && !Le(E[j]) && R(
    `Template ref "${j}" used on a non-ref value. It will not work in the production build.`
  ), To.has(E[j])) ? !1 : le(E, j), H = (j) => process.env.NODE_ENV === "production" || !To.has(j);
  if (m != null && m !== u) {
    if (Vo(t), Se(m))
      h[m] = null, A(m) && (p[m] = null);
    else if (Le(m)) {
      H(m) && (m.value = null);
      const j = t;
      j.k && (h[j.k] = null);
    }
  }
  if (q(u))
    ln(u, c, 12, [i, h]);
  else {
    const j = Se(u), _e = Le(u);
    if (j || _e) {
      const ne = () => {
        if (e.f) {
          const Z = j ? A(u) ? p[u] : h[u] : H(u) || !e.k ? u.value : h[e.k];
          if (o)
            K(Z) && Qr(Z, s);
          else if (K(Z))
            Z.includes(s) || Z.push(s);
          else if (j)
            h[u] = [s], A(u) && (p[u] = h[u]);
          else {
            const Q = [s];
            H(u) && (u.value = Q), e.k && (h[e.k] = Q);
          }
        } else j ? (h[u] = i, A(u) && (p[u] = i)) : _e ? (H(u) && (u.value = i), e.k && (h[e.k] = i)) : process.env.NODE_ENV !== "production" && R("Invalid template ref type:", u, `(${typeof u})`);
      };
      if (i) {
        const Z = () => {
          ne(), or.delete(e);
        };
        Z.id = -1, or.set(e, Z), Ke(Z, n);
      } else
        Vo(e), ne();
    } else process.env.NODE_ENV !== "production" && R("Invalid template ref type:", u, `(${typeof u})`);
  }
}
function Vo(e) {
  const t = or.get(e);
  t && (t.flags |= 8, or.delete(e));
}
Vn().requestIdleCallback;
Vn().cancelIdleCallback;
const En = (e) => !!e.type.__asyncLoader, In = (e) => e.type.__isKeepAlive;
function tl(e, t) {
  si(e, "a", t);
}
function nl(e, t) {
  si(e, "da", t);
}
function si(e, t, n = Fe) {
  const r = e.__wdc || (e.__wdc = () => {
    let o = n;
    for (; o; ) {
      if (o.isDeactivated)
        return;
      o = o.parent;
    }
    return e();
  });
  if (_r(t, r, n), n) {
    let o = n.parent;
    for (; o && o.parent; )
      In(o.parent.vnode) && rl(r, t, n, o), o = o.parent;
  }
}
function rl(e, t, n, r) {
  const o = _r(
    t,
    e,
    r,
    !0
    /* prepend */
  );
  li(() => {
    Qr(r[t], o);
  }, n);
}
function _r(e, t, n = Fe, r = !1) {
  if (n) {
    const o = n[e] || (n[e] = []), s = t.__weh || (t.__weh = (...i) => {
      ct();
      const c = Ln(n), u = at(t, n, e, i);
      return c(), lt(), u;
    });
    return r ? o.unshift(s) : o.push(s), s;
  } else if (process.env.NODE_ENV !== "production") {
    const o = jt(co[e].replace(/ hook$/, ""));
    R(
      `${o} is called when there is no active component instance to be associated with. Lifecycle injection APIs can only be used during execution of setup(). If you are using async setup(), make sure to register lifecycle hooks before the first await statement.`
    );
  }
}
const Ot = (e) => (t, n = Fe) => {
  (!Sn || e === "sp") && _r(e, (...r) => t(...r), n);
}, ol = Ot("bm"), ii = Ot("m"), sl = Ot(
  "bu"
), il = Ot("u"), ci = Ot(
  "bum"
), li = Ot("um"), cl = Ot(
  "sp"
), ll = Ot("rtg"), al = Ot("rtc");
function fl(e, t = Fe) {
  _r("ec", e, t);
}
const ul = Symbol.for("v-ndc"), Br = (e) => e ? Ai(e) ? _o(e) : Br(e.parent) : null, Kt = (
  // Move PURE marker to new line to workaround compiler discarding it
  // due to type annotation
  /* @__PURE__ */ Ve(/* @__PURE__ */ Object.create(null), {
    $: (e) => e,
    $el: (e) => e.vnode.el,
    $data: (e) => e.data,
    $props: (e) => process.env.NODE_ENV !== "production" ? ht(e.props) : e.props,
    $attrs: (e) => process.env.NODE_ENV !== "production" ? ht(e.attrs) : e.attrs,
    $slots: (e) => process.env.NODE_ENV !== "production" ? ht(e.slots) : e.slots,
    $refs: (e) => process.env.NODE_ENV !== "production" ? ht(e.refs) : e.refs,
    $parent: (e) => Br(e.parent),
    $root: (e) => Br(e.root),
    $host: (e) => e.ce,
    $emit: (e) => e.emit,
    $options: (e) => ui(e),
    $forceUpdate: (e) => e.f || (e.f = () => {
      mr(e.update);
    }),
    $nextTick: (e) => e.n || (e.n = Pc.bind(e.proxy)),
    $watch: (e) => Wl.bind(e)
  })
), uo = (e) => e === "_" || e === "$", Dr = (e, t) => e !== me && !e.__isScriptSetup && le(e, t), ai = {
  get({ _: e }, t) {
    if (t === "__v_skip")
      return !0;
    const { ctx: n, setupState: r, data: o, props: s, accessCache: i, type: c, appContext: u } = e;
    if (process.env.NODE_ENV !== "production" && t === "__isVue")
      return !0;
    let m;
    if (t[0] !== "$") {
      const A = i[t];
      if (A !== void 0)
        switch (A) {
          case 1:
            return r[t];
          case 2:
            return o[t];
          case 4:
            return n[t];
          case 3:
            return s[t];
        }
      else {
        if (Dr(r, t))
          return i[t] = 1, r[t];
        if (o !== me && le(o, t))
          return i[t] = 2, o[t];
        if (
          // only cache other properties when instance has declared (thus stable)
          // props
          (m = e.propsOptions[0]) && le(m, t)
        )
          return i[t] = 3, s[t];
        if (n !== me && le(n, t))
          return i[t] = 4, n[t];
        Wr && (i[t] = 0);
      }
    }
    const h = Kt[t];
    let p, E;
    if (h)
      return t === "$attrs" ? (Ie(e.attrs, "get", ""), process.env.NODE_ENV !== "production" && cr()) : process.env.NODE_ENV !== "production" && t === "$slots" && Ie(e, "get", t), h(e);
    if (
      // css module (injected by vue-loader)
      (p = c.__cssModules) && (p = p[t])
    )
      return p;
    if (n !== me && le(n, t))
      return i[t] = 4, n[t];
    if (
      // global properties
      E = u.config.globalProperties, le(E, t)
    )
      return E[t];
    process.env.NODE_ENV !== "production" && Je && (!Se(t) || // #1091 avoid internal isRef/isVNode checks on component instance leading
    // to infinite warning loop
    t.indexOf("__v") !== 0) && (o !== me && uo(t[0]) && le(o, t) ? R(
      `Property ${JSON.stringify(
        t
      )} must be accessed via $data because it starts with a reserved character ("$" or "_") and is not proxied on the render context.`
    ) : e === Je && R(
      `Property ${JSON.stringify(t)} was accessed during render but is not defined on instance.`
    ));
  },
  set({ _: e }, t, n) {
    const { data: r, setupState: o, ctx: s } = e;
    return Dr(o, t) ? (o[t] = n, !0) : process.env.NODE_ENV !== "production" && o.__isScriptSetup && le(o, t) ? (R(`Cannot mutate <script setup> binding "${t}" from Options API.`), !1) : r !== me && le(r, t) ? (r[t] = n, !0) : le(e.props, t) ? (process.env.NODE_ENV !== "production" && R(`Attempting to mutate prop "${t}". Props are readonly.`), !1) : t[0] === "$" && t.slice(1) in e ? (process.env.NODE_ENV !== "production" && R(
      `Attempting to mutate public property "${t}". Properties starting with $ are reserved and readonly.`
    ), !1) : (process.env.NODE_ENV !== "production" && t in e.appContext.config.globalProperties ? Object.defineProperty(s, t, {
      enumerable: !0,
      configurable: !0,
      value: n
    }) : s[t] = n, !0);
  },
  has({
    _: { data: e, setupState: t, accessCache: n, ctx: r, appContext: o, propsOptions: s, type: i }
  }, c) {
    let u, m;
    return !!(n[c] || e !== me && c[0] !== "$" && le(e, c) || Dr(t, c) || (u = s[0]) && le(u, c) || le(r, c) || le(Kt, c) || le(o.config.globalProperties, c) || (m = i.__cssModules) && m[c]);
  },
  defineProperty(e, t, n) {
    return n.get != null ? e._.accessCache[t] = 0 : le(n, "value") && this.set(e, t, n.value, null), Reflect.defineProperty(e, t, n);
  }
};
process.env.NODE_ENV !== "production" && (ai.ownKeys = (e) => (R(
  "Avoid app logic that relies on enumerating keys on a component instance. The keys will be empty in production mode to avoid performance overhead."
), Reflect.ownKeys(e)));
function dl(e) {
  const t = {};
  return Object.defineProperty(t, "_", {
    configurable: !0,
    enumerable: !1,
    get: () => e
  }), Object.keys(Kt).forEach((n) => {
    Object.defineProperty(t, n, {
      configurable: !0,
      enumerable: !1,
      get: () => Kt[n](e),
      // intercepted by the proxy so no need for implementation,
      // but needed to prevent set errors
      set: Re
    });
  }), t;
}
function pl(e) {
  const {
    ctx: t,
    propsOptions: [n]
  } = e;
  n && Object.keys(n).forEach((r) => {
    Object.defineProperty(t, r, {
      enumerable: !0,
      configurable: !0,
      get: () => e.props[r],
      set: Re
    });
  });
}
function hl(e) {
  const { ctx: t, setupState: n } = e;
  Object.keys(re(n)).forEach((r) => {
    if (!n.__isScriptSetup) {
      if (uo(r[0])) {
        R(
          `setup() return property ${JSON.stringify(
            r
          )} should not start with "$" or "_" which are reserved prefixes for Vue internals.`
        );
        return;
      }
      Object.defineProperty(t, r, {
        enumerable: !0,
        configurable: !0,
        get: () => n[r],
        set: Re
      });
    }
  });
}
function Ao(e) {
  return K(e) ? e.reduce(
    (t, n) => (t[n] = null, t),
    {}
  ) : e;
}
function gl() {
  const e = /* @__PURE__ */ Object.create(null);
  return (t, n) => {
    e[n] ? R(`${t} property "${n}" is already defined in ${e[n]}.`) : e[n] = t;
  };
}
let Wr = !0;
function vl(e) {
  const t = ui(e), n = e.proxy, r = e.ctx;
  Wr = !1, t.beforeCreate && Mo(t.beforeCreate, e, "bc");
  const {
    // state
    data: o,
    computed: s,
    methods: i,
    watch: c,
    provide: u,
    inject: m,
    // lifecycle
    created: h,
    beforeMount: p,
    mounted: E,
    beforeUpdate: A,
    updated: H,
    activated: j,
    deactivated: _e,
    beforeDestroy: ne,
    beforeUnmount: Z,
    destroyed: Q,
    unmounted: Oe,
    render: B,
    renderTracked: ce,
    renderTriggered: De,
    errorCaptured: we,
    serverPrefetch: Y,
    // public API
    expose: ae,
    inheritAttrs: ue,
    // assets
    components: $,
    directives: be,
    filters: X
  } = t, ke = process.env.NODE_ENV !== "production" ? gl() : null;
  if (process.env.NODE_ENV !== "production") {
    const [oe] = e.propsOptions;
    if (oe)
      for (const se in oe)
        ke("Props", se);
  }
  if (m && ml(m, r, ke), i)
    for (const oe in i) {
      const se = i[oe];
      q(se) ? (process.env.NODE_ENV !== "production" ? Object.defineProperty(r, oe, {
        value: se.bind(n),
        configurable: !0,
        enumerable: !0,
        writable: !0
      }) : r[oe] = se.bind(n), process.env.NODE_ENV !== "production" && ke("Methods", oe)) : process.env.NODE_ENV !== "production" && R(
        `Method "${oe}" has type "${typeof se}" in the component definition. Did you reference the function correctly?`
      );
    }
  if (o) {
    process.env.NODE_ENV !== "production" && !q(o) && R(
      "The data option must be a function. Plain object usage is no longer supported."
    );
    const oe = o.call(n, n);
    if (process.env.NODE_ENV !== "production" && Zr(oe) && R(
      "data() returned a Promise - note data() cannot be async; If you intend to perform data fetching before component renders, use async setup() + <Suspense>."
    ), !he(oe))
      process.env.NODE_ENV !== "production" && R("data() should return an object.");
    else if (e.data = io(oe), process.env.NODE_ENV !== "production")
      for (const se in oe)
        ke("Data", se), uo(se[0]) || Object.defineProperty(r, se, {
          configurable: !0,
          enumerable: !0,
          get: () => oe[se],
          set: Re
        });
  }
  if (Wr = !0, s)
    for (const oe in s) {
      const se = s[oe], Te = q(se) ? se.bind(n, n) : q(se.get) ? se.get.bind(n, n) : Re;
      process.env.NODE_ENV !== "production" && Te === Re && R(`Computed property "${oe}" has no getter.`);
      const mt = !q(se) && q(se.set) ? se.set.bind(n) : process.env.NODE_ENV !== "production" ? () => {
        R(
          `Write operation failed: computed property "${oe}" is readonly.`
        );
      } : Re, je = va({
        get: Te,
        set: mt
      });
      Object.defineProperty(r, oe, {
        enumerable: !0,
        configurable: !0,
        get: () => je.value,
        set: (Ge) => je.value = Ge
      }), process.env.NODE_ENV !== "production" && ke("Computed", oe);
    }
  if (c)
    for (const oe in c)
      fi(c[oe], r, n, oe);
  if (u) {
    const oe = q(u) ? u.call(n) : u;
    Reflect.ownKeys(oe).forEach((se) => {
      xl(se, oe[se]);
    });
  }
  h && Mo(h, e, "c");
  function Me(oe, se) {
    K(se) ? se.forEach((Te) => oe(Te.bind(n))) : se && oe(se.bind(n));
  }
  if (Me(ol, p), Me(ii, E), Me(sl, A), Me(il, H), Me(tl, j), Me(nl, _e), Me(fl, we), Me(al, ce), Me(ll, De), Me(ci, Z), Me(li, Oe), Me(cl, Y), K(ae))
    if (ae.length) {
      const oe = e.exposed || (e.exposed = {});
      ae.forEach((se) => {
        Object.defineProperty(oe, se, {
          get: () => n[se],
          set: (Te) => n[se] = Te,
          enumerable: !0
        });
      });
    } else e.exposed || (e.exposed = {});
  B && e.render === Re && (e.render = B), ue != null && (e.inheritAttrs = ue), $ && (e.components = $), be && (e.directives = be), Y && oi(e);
}
function ml(e, t, n = Re) {
  K(e) && (e = zr(e));
  for (const r in e) {
    const o = e[r];
    let s;
    he(o) ? "default" in o ? s = Gn(
      o.from || r,
      o.default,
      !0
    ) : s = Gn(o.from || r) : s = Gn(o), Le(s) ? Object.defineProperty(t, r, {
      enumerable: !0,
      configurable: !0,
      get: () => s.value,
      set: (i) => s.value = i
    }) : t[r] = s, process.env.NODE_ENV !== "production" && n("Inject", r);
  }
}
function Mo(e, t, n) {
  at(
    K(e) ? e.map((r) => r.bind(t.proxy)) : e.bind(t.proxy),
    t,
    n
  );
}
function fi(e, t, n, r) {
  let o = r.includes(".") ? xi(n, r) : () => n[r];
  if (Se(e)) {
    const s = t[e];
    q(s) ? Vr(o, s) : process.env.NODE_ENV !== "production" && R(`Invalid watch handler specified by key "${e}"`, s);
  } else if (q(e))
    Vr(o, e.bind(n));
  else if (he(e))
    if (K(e))
      e.forEach((s) => fi(s, t, n, r));
    else {
      const s = q(e.handler) ? e.handler.bind(n) : t[e.handler];
      q(s) ? Vr(o, s, e) : process.env.NODE_ENV !== "production" && R(`Invalid watch handler specified by key "${e.handler}"`, s);
    }
  else process.env.NODE_ENV !== "production" && R(`Invalid watch option: "${r}"`, e);
}
function ui(e) {
  const t = e.type, { mixins: n, extends: r } = t, {
    mixins: o,
    optionsCache: s,
    config: { optionMergeStrategies: i }
  } = e.appContext, c = s.get(t);
  let u;
  return c ? u = c : !o.length && !n && !r ? u = t : (u = {}, o.length && o.forEach(
    (m) => sr(u, m, i, !0)
  ), sr(u, t, i)), he(t) && s.set(t, u), u;
}
function sr(e, t, n, r = !1) {
  const { mixins: o, extends: s } = t;
  s && sr(e, s, n, !0), o && o.forEach(
    (i) => sr(e, i, n, !0)
  );
  for (const i in t)
    if (r && i === "expose")
      process.env.NODE_ENV !== "production" && R(
        '"expose" option is ignored when declared in mixins or extends. It should only be declared in the base component itself.'
      );
    else {
      const c = _l[i] || n && n[i];
      e[i] = c ? c(e[i], t[i]) : t[i];
    }
  return e;
}
const _l = {
  data: Io,
  props: Ro,
  emits: Ro,
  // objects
  methods: gn,
  computed: gn,
  // lifecycle
  beforeCreate: Ue,
  created: Ue,
  beforeMount: Ue,
  mounted: Ue,
  beforeUpdate: Ue,
  updated: Ue,
  beforeDestroy: Ue,
  beforeUnmount: Ue,
  destroyed: Ue,
  unmounted: Ue,
  activated: Ue,
  deactivated: Ue,
  errorCaptured: Ue,
  serverPrefetch: Ue,
  // assets
  components: gn,
  directives: gn,
  // watch
  watch: El,
  // provide / inject
  provide: Io,
  inject: bl
};
function Io(e, t) {
  return t ? e ? function() {
    return Ve(
      q(e) ? e.call(this, this) : e,
      q(t) ? t.call(this, this) : t
    );
  } : t : e;
}
function bl(e, t) {
  return gn(zr(e), zr(t));
}
function zr(e) {
  if (K(e)) {
    const t = {};
    for (let n = 0; n < e.length; n++)
      t[e[n]] = e[n];
    return t;
  }
  return e;
}
function Ue(e, t) {
  return e ? [...new Set([].concat(e, t))] : t;
}
function gn(e, t) {
  return e ? Ve(/* @__PURE__ */ Object.create(null), e, t) : t;
}
function Ro(e, t) {
  return e ? K(e) && K(t) ? [.../* @__PURE__ */ new Set([...e, ...t])] : Ve(
    /* @__PURE__ */ Object.create(null),
    Ao(e),
    Ao(t ?? {})
  ) : t;
}
function El(e, t) {
  if (!e) return t;
  if (!t) return e;
  const n = Ve(/* @__PURE__ */ Object.create(null), e);
  for (const r in t)
    n[r] = Ue(e[r], t[r]);
  return n;
}
function di() {
  return {
    app: null,
    config: {
      isNativeTag: gs,
      performance: !1,
      globalProperties: {},
      optionMergeStrategies: {},
      errorHandler: void 0,
      warnHandler: void 0,
      compilerOptions: {}
    },
    mixins: [],
    components: {},
    directives: {},
    provides: /* @__PURE__ */ Object.create(null),
    optionsCache: /* @__PURE__ */ new WeakMap(),
    propsCache: /* @__PURE__ */ new WeakMap(),
    emitsCache: /* @__PURE__ */ new WeakMap()
  };
}
let yl = 0;
function Nl(e, t) {
  return function(r, o = null) {
    q(r) || (r = Ve({}, r)), o != null && !he(o) && (process.env.NODE_ENV !== "production" && R("root props passed to app.mount() must be an object."), o = null);
    const s = di(), i = /* @__PURE__ */ new WeakSet(), c = [];
    let u = !1;
    const m = s.app = {
      _uid: yl++,
      _component: r,
      _props: o,
      _container: null,
      _context: s,
      _instance: null,
      version: zo,
      get config() {
        return s.config;
      },
      set config(h) {
        process.env.NODE_ENV !== "production" && R(
          "app.config cannot be replaced. Modify individual options instead."
        );
      },
      use(h, ...p) {
        return i.has(h) ? process.env.NODE_ENV !== "production" && R("Plugin has already been applied to target app.") : h && q(h.install) ? (i.add(h), h.install(m, ...p)) : q(h) ? (i.add(h), h(m, ...p)) : process.env.NODE_ENV !== "production" && R(
          'A plugin must either be a function or an object with an "install" function.'
        ), m;
      },
      mixin(h) {
        return s.mixins.includes(h) ? process.env.NODE_ENV !== "production" && R(
          "Mixin has already been applied to target app" + (h.name ? `: ${h.name}` : "")
        ) : s.mixins.push(h), m;
      },
      component(h, p) {
        return process.env.NODE_ENV !== "production" && qr(h, s.config), p ? (process.env.NODE_ENV !== "production" && s.components[h] && R(`Component "${h}" has already been registered in target app.`), s.components[h] = p, m) : s.components[h];
      },
      directive(h, p) {
        return process.env.NODE_ENV !== "production" && Xs(h), p ? (process.env.NODE_ENV !== "production" && s.directives[h] && R(`Directive "${h}" has already been registered in target app.`), s.directives[h] = p, m) : s.directives[h];
      },
      mount(h, p, E) {
        if (u)
          process.env.NODE_ENV !== "production" && R(
            "App has already been mounted.\nIf you want to remount the same app, move your app creation logic into a factory function and create fresh app instances for each mount - e.g. `const createMyApp = () => createApp(App)`"
          );
        else {
          process.env.NODE_ENV !== "production" && h.__vue_app__ && R(
            "There is already an app instance mounted on the host container.\n If you want to mount another app on the same host container, you need to unmount the previous app by calling `app.unmount()` first."
          );
          const A = m._ceVNode || ze(r, o);
          return A.appContext = s, E === !0 ? E = "svg" : E === !1 && (E = void 0), process.env.NODE_ENV !== "production" && (s.reload = () => {
            const H = vt(A);
            H.el = null, e(H, h, E);
          }), e(A, h, E), u = !0, m._container = h, h.__vue_app__ = m, process.env.NODE_ENV !== "production" && (m._instance = A.component, Bc(m, zo)), _o(A.component);
        }
      },
      onUnmount(h) {
        process.env.NODE_ENV !== "production" && typeof h != "function" && R(
          `Expected function as first argument to app.onUnmount(), but got ${typeof h}`
        ), c.push(h);
      },
      unmount() {
        u ? (at(
          c,
          m._instance,
          16
        ), e(null, m._container), process.env.NODE_ENV !== "production" && (m._instance = null, Wc(m)), delete m._container.__vue_app__) : process.env.NODE_ENV !== "production" && R("Cannot unmount an app that is not mounted.");
      },
      provide(h, p) {
        return process.env.NODE_ENV !== "production" && h in s.provides && (le(s.provides, h) ? R(
          `App already provides property with key "${String(h)}". It will be overwritten with the new value.`
        ) : R(
          `App already provides property with key "${String(h)}" inherited from its parent element. It will be overwritten with the new value.`
        )), s.provides[h] = p, m;
      },
      runWithContext(h) {
        const p = on;
        on = m;
        try {
          return h();
        } finally {
          on = p;
        }
      }
    };
    return m;
  };
}
let on = null;
function xl(e, t) {
  if (!Fe)
    process.env.NODE_ENV !== "production" && R("provide() can only be used inside setup().");
  else {
    let n = Fe.provides;
    const r = Fe.parent && Fe.parent.provides;
    r === n && (n = Fe.provides = Object.create(r)), n[e] = t;
  }
}
function Gn(e, t, n = !1) {
  const r = mo();
  if (r || on) {
    let o = on ? on._context.provides : r ? r.parent == null || r.ce ? r.vnode.appContext && r.vnode.appContext.provides : r.parent.provides : void 0;
    if (o && e in o)
      return o[e];
    if (arguments.length > 1)
      return n && q(t) ? t.call(r && r.proxy) : t;
    process.env.NODE_ENV !== "production" && R(`injection "${String(e)}" not found.`);
  } else process.env.NODE_ENV !== "production" && R("inject() can only be used inside setup() or functional components.");
}
const pi = {}, hi = () => Object.create(pi), gi = (e) => Object.getPrototypeOf(e) === pi;
function wl(e, t, n, r = !1) {
  const o = {}, s = hi();
  e.propsDefaults = /* @__PURE__ */ Object.create(null), vi(e, t, o, s);
  for (const i in e.propsOptions[0])
    i in o || (o[i] = void 0);
  process.env.NODE_ENV !== "production" && _i(t || {}, o, e), n ? e.props = r ? o : Nc(o) : e.type.props ? e.props = o : e.props = s, e.attrs = s;
}
function Ol(e) {
  for (; e; ) {
    if (e.type.__hmrId) return !0;
    e = e.parent;
  }
}
function Cl(e, t, n, r) {
  const {
    props: o,
    attrs: s,
    vnode: { patchFlag: i }
  } = e, c = re(o), [u] = e.propsOptions;
  let m = !1;
  if (
    // always force full diff in dev
    // - #1942 if hmr is enabled with sfc component
    // - vite#872 non-sfc component used by sfc component
    !(process.env.NODE_ENV !== "production" && Ol(e)) && (r || i > 0) && !(i & 16)
  ) {
    if (i & 8) {
      const h = e.vnode.dynamicProps;
      for (let p = 0; p < h.length; p++) {
        let E = h[p];
        if (br(e.emitsOptions, E))
          continue;
        const A = t[E];
        if (u)
          if (le(s, E))
            A !== s[E] && (s[E] = A, m = !0);
          else {
            const H = ot(E);
            o[H] = Gr(
              u,
              c,
              H,
              A,
              e,
              !1
            );
          }
        else
          A !== s[E] && (s[E] = A, m = !0);
      }
    }
  } else {
    vi(e, t, o, s) && (m = !0);
    let h;
    for (const p in c)
      (!t || // for camelCase
      !le(t, p) && // it's possible the original props was passed in as kebab-case
      // and converted to camelCase (#955)
      ((h = Mt(p)) === p || !le(t, h))) && (u ? n && // for camelCase
      (n[p] !== void 0 || // for kebab-case
      n[h] !== void 0) && (o[p] = Gr(
        u,
        c,
        p,
        void 0,
        e,
        !0
      )) : delete o[p]);
    if (s !== c)
      for (const p in s)
        (!t || !le(t, p)) && (delete s[p], m = !0);
  }
  m && pt(e.attrs, "set", ""), process.env.NODE_ENV !== "production" && _i(t || {}, o, e);
}
function vi(e, t, n, r) {
  const [o, s] = e.propsOptions;
  let i = !1, c;
  if (t)
    for (let u in t) {
      if (vn(u))
        continue;
      const m = t[u];
      let h;
      o && le(o, h = ot(u)) ? !s || !s.includes(h) ? n[h] = m : (c || (c = {}))[h] = m : br(e.emitsOptions, u) || (!(u in r) || m !== r[u]) && (r[u] = m, i = !0);
    }
  if (s) {
    const u = re(n), m = c || me;
    for (let h = 0; h < s.length; h++) {
      const p = s[h];
      n[p] = Gr(
        o,
        u,
        p,
        m[p],
        e,
        !le(m, p)
      );
    }
  }
  return i;
}
function Gr(e, t, n, r, o, s) {
  const i = e[n];
  if (i != null) {
    const c = le(i, "default");
    if (c && r === void 0) {
      const u = i.default;
      if (i.type !== Function && !i.skipFactory && q(u)) {
        const { propsDefaults: m } = o;
        if (n in m)
          r = m[n];
        else {
          const h = Ln(o);
          r = m[n] = u.call(
            null,
            t
          ), h();
        }
      } else
        r = u;
      o.ce && o.ce._setProp(n, r);
    }
    i[
      0
      /* shouldCast */
    ] && (s && !c ? r = !1 : i[
      1
      /* shouldCastTrue */
    ] && (r === "" || r === Mt(n)) && (r = !0));
  }
  return r;
}
const Sl = /* @__PURE__ */ new WeakMap();
function mi(e, t, n = !1) {
  const r = n ? Sl : t.propsCache, o = r.get(e);
  if (o)
    return o;
  const s = e.props, i = {}, c = [];
  let u = !1;
  if (!q(e)) {
    const h = (p) => {
      u = !0;
      const [E, A] = mi(p, t, !0);
      Ve(i, E), A && c.push(...A);
    };
    !n && t.mixins.length && t.mixins.forEach(h), e.extends && h(e.extends), e.mixins && e.mixins.forEach(h);
  }
  if (!s && !u)
    return he(e) && r.set(e, tn), tn;
  if (K(s))
    for (let h = 0; h < s.length; h++) {
      process.env.NODE_ENV !== "production" && !Se(s[h]) && R("props must be strings when using array syntax.", s[h]);
      const p = ot(s[h]);
      Lo(p) && (i[p] = me);
    }
  else if (s) {
    process.env.NODE_ENV !== "production" && !he(s) && R("invalid props options", s);
    for (const h in s) {
      const p = ot(h);
      if (Lo(p)) {
        const E = s[h], A = i[p] = K(E) || q(E) ? { type: E } : Ve({}, E), H = A.type;
        let j = !1, _e = !0;
        if (K(H))
          for (let ne = 0; ne < H.length; ++ne) {
            const Z = H[ne], Q = q(Z) && Z.name;
            if (Q === "Boolean") {
              j = !0;
              break;
            } else Q === "String" && (_e = !1);
          }
        else
          j = q(H) && H.name === "Boolean";
        A[
          0
          /* shouldCast */
        ] = j, A[
          1
          /* shouldCastTrue */
        ] = _e, (j || le(A, "default")) && c.push(p);
      }
    }
  }
  const m = [i, c];
  return he(e) && r.set(e, m), m;
}
function Lo(e) {
  return e[0] !== "$" && !vn(e) ? !0 : (process.env.NODE_ENV !== "production" && R(`Invalid prop name: "${e}" is a reserved property.`), !1);
}
function Dl(e) {
  return e === null ? "null" : typeof e == "function" ? e.name || "" : typeof e == "object" && e.constructor && e.constructor.name || "";
}
function _i(e, t, n) {
  const r = re(t), o = n.propsOptions[0], s = Object.keys(e).map((i) => ot(i));
  for (const i in o) {
    let c = o[i];
    c != null && Tl(
      i,
      r[i],
      c,
      process.env.NODE_ENV !== "production" ? ht(r) : r,
      !s.includes(i)
    );
  }
}
function Tl(e, t, n, r, o) {
  const { type: s, required: i, validator: c, skipCheck: u } = n;
  if (i && o) {
    R('Missing required prop: "' + e + '"');
    return;
  }
  if (!(t == null && !i)) {
    if (s != null && s !== !0 && !u) {
      let m = !1;
      const h = K(s) ? s : [s], p = [];
      for (let E = 0; E < h.length && !m; E++) {
        const { valid: A, expectedType: H } = Al(t, h[E]);
        p.push(H || ""), m = A;
      }
      if (!m) {
        R(Ml(e, t, p));
        return;
      }
    }
    c && !c(t, r) && R('Invalid prop: custom validator check failed for prop "' + e + '".');
  }
}
const Vl = /* @__PURE__ */ wt(
  "String,Number,Boolean,Function,Symbol,BigInt"
);
function Al(e, t) {
  let n;
  const r = Dl(t);
  if (r === "null")
    n = e === null;
  else if (Vl(r)) {
    const o = typeof e;
    n = o === r.toLowerCase(), !n && o === "object" && (n = e instanceof t);
  } else r === "Object" ? n = he(e) : r === "Array" ? n = K(e) : n = e instanceof t;
  return {
    valid: n,
    expectedType: r
  };
}
function Ml(e, t, n) {
  if (n.length === 0)
    return `Prop type [] for prop "${e}" won't match anything. Did you mean to use type Array instead?`;
  let r = `Invalid prop: type check failed for prop "${e}". Expected ${n.map(dr).join(" | ")}`;
  const o = n[0], s = eo(t), i = ko(t, o), c = ko(t, s);
  return n.length === 1 && Po(o) && !Il(o, s) && (r += ` with value ${i}`), r += `, got ${s} `, Po(s) && (r += `with value ${c}.`), r;
}
function ko(e, t) {
  return t === "String" ? `"${e}"` : t === "Number" ? `${Number(e)}` : `${e}`;
}
function Po(e) {
  return ["string", "number", "boolean"].some((n) => e.toLowerCase() === n);
}
function Il(...e) {
  return e.some((t) => t.toLowerCase() === "boolean");
}
const po = (e) => e === "_" || e === "_ctx" || e === "$stable", ho = (e) => K(e) ? e.map(nt) : [nt(e)], Rl = (e, t, n) => {
  if (t._n)
    return t;
  const r = qs((...o) => (process.env.NODE_ENV !== "production" && Fe && !(n === null && Je) && !(n && n.root !== Fe.root) && R(
    `Slot "${e}" invoked outside of the render function: this will not track dependencies used in the slot. Invoke the slot function inside the render function instead.`
  ), ho(t(...o))), n);
  return r._c = !1, r;
}, bi = (e, t, n) => {
  const r = e._ctx;
  for (const o in e) {
    if (po(o)) continue;
    const s = e[o];
    if (q(s))
      t[o] = Rl(o, s, r);
    else if (s != null) {
      process.env.NODE_ENV !== "production" && R(
        `Non-function value encountered for slot "${o}". Prefer function slots for better performance.`
      );
      const i = ho(s);
      t[o] = () => i;
    }
  }
}, Ei = (e, t) => {
  process.env.NODE_ENV !== "production" && !In(e.vnode) && R(
    "Non-function value encountered for default slot. Prefer function slots for better performance."
  );
  const n = ho(t);
  e.slots.default = () => n;
}, Kr = (e, t, n) => {
  for (const r in t)
    (n || !po(r)) && (e[r] = t[r]);
}, Ll = (e, t, n) => {
  const r = e.slots = hi();
  if (e.vnode.shapeFlag & 32) {
    const o = t._;
    o ? (Kr(r, t, n), n && Qn(r, "_", o, !0)) : bi(t, r);
  } else t && Ei(e, t);
}, kl = (e, t, n) => {
  const { vnode: r, slots: o } = e;
  let s = !0, i = me;
  if (r.shapeFlag & 32) {
    const c = t._;
    c ? process.env.NODE_ENV !== "production" && gt ? (Kr(o, t, n), pt(e, "set", "$slots")) : n && c === 1 ? s = !1 : Kr(o, t, n) : (s = !t.$stable, bi(t, o)), i = t;
  } else t && (Ei(e, t), i = { default: 1 });
  if (s)
    for (const c in o)
      !po(c) && i[c] == null && delete o[c];
};
let un, Nt;
function Qt(e, t) {
  e.appContext.config.performance && ir() && Nt.mark(`vue-${t}-${e.uid}`), process.env.NODE_ENV !== "production" && Yc(e, t, ir() ? Nt.now() : Date.now());
}
function Zt(e, t) {
  if (e.appContext.config.performance && ir()) {
    const n = `vue-${t}-${e.uid}`, r = n + ":end", o = `<${Er(e, e.type)}> ${t}`;
    Nt.mark(r), Nt.measure(o, n, r), Nt.clearMeasures(o), Nt.clearMarks(n), Nt.clearMarks(r);
  }
  process.env.NODE_ENV !== "production" && Jc(e, t, ir() ? Nt.now() : Date.now());
}
function ir() {
  return un !== void 0 || (typeof window < "u" && window.performance ? (un = !0, Nt = window.performance) : un = !1), un;
}
function Pl() {
  const e = [];
  if (process.env.NODE_ENV !== "production" && e.length) {
    const t = e.length > 1;
    console.warn(
      `Feature flag${t ? "s" : ""} ${e.join(", ")} ${t ? "are" : "is"} not explicitly defined. You are running the esm-bundler build of Vue, which expects these compile-time feature flags to be globally injected via the bundler config in order to get better tree-shaking in the production bundle.

For more details, see https://link.vuejs.org/feature-flags.`
    );
  }
}
const Ke = Ql;
function $l(e) {
  return Fl(e);
}
function Fl(e, t) {
  Pl();
  const n = Vn();
  n.__VUE__ = !0, process.env.NODE_ENV !== "production" && ao(n.__VUE_DEVTOOLS_GLOBAL_HOOK__, n);
  const {
    insert: r,
    remove: o,
    patchProp: s,
    createElement: i,
    createText: c,
    createComment: u,
    setText: m,
    setElementText: h,
    parentNode: p,
    nextSibling: E,
    setScopeId: A = Re,
    insertStaticContent: H
  } = e, j = (l, a, v, x = null, w = null, b = null, S = void 0, y = null, D = process.env.NODE_ENV !== "production" && gt ? !1 : !!a.dynamicChildren) => {
    if (l === a)
      return;
    l && !Ht(l, a) && (x = f(l), Ne(l, w, b, !0), l = null), a.patchFlag === -2 && (D = !1, a.dynamicChildren = null);
    const { type: O, ref: M, shapeFlag: N } = a;
    switch (O) {
      case Rn:
        _e(l, a, v, x);
        break;
      case Ae:
        ne(l, a, v, x);
        break;
      case Yn:
        l == null ? Z(a, v, x, S) : process.env.NODE_ENV !== "production" && Q(l, a, v, S);
        break;
      case tt:
        be(
          l,
          a,
          v,
          x,
          w,
          b,
          S,
          y,
          D
        );
        break;
      default:
        N & 1 ? ce(
          l,
          a,
          v,
          x,
          w,
          b,
          S,
          y,
          D
        ) : N & 6 ? X(
          l,
          a,
          v,
          x,
          w,
          b,
          S,
          y,
          D
        ) : N & 64 || N & 128 ? O.process(
          l,
          a,
          v,
          x,
          w,
          b,
          S,
          y,
          D,
          V
        ) : process.env.NODE_ENV !== "production" && R("Invalid VNode type:", O, `(${typeof O})`);
    }
    M != null && w ? bn(M, l && l.ref, b, a || l, !a) : M == null && l && l.ref != null && bn(l.ref, null, b, l, !0);
  }, _e = (l, a, v, x) => {
    if (l == null)
      r(
        a.el = c(a.children),
        v,
        x
      );
    else {
      const w = a.el = l.el;
      a.children !== l.children && m(w, a.children);
    }
  }, ne = (l, a, v, x) => {
    l == null ? r(
      a.el = u(a.children || ""),
      v,
      x
    ) : a.el = l.el;
  }, Z = (l, a, v, x) => {
    [l.el, l.anchor] = H(
      l.children,
      a,
      v,
      x,
      l.el,
      l.anchor
    );
  }, Q = (l, a, v, x) => {
    if (a.children !== l.children) {
      const w = E(l.anchor);
      B(l), [a.el, a.anchor] = H(
        a.children,
        v,
        w,
        x
      );
    } else
      a.el = l.el, a.anchor = l.anchor;
  }, Oe = ({ el: l, anchor: a }, v, x) => {
    let w;
    for (; l && l !== a; )
      w = E(l), r(l, v, x), l = w;
    r(a, v, x);
  }, B = ({ el: l, anchor: a }) => {
    let v;
    for (; l && l !== a; )
      v = E(l), o(l), l = v;
    o(a);
  }, ce = (l, a, v, x, w, b, S, y, D) => {
    a.type === "svg" ? S = "svg" : a.type === "math" && (S = "mathml"), l == null ? De(
      a,
      v,
      x,
      w,
      b,
      S,
      y,
      D
    ) : ae(
      l,
      a,
      w,
      b,
      S,
      y,
      D
    );
  }, De = (l, a, v, x, w, b, S, y) => {
    let D, O;
    const { props: M, shapeFlag: N, transition: I, dirs: L } = l;
    if (D = l.el = i(
      l.type,
      b,
      M && M.is,
      M
    ), N & 8 ? h(D, l.children) : N & 16 && Y(
      l.children,
      D,
      null,
      x,
      w,
      Tr(l, b),
      S,
      y
    ), L && kt(l, null, x, "created"), we(D, l, l.scopeId, S, x), M) {
      for (const U in M)
        U !== "value" && !vn(U) && s(D, U, null, M[U], b, x);
      "value" in M && s(D, "value", null, M.value, b), (O = M.onVnodeBeforeMount) && ut(O, x, l);
    }
    process.env.NODE_ENV !== "production" && (Qn(D, "__vnode", l, !0), Qn(D, "__vueParentComponent", x, !0)), L && kt(l, null, x, "beforeMount");
    const W = jl(w, I);
    W && I.beforeEnter(D), r(D, a, v), ((O = M && M.onVnodeMounted) || W || L) && Ke(() => {
      O && ut(O, x, l), W && I.enter(D), L && kt(l, null, x, "mounted");
    }, w);
  }, we = (l, a, v, x, w) => {
    if (v && A(l, v), x)
      for (let b = 0; b < x.length; b++)
        A(l, x[b]);
    if (w) {
      let b = w.subTree;
      if (process.env.NODE_ENV !== "production" && b.patchFlag > 0 && b.patchFlag & 2048 && (b = go(b.children) || b), a === b || Ci(b.type) && (b.ssContent === a || b.ssFallback === a)) {
        const S = w.vnode;
        we(
          l,
          S,
          S.scopeId,
          S.slotScopeIds,
          w.parent
        );
      }
    }
  }, Y = (l, a, v, x, w, b, S, y, D = 0) => {
    for (let O = D; O < l.length; O++) {
      const M = l[O] = y ? Vt(l[O]) : nt(l[O]);
      j(
        null,
        M,
        a,
        v,
        x,
        w,
        b,
        S,
        y
      );
    }
  }, ae = (l, a, v, x, w, b, S) => {
    const y = a.el = l.el;
    process.env.NODE_ENV !== "production" && (y.__vnode = a);
    let { patchFlag: D, dynamicChildren: O, dirs: M } = a;
    D |= l.patchFlag & 16;
    const N = l.props || me, I = a.props || me;
    let L;
    if (v && Pt(v, !1), (L = I.onVnodeBeforeUpdate) && ut(L, v, a, l), M && kt(a, l, v, "beforeUpdate"), v && Pt(v, !0), process.env.NODE_ENV !== "production" && gt && (D = 0, S = !1, O = null), (N.innerHTML && I.innerHTML == null || N.textContent && I.textContent == null) && h(y, ""), O ? (ue(
      l.dynamicChildren,
      O,
      y,
      v,
      x,
      Tr(a, w),
      b
    ), process.env.NODE_ENV !== "production" && Kn(l, a)) : S || Te(
      l,
      a,
      y,
      null,
      v,
      x,
      Tr(a, w),
      b,
      !1
    ), D > 0) {
      if (D & 16)
        $(y, N, I, v, w);
      else if (D & 2 && N.class !== I.class && s(y, "class", null, I.class, w), D & 4 && s(y, "style", N.style, I.style, w), D & 8) {
        const W = a.dynamicProps;
        for (let U = 0; U < W.length; U++) {
          const G = W[U], F = N[G], z = I[G];
          (z !== F || G === "value") && s(y, G, F, z, w, v);
        }
      }
      D & 1 && l.children !== a.children && h(y, a.children);
    } else !S && O == null && $(y, N, I, v, w);
    ((L = I.onVnodeUpdated) || M) && Ke(() => {
      L && ut(L, v, a, l), M && kt(a, l, v, "updated");
    }, x);
  }, ue = (l, a, v, x, w, b, S) => {
    for (let y = 0; y < a.length; y++) {
      const D = l[y], O = a[y], M = (
        // oldVNode may be an errored async setup() component inside Suspense
        // which will not have a mounted element
        D.el && // - In the case of a Fragment, we need to provide the actual parent
        // of the Fragment itself so it can move its children.
        (D.type === tt || // - In the case of different nodes, there is going to be a replacement
        // which also requires the correct parent container
        !Ht(D, O) || // - In the case of a component, it could contain anything.
        D.shapeFlag & 198) ? p(D.el) : (
          // In other cases, the parent container is not actually used so we
          // just pass the block element here to avoid a DOM parentNode call.
          v
        )
      );
      j(
        D,
        O,
        M,
        null,
        x,
        w,
        b,
        S,
        !0
      );
    }
  }, $ = (l, a, v, x, w) => {
    if (a !== v) {
      if (a !== me)
        for (const b in a)
          !vn(b) && !(b in v) && s(
            l,
            b,
            a[b],
            null,
            w,
            x
          );
      for (const b in v) {
        if (vn(b)) continue;
        const S = v[b], y = a[b];
        S !== y && b !== "value" && s(l, b, y, S, w, x);
      }
      "value" in v && s(l, "value", a.value, v.value, w);
    }
  }, be = (l, a, v, x, w, b, S, y, D) => {
    const O = a.el = l ? l.el : c(""), M = a.anchor = l ? l.anchor : c("");
    let { patchFlag: N, dynamicChildren: I, slotScopeIds: L } = a;
    process.env.NODE_ENV !== "production" && // #5523 dev root fragment may inherit directives
    (gt || N & 2048) && (N = 0, D = !1, I = null), L && (y = y ? y.concat(L) : L), l == null ? (r(O, v, x), r(M, v, x), Y(
      // #10007
      // such fragment like `<></>` will be compiled into
      // a fragment which doesn't have a children.
      // In this case fallback to an empty array
      a.children || [],
      v,
      M,
      w,
      b,
      S,
      y,
      D
    )) : N > 0 && N & 64 && I && // #2715 the previous fragment could've been a BAILed one as a result
    // of renderSlot() with no valid children
    l.dynamicChildren ? (ue(
      l.dynamicChildren,
      I,
      v,
      w,
      b,
      S,
      y
    ), process.env.NODE_ENV !== "production" ? Kn(l, a) : (
      // #2080 if the stable fragment has a key, it's a <template v-for> that may
      //  get moved around. Make sure all root level vnodes inherit el.
      // #2134 or if it's a component root, it may also get moved around
      // as the component is being moved.
      (a.key != null || w && a === w.subTree) && Kn(
        l,
        a,
        !0
        /* shallow */
      )
    )) : Te(
      l,
      a,
      v,
      M,
      w,
      b,
      S,
      y,
      D
    );
  }, X = (l, a, v, x, w, b, S, y, D) => {
    a.slotScopeIds = y, l == null ? a.shapeFlag & 512 ? w.ctx.activate(
      a,
      v,
      x,
      S,
      D
    ) : ke(
      a,
      v,
      x,
      w,
      b,
      S,
      D
    ) : Me(l, a, D);
  }, ke = (l, a, v, x, w, b, S) => {
    const y = l.component = ca(
      l,
      x,
      w
    );
    if (process.env.NODE_ENV !== "production" && y.type.__hmrId && Fc(y), process.env.NODE_ENV !== "production" && (Bn(l), Qt(y, "mount")), In(l) && (y.ctx.renderer = V), process.env.NODE_ENV !== "production" && Qt(y, "init"), aa(y, !1, S), process.env.NODE_ENV !== "production" && Zt(y, "init"), process.env.NODE_ENV !== "production" && gt && (l.el = null), y.asyncDep) {
      if (w && w.registerDep(y, oe, S), !l.el) {
        const D = y.subTree = ze(Ae);
        ne(null, D, a, v), l.placeholder = D.el;
      }
    } else
      oe(
        y,
        l,
        a,
        v,
        w,
        b,
        S
      );
    process.env.NODE_ENV !== "production" && (Wn(), Zt(y, "mount"));
  }, Me = (l, a, v) => {
    const x = a.component = l.component;
    if (ql(l, a, v))
      if (x.asyncDep && !x.asyncResolved) {
        process.env.NODE_ENV !== "production" && Bn(a), se(x, a, v), process.env.NODE_ENV !== "production" && Wn();
        return;
      } else
        x.next = a, x.update();
    else
      a.el = l.el, x.vnode = a;
  }, oe = (l, a, v, x, w, b, S) => {
    const y = () => {
      if (l.isMounted) {
        let { next: N, bu: I, u: L, parent: W, vnode: U } = l;
        {
          const ie = yi(l);
          if (ie) {
            N && (N.el = U.el, se(l, N, S)), ie.asyncDep.then(() => {
              l.isUnmounted || y();
            });
            return;
          }
        }
        let G = N, F;
        process.env.NODE_ENV !== "production" && Bn(N || l.vnode), Pt(l, !1), N ? (N.el = U.el, se(l, N, S)) : N = U, I && an(I), (F = N.props && N.props.onVnodeBeforeUpdate) && ut(F, W, N, U), Pt(l, !0), process.env.NODE_ENV !== "production" && Qt(l, "render");
        const z = Fo(l);
        process.env.NODE_ENV !== "production" && Zt(l, "render");
        const P = l.subTree;
        l.subTree = z, process.env.NODE_ENV !== "production" && Qt(l, "patch"), j(
          P,
          z,
          // parent may have changed if it's in a teleport
          p(P.el),
          // anchor may have changed if it's in a fragment
          f(P),
          l,
          w,
          b
        ), process.env.NODE_ENV !== "production" && Zt(l, "patch"), N.el = z.el, G === null && Xl(l, z.el), L && Ke(L, w), (F = N.props && N.props.onVnodeUpdated) && Ke(
          () => ut(F, W, N, U),
          w
        ), process.env.NODE_ENV !== "production" && Ks(l), process.env.NODE_ENV !== "production" && Wn();
      } else {
        let N;
        const { el: I, props: L } = a, { bm: W, m: U, parent: G, root: F, type: z } = l, P = En(a);
        Pt(l, !1), W && an(W), !P && (N = L && L.onVnodeBeforeMount) && ut(N, G, a), Pt(l, !0);
        {
          F.ce && // @ts-expect-error _def is private
          F.ce._def.shadowRoot !== !1 && F.ce._injectChildStyle(z), process.env.NODE_ENV !== "production" && Qt(l, "render");
          const ie = l.subTree = Fo(l);
          process.env.NODE_ENV !== "production" && Zt(l, "render"), process.env.NODE_ENV !== "production" && Qt(l, "patch"), j(
            null,
            ie,
            v,
            x,
            l,
            w,
            b
          ), process.env.NODE_ENV !== "production" && Zt(l, "patch"), a.el = ie.el;
        }
        if (U && Ke(U, w), !P && (N = L && L.onVnodeMounted)) {
          const ie = a;
          Ke(
            () => ut(N, G, ie),
            w
          );
        }
        (a.shapeFlag & 256 || G && En(G.vnode) && G.vnode.shapeFlag & 256) && l.a && Ke(l.a, w), l.isMounted = !0, process.env.NODE_ENV !== "production" && zc(l), a = v = x = null;
      }
    };
    l.scope.on();
    const D = l.effect = new Ns(y);
    l.scope.off();
    const O = l.update = D.run.bind(D), M = l.job = D.runIfDirty.bind(D);
    M.i = l, M.id = l.uid, D.scheduler = () => mr(M), Pt(l, !0), process.env.NODE_ENV !== "production" && (D.onTrack = l.rtc ? (N) => an(l.rtc, N) : void 0, D.onTrigger = l.rtg ? (N) => an(l.rtg, N) : void 0), O();
  }, se = (l, a, v) => {
    a.component = l;
    const x = l.vnode.props;
    l.vnode = a, l.next = null, Cl(l, a.props, x, v), kl(l, a.children, v), ct(), Co(l), lt();
  }, Te = (l, a, v, x, w, b, S, y, D = !1) => {
    const O = l && l.children, M = l ? l.shapeFlag : 0, N = a.children, { patchFlag: I, shapeFlag: L } = a;
    if (I > 0) {
      if (I & 128) {
        je(
          O,
          N,
          v,
          x,
          w,
          b,
          S,
          y,
          D
        );
        return;
      } else if (I & 256) {
        mt(
          O,
          N,
          v,
          x,
          w,
          b,
          S,
          y,
          D
        );
        return;
      }
    }
    L & 8 ? (M & 16 && g(O, w, b), N !== O && h(v, N)) : M & 16 ? L & 16 ? je(
      O,
      N,
      v,
      x,
      w,
      b,
      S,
      y,
      D
    ) : g(O, w, b, !0) : (M & 8 && h(v, ""), L & 16 && Y(
      N,
      v,
      x,
      w,
      b,
      S,
      y,
      D
    ));
  }, mt = (l, a, v, x, w, b, S, y, D) => {
    l = l || tn, a = a || tn;
    const O = l.length, M = a.length, N = Math.min(O, M);
    let I;
    for (I = 0; I < N; I++) {
      const L = a[I] = D ? Vt(a[I]) : nt(a[I]);
      j(
        l[I],
        L,
        v,
        null,
        w,
        b,
        S,
        y,
        D
      );
    }
    O > M ? g(
      l,
      w,
      b,
      !0,
      !1,
      N
    ) : Y(
      a,
      v,
      x,
      w,
      b,
      S,
      y,
      D,
      N
    );
  }, je = (l, a, v, x, w, b, S, y, D) => {
    let O = 0;
    const M = a.length;
    let N = l.length - 1, I = M - 1;
    for (; O <= N && O <= I; ) {
      const L = l[O], W = a[O] = D ? Vt(a[O]) : nt(a[O]);
      if (Ht(L, W))
        j(
          L,
          W,
          v,
          null,
          w,
          b,
          S,
          y,
          D
        );
      else
        break;
      O++;
    }
    for (; O <= N && O <= I; ) {
      const L = l[N], W = a[I] = D ? Vt(a[I]) : nt(a[I]);
      if (Ht(L, W))
        j(
          L,
          W,
          v,
          null,
          w,
          b,
          S,
          y,
          D
        );
      else
        break;
      N--, I--;
    }
    if (O > N) {
      if (O <= I) {
        const L = I + 1, W = L < M ? a[L].el : x;
        for (; O <= I; )
          j(
            null,
            a[O] = D ? Vt(a[O]) : nt(a[O]),
            v,
            W,
            w,
            b,
            S,
            y,
            D
          ), O++;
      }
    } else if (O > I)
      for (; O <= N; )
        Ne(l[O], w, b, !0), O++;
    else {
      const L = O, W = O, U = /* @__PURE__ */ new Map();
      for (O = W; O <= I; O++) {
        const J = a[O] = D ? Vt(a[O]) : nt(a[O]);
        J.key != null && (process.env.NODE_ENV !== "production" && U.has(J.key) && R(
          "Duplicate keys found during update:",
          JSON.stringify(J.key),
          "Make sure keys are unique."
        ), U.set(J.key, O));
      }
      let G, F = 0;
      const z = I - W + 1;
      let P = !1, ie = 0;
      const fe = new Array(z);
      for (O = 0; O < z; O++) fe[O] = 0;
      for (O = L; O <= N; O++) {
        const J = l[O];
        if (F >= z) {
          Ne(J, w, b, !0);
          continue;
        }
        let te;
        if (J.key != null)
          te = U.get(J.key);
        else
          for (G = W; G <= I; G++)
            if (fe[G - W] === 0 && Ht(J, a[G])) {
              te = G;
              break;
            }
        te === void 0 ? Ne(J, w, b, !0) : (fe[te - W] = O + 1, te >= ie ? ie = te : P = !0, j(
          J,
          a[te],
          v,
          null,
          w,
          b,
          S,
          y,
          D
        ), F++);
      }
      const ee = P ? Ul(fe) : tn;
      for (G = ee.length - 1, O = z - 1; O >= 0; O--) {
        const J = W + O, te = a[J], ge = a[J + 1], de = J + 1 < M ? (
          // #13559, fallback to el placeholder for unresolved async component
          ge.el || ge.placeholder
        ) : x;
        fe[O] === 0 ? j(
          null,
          te,
          v,
          de,
          w,
          b,
          S,
          y,
          D
        ) : P && (G < 0 || O !== ee[G] ? Ge(te, v, de, 2) : G--);
      }
    }
  }, Ge = (l, a, v, x, w = null) => {
    const { el: b, type: S, transition: y, children: D, shapeFlag: O } = l;
    if (O & 6) {
      Ge(l.component.subTree, a, v, x);
      return;
    }
    if (O & 128) {
      l.suspense.move(a, v, x);
      return;
    }
    if (O & 64) {
      S.move(l, a, v, V);
      return;
    }
    if (S === tt) {
      r(b, a, v);
      for (let N = 0; N < D.length; N++)
        Ge(D[N], a, v, x);
      r(l.anchor, a, v);
      return;
    }
    if (S === Yn) {
      Oe(l, a, v);
      return;
    }
    if (x !== 2 && O & 1 && y)
      if (x === 0)
        y.beforeEnter(b), r(b, a, v), Ke(() => y.enter(b), w);
      else {
        const { leave: N, delayLeave: I, afterLeave: L } = y, W = () => {
          l.ctx.isUnmounted ? o(b) : r(b, a, v);
        }, U = () => {
          b._isLeaving && b[yt](
            !0
            /* cancelled */
          ), N(b, () => {
            W(), L && L();
          });
        };
        I ? I(b, W, U) : U();
      }
    else
      r(b, a, v);
  }, Ne = (l, a, v, x = !1, w = !1) => {
    const {
      type: b,
      props: S,
      ref: y,
      children: D,
      dynamicChildren: O,
      shapeFlag: M,
      patchFlag: N,
      dirs: I,
      cacheIndex: L
    } = l;
    if (N === -2 && (w = !1), y != null && (ct(), bn(y, null, v, l, !0), lt()), L != null && (a.renderCache[L] = void 0), M & 256) {
      a.ctx.deactivate(l);
      return;
    }
    const W = M & 1 && I, U = !En(l);
    let G;
    if (U && (G = S && S.onVnodeBeforeUnmount) && ut(G, a, l), M & 6)
      d(l.component, v, x);
    else {
      if (M & 128) {
        l.suspense.unmount(v, x);
        return;
      }
      W && kt(l, null, a, "beforeUnmount"), M & 64 ? l.type.remove(
        l,
        a,
        v,
        V,
        x
      ) : O && // #5154
      // when v-once is used inside a block, setBlockTracking(-1) marks the
      // parent block with hasOnce: true
      // so that it doesn't take the fast path during unmount - otherwise
      // components nested in v-once are never unmounted.
      !O.hasOnce && // #1153: fast path should not be taken for non-stable (v-for) fragments
      (b !== tt || N > 0 && N & 64) ? g(
        O,
        a,
        v,
        !1,
        !0
      ) : (b === tt && N & 384 || !w && M & 16) && g(D, a, v), x && k(l);
    }
    (U && (G = S && S.onVnodeUnmounted) || W) && Ke(() => {
      G && ut(G, a, l), W && kt(l, null, a, "unmounted");
    }, v);
  }, k = (l) => {
    const { type: a, el: v, anchor: x, transition: w } = l;
    if (a === tt) {
      process.env.NODE_ENV !== "production" && l.patchFlag > 0 && l.patchFlag & 2048 && w && !w.persisted ? l.children.forEach((S) => {
        S.type === Ae ? o(S.el) : k(S);
      }) : kn(v, x);
      return;
    }
    if (a === Yn) {
      B(l);
      return;
    }
    const b = () => {
      o(v), w && !w.persisted && w.afterLeave && w.afterLeave();
    };
    if (l.shapeFlag & 1 && w && !w.persisted) {
      const { leave: S, delayLeave: y } = w, D = () => S(v, b);
      y ? y(l.el, b, D) : D();
    } else
      b();
  }, kn = (l, a) => {
    let v;
    for (; l !== a; )
      v = E(l), o(l), l = v;
    o(a);
  }, d = (l, a, v) => {
    process.env.NODE_ENV !== "production" && l.type.__hmrId && jc(l);
    const { bum: x, scope: w, job: b, subTree: S, um: y, m: D, a: O } = l;
    $o(D), $o(O), x && an(x), w.stop(), b && (b.flags |= 8, Ne(S, l, a, v)), y && Ke(y, a), Ke(() => {
      l.isUnmounted = !0;
    }, a), process.env.NODE_ENV !== "production" && Kc(l);
  }, g = (l, a, v, x = !1, w = !1, b = 0) => {
    for (let S = b; S < l.length; S++)
      Ne(l[S], a, v, x, w);
  }, f = (l) => {
    if (l.shapeFlag & 6)
      return f(l.component.subTree);
    if (l.shapeFlag & 128)
      return l.suspense.next();
    const a = E(l.anchor || l.el), v = a && a[Xc];
    return v ? E(v) : a;
  };
  let _ = !1;
  const C = (l, a, v) => {
    l == null ? a._vnode && Ne(a._vnode, null, null, !0) : j(
      a._vnode || null,
      l,
      a,
      null,
      null,
      null,
      v
    ), a._vnode = l, _ || (_ = !0, Co(), Ws(), _ = !1);
  }, V = {
    p: j,
    um: Ne,
    m: Ge,
    r: k,
    mt: ke,
    mc: Y,
    pc: Te,
    pbc: ue,
    n: f,
    o: e
  };
  return {
    render: C,
    hydrate: void 0,
    createApp: Nl(C)
  };
}
function Tr({ type: e, props: t }, n) {
  return n === "svg" && e === "foreignObject" || n === "mathml" && e === "annotation-xml" && t && t.encoding && t.encoding.includes("html") ? void 0 : n;
}
function Pt({ effect: e, job: t }, n) {
  n ? (e.flags |= 32, t.flags |= 4) : (e.flags &= -33, t.flags &= -5);
}
function jl(e, t) {
  return (!e || e && !e.pendingBranch) && t && !t.persisted;
}
function Kn(e, t, n = !1) {
  const r = e.children, o = t.children;
  if (K(r) && K(o))
    for (let s = 0; s < r.length; s++) {
      const i = r[s];
      let c = o[s];
      c.shapeFlag & 1 && !c.dynamicChildren && ((c.patchFlag <= 0 || c.patchFlag === 32) && (c = o[s] = Vt(o[s]), c.el = i.el), !n && c.patchFlag !== -2 && Kn(i, c)), c.type === Rn && // avoid cached text nodes retaining detached dom nodes
      c.patchFlag !== -1 && (c.el = i.el), c.type === Ae && !c.el && (c.el = i.el), process.env.NODE_ENV !== "production" && c.el && (c.el.__vnode = c);
    }
}
function Ul(e) {
  const t = e.slice(), n = [0];
  let r, o, s, i, c;
  const u = e.length;
  for (r = 0; r < u; r++) {
    const m = e[r];
    if (m !== 0) {
      if (o = n[n.length - 1], e[o] < m) {
        t[r] = o, n.push(r);
        continue;
      }
      for (s = 0, i = n.length - 1; s < i; )
        c = s + i >> 1, e[n[c]] < m ? s = c + 1 : i = c;
      m < e[n[s]] && (s > 0 && (t[r] = n[s - 1]), n[s] = r);
    }
  }
  for (s = n.length, i = n[s - 1]; s-- > 0; )
    n[s] = i, i = t[i];
  return n;
}
function yi(e) {
  const t = e.subTree.component;
  if (t)
    return t.asyncDep && !t.asyncResolved ? t : yi(t);
}
function $o(e) {
  if (e)
    for (let t = 0; t < e.length; t++)
      e[t].flags |= 8;
}
const Hl = Symbol.for("v-scx"), Bl = () => {
  {
    const e = Gn(Hl);
    return e || process.env.NODE_ENV !== "production" && R(
      "Server rendering context not provided. Make sure to only call useSSRContext() conditionally in the server build."
    ), e;
  }
};
function Vr(e, t, n) {
  return process.env.NODE_ENV !== "production" && !q(t) && R(
    "`watch(fn, options?)` signature has been moved to a separate API. Use `watchEffect(fn, options?)` instead. `watch` now only supports `watch(source, cb, options?) signature."
  ), Ni(e, t, n);
}
function Ni(e, t, n = me) {
  const { immediate: r, deep: o, flush: s, once: i } = n;
  process.env.NODE_ENV !== "production" && !t && (r !== void 0 && R(
    'watch() "immediate" option is only respected when using the watch(source, callback, options?) signature.'
  ), o !== void 0 && R(
    'watch() "deep" option is only respected when using the watch(source, callback, options?) signature.'
  ), i !== void 0 && R(
    'watch() "once" option is only respected when using the watch(source, callback, options?) signature.'
  ));
  const c = Ve({}, n);
  process.env.NODE_ENV !== "production" && (c.onWarn = R);
  const u = t && r || !t && s !== "post";
  let m;
  if (Sn) {
    if (s === "sync") {
      const A = Bl();
      m = A.__watcherHandles || (A.__watcherHandles = []);
    } else if (!u) {
      const A = () => {
      };
      return A.stop = Re, A.resume = Re, A.pause = Re, A;
    }
  }
  const h = Fe;
  c.call = (A, H, j) => at(A, h, H, j);
  let p = !1;
  s === "post" ? c.scheduler = (A) => {
    Ke(A, h && h.suspense);
  } : s !== "sync" && (p = !0, c.scheduler = (A, H) => {
    H ? A() : mr(A);
  }), c.augmentJob = (A) => {
    t && (A.flags |= 4), p && (A.flags |= 2, h && (A.id = h.uid, A.i = h));
  };
  const E = Tc(e, t, c);
  return Sn && (m ? m.push(E) : u && E()), E;
}
function Wl(e, t, n) {
  const r = this.proxy, o = Se(e) ? e.includes(".") ? xi(r, e) : () => r[e] : e.bind(r, r);
  let s;
  q(t) ? s = t : (s = t.handler, n = t);
  const i = Ln(this), c = Ni(o, s.bind(r), n);
  return i(), c;
}
function xi(e, t) {
  const n = t.split(".");
  return () => {
    let r = e;
    for (let o = 0; o < n.length && r; o++)
      r = r[n[o]];
    return r;
  };
}
const zl = (e, t) => t === "modelValue" || t === "model-value" ? e.modelModifiers : e[`${t}Modifiers`] || e[`${ot(t)}Modifiers`] || e[`${Mt(t)}Modifiers`];
function Gl(e, t, ...n) {
  if (e.isUnmounted) return;
  const r = e.vnode.props || me;
  if (process.env.NODE_ENV !== "production") {
    const {
      emitsOptions: h,
      propsOptions: [p]
    } = e;
    if (h)
      if (!(t in h))
        (!p || !(jt(ot(t)) in p)) && R(
          `Component emitted event "${t}" but it is neither declared in the emits option nor as an "${jt(ot(t))}" prop.`
        );
      else {
        const E = h[t];
        q(E) && (E(...n) || R(
          `Invalid event arguments: event validation failed for event "${t}".`
        ));
      }
  }
  let o = n;
  const s = t.startsWith("update:"), i = s && zl(r, t.slice(7));
  if (i && (i.trim && (o = n.map((h) => Se(h) ? h.trim() : h)), i.number && (o = n.map(Hi))), process.env.NODE_ENV !== "production" && qc(e, t, o), process.env.NODE_ENV !== "production") {
    const h = t.toLowerCase();
    h !== t && r[jt(h)] && R(
      `Event "${h}" is emitted in component ${Er(
        e,
        e.type
      )} but the handler is registered for "${t}". Note that HTML attributes are case-insensitive and you cannot use v-on to listen to camelCase events when using in-DOM templates. You should probably use "${Mt(
        t
      )}" instead of "${t}".`
    );
  }
  let c, u = r[c = jt(t)] || // also try camelCase event handler (#2249)
  r[c = jt(ot(t))];
  !u && s && (u = r[c = jt(Mt(t))]), u && at(
    u,
    e,
    6,
    o
  );
  const m = r[c + "Once"];
  if (m) {
    if (!e.emitted)
      e.emitted = {};
    else if (e.emitted[c])
      return;
    e.emitted[c] = !0, at(
      m,
      e,
      6,
      o
    );
  }
}
const Kl = /* @__PURE__ */ new WeakMap();
function wi(e, t, n = !1) {
  const r = n ? Kl : t.emitsCache, o = r.get(e);
  if (o !== void 0)
    return o;
  const s = e.emits;
  let i = {}, c = !1;
  if (!q(e)) {
    const u = (m) => {
      const h = wi(m, t, !0);
      h && (c = !0, Ve(i, h));
    };
    !n && t.mixins.length && t.mixins.forEach(u), e.extends && u(e.extends), e.mixins && e.mixins.forEach(u);
  }
  return !s && !c ? (he(e) && r.set(e, null), null) : (K(s) ? s.forEach((u) => i[u] = null) : Ve(i, s), he(e) && r.set(e, i), i);
}
function br(e, t) {
  return !e || !Tn(t) ? !1 : (t = t.slice(2).replace(/Once$/, ""), le(e, t[0].toLowerCase() + t.slice(1)) || le(e, Mt(t)) || le(e, t));
}
let Yr = !1;
function cr() {
  Yr = !0;
}
function Fo(e) {
  const {
    type: t,
    vnode: n,
    proxy: r,
    withProxy: o,
    propsOptions: [s],
    slots: i,
    attrs: c,
    emit: u,
    render: m,
    renderCache: h,
    props: p,
    data: E,
    setupState: A,
    ctx: H,
    inheritAttrs: j
  } = e, _e = rr(e);
  let ne, Z;
  process.env.NODE_ENV !== "production" && (Yr = !1);
  try {
    if (n.shapeFlag & 4) {
      const B = o || r, ce = process.env.NODE_ENV !== "production" && A.__isScriptSetup ? new Proxy(B, {
        get(De, we, Y) {
          return R(
            `Property '${String(
              we
            )}' was accessed via 'this'. Avoid using 'this' in templates.`
          ), Reflect.get(De, we, Y);
        }
      }) : B;
      ne = nt(
        m.call(
          ce,
          B,
          h,
          process.env.NODE_ENV !== "production" ? ht(p) : p,
          A,
          E,
          H
        )
      ), Z = c;
    } else {
      const B = t;
      process.env.NODE_ENV !== "production" && c === p && cr(), ne = nt(
        B.length > 1 ? B(
          process.env.NODE_ENV !== "production" ? ht(p) : p,
          process.env.NODE_ENV !== "production" ? {
            get attrs() {
              return cr(), ht(c);
            },
            slots: i,
            emit: u
          } : { attrs: c, slots: i, emit: u }
        ) : B(
          process.env.NODE_ENV !== "production" ? ht(p) : p,
          null
        )
      ), Z = t.props ? c : Yl(c);
    }
  } catch (B) {
    yn.length = 0, An(B, e, 1), ne = ze(Ae);
  }
  let Q = ne, Oe;
  if (process.env.NODE_ENV !== "production" && ne.patchFlag > 0 && ne.patchFlag & 2048 && ([Q, Oe] = Oi(ne)), Z && j !== !1) {
    const B = Object.keys(Z), { shapeFlag: ce } = Q;
    if (B.length) {
      if (ce & 7)
        s && B.some(Xn) && (Z = Jl(
          Z,
          s
        )), Q = vt(Q, Z, !1, !0);
      else if (process.env.NODE_ENV !== "production" && !Yr && Q.type !== Ae) {
        const De = Object.keys(c), we = [], Y = [];
        for (let ae = 0, ue = De.length; ae < ue; ae++) {
          const $ = De[ae];
          Tn($) ? Xn($) || we.push($[2].toLowerCase() + $.slice(3)) : Y.push($);
        }
        Y.length && R(
          `Extraneous non-props attributes (${Y.join(", ")}) were passed to component but could not be automatically inherited because component renders fragment or text or teleport root nodes.`
        ), we.length && R(
          `Extraneous non-emits event listeners (${we.join(", ")}) were passed to component but could not be automatically inherited because component renders fragment or text root nodes. If the listener is intended to be a component custom event listener only, declare it using the "emits" option.`
        );
      }
    }
  }
  return n.dirs && (process.env.NODE_ENV !== "production" && !jo(Q) && R(
    "Runtime directive used on component with non-element root node. The directives will not function as intended."
  ), Q = vt(Q, null, !1, !0), Q.dirs = Q.dirs ? Q.dirs.concat(n.dirs) : n.dirs), n.transition && (process.env.NODE_ENV !== "production" && !jo(Q) && R(
    "Component inside <Transition> renders non-element root node that cannot be animated."
  ), On(Q, n.transition)), process.env.NODE_ENV !== "production" && Oe ? Oe(Q) : ne = Q, rr(_e), ne;
}
const Oi = (e) => {
  const t = e.children, n = e.dynamicChildren, r = go(t, !1);
  if (r) {
    if (process.env.NODE_ENV !== "production" && r.patchFlag > 0 && r.patchFlag & 2048)
      return Oi(r);
  } else return [e, void 0];
  const o = t.indexOf(r), s = n ? n.indexOf(r) : -1, i = (c) => {
    t[o] = c, n && (s > -1 ? n[s] = c : c.patchFlag > 0 && (e.dynamicChildren = [...n, c]));
  };
  return [nt(r), i];
};
function go(e, t = !0) {
  let n;
  for (let r = 0; r < e.length; r++) {
    const o = e[r];
    if (cn(o)) {
      if (o.type !== Ae || o.children === "v-if") {
        if (n)
          return;
        if (n = o, process.env.NODE_ENV !== "production" && t && n.patchFlag > 0 && n.patchFlag & 2048)
          return go(n.children);
      }
    } else
      return;
  }
  return n;
}
const Yl = (e) => {
  let t;
  for (const n in e)
    (n === "class" || n === "style" || Tn(n)) && ((t || (t = {}))[n] = e[n]);
  return t;
}, Jl = (e, t) => {
  const n = {};
  for (const r in e)
    (!Xn(r) || !(r.slice(9) in t)) && (n[r] = e[r]);
  return n;
}, jo = (e) => e.shapeFlag & 7 || e.type === Ae;
function ql(e, t, n) {
  const { props: r, children: o, component: s } = e, { props: i, children: c, patchFlag: u } = t, m = s.emitsOptions;
  if (process.env.NODE_ENV !== "production" && (o || c) && gt || t.dirs || t.transition)
    return !0;
  if (n && u >= 0) {
    if (u & 1024)
      return !0;
    if (u & 16)
      return r ? Uo(r, i, m) : !!i;
    if (u & 8) {
      const h = t.dynamicProps;
      for (let p = 0; p < h.length; p++) {
        const E = h[p];
        if (i[E] !== r[E] && !br(m, E))
          return !0;
      }
    }
  } else
    return (o || c) && (!c || !c.$stable) ? !0 : r === i ? !1 : r ? i ? Uo(r, i, m) : !0 : !!i;
  return !1;
}
function Uo(e, t, n) {
  const r = Object.keys(t);
  if (r.length !== Object.keys(e).length)
    return !0;
  for (let o = 0; o < r.length; o++) {
    const s = r[o];
    if (t[s] !== e[s] && !br(n, s))
      return !0;
  }
  return !1;
}
function Xl({ vnode: e, parent: t }, n) {
  for (; t; ) {
    const r = t.subTree;
    if (r.suspense && r.suspense.activeBranch === e && (r.el = e.el), r === e)
      (e = t.vnode).el = n, t = t.parent;
    else
      break;
  }
}
const Ci = (e) => e.__isSuspense;
function Ql(e, t) {
  t && t.pendingBranch ? K(e) ? t.effects.push(...e) : t.effects.push(e) : Bs(e);
}
const tt = Symbol.for("v-fgt"), Rn = Symbol.for("v-txt"), Ae = Symbol.for("v-cmt"), Yn = Symbol.for("v-stc"), yn = [];
let qe = null;
function et(e = !1) {
  yn.push(qe = e ? null : []);
}
function Zl() {
  yn.pop(), qe = yn[yn.length - 1] || null;
}
let Cn = 1;
function lr(e, t = !1) {
  Cn += e, e < 0 && qe && t && (qe.hasOnce = !0);
}
function Si(e) {
  return e.dynamicChildren = Cn > 0 ? qe || tn : null, Zl(), Cn > 0 && qe && qe.push(e), e;
}
function ft(e, t, n, r, o, s) {
  return Si(
    He(
      e,
      t,
      n,
      r,
      o,
      s,
      !0
    )
  );
}
function ea(e, t, n, r, o) {
  return Si(
    ze(
      e,
      t,
      n,
      r,
      o,
      !0
    )
  );
}
function cn(e) {
  return e ? e.__v_isVNode === !0 : !1;
}
function Ht(e, t) {
  if (process.env.NODE_ENV !== "production" && t.shapeFlag & 6 && e.component) {
    const n = zn.get(t.type);
    if (n && n.has(e.component))
      return e.shapeFlag &= -257, t.shapeFlag &= -513, !1;
  }
  return e.type === t.type && e.key === t.key;
}
const ta = (...e) => Ti(
  ...e
), Di = ({ key: e }) => e ?? null, Jn = ({
  ref: e,
  ref_key: t,
  ref_for: n
}) => (typeof e == "number" && (e = "" + e), e != null ? Se(e) || Le(e) || q(e) ? { i: Je, r: e, k: t, f: !!n } : e : null);
function He(e, t = null, n = null, r = 0, o = null, s = e === tt ? 0 : 1, i = !1, c = !1) {
  const u = {
    __v_isVNode: !0,
    __v_skip: !0,
    type: e,
    props: t,
    key: t && Di(t),
    ref: t && Jn(t),
    scopeId: Js,
    slotScopeIds: null,
    children: n,
    component: null,
    suspense: null,
    ssContent: null,
    ssFallback: null,
    dirs: null,
    transition: null,
    el: null,
    anchor: null,
    target: null,
    targetStart: null,
    targetAnchor: null,
    staticCount: 0,
    shapeFlag: s,
    patchFlag: r,
    dynamicProps: o,
    dynamicChildren: null,
    appContext: null,
    ctx: Je
  };
  return c ? (vo(u, n), s & 128 && e.normalize(u)) : n && (u.shapeFlag |= Se(n) ? 8 : 16), process.env.NODE_ENV !== "production" && u.key !== u.key && R("VNode created with invalid key (NaN). VNode type:", u.type), Cn > 0 && // avoid a block node from tracking itself
  !i && // has current parent block
  qe && // presence of a patch flag indicates this node needs patching on updates.
  // component nodes also should always be patched, because even if the
  // component doesn't need to update, it needs to persist the instance on to
  // the next vnode so that it can be properly unmounted later.
  (u.patchFlag > 0 || s & 6) && // the EVENTS flag is only for hydration and if it is the only flag, the
  // vnode should not be considered dynamic due to handler caching.
  u.patchFlag !== 32 && qe.push(u), u;
}
const ze = process.env.NODE_ENV !== "production" ? ta : Ti;
function Ti(e, t = null, n = null, r = 0, o = null, s = !1) {
  if ((!e || e === ul) && (process.env.NODE_ENV !== "production" && !e && R(`Invalid vnode type when creating vnode: ${e}.`), e = Ae), cn(e)) {
    const c = vt(
      e,
      t,
      !0
      /* mergeRef: true */
    );
    return n && vo(c, n), Cn > 0 && !s && qe && (c.shapeFlag & 6 ? qe[qe.indexOf(e)] = c : qe.push(c)), c.patchFlag = -2, c;
  }
  if (Ri(e) && (e = e.__vccOpts), t) {
    t = na(t);
    let { class: c, style: u } = t;
    c && !Se(c) && (t.class = hr(c)), he(u) && (Zn(u) && !K(u) && (u = Ve({}, u)), t.style = pr(u));
  }
  const i = Se(e) ? 1 : Ci(e) ? 128 : Qs(e) ? 64 : he(e) ? 4 : q(e) ? 2 : 0;
  return process.env.NODE_ENV !== "production" && i & 4 && Zn(e) && (e = re(e), R(
    "Vue received a Component that was made a reactive object. This can lead to unnecessary performance overhead and should be avoided by marking the component with `markRaw` or using `shallowRef` instead of `ref`.",
    `
Component that was made reactive: `,
    e
  )), He(
    e,
    t,
    n,
    r,
    o,
    i,
    s,
    !0
  );
}
function na(e) {
  return e ? Zn(e) || gi(e) ? Ve({}, e) : e : null;
}
function vt(e, t, n = !1, r = !1) {
  const { props: o, ref: s, patchFlag: i, children: c, transition: u } = e, m = t ? oa(o || {}, t) : o, h = {
    __v_isVNode: !0,
    __v_skip: !0,
    type: e.type,
    props: m,
    key: m && Di(m),
    ref: t && t.ref ? (
      // #2078 in the case of <component :is="vnode" ref="extra"/>
      // if the vnode itself already has a ref, cloneVNode will need to merge
      // the refs so the single vnode can be set on multiple refs
      n && s ? K(s) ? s.concat(Jn(t)) : [s, Jn(t)] : Jn(t)
    ) : s,
    scopeId: e.scopeId,
    slotScopeIds: e.slotScopeIds,
    children: process.env.NODE_ENV !== "production" && i === -1 && K(c) ? c.map(Vi) : c,
    target: e.target,
    targetStart: e.targetStart,
    targetAnchor: e.targetAnchor,
    staticCount: e.staticCount,
    shapeFlag: e.shapeFlag,
    // if the vnode is cloned with extra props, we can no longer assume its
    // existing patch flag to be reliable and need to add the FULL_PROPS flag.
    // note: preserve flag for fragments since they use the flag for children
    // fast paths only.
    patchFlag: t && e.type !== tt ? i === -1 ? 16 : i | 16 : i,
    dynamicProps: e.dynamicProps,
    dynamicChildren: e.dynamicChildren,
    appContext: e.appContext,
    dirs: e.dirs,
    transition: u,
    // These should technically only be non-null on mounted VNodes. However,
    // they *should* be copied for kept-alive vnodes. So we just always copy
    // them since them being non-null during a mount doesn't affect the logic as
    // they will simply be overwritten.
    component: e.component,
    suspense: e.suspense,
    ssContent: e.ssContent && vt(e.ssContent),
    ssFallback: e.ssFallback && vt(e.ssFallback),
    placeholder: e.placeholder,
    el: e.el,
    anchor: e.anchor,
    ctx: e.ctx,
    ce: e.ce
  };
  return u && r && On(
    h,
    u.clone(h)
  ), h;
}
function Vi(e) {
  const t = vt(e);
  return K(e.children) && (t.children = e.children.map(Vi)), t;
}
function ra(e = " ", t = 0) {
  return ze(Rn, null, e, t);
}
function Hn(e = "", t = !1) {
  return t ? (et(), ea(Ae, null, e)) : ze(Ae, null, e);
}
function nt(e) {
  return e == null || typeof e == "boolean" ? ze(Ae) : K(e) ? ze(
    tt,
    null,
    // #3666, avoid reference pollution when reusing vnode
    e.slice()
  ) : cn(e) ? Vt(e) : ze(Rn, null, String(e));
}
function Vt(e) {
  return e.el === null && e.patchFlag !== -1 || e.memo ? e : vt(e);
}
function vo(e, t) {
  let n = 0;
  const { shapeFlag: r } = e;
  if (t == null)
    t = null;
  else if (K(t))
    n = 16;
  else if (typeof t == "object")
    if (r & 65) {
      const o = t.default;
      o && (o._c && (o._d = !1), vo(e, o()), o._c && (o._d = !0));
      return;
    } else {
      n = 32;
      const o = t._;
      !o && !gi(t) ? t._ctx = Je : o === 3 && Je && (Je.slots._ === 1 ? t._ = 1 : (t._ = 2, e.patchFlag |= 1024));
    }
  else q(t) ? (t = { default: t, _ctx: Je }, n = 32) : (t = String(t), r & 64 ? (n = 16, t = [ra(t)]) : n = 8);
  e.children = t, e.shapeFlag |= n;
}
function oa(...e) {
  const t = {};
  for (let n = 0; n < e.length; n++) {
    const r = e[n];
    for (const o in r)
      if (o === "class")
        t.class !== r.class && (t.class = hr([t.class, r.class]));
      else if (o === "style")
        t.style = pr([t.style, r.style]);
      else if (Tn(o)) {
        const s = t[o], i = r[o];
        i && s !== i && !(K(s) && s.includes(i)) && (t[o] = s ? [].concat(s, i) : i);
      } else o !== "" && (t[o] = r[o]);
  }
  return t;
}
function ut(e, t, n, r = null) {
  at(e, t, 7, [
    n,
    r
  ]);
}
const sa = di();
let ia = 0;
function ca(e, t, n) {
  const r = e.type, o = (t ? t.appContext : e.appContext) || sa, s = {
    uid: ia++,
    vnode: e,
    type: r,
    parent: t,
    appContext: o,
    root: null,
    // to be immediately set
    next: null,
    subTree: null,
    // will be set synchronously right after creation
    effect: null,
    update: null,
    // will be set synchronously right after creation
    job: null,
    scope: new nc(
      !0
      /* detached */
    ),
    render: null,
    proxy: null,
    exposed: null,
    exposeProxy: null,
    withProxy: null,
    provides: t ? t.provides : Object.create(o.provides),
    ids: t ? t.ids : ["", 0, 0],
    accessCache: null,
    renderCache: [],
    // local resolved assets
    components: null,
    directives: null,
    // resolved props and emits options
    propsOptions: mi(r, o),
    emitsOptions: wi(r, o),
    // emit
    emit: null,
    // to be set immediately
    emitted: null,
    // props default value
    propsDefaults: me,
    // inheritAttrs
    inheritAttrs: r.inheritAttrs,
    // state
    ctx: me,
    data: me,
    props: me,
    attrs: me,
    slots: me,
    refs: me,
    setupState: me,
    setupContext: null,
    // suspense related
    suspense: n,
    suspenseId: n ? n.pendingId : 0,
    asyncDep: null,
    asyncResolved: !1,
    // lifecycle hooks
    // not using enums here because it results in computed properties
    isMounted: !1,
    isUnmounted: !1,
    isDeactivated: !1,
    bc: null,
    c: null,
    bm: null,
    m: null,
    bu: null,
    u: null,
    um: null,
    bum: null,
    da: null,
    a: null,
    rtg: null,
    rtc: null,
    ec: null,
    sp: null
  };
  return process.env.NODE_ENV !== "production" ? s.ctx = dl(s) : s.ctx = { _: s }, s.root = t ? t.root : s, s.emit = Gl.bind(null, s), e.ce && e.ce(s), s;
}
let Fe = null;
const mo = () => Fe || Je;
let ar, Jr;
{
  const e = Vn(), t = (n, r) => {
    let o;
    return (o = e[n]) || (o = e[n] = []), o.push(r), (s) => {
      o.length > 1 ? o.forEach((i) => i(s)) : o[0](s);
    };
  };
  ar = t(
    "__VUE_INSTANCE_SETTERS__",
    (n) => Fe = n
  ), Jr = t(
    "__VUE_SSR_SETTERS__",
    (n) => Sn = n
  );
}
const Ln = (e) => {
  const t = Fe;
  return ar(e), e.scope.on(), () => {
    e.scope.off(), ar(t);
  };
}, Ho = () => {
  Fe && Fe.scope.off(), ar(null);
}, la = /* @__PURE__ */ wt("slot,component");
function qr(e, { isNativeTag: t }) {
  (la(e) || t(e)) && R(
    "Do not use built-in or reserved HTML elements as component id: " + e
  );
}
function Ai(e) {
  return e.vnode.shapeFlag & 4;
}
let Sn = !1;
function aa(e, t = !1, n = !1) {
  t && Jr(t);
  const { props: r, children: o } = e.vnode, s = Ai(e);
  wl(e, r, s, t), Ll(e, o, n || t);
  const i = s ? fa(e, t) : void 0;
  return t && Jr(!1), i;
}
function fa(e, t) {
  var n;
  const r = e.type;
  if (process.env.NODE_ENV !== "production") {
    if (r.name && qr(r.name, e.appContext.config), r.components) {
      const s = Object.keys(r.components);
      for (let i = 0; i < s.length; i++)
        qr(s[i], e.appContext.config);
    }
    if (r.directives) {
      const s = Object.keys(r.directives);
      for (let i = 0; i < s.length; i++)
        Xs(s[i]);
    }
    r.compilerOptions && ua() && R(
      '"compilerOptions" is only supported when using a build of Vue that includes the runtime compiler. Since you are using a runtime-only build, the options should be passed via your build tool config instead.'
    );
  }
  e.accessCache = /* @__PURE__ */ Object.create(null), e.proxy = new Proxy(e.ctx, ai), process.env.NODE_ENV !== "production" && pl(e);
  const { setup: o } = r;
  if (o) {
    ct();
    const s = e.setupContext = o.length > 1 ? pa(e) : null, i = Ln(e), c = ln(
      o,
      e,
      0,
      [
        process.env.NODE_ENV !== "production" ? ht(e.props) : e.props,
        s
      ]
    ), u = Zr(c);
    if (lt(), i(), (u || e.sp) && !En(e) && oi(e), u) {
      if (c.then(Ho, Ho), t)
        return c.then((m) => {
          Bo(e, m, t);
        }).catch((m) => {
          An(m, e, 0);
        });
      if (e.asyncDep = c, process.env.NODE_ENV !== "production" && !e.suspense) {
        const m = (n = r.name) != null ? n : "Anonymous";
        R(
          `Component <${m}>: setup function returned a promise, but no <Suspense> boundary was found in the parent component tree. A component with async setup() must be nested in a <Suspense> in order to be rendered.`
        );
      }
    } else
      Bo(e, c, t);
  } else
    Mi(e, t);
}
function Bo(e, t, n) {
  q(t) ? e.type.__ssrInlineRender ? e.ssrRender = t : e.render = t : he(t) ? (process.env.NODE_ENV !== "production" && cn(t) && R(
    "setup() should not return VNodes directly - return a render function instead."
  ), process.env.NODE_ENV !== "production" && (e.devtoolsRawSetupState = t), e.setupState = Fs(t), process.env.NODE_ENV !== "production" && hl(e)) : process.env.NODE_ENV !== "production" && t !== void 0 && R(
    `setup() should return an object. Received: ${t === null ? "null" : typeof t}`
  ), Mi(e, n);
}
const ua = () => !0;
function Mi(e, t, n) {
  const r = e.type;
  e.render || (e.render = r.render || Re);
  {
    const o = Ln(e);
    ct();
    try {
      vl(e);
    } finally {
      lt(), o();
    }
  }
  process.env.NODE_ENV !== "production" && !r.render && e.render === Re && !t && (r.template ? R(
    'Component provided template option but runtime compilation is not supported in this build of Vue. Configure your bundler to alias "vue" to "vue/dist/vue.esm-bundler.js".'
  ) : R("Component is missing template or render function: ", r));
}
const Wo = process.env.NODE_ENV !== "production" ? {
  get(e, t) {
    return cr(), Ie(e, "get", ""), e[t];
  },
  set() {
    return R("setupContext.attrs is readonly."), !1;
  },
  deleteProperty() {
    return R("setupContext.attrs is readonly."), !1;
  }
} : {
  get(e, t) {
    return Ie(e, "get", ""), e[t];
  }
};
function da(e) {
  return new Proxy(e.slots, {
    get(t, n) {
      return Ie(e, "get", "$slots"), t[n];
    }
  });
}
function pa(e) {
  const t = (n) => {
    if (process.env.NODE_ENV !== "production" && (e.exposed && R("expose() should be called only once per setup()."), n != null)) {
      let r = typeof n;
      r === "object" && (K(n) ? r = "array" : Le(n) && (r = "ref")), r !== "object" && R(
        `expose() should be passed a plain object, received ${r}.`
      );
    }
    e.exposed = n || {};
  };
  if (process.env.NODE_ENV !== "production") {
    let n, r;
    return Object.freeze({
      get attrs() {
        return n || (n = new Proxy(e.attrs, Wo));
      },
      get slots() {
        return r || (r = da(e));
      },
      get emit() {
        return (o, ...s) => e.emit(o, ...s);
      },
      expose: t
    });
  } else
    return {
      attrs: new Proxy(e.attrs, Wo),
      slots: e.slots,
      emit: e.emit,
      expose: t
    };
}
function _o(e) {
  return e.exposed ? e.exposeProxy || (e.exposeProxy = new Proxy(Fs(xc(e.exposed)), {
    get(t, n) {
      if (n in t)
        return t[n];
      if (n in Kt)
        return Kt[n](e);
    },
    has(t, n) {
      return n in t || n in Kt;
    }
  })) : e.proxy;
}
const ha = /(?:^|[-_])\w/g, ga = (e) => e.replace(ha, (t) => t.toUpperCase()).replace(/[-_]/g, "");
function Ii(e, t = !0) {
  return q(e) ? e.displayName || e.name : e.name || t && e.__name;
}
function Er(e, t, n = !1) {
  let r = Ii(t);
  if (!r && t.__file) {
    const o = t.__file.match(/([^/\\]+)\.\w+$/);
    o && (r = o[1]);
  }
  if (!r && e && e.parent) {
    const o = (s) => {
      for (const i in s)
        if (s[i] === t)
          return i;
    };
    r = o(
      e.components || e.parent.type.components
    ) || o(e.appContext.components);
  }
  return r ? ga(r) : n ? "App" : "Anonymous";
}
function Ri(e) {
  return q(e) && "__vccOpts" in e;
}
const va = (e, t) => {
  const n = Sc(e, t, Sn);
  if (process.env.NODE_ENV !== "production") {
    const r = mo();
    r && r.appContext.config.warnRecursiveComputed && (n._warnRecursive = !0);
  }
  return n;
};
function Li(e, t, n) {
  try {
    lr(-1);
    const r = arguments.length;
    return r === 2 ? he(t) && !K(t) ? cn(t) ? ze(e, null, [t]) : ze(e, t) : ze(e, null, t) : (r > 3 ? n = Array.prototype.slice.call(arguments, 2) : r === 3 && cn(n) && (n = [n]), ze(e, t, n));
  } finally {
    lr(1);
  }
}
function ma() {
  if (process.env.NODE_ENV === "production" || typeof window > "u")
    return;
  const e = { style: "color:#3ba776" }, t = { style: "color:#1677ff" }, n = { style: "color:#f5222d" }, r = { style: "color:#eb2f96" }, o = {
    __vue_custom_formatter: !0,
    header(p) {
      if (!he(p))
        return null;
      if (p.__isVue)
        return ["div", e, "VueInstance"];
      if (Le(p)) {
        ct();
        const E = p.value;
        return lt(), [
          "div",
          {},
          ["span", e, h(p)],
          "<",
          c(E),
          ">"
        ];
      } else {
        if (nn(p))
          return [
            "div",
            {},
            ["span", e, Xe(p) ? "ShallowReactive" : "Reactive"],
            "<",
            c(p),
            `>${It(p) ? " (readonly)" : ""}`
          ];
        if (It(p))
          return [
            "div",
            {},
            ["span", e, Xe(p) ? "ShallowReadonly" : "Readonly"],
            "<",
            c(p),
            ">"
          ];
      }
      return null;
    },
    hasBody(p) {
      return p && p.__isVue;
    },
    body(p) {
      if (p && p.__isVue)
        return [
          "div",
          {},
          ...s(p.$)
        ];
    }
  };
  function s(p) {
    const E = [];
    p.type.props && p.props && E.push(i("props", re(p.props))), p.setupState !== me && E.push(i("setup", p.setupState)), p.data !== me && E.push(i("data", re(p.data)));
    const A = u(p, "computed");
    A && E.push(i("computed", A));
    const H = u(p, "inject");
    return H && E.push(i("injected", H)), E.push([
      "div",
      {},
      [
        "span",
        {
          style: r.style + ";opacity:0.66"
        },
        "$ (internal): "
      ],
      ["object", { object: p }]
    ]), E;
  }
  function i(p, E) {
    return E = Ve({}, E), Object.keys(E).length ? [
      "div",
      { style: "line-height:1.25em;margin-bottom:0.6em" },
      [
        "div",
        {
          style: "color:#476582"
        },
        p
      ],
      [
        "div",
        {
          style: "padding-left:1.25em"
        },
        ...Object.keys(E).map((A) => [
          "div",
          {},
          ["span", r, A + ": "],
          c(E[A], !1)
        ])
      ]
    ] : ["span", {}];
  }
  function c(p, E = !0) {
    return typeof p == "number" ? ["span", t, p] : typeof p == "string" ? ["span", n, JSON.stringify(p)] : typeof p == "boolean" ? ["span", r, p] : he(p) ? ["object", { object: E ? re(p) : p }] : ["span", n, String(p)];
  }
  function u(p, E) {
    const A = p.type;
    if (q(A))
      return;
    const H = {};
    for (const j in p.ctx)
      m(A, j, E) && (H[j] = p.ctx[j]);
    return H;
  }
  function m(p, E, A) {
    const H = p[A];
    if (K(H) && H.includes(E) || he(H) && E in H || p.extends && m(p.extends, E, A) || p.mixins && p.mixins.some((j) => m(j, E, A)))
      return !0;
  }
  function h(p) {
    return Xe(p) ? "ShallowRef" : p.effect ? "ComputedRef" : "Ref";
  }
  window.devtoolsFormatters ? window.devtoolsFormatters.push(o) : window.devtoolsFormatters = [o];
}
const zo = "3.5.22", xt = process.env.NODE_ENV !== "production" ? R : Re;
process.env.NODE_ENV;
process.env.NODE_ENV;
/**
* @vue/runtime-dom v3.5.22
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
let Xr;
const Go = typeof window < "u" && window.trustedTypes;
if (Go)
  try {
    Xr = /* @__PURE__ */ Go.createPolicy("vue", {
      createHTML: (e) => e
    });
  } catch (e) {
    process.env.NODE_ENV !== "production" && xt(`Error creating trusted types policy: ${e}`);
  }
const ki = Xr ? (e) => Xr.createHTML(e) : (e) => e, _a = "http://www.w3.org/2000/svg", ba = "http://www.w3.org/1998/Math/MathML", Et = typeof document < "u" ? document : null, Ko = Et && /* @__PURE__ */ Et.createElement("template"), Ea = {
  insert: (e, t, n) => {
    t.insertBefore(e, n || null);
  },
  remove: (e) => {
    const t = e.parentNode;
    t && t.removeChild(e);
  },
  createElement: (e, t, n, r) => {
    const o = t === "svg" ? Et.createElementNS(_a, e) : t === "mathml" ? Et.createElementNS(ba, e) : n ? Et.createElement(e, { is: n }) : Et.createElement(e);
    return e === "select" && r && r.multiple != null && o.setAttribute("multiple", r.multiple), o;
  },
  createText: (e) => Et.createTextNode(e),
  createComment: (e) => Et.createComment(e),
  setText: (e, t) => {
    e.nodeValue = t;
  },
  setElementText: (e, t) => {
    e.textContent = t;
  },
  parentNode: (e) => e.parentNode,
  nextSibling: (e) => e.nextSibling,
  querySelector: (e) => Et.querySelector(e),
  setScopeId(e, t) {
    e.setAttribute(t, "");
  },
  // __UNSAFE__
  // Reason: innerHTML.
  // Static content here can only come from compiled templates.
  // As long as the user only uses trusted templates, this is safe.
  insertStaticContent(e, t, n, r, o, s) {
    const i = n ? n.previousSibling : t.lastChild;
    if (o && (o === s || o.nextSibling))
      for (; t.insertBefore(o.cloneNode(!0), n), !(o === s || !(o = o.nextSibling)); )
        ;
    else {
      Ko.innerHTML = ki(
        r === "svg" ? `<svg>${e}</svg>` : r === "mathml" ? `<math>${e}</math>` : e
      );
      const c = Ko.content;
      if (r === "svg" || r === "mathml") {
        const u = c.firstChild;
        for (; u.firstChild; )
          c.appendChild(u.firstChild);
        c.removeChild(u);
      }
      t.insertBefore(c, n);
    }
    return [
      // first
      i ? i.nextSibling : t.firstChild,
      // last
      n ? n.previousSibling : t.lastChild
    ];
  }
}, Dt = "transition", dn = "animation", Dn = Symbol("_vtc"), Pi = {
  name: String,
  type: String,
  css: {
    type: Boolean,
    default: !0
  },
  duration: [String, Number, Object],
  enterFromClass: String,
  enterActiveClass: String,
  enterToClass: String,
  appearFromClass: String,
  appearActiveClass: String,
  appearToClass: String,
  leaveFromClass: String,
  leaveActiveClass: String,
  leaveToClass: String
}, ya = /* @__PURE__ */ Ve(
  {},
  Zs,
  Pi
), Na = (e) => (e.displayName = "Transition", e.props = ya, e), xa = /* @__PURE__ */ Na(
  (e, { slots: t }) => Li(el, wa(e), t)
), $t = (e, t = []) => {
  K(e) ? e.forEach((n) => n(...t)) : e && e(...t);
}, Yo = (e) => e ? K(e) ? e.some((t) => t.length > 1) : e.length > 1 : !1;
function wa(e) {
  const t = {};
  for (const $ in e)
    $ in Pi || (t[$] = e[$]);
  if (e.css === !1)
    return t;
  const {
    name: n = "v",
    type: r,
    duration: o,
    enterFromClass: s = `${n}-enter-from`,
    enterActiveClass: i = `${n}-enter-active`,
    enterToClass: c = `${n}-enter-to`,
    appearFromClass: u = s,
    appearActiveClass: m = i,
    appearToClass: h = c,
    leaveFromClass: p = `${n}-leave-from`,
    leaveActiveClass: E = `${n}-leave-active`,
    leaveToClass: A = `${n}-leave-to`
  } = e, H = Oa(o), j = H && H[0], _e = H && H[1], {
    onBeforeEnter: ne,
    onEnter: Z,
    onEnterCancelled: Q,
    onLeave: Oe,
    onLeaveCancelled: B,
    onBeforeAppear: ce = ne,
    onAppear: De = Z,
    onAppearCancelled: we = Q
  } = t, Y = ($, be, X, ke) => {
    $._enterCancelled = ke, Ft($, be ? h : c), Ft($, be ? m : i), X && X();
  }, ae = ($, be) => {
    $._isLeaving = !1, Ft($, p), Ft($, A), Ft($, E), be && be();
  }, ue = ($) => (be, X) => {
    const ke = $ ? De : Z, Me = () => Y(be, $, X);
    $t(ke, [be, Me]), Jo(() => {
      Ft(be, $ ? u : s), bt(be, $ ? h : c), Yo(ke) || qo(be, r, j, Me);
    });
  };
  return Ve(t, {
    onBeforeEnter($) {
      $t(ne, [$]), bt($, s), bt($, i);
    },
    onBeforeAppear($) {
      $t(ce, [$]), bt($, u), bt($, m);
    },
    onEnter: ue(!1),
    onAppear: ue(!0),
    onLeave($, be) {
      $._isLeaving = !0;
      const X = () => ae($, be);
      bt($, p), $._enterCancelled ? (bt($, E), Zo($)) : (Zo($), bt($, E)), Jo(() => {
        $._isLeaving && (Ft($, p), bt($, A), Yo(Oe) || qo($, r, _e, X));
      }), $t(Oe, [$, X]);
    },
    onEnterCancelled($) {
      Y($, !1, void 0, !0), $t(Q, [$]);
    },
    onAppearCancelled($) {
      Y($, !0, void 0, !0), $t(we, [$]);
    },
    onLeaveCancelled($) {
      ae($), $t(B, [$]);
    }
  });
}
function Oa(e) {
  if (e == null)
    return null;
  if (he(e))
    return [Ar(e.enter), Ar(e.leave)];
  {
    const t = Ar(e);
    return [t, t];
  }
}
function Ar(e) {
  const t = Bi(e);
  return process.env.NODE_ENV !== "production" && Rc(t, "<transition> explicit duration"), t;
}
function bt(e, t) {
  t.split(/\s+/).forEach((n) => n && e.classList.add(n)), (e[Dn] || (e[Dn] = /* @__PURE__ */ new Set())).add(t);
}
function Ft(e, t) {
  t.split(/\s+/).forEach((r) => r && e.classList.remove(r));
  const n = e[Dn];
  n && (n.delete(t), n.size || (e[Dn] = void 0));
}
function Jo(e) {
  requestAnimationFrame(() => {
    requestAnimationFrame(e);
  });
}
let Ca = 0;
function qo(e, t, n, r) {
  const o = e._endId = ++Ca, s = () => {
    o === e._endId && r();
  };
  if (n != null)
    return setTimeout(s, n);
  const { type: i, timeout: c, propCount: u } = Sa(e, t);
  if (!i)
    return r();
  const m = i + "end";
  let h = 0;
  const p = () => {
    e.removeEventListener(m, E), s();
  }, E = (A) => {
    A.target === e && ++h >= u && p();
  };
  setTimeout(() => {
    h < u && p();
  }, c + 1), e.addEventListener(m, E);
}
function Sa(e, t) {
  const n = window.getComputedStyle(e), r = (H) => (n[H] || "").split(", "), o = r(`${Dt}Delay`), s = r(`${Dt}Duration`), i = Xo(o, s), c = r(`${dn}Delay`), u = r(`${dn}Duration`), m = Xo(c, u);
  let h = null, p = 0, E = 0;
  t === Dt ? i > 0 && (h = Dt, p = i, E = s.length) : t === dn ? m > 0 && (h = dn, p = m, E = u.length) : (p = Math.max(i, m), h = p > 0 ? i > m ? Dt : dn : null, E = h ? h === Dt ? s.length : u.length : 0);
  const A = h === Dt && /\b(?:transform|all)(?:,|$)/.test(
    r(`${Dt}Property`).toString()
  );
  return {
    type: h,
    timeout: p,
    propCount: E,
    hasTransform: A
  };
}
function Xo(e, t) {
  for (; e.length < t.length; )
    e = e.concat(e);
  return Math.max(...t.map((n, r) => Qo(n) + Qo(e[r])));
}
function Qo(e) {
  return e === "auto" ? 0 : Number(e.slice(0, -1).replace(",", ".")) * 1e3;
}
function Zo(e) {
  return (e ? e.ownerDocument : document).body.offsetHeight;
}
function Da(e, t, n) {
  const r = e[Dn];
  r && (t = (t ? [t, ...r] : [...r]).join(" ")), t == null ? e.removeAttribute("class") : n ? e.setAttribute("class", t) : e.className = t;
}
const es = Symbol("_vod"), Ta = Symbol("_vsh"), Va = Symbol(process.env.NODE_ENV !== "production" ? "CSS_VAR_TEXT" : ""), Aa = /(?:^|;)\s*display\s*:/;
function Ma(e, t, n) {
  const r = e.style, o = Se(n);
  let s = !1;
  if (n && !o) {
    if (t)
      if (Se(t))
        for (const i of t.split(";")) {
          const c = i.slice(0, i.indexOf(":")).trim();
          n[c] == null && qn(r, c, "");
        }
      else
        for (const i in t)
          n[i] == null && qn(r, i, "");
    for (const i in n)
      i === "display" && (s = !0), qn(r, i, n[i]);
  } else if (o) {
    if (t !== n) {
      const i = r[Va];
      i && (n += ";" + i), r.cssText = n, s = Aa.test(n);
    }
  } else t && e.removeAttribute("style");
  es in e && (e[es] = s ? r.display : "", e[Ta] && (r.display = "none"));
}
const Ia = /[^\\];\s*$/, ts = /\s*!important$/;
function qn(e, t, n) {
  if (K(n))
    n.forEach((r) => qn(e, t, r));
  else if (n == null && (n = ""), process.env.NODE_ENV !== "production" && Ia.test(n) && xt(
    `Unexpected semicolon at the end of '${t}' style value: '${n}'`
  ), t.startsWith("--"))
    e.setProperty(t, n);
  else {
    const r = Ra(e, t);
    ts.test(n) ? e.setProperty(
      Mt(r),
      n.replace(ts, ""),
      "important"
    ) : e[r] = n;
  }
}
const ns = ["Webkit", "Moz", "ms"], Mr = {};
function Ra(e, t) {
  const n = Mr[t];
  if (n)
    return n;
  let r = ot(t);
  if (r !== "filter" && r in e)
    return Mr[t] = r;
  r = dr(r);
  for (let o = 0; o < ns.length; o++) {
    const s = ns[o] + r;
    if (s in e)
      return Mr[t] = s;
  }
  return t;
}
const rs = "http://www.w3.org/1999/xlink";
function os(e, t, n, r, o, s = tc(t)) {
  r && t.startsWith("xlink:") ? n == null ? e.removeAttributeNS(rs, t.slice(6, t.length)) : e.setAttributeNS(rs, t, n) : n == null || s && !bs(n) ? e.removeAttribute(t) : e.setAttribute(
    t,
    s ? "" : Rt(n) ? String(n) : n
  );
}
function ss(e, t, n, r, o) {
  if (t === "innerHTML" || t === "textContent") {
    n != null && (e[t] = t === "innerHTML" ? ki(n) : n);
    return;
  }
  const s = e.tagName;
  if (t === "value" && s !== "PROGRESS" && // custom elements may use _value internally
  !s.includes("-")) {
    const c = s === "OPTION" ? e.getAttribute("value") || "" : e.value, u = n == null ? (
      // #11647: value should be set as empty string for null and undefined,
      // but <input type="checkbox"> should be set as 'on'.
      e.type === "checkbox" ? "on" : ""
    ) : String(n);
    (c !== u || !("_value" in e)) && (e.value = u), n == null && e.removeAttribute(t), e._value = n;
    return;
  }
  let i = !1;
  if (n === "" || n == null) {
    const c = typeof e[t];
    c === "boolean" ? n = bs(n) : n == null && c === "string" ? (n = "", i = !0) : c === "number" && (n = 0, i = !0);
  }
  try {
    e[t] = n;
  } catch (c) {
    process.env.NODE_ENV !== "production" && !i && xt(
      `Failed setting prop "${t}" on <${s.toLowerCase()}>: value ${n} is invalid.`,
      c
    );
  }
  i && e.removeAttribute(o || t);
}
function La(e, t, n, r) {
  e.addEventListener(t, n, r);
}
function ka(e, t, n, r) {
  e.removeEventListener(t, n, r);
}
const is = Symbol("_vei");
function Pa(e, t, n, r, o = null) {
  const s = e[is] || (e[is] = {}), i = s[t];
  if (r && i)
    i.value = process.env.NODE_ENV !== "production" ? ls(r, t) : r;
  else {
    const [c, u] = $a(t);
    if (r) {
      const m = s[t] = Ua(
        process.env.NODE_ENV !== "production" ? ls(r, t) : r,
        o
      );
      La(e, c, m, u);
    } else i && (ka(e, c, i, u), s[t] = void 0);
  }
}
const cs = /(?:Once|Passive|Capture)$/;
function $a(e) {
  let t;
  if (cs.test(e)) {
    t = {};
    let r;
    for (; r = e.match(cs); )
      e = e.slice(0, e.length - r[0].length), t[r[0].toLowerCase()] = !0;
  }
  return [e[2] === ":" ? e.slice(3) : Mt(e.slice(2)), t];
}
let Ir = 0;
const Fa = /* @__PURE__ */ Promise.resolve(), ja = () => Ir || (Fa.then(() => Ir = 0), Ir = Date.now());
function Ua(e, t) {
  const n = (r) => {
    if (!r._vts)
      r._vts = Date.now();
    else if (r._vts <= n.attached)
      return;
    at(
      Ha(r, n.value),
      t,
      5,
      [r]
    );
  };
  return n.value = e, n.attached = ja(), n;
}
function ls(e, t) {
  return q(e) || K(e) ? e : (xt(
    `Wrong type passed as event handler to ${t} - did you forget @ or : in front of your prop?
Expected function or array of functions, received type ${typeof e}.`
  ), Re);
}
function Ha(e, t) {
  if (K(t)) {
    const n = e.stopImmediatePropagation;
    return e.stopImmediatePropagation = () => {
      n.call(e), e._stopped = !0;
    }, t.map(
      (r) => (o) => !o._stopped && r && r(o)
    );
  } else
    return t;
}
const as = (e) => e.charCodeAt(0) === 111 && e.charCodeAt(1) === 110 && // lowercase letter
e.charCodeAt(2) > 96 && e.charCodeAt(2) < 123, Ba = (e, t, n, r, o, s) => {
  const i = o === "svg";
  t === "class" ? Da(e, r, i) : t === "style" ? Ma(e, n, r) : Tn(t) ? Xn(t) || Pa(e, t, n, r, s) : (t[0] === "." ? (t = t.slice(1), !0) : t[0] === "^" ? (t = t.slice(1), !1) : Wa(e, t, r, i)) ? (ss(e, t, r), !e.tagName.includes("-") && (t === "value" || t === "checked" || t === "selected") && os(e, t, r, i, s, t !== "value")) : /* #11081 force set props for possible async custom element */ e._isVueCE && (/[A-Z]/.test(t) || !Se(r)) ? ss(e, ot(t), r, s, t) : (t === "true-value" ? e._trueValue = r : t === "false-value" && (e._falseValue = r), os(e, t, r, i));
};
function Wa(e, t, n, r) {
  if (r)
    return !!(t === "innerHTML" || t === "textContent" || t in e && as(t) && q(n));
  if (t === "spellcheck" || t === "draggable" || t === "translate" || t === "autocorrect" || t === "form" || t === "list" && e.tagName === "INPUT" || t === "type" && e.tagName === "TEXTAREA")
    return !1;
  if (t === "width" || t === "height") {
    const o = e.tagName;
    if (o === "IMG" || o === "VIDEO" || o === "CANVAS" || o === "SOURCE")
      return !1;
  }
  return as(t) && Se(n) ? !1 : t in e;
}
const za = /* @__PURE__ */ Ve({ patchProp: Ba }, Ea);
let fs;
function Ga() {
  return fs || (fs = $l(za));
}
const Ka = ((...e) => {
  const t = Ga().createApp(...e);
  process.env.NODE_ENV !== "production" && (Ja(t), qa(t));
  const { mount: n } = t;
  return t.mount = (r) => {
    const o = Xa(r);
    if (!o) return;
    const s = t._component;
    !q(s) && !s.render && !s.template && (s.template = o.innerHTML), o.nodeType === 1 && (o.textContent = "");
    const i = n(o, !1, Ya(o));
    return o instanceof Element && (o.removeAttribute("v-cloak"), o.setAttribute("data-v-app", "")), i;
  }, t;
});
function Ya(e) {
  if (e instanceof SVGElement)
    return "svg";
  if (typeof MathMLElement == "function" && e instanceof MathMLElement)
    return "mathml";
}
function Ja(e) {
  Object.defineProperty(e.config, "isNativeTag", {
    value: (t) => Xi(t) || Qi(t) || Zi(t),
    writable: !1
  });
}
function qa(e) {
  {
    const t = e.config.isCustomElement;
    Object.defineProperty(e.config, "isCustomElement", {
      get() {
        return t;
      },
      set() {
        xt(
          "The `isCustomElement` config option is deprecated. Use `compilerOptions.isCustomElement` instead."
        );
      }
    });
    const n = e.config.compilerOptions, r = 'The `compilerOptions` config option is only respected when using a build of Vue.js that includes the runtime compiler (aka "full build"). Since you are using the runtime-only build, `compilerOptions` must be passed to `@vue/compiler-dom` in the build setup instead.\n- For vue-loader: pass it via vue-loader\'s `compilerOptions` loader option.\n- For vue-cli: see https://cli.vuejs.org/guide/webpack.html#modifying-options-of-a-loader\n- For vite: pass it via @vitejs/plugin-vue options. See https://github.com/vitejs/vite-plugin-vue/tree/main/packages/plugin-vue#example-for-passing-options-to-vuecompiler-sfc';
    Object.defineProperty(e.config, "compilerOptions", {
      get() {
        return xt(r), n;
      },
      set() {
        xt(r);
      }
    });
  }
}
function Xa(e) {
  if (Se(e)) {
    const t = document.querySelector(e);
    return process.env.NODE_ENV !== "production" && !t && xt(
      `Failed to mount app: mount target selector "${e}" returned null.`
    ), t;
  }
  return process.env.NODE_ENV !== "production" && window.ShadowRoot && e instanceof window.ShadowRoot && e.mode === "closed" && xt(
    'mounting on a ShadowRoot with `{mode: "closed"}` may lead to unpredictable bugs'
  ), e;
}
/**
* vue v3.5.22
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
function Qa() {
  ma();
}
process.env.NODE_ENV !== "production" && Qa();
function Za(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var Rr = { exports: {} }, us;
function ef() {
  return us || (us = 1, (function(e) {
    (function(t) {
      var n = typeof window == "object" && !!window.document, r = n ? window : Object;
      t(r, n), e.exports && (e.exports = r.Recorder);
    })(function(t, n) {
      var r = function() {
      }, o = function(d) {
        return typeof d == "number";
      }, s = function(d) {
        return JSON.stringify(d);
      }, i = function(d) {
        return new oe(d);
      }, c = i.LM = "2025-01-11 09:28", u = "https://github.com/xiangyuecn/Recorder", m = "Recorder", h = "getUserMedia", p = "srcSampleRate", E = "sampleRate", A = "bitRate", H = "catch", j = t[m];
      if (j && j.LM == c) {
        j.CLog(j.i18n.$T("K8zP::重复导入{1}", 0, m), 3);
        return;
      }
      i.IsOpen = function() {
        var d = i.Stream;
        if (d) {
          var g = be(d), f = g[0];
          if (f) {
            var _ = f.readyState;
            return _ == "live" || _ == f.LIVE;
          }
        }
        return !1;
      }, i.BufferSize = 4096, i.Destroy = function() {
        X(m + " Destroy"), ue();
        for (var d in _e)
          _e[d]();
      };
      var _e = {};
      i.BindDestroy = function(d, g) {
        _e[d] = g;
      }, i.Support = function() {
        if (!n) return !1;
        var d = navigator.mediaDevices || {};
        return d[h] || (d = navigator, d[h] || (d[h] = d.webkitGetUserMedia || d.mozGetUserMedia || d.msGetUserMedia)), !(!d[h] || (i.Scope = d, !i.GetContext()));
      }, i.GetContext = function(d) {
        if (!n) return null;
        var g = window.AudioContext;
        if (g || (g = window.webkitAudioContext), !g)
          return null;
        var f = i.Ctx, _ = 0;
        return f || (f = i.Ctx = new g(), _ = 1, i.NewCtxs = i.NewCtxs || [], i.BindDestroy("Ctx", function() {
          var C = i.Ctx;
          C && C.close && (ne(C), i.Ctx = 0);
          var V = i.NewCtxs;
          i.NewCtxs = [];
          for (var T = 0; T < V.length; T++) ne(V[T]);
        })), d && f.close && (_ || (f._useC || ne(f), f = new g()), f._useC = 1, i.NewCtxs.push(f)), f;
      }, i.CloseNewCtx = function(d) {
        if (d && d.close) {
          ne(d);
          for (var g = i.NewCtxs || [], f = g.length, _ = 0; _ < g.length; _++)
            if (g[_] == d) {
              g.splice(_, 1);
              break;
            }
          X(k("mSxV::剩{1}个GetContext未close", 0, f + "-1=" + g.length), g.length ? 3 : 0);
        }
      };
      var ne = function(d) {
        if (d && d.close && !d._isC && (d._isC = 1, d.state != "closed"))
          try {
            d.close();
          } catch (g) {
            X("ctx close err", 1, g);
          }
      }, Z = i.ResumeCtx = function(d, g, f, _) {
        var C = 0, V = 0, T = 0, l = 0, a = "EventListener", v = "ResumeCtx ", x = function(S, y) {
          V && w(), C || (C = 1, S && _(S, l), y && f(l)), y && (!d._LsSC && d["add" + a] && d["add" + a]("statechange", b), d._LsSC = 1, T = 1);
        }, w = function(S) {
          if (!(S && V)) {
            V = S ? 1 : 0;
            for (var y = ["focus", "mousedown", "mouseup", "touchstart", "touchend"], D = 0; D < y.length; D++)
              window[(S ? "add" : "remove") + a](y[D], b, !0);
          }
        }, b = function() {
          var S = d.state, y = Q(S);
          if (!C && !g(y ? ++l : l)) return x();
          y ? (T && X(v + "sc " + S, 3), w(1), d.resume().then(function() {
            T && X(v + "sc " + d.state), x(0, 1);
          })[H](function(D) {
            X(v + "error", 1, D), Q(d.state) || x(D.message || "error");
          })) : S == "closed" ? (T && !d._isC && X(v + "sc " + S, 1), x("ctx closed")) : x(0, 1);
        };
        b();
      }, Q = i.CtxSpEnd = function(d) {
        return d == "suspended" || d == "interrupted";
      }, Oe = function(d) {
        var g = d.state, f = "ctx.state=" + g;
        return Q(g) && (f += k("nMIy::（注意：ctx不是running状态，rec.open和start至少要有一个在用户操作(触摸、点击等)时进行调用，否则将在rec.start时尝试进行ctx.resume，可能会产生兼容性问题(仅iOS)，请参阅文档中runningContext配置）")), f;
      }, B = "ConnectEnableWebM";
      i[B] = !0;
      var ce = "ConnectEnableWorklet";
      i[ce] = !1;
      var De = function(d) {
        var g = d.BufferSize || i.BufferSize, f = d.Stream, _ = f._c, C = _[E], V = {}, T = be(f), l = T[0], a = null, v = "";
        if (l && l.getSettings) {
          a = l.getSettings();
          var x = a[E];
          x && x != C && (v = k("eS8i::Stream的采样率{1}不等于{2}，将进行采样率转换（注意：音质不会变好甚至可能变差），主要在移动端未禁用回声消除时会产生此现象，浏览器有回声消除时可能只会返回16k采样率的音频数据，", 0, x, C));
        }
        f._ts = a, X(v + "Stream TrackSet: " + s(a), v ? 3 : 0);
        var w = function(ee) {
          var J = f._m = _.createMediaStreamSource(f), te = _.destination, ge = "createMediaStreamDestination";
          _[ge] && (te = f._d = _[ge]()), J.connect(ee), ee.connect(te);
        }, b, S, y, D = "", O = f._call, M = function(ee, J) {
          for (var te in O) {
            if (J != C) {
              V.index = 0, V = i.SampleData([ee], J, C, V, { _sum: 1 });
              var ge = V.data, de = V._sum;
            } else {
              V = {};
              for (var ve = ee.length, ge = new Int16Array(ve), de = 0, Ce = 0; Ce < ve; Ce++) {
                var ye = Math.max(-1, Math.min(1, ee[Ce]));
                ye = ye < 0 ? ye * 32768 : ye * 32767, ge[Ce] = ye, de += Math.abs(ye);
              }
            }
            for (var xe in O)
              O[xe](ge, de);
            return;
          }
        }, N = "ScriptProcessor", I = "audioWorklet", L = m + " " + I, W = "RecProc", U = "MediaRecorder", G = U + ".WebM.PCM", F = _.createScriptProcessor || _.createJavaScriptNode, z = k("ZGlf::。由于{1}内部1秒375次回调，在移动端可能会有性能问题导致回调丢失录音变短，PC端无影响，暂不建议开启{1}。", 0, I), P = function() {
          S = f.isWorklet = !1, Y(f), X(k("7TU0::Connect采用老的{1}，", 0, N) + Ne.get(
            i[ce] ? k("JwCL::但已设置{1}尝试启用{2}", 2) : k("VGjB::可设置{1}尝试启用{2}", 2),
            [m + "." + ce + "=true", I]
          ) + D + z, 3);
          var ee = f._p = F.call(_, g, 1, 1);
          w(ee), ee.onaudioprocess = function(J) {
            var te = J.inputBuffer.getChannelData(0);
            M(te, C);
          };
        }, ie = function() {
          b = f.isWebM = !1, ae(f), S = f.isWorklet = !F || i[ce];
          var ee = window.AudioWorkletNode;
          if (!(S && _[I] && ee)) {
            P();
            return;
          }
          var J = function() {
            var Ce = function(xe) {
              return xe.toString().replace(/^function|DEL_/g, "").replace(/\$RA/g, L);
            }, ye = "class " + W + " extends AudioWorkletProcessor{";
            return ye += "constructor " + Ce(function(xe) {
              DEL_super(xe);
              var $e = this, Ee = xe.processorOptions.bufferSize;
              $e.bufferSize = Ee, $e.buffer = new Float32Array(Ee * 2), $e.pos = 0, $e.port.onmessage = function(Pe) {
                Pe.data.kill && ($e.kill = !0, $C.log("$RA kill call"));
              }, $C.log("$RA .ctor call", xe);
            }), ye += "process " + Ce(function(xe, $e, Ee) {
              var Pe = this, Jt = Pe.bufferSize, Ct = Pe.buffer, St = Pe.pos;
              if (xe = (xe[0] || [])[0] || [], xe.length) {
                Ct.set(xe, St), St += xe.length;
                var Lt = ~~(St / Jt) * Jt;
                if (Lt) {
                  this.port.postMessage({ val: Ct.slice(0, Lt) });
                  var Pn = Ct.subarray(Lt, St);
                  Ct = new Float32Array(Jt * 2), Ct.set(Pn), St = Pn.length, Pe.buffer = Ct;
                }
                Pe.pos = St;
              }
              return !Pe.kill;
            }), ye += '}try{registerProcessor("' + W + '", ' + W + ')}catch(e){$C.error("' + L + ' Reg Error",e)}', ye = ye.replace(/\$C\./g, "console."), "data:text/javascript;base64," + btoa(unescape(encodeURIComponent(ye)));
          }, te = function() {
            return S && f._na;
          }, ge = f._na = function() {
            y !== "" && (clearTimeout(y), y = setTimeout(function() {
              y = 0, te() && (X(k("MxX1::{1}未返回任何音频，恢复使用{2}", 0, I, N), 3), F && P());
            }, 500));
          }, de = function() {
            if (te()) {
              var Ce = f._n = new ee(_, W, {
                processorOptions: { bufferSize: g }
              });
              w(Ce), Ce.port.onmessage = function(ye) {
                y && (clearTimeout(y), y = ""), te() ? M(ye.data.val, C) : S || X(k("XUap::{1}多余回调", 0, I), 3);
              }, X(k("yOta::Connect采用{1}，设置{2}可恢复老式{3}", 0, I, m + "." + ce + "=false", N) + D + z, 3);
            }
          }, ve = function() {
            if (te()) {
              if (_[W]) {
                de();
                return;
              }
              var Ce = J();
              _[I].addModule(Ce).then(function(ye) {
                te() && (_[W] = 1, de(), y && ge());
              })[H](function(ye) {
                X(I + ".addModule Error", 1, ye), te() && P();
              });
            }
          };
          Z(_, function() {
            return te();
          }, ve, ve);
        }, fe = function() {
          var ee = window[U], J = "ondataavailable", te = "audio/webm; codecs=pcm";
          b = f.isWebM = i[B];
          var ge = ee && J in ee.prototype && ee.isTypeSupported(te);
          if (D = ge ? "" : k("VwPd::（此浏览器不支持{1}）", 0, G), !b || !ge) {
            ie();
            return;
          }
          var de = function() {
            return b && f._ra;
          };
          f._ra = function() {
            y !== "" && (clearTimeout(y), y = setTimeout(function() {
              de() && (X(k("vHnb::{1}未返回任何音频，降级使用{2}", 0, U, I), 3), ie());
            }, 500));
          };
          var ve = Object.assign({ mimeType: te }, i.ConnectWebMOptions), Ce = f._r = new ee(f, ve), ye = f._rd = {};
          Ce[J] = function(xe) {
            var $e = new FileReader();
            $e.onloadend = function() {
              if (de()) {
                var Ee = se(new Uint8Array($e.result), ye);
                if (!Ee) return;
                if (Ee == -1) {
                  ie();
                  return;
                }
                y && (clearTimeout(y), y = ""), M(Ee, ye.webmSR);
              } else b || X(k("O9P7::{1}多余回调", 0, U), 3);
            }, $e.readAsArrayBuffer(xe.data);
          };
          try {
            Ce.start(~~(g / 48)), X(k("LMEm::Connect采用{1}，设置{2}可恢复使用{3}或老式{4}", 0, G, m + "." + B + "=false", I, N));
          } catch (xe) {
            X("mr start err", 1, xe), ie();
          }
        };
        fe();
      }, we = function(d) {
        d._na && d._na(), d._ra && d._ra();
      }, Y = function(d) {
        d._na = null, d._n && (d._n.port.postMessage({ kill: !0 }), d._n.disconnect(), d._n = null);
      }, ae = function(d) {
        if (d._ra = null, d._r) {
          try {
            d._r.stop();
          } catch (g) {
            X("mr stop err", 1, g);
          }
          d._r = null;
        }
      }, ue = function(d) {
        d = d || i;
        var g = d == i, f = d.Stream;
        f && (f._m && (f._m.disconnect(), f._m = null), !f._RC && f._c && i.CloseNewCtx(f._c), f._RC = null, f._c = null, f._d && ($(f._d.stream), f._d = null), f._p && (f._p.disconnect(), f._p.onaudioprocess = f._p = null), Y(f), ae(f), g && $(f)), d.Stream = 0;
      }, $ = i.StopS_ = function(d) {
        for (var g = be(d), f = 0; f < g.length; f++) {
          var _ = g[f];
          _.stop && _.stop();
        }
        d.stop && d.stop();
      }, be = function(d) {
        var g = 0, f = 0, _ = [];
        d.getAudioTracks && (g = d.getAudioTracks(), f = d.getVideoTracks()), g || (g = d.audioTracks, f = d.videoTracks);
        for (var C = 0, V = g ? g.length : 0; C < V; C++) _.push(g[C]);
        for (var C = 0, V = f ? f.length : 0; C < V; C++) _.push(f[C]);
        return _;
      };
      i.SampleData = function(d, g, f, _, C) {
        var V = "SampleData";
        _ || (_ = {});
        var T = _.index || 0, l = _.offset || 0, a = _.raisePrev || 0, v = _.filter;
        if (v && v.fn && (v.sr && v.sr != g || v.srn && v.srn != f) && (v = null, X(k("d48C::{1}的filter采样率变了，重设滤波", 0, V), 3)), !v)
          if (f <= g) {
            var x = f > g * 3 / 4 ? 0 : f / 2 * 3 / 4;
            v = { fn: x ? i.IIRFilter(!0, g, x) : 0 };
          } else {
            var x = g > f * 3 / 4 ? 0 : g / 2 * 3 / 4;
            v = { fn: x ? i.IIRFilter(!0, f, x) : 0 };
          }
        v.sr = g, v.srn = f;
        var w = v.fn, b = _.frameNext || [];
        C || (C = {});
        var S = C.frameSize || 1;
        C.frameType && (S = C.frameType == "mp3" ? 1152 : 1);
        var y = C._sum, D = 0, O = d.length;
        T > O + 1 && X(k("tlbC::{1}似乎传入了未重置chunk {2}", 0, V, T + ">" + O), 3);
        for (var M = 0, N = T; N < O; N++)
          M += d[N].length;
        var I = g / f;
        if (I > 1)
          M = Math.max(0, M - Math.floor(l)), M = Math.floor(M / I);
        else if (I < 1) {
          var L = 1 / I;
          M = Math.floor(M * L);
        }
        M += b.length;
        for (var W = new Int16Array(M), U = 0, N = 0; N < b.length; N++)
          W[U] = b[N], U++;
        for (; T < O; T++) {
          var G = d[T], F = G instanceof Float32Array, N = l, z = G.length, P = w && w.Embed, ie = 0, fe = 0, ee = 0, J = 0;
          if (I < 1) {
            for (var te = U + N, ge = a, de = 0; de < z; de++) {
              var ve = G[de];
              F && (ve = Math.max(-1, Math.min(1, ve)), ve = ve < 0 ? ve * 32768 : ve * 32767);
              var Ce = Math.floor(te);
              te += L;
              for (var ye = Math.floor(te), xe = (ve - ge) / (ye - Ce), $e = 1; Ce < ye; Ce++, $e++) {
                var Ee = Math.floor(ge + $e * xe);
                P ? (ee = Ee, J = P.b0 * ee + P.b1 * P.x1 + P.b0 * P.x2 - P.a1 * P.y1 - P.a2 * P.y2, P.x2 = P.x1, P.x1 = ee, P.y2 = P.y1, P.y1 = J, Ee = J) : Ee = w ? w(Ee) : Ee, Ee > 32767 ? Ee = 32767 : Ee < -32768 && (Ee = -32768), y && (D += Math.abs(Ee)), W[Ce] = Ee, U++;
              }
              ge = a = ve, N += L;
            }
            l = N % 1;
            continue;
          }
          for (var de = 0, Pe = 0; de < z; de++, Pe++) {
            if (Pe < z) {
              var ve = G[Pe];
              F && (ve = Math.max(-1, Math.min(1, ve)), ve = ve < 0 ? ve * 32768 : ve * 32767), P ? (ee = ve, J = P.b0 * ee + P.b1 * P.x1 + P.b0 * P.x2 - P.a1 * P.y1 - P.a2 * P.y2, P.x2 = P.x1, P.x1 = ee, P.y2 = P.y1, P.y1 = J) : J = w ? w(ve) : ve;
            }
            if (ie = fe, fe = J, Pe == 0) {
              de--;
              continue;
            }
            var Jt = Math.floor(N);
            if (de == Jt) {
              var Ct = Math.ceil(N), St = N - Jt, Lt = ie, Pn = Ct < z ? fe : Lt, qt = Lt + (Pn - Lt) * St;
              qt > 32767 ? qt = 32767 : qt < -32768 && (qt = -32768), y && (D += Math.abs(qt)), W[U] = qt, U++, N += I;
            }
          }
          l = Math.max(0, N - z);
        }
        I < 1 && U + 1 == M && (M--, W = new Int16Array(W.buffer.slice(0, M * 2))), U - 1 != M && U != M && X(V + " idx:" + U + " != size:" + M, 3), b = null;
        var bo = M % S;
        if (bo > 0) {
          var Eo = (M - bo) * 2;
          b = new Int16Array(W.buffer.slice(Eo)), W = new Int16Array(W.buffer.slice(0, Eo));
        }
        var yo = {
          index: T,
          offset: l,
          raisePrev: a,
          filter: v,
          frameNext: b,
          sampleRate: f,
          data: W
        };
        return y && (yo._sum = D), yo;
      }, i.IIRFilter = function(d, g, f) {
        var _ = 2 * Math.PI * f / g, C = Math.sin(_), V = Math.cos(_), T = C / 2, l = 1 + T, a = -2 * V / l, v = (1 - T) / l;
        if (d)
          var x = (1 - V) / 2 / l, w = (1 - V) / l;
        else
          var x = (1 + V) / 2 / l, w = -(1 + V) / l;
        var b = 0, S = 0, y = 0, D = 0, O = 0, M = function(N) {
          return y = x * N + w * b + x * S - a * D - v * O, S = b, b = N, O = D, D = y, y;
        };
        return M.Embed = { x1: 0, x2: 0, y1: 0, y2: 0, b0: x, b1: w, a1: a, a2: v }, M;
      }, i.PowerLevel = function(d, g) {
        var f = d / g || 0, _;
        return f < 1251 ? _ = Math.round(f / 1250 * 10) : _ = Math.round(Math.min(100, Math.max(0, (1 + Math.log(f / 1e4) / Math.log(10)) * 100))), _;
      }, i.PowerDBFS = function(d) {
        var g = Math.max(0.1, d || 0), f = 32767;
        return g = Math.min(g, f), g = 20 * Math.log(g / f) / Math.log(10), Math.max(-100, Math.round(g));
      }, i.CLog = function(d, g) {
        if (typeof console == "object") {
          var f = /* @__PURE__ */ new Date(), _ = ("0" + f.getMinutes()).substr(-2) + ":" + ("0" + f.getSeconds()).substr(-2) + "." + ("00" + f.getMilliseconds()).substr(-3), C = this && this.envIn && this.envCheck && this.id, V = ["[" + _ + " " + m + (C ? ":" + C : "") + "]" + d], T = arguments, l = i.CLog, a = 2, v = l.log || console.log;
          for (o(g) ? v = g == 1 ? l.error || console.error : g == 3 ? l.warn || console.warn : v : a = 1; a < T.length; a++)
            V.push(T[a]);
          ke ? v && v("[IsLoser]" + V[0], V.length > 1 ? V : "") : v.apply(console, V);
        }
      };
      var X = function() {
        i.CLog.apply(this, arguments);
      }, ke = !0;
      try {
        ke = !console.log.apply;
      } catch {
      }
      var Me = 0;
      function oe(d) {
        var g = this;
        g.id = ++Me, kn();
        var f = {
          type: "mp3",
          onProcess: r
          //fn(buffers,powerLevel,bufferDuration,bufferSampleRate,newBufferIdx,asyncEnd) buffers=[[Int16,...],...]：缓冲的PCM数据，为从开始录音到现在的所有pcm片段；powerLevel：当前缓冲的音量级别0-100，bufferDuration：已缓冲时长，bufferSampleRate：缓冲使用的采样率（当type支持边录边转码(Worker)时，此采样率和设置的采样率相同，否则不一定相同）；newBufferIdx:本次回调新增的buffer起始索引；asyncEnd:fn() 如果onProcess是异步的(返回值为true时)，处理完成时需要调用此回调，如果不是异步的请忽略此参数，此方法回调时必须是真异步（不能真异步时需用setTimeout包裹）。onProcess返回值：如果返回true代表开启异步模式，在某些大量运算的场合异步是必须的，必须在异步处理完成时调用asyncEnd(不能真异步时需用setTimeout包裹)，在onProcess执行后新增的buffer会全部替换成空数组，因此本回调开头应立即将newBufferIdx到本次回调结尾位置的buffer全部保存到另外一个数组内，处理完成后写回buffers中本次回调的结尾位置。
          //*******高级设置******
          //,sourceStream:MediaStream Object
          //可选直接提供一个媒体流，从这个流中录制、实时处理音频数据（当前Recorder实例独享此流）；不提供时为普通的麦克风录音，由getUserMedia提供音频流（所有Recorder实例共享同一个流）
          //比如：audio、video标签dom节点的captureStream方法（实验特性，不同浏览器支持程度不高）返回的流；WebRTC中的remote流；自己创建的流等
          //注意：流内必须至少存在一条音轨(Audio Track)，比如audio标签必须等待到可以开始播放后才会有音轨，否则open会失败
          //,runningContext:AudioContext
          //可选提供一个state为running状态的AudioContext对象(ctx)；默认会在rec.open时自动创建一个新的ctx，无用户操作（触摸、点击等）时调用rec.open的ctx.state可能为suspended，会在rec.start时尝试进行ctx.resume，如果也无用户操作ctx.resume可能不会恢复成running状态（目前仅iOS上有此兼容性问题），导致无法去读取媒体流，这时请提前在用户操作时调用Recorder.GetContext(true)来得到一个running状态AudioContext（用完需调用CloseNewCtx(ctx)关闭）
          //,audioTrackSet:{ deviceId:"",groupId:"", autoGainControl:true, echoCancellation:true, noiseSuppression:true }
          //普通麦克风录音时getUserMedia方法的audio配置参数，比如指定设备id，回声消除、降噪开关；注意：提供的任何配置值都不一定会生效
          //由于麦克风是全局共享的，所以新配置后需要close掉以前的再重新open
          //同样可配置videoTrackSet，更多参考: https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackConstraints
          //,disableEnvInFix:false 内部参数，禁用设备卡顿时音频输入丢失补偿功能
          //,takeoffEncodeChunk:NOOP //fn(chunkBytes) chunkBytes=[Uint8,...]：实时编码环境下接管编码器输出，当编码器实时编码出一块有效的二进制音频数据时实时回调此方法；参数为二进制的Uint8Array，就是编码出来的音频数据片段，所有的chunkBytes拼接在一起即为完整音频。本实现的想法最初由QQ2543775048提出
          //当提供此回调方法时，将接管编码器的数据输出，编码器内部将放弃存储生成的音频数据；如果当前编码器或环境不支持实时编码处理，将在open时直接走fail逻辑
          //因此提供此回调后调用stop方法将无法获得有效的音频数据，因为编码器内没有音频数据，因此stop时返回的blob将是一个字节长度为0的blob
          //大部分录音格式编码器都支持实时编码（边录边转码），比如mp3格式：会实时的将编码出来的mp3片段通过此方法回调，所有的chunkBytes拼接到一起即为完整的mp3，此种拼接的结果比mock方法实时生成的音质更加，因为天然避免了首尾的静默
          //不支持实时编码的录音格式不可以提供此回调（wav格式不支持，因为wav文件头中需要提供文件最终长度），提供了将在open时直接走fail逻辑
        };
        for (var _ in d)
          f[_] = d[_];
        g.set = f;
        var C = f[A], V = f[E];
        (C && !o(C) || V && !o(V)) && g.CLog(k.G("IllegalArgs-1", [k("VtS4::{1}和{2}必须是数值", 0, E, A)]), 1, d), f[A] = +C || 16, f[E] = +V || 16e3, g.state = 0, g._S = 9, g.Sync = { O: 9, C: 9 };
      }
      i.Sync = {
        /*open*/
        O: 9,
        /*close*/
        C: 9
      }, i.prototype = oe.prototype = {
        CLog: X,
        _streamStore: function() {
          return this.set.sourceStream ? this : i;
        },
        _streamGet: function() {
          return this._streamStore().Stream;
        },
        _streamCtx: function() {
          var d = this._streamGet();
          return d && d._c;
        },
        open: function(d, g) {
          var f = this, _ = f.set, C = f._streamStore(), V = 0;
          d = d || r;
          var T = function(F, z) {
            z = !!z, f.CLog(k("5tWi::录音open失败：") + F + ",isUserNotAllow:" + z, 1), V && i.CloseNewCtx(V), g && g(F, z);
          };
          f._streamTag = h;
          var l = function() {
            f.CLog("open ok, id:" + f.id + " stream:" + f._streamTag), d(), f._SO = 0;
          }, a = C.Sync, v = ++a.O, x = a.C;
          f._O = f._O_ = v, f._SO = f._S;
          var w = function() {
            if (x != a.C || !f._O) {
              var F = k("dFm8::open被取消");
              return v == a.O ? f.close() : F = k("VtJO::open被中断"), T(F), !0;
            }
          };
          if (!n) {
            T(k.G("NonBrowser-1", ["open"]) + k("EMJq::，可尝试使用RecordApp解决方案") + "(" + u + "/tree/master/app-support-sample)");
            return;
          }
          var b = f.envCheck({ envName: "H5", canProcess: !0 });
          if (b) {
            T(k("A5bm::不能录音：") + b);
            return;
          }
          var S, y = function() {
            S = _.runningContext, S || (S = V = i.GetContext(!0));
          };
          if (_.sourceStream) {
            if (f._streamTag = "set.sourceStream", !i.GetContext()) {
              T(k("1iU7::不支持此浏览器从流中获取录音"));
              return;
            }
            y(), ue(C);
            var D = f.Stream = _.sourceStream;
            D._c = S, D._RC = _.runningContext, D._call = {};
            try {
              De(C);
            } catch (F) {
              ue(C), T(k("BTW2::从流中打开录音失败：") + F.message);
              return;
            }
            l();
            return;
          }
          var O = function(F, z) {
            try {
              window.top.a;
            } catch {
              T(k("Nclz::无权录音(跨域，请尝试给iframe添加麦克风访问策略，如{1})", 0, 'allow="camera;microphone"'));
              return;
            }
            M(1, F) && (/Found/i.test(F) ? T(z + k("jBa9::，无可用麦克风")) : T(z));
          }, M = function(F, z) {
            if (/Permission|Allow/i.test(z))
              F && T(k("gyO5::用户拒绝了录音权限"), !0);
            else if (window.isSecureContext === !1)
              F && T(k("oWNo::浏览器禁止不安全页面录音，可开启https解决"));
            else
              return 1;
          };
          if (i.IsOpen()) {
            l();
            return;
          }
          if (!i.Support()) {
            O("", k("COxc::此浏览器不支持录音"));
            return;
          }
          y();
          var N = function(F) {
            setTimeout(function() {
              F._call = {};
              var z = i.Stream;
              z && (ue(), F._call = z._call), i.Stream = F, F._c = S, F._RC = _.runningContext, !w() && (i.IsOpen() ? (z && f.CLog(k("upb8::发现同时多次调用open"), 1), De(C), l()) : T(k("Q1GA::录音功能无效：无音频流")));
            }, 100);
          }, I = function(F) {
            var z = F.name || F.message || F.code + ":" + F, P = "";
            L == 1 && M(0, z) && (P = k("KxE2::，将尝试禁用回声消除后重试"));
            var ie = k("xEQR::请求录音权限错误"), fe = k("bDOG::无法录音：");
            f.CLog(ie + P + "|" + F, P || U ? 3 : 1, F), P ? (W = z, U = F, G(1)) : U ? (f.CLog(ie + "|" + U, 1, U), O(W, fe + U)) : O(z, fe + F);
          }, L = 0, W, U, G = function(F) {
            L++;
            var z = "audioTrackSet", P = "autoGainControl", ie = "echoCancellation", fe = "noiseSuppression", ee = z + ":{" + ie + "," + fe + "," + P + "}", J = JSON.parse(s(_[z] || !0));
            f.CLog("open... " + L + " " + z + ":" + s(J)), F && (typeof J != "object" && (J = {}), J[P] = !1, J[ie] = !1, J[fe] = !1), J[E] && f.CLog(k("IjL3::注意：已配置{1}参数，可能会出现浏览器不能正确选用麦克风、移动端无法启用回声消除等现象", 0, z + "." + E), 3);
            var te = { audio: J, video: _.videoTrackSet || !1 };
            try {
              var ge = i.Scope[h](te, N, I);
            } catch (de) {
              f.CLog(h, 3, de), te = { audio: !0, video: !1 }, ge = i.Scope[h](te, N, I);
            }
            f.CLog(h + "(" + s(te) + ") " + Oe(S) + k("RiWe::，未配置 {1} 时浏览器可能会自动启用回声消除，移动端未禁用回声消除时可能会降低系统播放音量（关闭录音后可恢复）和仅提供16k采样率的音频流（不需要回声消除时可明确配置成禁用来获得48k高音质的流），请参阅文档中{2}配置", 0, ee, z) + "(" + u + ") LM:" + c + " UA:" + navigator.userAgent), ge && ge.then && ge.then(N)[H](I);
          };
          G();
        },
        close: function(d) {
          d = d || r;
          var g = this, f = g._streamStore();
          g._stop();
          var _ = " stream:" + g._streamTag, C = f.Sync;
          if (g._O = 0, g._O_ != C.O) {
            g.CLog(k("hWVz::close被忽略（因为同时open了多个rec，只有最后一个会真正close）") + _, 3), d();
            return;
          }
          C.C++, ue(f), g.CLog("close," + _), d();
        },
        mock: function(d, g) {
          var f = this;
          return f._stop(), f.isMock = 1, f.mockEnvInfo = null, f.buffers = [d], f.recSize = d.length, f._setSrcSR(g), f._streamTag = "mock", f;
        },
        _setSrcSR: function(d) {
          var g = this, f = g.set, _ = f[E];
          _ > d ? f[E] = d : _ = 0, g[p] = d, g.CLog(p + ": " + d + " set." + E + ": " + f[E] + (_ ? " " + k("UHvm::忽略") + ": " + _ : ""), _ ? 3 : 0);
        },
        envCheck: function(d) {
          var g, f = this, _ = f.set, C = "CPU_BE";
          if (!g && !i[C] && typeof Int8Array == "function" && !new Int8Array(new Int32Array([1]).buffer)[0] && (kn(C), g = k("Essp::不支持{1}架构", 0, C)), !g) {
            var V = _.type, T = f[V + "_envCheck"];
            _.takeoffEncodeChunk && (T ? d.canProcess || (g = k("7uMV::{1}环境不支持实时处理", 0, d.envName)) : g = k("2XBl::{1}类型不支持设置takeoffEncodeChunk", 0, V) + (f[V] ? "" : k("LG7e::(未加载编码器)"))), !g && T && (g = f[V + "_envCheck"](d, _));
          }
          return g || "";
        },
        envStart: function(d, g) {
          var f = this, _ = f.set;
          if (f.isMock = d ? 1 : 0, f.mockEnvInfo = d, f.buffers = [], f.recSize = 0, d && (f._streamTag = "env$" + d.envName), f.state = 1, f.envInLast = 0, f.envInFirst = 0, f.envInFix = 0, f.envInFixTs = [], f._setSrcSR(g), f.engineCtx = 0, f[_.type + "_start"]) {
            var C = f.engineCtx = f[_.type + "_start"](_);
            C && (C.pcmDatas = [], C.pcmSize = 0);
          }
        },
        envResume: function() {
          this.envInFixTs = [];
        },
        envIn: function(d, g) {
          var f = this, _ = f.set, C = f.engineCtx;
          if (f.state != 1) {
            f.state || f.CLog("envIn at state=0", 3);
            return;
          }
          var V = f[p], T = d.length, l = i.PowerLevel(g, T), a = f.buffers, v = a.length;
          a.push(d);
          var x = a, w = v, b = Date.now(), S = Math.round(T / V * 1e3);
          f.envInLast = b, f.buffers.length == 1 && (f.envInFirst = b - S);
          var y = f.envInFixTs;
          y.splice(0, 0, { t: b, d: S });
          for (var D = b, O = 0, M = 0; M < y.length; M++) {
            var N = y[M];
            if (b - N.t > 3e3) {
              y.length = M;
              break;
            }
            D = N.t, O += N.d;
          }
          var I = y[1], L = b - D, W = L - O;
          if (W > L / 3 && (I && L > 1e3 || y.length >= 6)) {
            var U = b - I.t - S;
            if (U > S / 5) {
              var G = !_.disableEnvInFix;
              if (f.CLog("[" + b + "]" + Ne.get(k(G ? "4Kfd::补偿{1}ms" : "bM5i::未补偿{1}ms", 1), [U]), 3), f.envInFix += U, G) {
                var F = new Int16Array(U * V / 1e3);
                T += F.length, a.push(F);
              }
            }
          }
          var z = f.recSize, P = T, ie = z + P;
          if (f.recSize = ie, C) {
            var fe = i.SampleData(a, V, _[E], C.chunkInfo);
            C.chunkInfo = fe, z = C.pcmSize, P = fe.data.length, ie = z + P, C.pcmSize = ie, a = C.pcmDatas, v = a.length, a.push(fe.data), V = fe[E];
          }
          var ee = Math.round(ie / V * 1e3), J = a.length, te = x.length, ge = function() {
            for (var xe = de ? 0 : -P, $e = a[0] == null, Ee = v; Ee < J; Ee++) {
              var Pe = a[Ee];
              Pe == null ? $e = 1 : (xe += Pe.length, C && Pe.length && f[_.type + "_encode"](C, Pe));
            }
            if ($e && C) {
              var Ee = w;
              for (x[0] && (Ee = 0); Ee < te; Ee++)
                x[Ee] = null;
            }
            $e && (xe = de ? P : 0, a[0] = null), C ? C.pcmSize += xe : f.recSize += xe;
          }, de = 0, ve = "rec.set.onProcess";
          try {
            de = _.onProcess(a, l, ee, V, v, ge), de = de === !0;
          } catch (xe) {
            console.error(ve + k("gFUF::回调出错是不允许的，需保证不会抛异常"), xe);
          }
          var Ce = Date.now() - b;
          if (Ce > 10 && f.envInFirst - b > 1e3 && f.CLog(ve + k("2ghS::低性能，耗时{1}ms", 0, Ce), 3), de) {
            for (var ye = 0, M = v; M < J; M++)
              a[M] == null ? ye = 1 : a[M] = new Int16Array(0);
            ye ? f.CLog(k("ufqH::未进入异步前不能清除buffers"), 3) : C ? C.pcmSize -= P : f.recSize -= P;
          } else
            ge();
        },
        start: function() {
          var d = this, g = 1;
          if (d.set.sourceStream ? d.Stream || (g = 0) : i.IsOpen() || (g = 0), !g) {
            d.CLog(k("6WmN::start失败：未open"), 1);
            return;
          }
          var f = d._streamCtx();
          if (d.CLog(k("kLDN::start 开始录音，") + Oe(f) + " stream:" + d._streamTag), d._stop(), d.envStart(null, f[E]), d.state = 3, d._SO && d._SO + 1 != d._S) {
            d.CLog(k("Bp2y::start被中断"), 3);
            return;
          }
          d._SO = 0;
          var _ = function() {
            d.state == 3 && (d.state = 1, d.resume());
          }, C = "AudioContext resume: ", V = d._streamGet();
          V._call[d.id] = function() {
            d.CLog(C + f.state + "|stream ok"), _();
          }, Z(f, function(T) {
            return T && d.CLog(C + "wait..."), d.state == 3;
          }, function(T) {
            T && d.CLog(C + f.state), _();
          }, function(T) {
            d.CLog(C + f.state + k("upkE::，可能无法录音：") + T, 1), _();
          });
        },
        pause: function() {
          var d = this, g = d._streamGet();
          d.state && (d.state = 2, d.CLog("pause"), g && delete g._call[d.id]);
        },
        resume: function() {
          var d = this, g = d._streamGet(), f = "resume", _ = f + "(wait ctx)";
          if (d.state == 3)
            d.CLog(_);
          else if (d.state) {
            d.state = 1, d.CLog(f), d.envResume(), g && (g._call[d.id] = function(V, T) {
              d.state == 1 && d.envIn(V, T);
            }, we(g));
            var C = d._streamCtx();
            C && Z(C, function(V) {
              return V && d.CLog(_ + "..."), d.state == 1;
            }, function(V) {
              V && d.CLog(_ + C.state), we(g);
            }, function(V) {
              d.CLog(_ + C.state + "[err]" + V, 1);
            });
          }
        },
        _stop: function(d) {
          var g = this, f = g.set;
          g.isMock || g._S++, g.state && (g.pause(), g.state = 0), !d && g[f.type + "_stop"] && (g[f.type + "_stop"](g.engineCtx), g.engineCtx = 0);
        },
        stop: function(d, g, f) {
          var _ = this, C = _.set, V, T = _.envInLast - _.envInFirst, l = T && _.buffers.length;
          _.CLog(k("Xq4s::stop 和start时差:") + (T ? T + "ms " + k("3CQP::补偿:") + _.envInFix + "ms envIn:" + l + " fps:" + (l / T * 1e3).toFixed(1) : "-") + " stream:" + _._streamTag + " (" + u + ") LM:" + c);
          var a = function() {
            _._stop(), f && _.close();
          }, v = function(N) {
            _.CLog(k("u8JG::结束录音失败：") + N, 1), g && g(N), a();
          }, x = function(N, I, L) {
            var W = "blob", U = "arraybuffer", G = "dataType", F = "DefaultDataType", z = _[G] || i[F] || W, P = G + "=" + z, ie = N instanceof ArrayBuffer, fe = 0, ee = ie ? N.byteLength : N.size;
            if (z == U ? ie || (fe = 1) : z == W ? typeof Blob != "function" ? fe = k.G("NonBrowser-1", [P]) + k("1skY::，请设置{1}", 0, m + "." + F + '="' + U + '"') : (ie && (N = new Blob([N], { type: I })), N instanceof Blob || (fe = 1), I = N.type || I) : fe = k.G("NotSupport-1", [P]), _.CLog(k("Wv7l::结束录音 编码花{1}ms 音频时长{2}ms 文件大小{3}b", 0, Date.now() - V, L, ee) + " " + P + "," + I), fe) {
              v(fe != 1 ? fe : k("Vkbd::{1}编码器返回的不是{2}", 0, C.type, z) + ", " + P);
              return;
            }
            if (C.takeoffEncodeChunk)
              _.CLog(k("QWnr::启用takeoffEncodeChunk后stop返回的blob长度为0不提供音频数据"), 3);
            else if (ee < Math.max(50, L / 5)) {
              v(k("Sz2H::生成的{1}无效", 0, C.type));
              return;
            }
            d && d(N, L, I), a();
          };
          if (!_.isMock) {
            var w = _.state == 3;
            if (!_.state || w) {
              v(k("wf9t::未开始录音") + (w ? k("Dl2c::，开始录音前无用户交互导致AudioContext未运行") : ""));
              return;
            }
          }
          _._stop(!0);
          var b = _.recSize;
          if (!b) {
            v(k("Ltz3::未采集到录音"));
            return;
          }
          if (!_[C.type]) {
            v(k("xGuI::未加载{1}编码器，请尝试到{2}的src/engine内找到{1}的编码器并加载", 0, C.type, m));
            return;
          }
          if (_.isMock) {
            var S = _.envCheck(_.mockEnvInfo || { envName: "mock", canProcess: !1 });
            if (S) {
              v(k("AxOH::录音错误：") + S);
              return;
            }
          }
          var y = _.engineCtx;
          if (_[C.type + "_complete"] && y) {
            var M = Math.round(y.pcmSize / C[E] * 1e3);
            V = Date.now(), _[C.type + "_complete"](y, function(I, L) {
              x(I, L, M);
            }, v);
            return;
          }
          if (V = Date.now(), !_.buffers[0]) {
            v(k("xkKd::音频buffers被释放"));
            return;
          }
          var D = i.SampleData(_.buffers, _[p], C[E]);
          C[E] = D[E];
          var O = D.data, M = Math.round(O.length / C[E] * 1e3);
          _.CLog(k("CxeT::采样:{1} 花:{2}ms", 0, b + "->" + O.length, Date.now() - V)), setTimeout(function() {
            V = Date.now(), _[C.type](O, function(N, I) {
              x(N, I, M);
            }, function(N) {
              v(N);
            });
          });
        }
      };
      var se = function(d, g) {
        g.pos || (g.pos = [0], g.tracks = {}, g.bytes = []);
        var f = g.tracks, _ = [g.pos[0]], C = function() {
          g.pos[0] = _[0];
        }, V = g.bytes.length, T = new Uint8Array(V + d.length);
        if (T.set(g.bytes), T.set(d, V), g.bytes = T, !g._ht) {
          if (je(T, _), Ge(T, _), !Te(je(T, _), [24, 83, 128, 103]))
            return;
          for (je(T, _); _[0] < T.length; ) {
            var l = je(T, _), a = Ge(T, _), v = [0], x = 0;
            if (!a) return;
            if (Te(l, [22, 84, 174, 107])) {
              for (; v[0] < a.length; ) {
                var w = je(a, v), b = Ge(a, v), S = [0], y = { channels: 0, sampleRate: 0 };
                if (Te(w, [174]))
                  for (; S[0] < b.length; ) {
                    var D = je(b, S), O = Ge(b, S), M = [0];
                    if (Te(D, [215])) {
                      var N = mt(O);
                      y.number = N, f[N] = y;
                    } else if (Te(D, [131])) {
                      var N = mt(O);
                      N == 1 ? y.type = "video" : N == 2 ? (y.type = "audio", x || (g.track0 = y), y.idx = x++) : y.type = "Type-" + N;
                    } else if (Te(D, [134])) {
                      for (var I = "", L = 0; L < O.length; L++)
                        I += String.fromCharCode(O[L]);
                      y.codec = I;
                    } else if (Te(D, [225]))
                      for (; M[0] < O.length; ) {
                        var W = je(O, M), U = Ge(O, M);
                        if (Te(W, [181])) {
                          var N = 0, G = new Uint8Array(U.reverse()).buffer;
                          U.length == 4 ? N = new Float32Array(G)[0] : U.length == 8 ? N = new Float64Array(G)[0] : X("WebM Track !Float", 1, U), y[E] = Math.round(N);
                        } else Te(W, [98, 100]) ? y.bitDepth = mt(U) : Te(W, [159]) && (y.channels = mt(U));
                      }
                  }
              }
              g._ht = 1, X("WebM Tracks", f), C();
              break;
            }
          }
        }
        var F = g.track0;
        if (F) {
          var z = F[E];
          if (g.webmSR = z, F.bitDepth == 16 && /FLOAT/i.test(F.codec) && (F.bitDepth = 32, X("WebM 16->32 bit", 3)), z < 8e3 || F.bitDepth != 32 || F.channels < 1 || !/(\b|_)PCM\b/i.test(F.codec))
            return g.bytes = [], g.bad || X("WebM Track Unexpected", 3, g), g.bad = 1, -1;
          for (var P = [], ie = 0; _[0] < T.length; ) {
            var w = je(T, _), b = Ge(T, _);
            if (!b) break;
            if (Te(w, [163])) {
              var fe = b[0] & 15, y = f[fe];
              if (y) {
                if (y.idx === 0) {
                  for (var ee = new Uint8Array(b.length - 4), L = 4; L < b.length; L++)
                    ee[L - 4] = b[L];
                  P.push(ee), ie += ee.length;
                }
              } else return X("WebM !Track" + fe, 1, f), -1;
            }
            C();
          }
          if (ie) {
            var J = new Uint8Array(T.length - g.pos[0]);
            J.set(T.subarray(g.pos[0])), g.bytes = J, g.pos[0] = 0;
            for (var ee = new Uint8Array(ie), L = 0, te = 0; L < P.length; L++)
              ee.set(P[L], te), te += P[L].length;
            var G = new Float32Array(ee.buffer);
            if (F.channels > 1) {
              for (var ge = [], L = 0; L < G.length; )
                ge.push(G[L]), L += F.channels;
              G = new Float32Array(ge);
            }
            return G;
          }
        }
      }, Te = function(d, g) {
        if (!d || d.length != g.length) return !1;
        if (d.length == 1) return d[0] == g[0];
        for (var f = 0; f < d.length; f++)
          if (d[f] != g[f]) return !1;
        return !0;
      }, mt = function(d) {
        for (var g = "", f = 0; f < d.length; f++) {
          var _ = d[f];
          g += (_ < 16 ? "0" : "") + _.toString(16);
        }
        return parseInt(g, 16) || 0;
      }, je = function(d, g, f) {
        var _ = g[0];
        if (!(_ >= d.length)) {
          var C = d[_], V = ("0000000" + C.toString(2)).substr(-8), T = /^(0*1)(\d*)$/.exec(V);
          if (T) {
            var l = T[1].length, a = [];
            if (!(_ + l > d.length)) {
              for (var v = 0; v < l; v++)
                a[v] = d[_], _++;
              return f && (a[0] = parseInt(T[2] || "0", 2)), g[0] = _, a;
            }
          }
        }
      }, Ge = function(d, g) {
        var f = je(d, g, 1);
        if (f) {
          var _ = mt(f), C = g[0], V = [];
          if (_ < 2147483647) {
            if (C + _ > d.length) return;
            for (var T = 0; T < _; T++)
              V[T] = d[C], C++;
          }
          return g[0] = C, V;
        }
      }, Ne = i.i18n = {
        lang: "zh-CN",
        alias: { "zh-CN": "zh", "en-US": "en" },
        locales: {},
        data: {},
        put: function(d, g) {
          var f = m + ".i18n.put: ", _ = d.overwrite;
          _ = _ == null || _;
          var C = d.lang;
          if (C = Ne.alias[C] || C, !C) throw new Error(f + "set.lang?");
          var V = Ne.locales[C];
          V || (V = {}, Ne.locales[C] = V);
          for (var T = /^([\w\-]+):/, l, a = 0; a < g.length; a++) {
            var x = g[a];
            if (l = T.exec(x), !l) {
              X(f + "'key:'? " + x, 3, d);
              continue;
            }
            var v = l[1], x = x.substr(v.length + 1);
            !_ && V[v] || (V[v] = x);
          }
        },
        get: function() {
          return Ne.v_G.apply(null, arguments);
        },
        v_G: function(d, g, f) {
          g = g || [], f = f || Ne.lang, f = Ne.alias[f] || f;
          var _ = Ne.locales[f], C = _ && _[d] || "";
          return !C && f != "zh" ? f == "en" ? Ne.v_G(d, g, "zh") : Ne.v_G(d, g, "en") : (Ne.lastLang = f, C == "=Empty" ? "" : C.replace(/\{(\d+)(\!?)\}/g, function(V, T, l) {
            return T = +T || 0, V = g[T - 1], (T < 1 || T > g.length) && (V = "{?}", X("i18n[" + d + "] no {" + T + "}: " + C, 3)), l ? "" : V;
          }));
        },
        $T: function() {
          return Ne.v_T.apply(null, arguments);
        },
        v_T: function() {
          for (var d = arguments, g = "", f = [], _ = 0, C = m + ".i18n.$T:", V = /^([\w\-]*):/, T, l = 0; l < d.length; l++) {
            var a = d[l];
            if (l == 0) {
              if (T = V.exec(a), g = T && T[1], !g) throw new Error(C + "0 'key:'?");
              a = a.substr(g.length + 1);
            }
            if (_ === -1) f.push(a);
            else {
              if (_) throw new Error(C + " bad args");
              if (a === 0) _ = -1;
              else if (o(a)) {
                if (a < 1) throw new Error(C + " bad args");
                _ = a;
              } else {
                var v = l == 1 ? "en" : l ? "" : "zh";
                if (T = V.exec(a), T && (v = T[1] || v, a = a.substr(T[1].length + 1)), !T || !v) throw new Error(C + l + " 'lang:'?");
                Ne.put({ lang: v, overwrite: !1 }, [g + ":" + a]);
              }
            }
          }
          return g ? _ > 0 ? g : Ne.v_G(g, f) : "";
        }
      }, k = Ne.$T;
      k.G = Ne.get, k("NonBrowser-1::非浏览器环境，不支持{1}", 1), k("IllegalArgs-1::参数错误：{1}", 1), k("NeedImport-2::调用{1}需要先导入{2}", 2), k("NotSupport-1::不支持：{1}", 1), i.TrafficImgUrl = "//ia.51.la/go1?id=20469973&pvFlag=1";
      var kn = i.Traffic = function(d) {
        if (n) {
          d = d ? "/" + m + "/Report/" + d : "";
          var g = i.TrafficImgUrl;
          if (g) {
            var f = i.Traffic, _ = /^(https?:..[^\/#]*\/?)[^#]*/i.exec(location.href) || [], C = _[1] || "http://file/", V = (_[0] || C) + d;
            if (g.indexOf("//") == 0 && (/^https:/i.test(V) ? g = "https:" + g : g = "http:" + g), d && (g = g + "&cu=" + encodeURIComponent(C + d)), !f[V]) {
              f[V] = 1;
              var T = new Image();
              T.src = g, X("Traffic Analysis Image: " + (d || m + ".TrafficImgUrl=" + i.TrafficImgUrl));
            }
          }
        }
      };
      j && (X(k("8HO5::覆盖导入{1}", 0, m), 1), j.Destroy()), t[m] = i;
    });
  })(Rr)), Rr.exports;
}
var tf = ef();
const ds = /* @__PURE__ */ Za(tf);
(function(e) {
  var t = typeof window == "object" && !!window.document, n = t ? window : Object, r = n.Recorder, o = r.i18n;
  e(r, o, o.$T, t);
})(function(e, t, n, r) {
  e.prototype.enc_pcm = {
    stable: !0,
    fast: !0,
    getTestMsg: function() {
      return n("fWsN::pcm为未封装的原始音频数据，pcm音频文件无法直接播放，可用Recorder.pcm2wav()转码成wav播放；支持位数8位、16位（填在比特率里面），采样率取值无限制");
    }
  };
  var o = function(c) {
    var u = c.bitRate, m = u == 8 ? 8 : 16;
    u != m && e.CLog(n("uMUJ::PCM Info: 不支持{1}位，已更新成{2}位", 0, u, m), 3), c.bitRate = m;
  };
  e.prototype.pcm = function(c, u, m) {
    var h = this.set;
    o(h);
    var p = s(c, h.bitRate);
    u(p.buffer, "audio/pcm");
  };
  var s = function(c, u) {
    if (u == 8)
      for (var m = c.length, h = new Uint8Array(m), p = 0; p < m; p++) {
        var E = (c[p] >> 8) + 128;
        h[p] = E;
      }
    else {
      c = new Int16Array(c);
      var h = new Uint8Array(c.buffer);
    }
    return h;
  };
  e.pcm2wav = function(c, u, m) {
    c.blob || (c = { blob: c });
    var h = c.blob, p = c.sampleRate || 16e3, E = c.bitRate || 16;
    if ((!c.sampleRate || !c.bitRate) && e.CLog(n("KmRz::pcm2wav必须提供sampleRate和bitRate"), 3), !e.prototype.wav) {
      m(n.G("NeedImport-2", ["pcm2wav", "src/engine/wav.js"]));
      return;
    }
    var A = function(j, _e) {
      var ne;
      if (E == 8) {
        var Z = new Uint8Array(j);
        ne = new Int16Array(Z.length);
        for (var Q = 0; Q < Z.length; Q++)
          ne[Q] = Z[Q] - 128 << 8;
      } else
        ne = new Int16Array(j);
      var Oe = e({
        type: "wav",
        sampleRate: p,
        bitRate: E
      });
      _e && (Oe.dataType = "arraybuffer"), Oe.mock(ne, p).stop(function(B, ce, De) {
        u(B, ce, De);
      }, m);
    };
    if (h instanceof ArrayBuffer)
      A(h, 1);
    else {
      var H = new FileReader();
      H.onloadend = function() {
        A(H.result);
      }, H.readAsArrayBuffer(h);
    }
  }, e.prototype.pcm_envCheck = function(c, u) {
    return "";
  }, e.prototype.pcm_start = function(c) {
    return o(c), { set: c, memory: new Uint8Array(5e5), mOffset: 0 };
  };
  var i = function(c, u) {
    var m = u.length;
    if (c.mOffset + m > c.memory.length) {
      var h = new Uint8Array(c.memory.length + Math.max(5e5, m));
      h.set(c.memory.subarray(0, c.mOffset)), c.memory = h;
    }
    c.memory.set(u, c.mOffset), c.mOffset += m;
  };
  e.prototype.pcm_stop = function(c) {
    c && c.memory && (c.memory = null);
  }, e.prototype.pcm_encode = function(c, u) {
    if (c && c.memory) {
      var m = c.set, h = s(u, m.bitRate);
      m.takeoffEncodeChunk ? m.takeoffEncodeChunk(h) : i(c, h);
    }
  }, e.prototype.pcm_complete = function(c, u, m, h) {
    if (c && c.memory) {
      h && this.pcm_stop(c);
      var p = c.memory.buffer.slice(0, c.mOffset);
      u(p, "audio/pcm");
    } else
      m(n("sDkA::pcm编码器未start"));
  };
});
const nf = (e, t) => {
  const n = e.__vccOpts || e;
  for (const [r, o] of t)
    n[r] = o;
  return n;
}, rf = {}, ps = "ai-assistant-user-id", hs = 1e3, of = 3e4, sf = 10, cf = {
  name: "AIAssistantWidget",
  props: {
    backendUrl: {
      type: String,
      default: ""
    },
    theme: {
      type: String,
      default: "dark",
      validator: (e) => ["light", "dark"].includes(e)
    },
    initialPosition: {
      type: Object,
      default: () => ({ bottom: "20px", right: "20px" })
    }
  },
  data() {
    return {
      // Position & Drag
      position: { ...this.initialPosition },
      isDragging: !1,
      hasDragged: !1,
      dragStartX: 0,
      dragStartY: 0,
      elementStartX: 0,
      elementStartY: 0,
      // Recording State
      isRecording: !1,
      isConnecting: !1,
      recorder: null,
      // WebSocket
      socket: null,
      userId: null,
      isReconnecting: !1,
      reconnectAttempt: 0,
      maxReconnectAttempts: sf,
      reconnectDelay: hs,
      reconnectTimer: null,
      // Result Display
      showResultPanel: !1,
      llmResult: "",
      // Audio Processing
      clearBufferIdx: 0,
      processTime: 0,
      send_chunk: null,
      send_lastFrame: null,
      send_pcmSampleRate: 16e3,
      // Status
      statusText: ""
    };
  },
  computed: {
    widgetStyle() {
      const e = {};
      return this.position.top && (e.top = this.position.top), this.position.bottom && (e.bottom = this.position.bottom), this.position.left && (e.left = this.position.left), this.position.right && (e.right = this.position.right), e;
    },
    buttonTitle() {
      return this.isConnecting ? "连接中..." : this.isRecording ? "点击停止录音" : "点击开始录音";
    },
    wsUrl() {
      const e = this.backendUrl || this.getDefaultBackendUrl();
      try {
        const t = new URL(e);
        return `${t.protocol === "https:" ? "wss:" : "ws:"}//${t.host}/audio/ws/${this.userId}`;
      } catch {
        return `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${e}/audio/ws/${this.userId}`;
      }
    }
  },
  mounted() {
    this.initUserId(), document.addEventListener("mousemove", this.onDrag), document.addEventListener("mouseup", this.stopDrag), document.addEventListener("touchmove", this.onDrag, { passive: !1 }), document.addEventListener("touchend", this.stopDrag);
  },
  beforeUnmount() {
    this.cleanup(), document.removeEventListener("mousemove", this.onDrag), document.removeEventListener("mouseup", this.stopDrag), document.removeEventListener("touchmove", this.onDrag), document.removeEventListener("touchend", this.stopDrag), this.reconnectTimer && clearTimeout(this.reconnectTimer);
  },
  methods: {
    // ========== User ID Management ==========
    initUserId() {
      let e = localStorage.getItem(ps);
      e || (e = `user-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`, localStorage.setItem(ps, e)), this.userId = e, console.log("[AIAssistant] User ID:", this.userId);
    },
    getDefaultBackendUrl() {
      if (!(typeof import.meta < "u" && rf?.VITE_BACKEND_URL))
        return typeof import.meta < "u" ? window.location.origin : "https://local.morph.icu:5000";
    },
    // ========== Drag Functionality ==========
    startDrag(e) {
      if (this.isConnecting) return;
      this.isDragging = !0, this.hasDragged = !1;
      const t = e.type.includes("touch") ? e.touches[0].clientX : e.clientX, n = e.type.includes("touch") ? e.touches[0].clientY : e.clientY;
      this.dragStartX = t, this.dragStartY = n;
      const r = this.$refs.widgetRef.getBoundingClientRect();
      this.elementStartX = r.left, this.elementStartY = r.top, this.position = {
        left: `${r.left}px`,
        top: `${r.top}px`
      };
    },
    onDrag(e) {
      if (!this.isDragging) return;
      const t = e.type.includes("touch") ? e.touches[0].clientX : e.clientX, n = e.type.includes("touch") ? e.touches[0].clientY : e.clientY, r = t - this.dragStartX, o = n - this.dragStartY;
      (Math.abs(r) > 5 || Math.abs(o) > 5) && (this.hasDragged = !0);
      const s = this.elementStartX + r, i = this.elementStartY + o, c = window.innerWidth - 60, u = window.innerHeight - 60;
      this.position = {
        left: `${Math.max(0, Math.min(s, c))}px`,
        top: `${Math.max(0, Math.min(i, u))}px`
      }, e.type.includes("touch") && e.preventDefault();
    },
    stopDrag() {
      this.isDragging = !1;
    },
    // ========== Click Handler ==========
    handleClick() {
      if (this.hasDragged) {
        this.hasDragged = !1;
        return;
      }
      this.isRecording ? this.stopRecording() : this.startRecording();
    },
    // ========== Recording ==========
    async startRecording() {
      if (!(this.isRecording || this.isConnecting)) {
        this.isConnecting = !0, this.statusText = "正在连接...";
        try {
          this.recorder = ds({
            type: "unknown",
            sampleRate: 16e3,
            bitRate: 16,
            onProcess: (e, t, n, r, o) => {
              this.processTime = Date.now();
              for (let s = this.clearBufferIdx; s < o; s++)
                e[s] = null;
              this.clearBufferIdx = o, this.realTimeSendTry(e, r, !1);
            }
          }), await new Promise((e, t) => {
            this.recorder.open(e, (n, r) => {
              t(new Error((r ? "用户拒绝授权: " : "") + n));
            });
          }), await this.connectWebSocket(), this.recorder.start(), this.isRecording = !0, this.isConnecting = !1, this.showResultPanel = !0, this.statusText = "", this.startWatchdog();
        } catch (e) {
          console.error("[AIAssistant] Recording error:", e), this.statusText = "错误: " + e.message, this.isConnecting = !1, this.cleanup(), setTimeout(() => {
            this.statusText = "";
          }, 3e3);
        }
      }
    },
    stopRecording() {
      this.isRecording && (this.statusText = "正在停止...", this.recorder && (this.recorder.watchDogTimer = 0, this.recorder.close()), this.realTimeSendTry([], 0, !0), this.socket && this.socket.readyState === WebSocket.OPEN && this.socket.close(1e3, "Recording stopped"), this.cleanupRecording(), this.statusText = "");
    },
    startWatchdog() {
      const e = Date.now(), t = setInterval(() => {
        if (!this.recorder || this.recorder.watchDogTimer !== t) {
          clearInterval(t);
          return;
        }
        Date.now() - (this.processTime || e) > 1500 && (clearInterval(t), console.error("[AIAssistant]", this.processTime ? "录音被中断" : "录音未能正常开始"), this.statusText = this.processTime ? "录音中断" : "录音启动失败", this.stopRecording());
      }, 1e3);
      this.recorder.watchDogTimer = t;
    },
    // ========== WebSocket ==========
    connectWebSocket() {
      return new Promise((e, t) => {
        const n = this.wsUrl;
        console.log("[AIAssistant] Connecting to:", n), this.socket = new WebSocket(n);
        const r = setTimeout(() => {
          t(new Error("WebSocket connection timeout"));
        }, 1e4);
        this.socket.onopen = () => {
          clearTimeout(r), console.log("[AIAssistant] WebSocket connected");
          const o = {
            type: "config",
            format: "pcm",
            sampleRate: 16e3,
            sampleSize: 16,
            channelCount: 1
          };
          this.socket.send(JSON.stringify(o)), this.reconnectAttempt = 0, this.reconnectDelay = hs, this.isReconnecting = !1, e();
        }, this.socket.onmessage = (o) => {
          try {
            const s = JSON.parse(o.data);
            s.text || s.result || s.response ? this.llmResult = s.text || s.result || s.response : this.llmResult = JSON.stringify(s, null, 2);
          } catch {
            this.llmResult = o.data;
          }
        }, this.socket.onclose = (o) => {
          console.log("[AIAssistant] WebSocket closed:", o.code, o.reason), this.isRecording && o.code !== 1e3 && this.handleReconnect();
        }, this.socket.onerror = (o) => {
          clearTimeout(r), console.error("[AIAssistant] WebSocket error:", o), t(new Error("WebSocket连接失败"));
        };
      });
    },
    handleReconnect() {
      if (this.reconnectAttempt >= this.maxReconnectAttempts) {
        console.log("[AIAssistant] Max reconnect attempts reached"), this.statusText = "连接失败，请重试", this.cleanupRecording();
        return;
      }
      this.isReconnecting = !0, this.reconnectAttempt++, console.log(`[AIAssistant] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempt})`), this.reconnectTimer = setTimeout(async () => {
        try {
          await this.connectWebSocket(), console.log("[AIAssistant] Reconnected successfully");
        } catch (e) {
          console.error("[AIAssistant] Reconnect failed:", e), this.reconnectDelay = Math.min(this.reconnectDelay * 2, of), this.handleReconnect();
        }
      }, this.reconnectDelay);
    },
    // ========== Audio Processing ==========
    realTimeSendTry(e, t, n) {
      let r = new Int16Array(0);
      if (e.length > 0) {
        const o = ds.SampleData(e, t, 16e3, this.send_chunk);
        this.send_chunk = o, r = o.data, this.send_pcmSampleRate = o.sampleRate;
      }
      this.transferUpload(r, n);
    },
    transferUpload(e, t) {
      if (t && e.length === 0) {
        const n = this.send_lastFrame ? this.send_lastFrame.length : Math.round(this.send_pcmSampleRate / 1e3 * 50);
        e = new Int16Array(n);
      }
      this.send_lastFrame = e, this.socket && this.socket.readyState === WebSocket.OPEN && this.socket.send(e.buffer);
    },
    // ========== Cleanup ==========
    cleanupRecording() {
      this.recorder = null, this.socket = null, this.isRecording = !1, this.isConnecting = !1, this.clearBufferIdx = 0, this.processTime = 0, this.send_chunk = null, this.send_lastFrame = null;
    },
    cleanup() {
      this.reconnectTimer && clearTimeout(this.reconnectTimer), this.stopRecording();
    }
  }
}, lf = ["disabled", "title"], af = { class: "ai-icon" }, ff = {
  key: 0,
  viewBox: "0 0 24 24",
  fill: "currentColor"
}, uf = {
  key: 1,
  class: "spin",
  viewBox: "0 0 24 24",
  fill: "currentColor"
}, df = {
  key: 2,
  viewBox: "0 0 24 24",
  fill: "currentColor"
}, pf = {
  key: 0,
  class: "pulse-ring"
}, hf = {
  key: 0,
  class: "status-indicator"
}, gf = {
  key: 0,
  class: "result-panel"
}, vf = { class: "result-header" }, mf = { class: "result-content" }, _f = {
  key: 0,
  class: "result-text"
}, bf = {
  key: 1,
  class: "result-placeholder"
}, Ef = {
  key: 1,
  class: "reconnect-overlay"
}, yf = { class: "reconnect-content" };
function Nf(e, t, n, r, o, s) {
  return et(), ft("div", {
    class: hr(["ai-assistant-widget", {
      "is-recording": o.isRecording,
      "is-connecting": o.isConnecting,
      "is-expanded": o.showResultPanel,
      "theme-dark": n.theme === "dark"
    }]),
    style: pr(s.widgetStyle),
    ref: "widgetRef"
  }, [
    He("button", {
      class: "ai-btn",
      onMousedown: t[0] || (t[0] = (...i) => s.startDrag && s.startDrag(...i)),
      onTouchstartPassive: t[1] || (t[1] = (...i) => s.startDrag && s.startDrag(...i)),
      onClick: t[2] || (t[2] = (...i) => s.handleClick && s.handleClick(...i)),
      disabled: o.isConnecting,
      title: s.buttonTitle
    }, [
      He("div", af, [
        !o.isRecording && !o.isConnecting ? (et(), ft("svg", ff, [...t[4] || (t[4] = [
          He("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-4h2v2h-2zm1.61-9.96c-2.06-.3-3.88.97-4.43 2.79-.18.58.26 1.17.87 1.17h.2c.41 0 .74-.29.88-.67.32-.89 1.27-1.5 2.3-1.28.95.2 1.65 1.13 1.57 2.1-.1 1.34-1.62 1.63-2.45 2.88 0 .01-.01.01-.01.02-.01.02-.02.03-.03.05-.09.15-.18.32-.25.5-.01.03-.03.05-.04.08-.01.02-.01.04-.02.07-.12.34-.2.75-.2 1.25h2c0-.42.11-.77.28-1.07.02-.03.03-.06.05-.09.08-.14.18-.27.28-.39.01-.01.02-.03.03-.04.1-.12.21-.23.33-.34.96-.91 2.26-1.65 1.99-3.56-.24-1.74-1.61-3.21-3.35-3.47z" }, null, -1)
        ])])) : o.isConnecting ? (et(), ft("svg", uf, [...t[5] || (t[5] = [
          He("path", { d: "M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z" }, null, -1)
        ])])) : (et(), ft("svg", df, [...t[6] || (t[6] = [
          He("path", { d: "M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5z" }, null, -1),
          He("path", { d: "M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" }, null, -1)
        ])]))
      ]),
      o.isRecording ? (et(), ft("div", pf)) : Hn("", !0)
    ], 40, lf),
    o.statusText ? (et(), ft("div", hf, pn(o.statusText), 1)) : Hn("", !0),
    ze(xa, { name: "slide-up" }, {
      default: qs(() => [
        o.showResultPanel ? (et(), ft("div", gf, [
          He("div", vf, [
            t[7] || (t[7] = He("span", null, "AI 响应", -1)),
            He("button", {
              class: "close-btn",
              onClick: t[3] || (t[3] = (i) => o.showResultPanel = !1)
            }, "×")
          ]),
          He("div", mf, [
            o.llmResult ? (et(), ft("div", _f, pn(o.llmResult), 1)) : (et(), ft("div", bf, "等待响应..."))
          ])
        ])) : Hn("", !0)
      ]),
      _: 1
    }),
    o.isReconnecting ? (et(), ft("div", Ef, [
      He("div", yf, [
        t[8] || (t[8] = He("span", { class: "reconnect-spinner" }, null, -1)),
        He("span", null, "重新连接中... (" + pn(o.reconnectAttempt) + "/" + pn(o.maxReconnectAttempts) + ")", 1)
      ])
    ])) : Hn("", !0)
  ], 6);
}
const xf = /* @__PURE__ */ nf(cf, [["render", Nf], ["__scopeId", "data-v-054b2702"]]);
let sn = null, Ze = null;
const wf = {
  backendUrl: "",
  position: { bottom: "20px", right: "20px" },
  theme: "dark",
  containerId: "ai-assistant-container"
};
function Of(e = {}) {
  const t = { ...wf, ...e };
  if (sn) {
    console.warn("[AIAssistant] Already initialized. Call destroy() first to reinitialize.");
    return;
  }
  Ze = document.createElement("div"), Ze.id = t.containerId, Ze.style.cssText = "position: fixed; z-index: 99999; pointer-events: none;", document.body.appendChild(Ze);
  let n = Ze;
  if (typeof Ze.attachShadow == "function")
    try {
      const r = Ze.attachShadow({ mode: "open" }), o = document.createElement("div");
      o.style.cssText = "pointer-events: auto;", r.appendChild(o), n = o;
      const s = document.createElement("style");
      s.textContent = Sf(), r.appendChild(s);
    } catch {
      console.warn("[AIAssistant] Shadow DOM not available, using regular DOM");
    }
  sn = Ka({
    render() {
      return Li(xf, {
        backendUrl: t.backendUrl,
        theme: t.theme,
        initialPosition: t.position
      });
    }
  }), sn.mount(n), console.log("[AIAssistant] Initialized successfully");
}
function Cf() {
  sn && (sn.unmount(), sn = null), Ze && Ze.parentNode && (Ze.parentNode.removeChild(Ze), Ze = null), console.log("[AIAssistant] Destroyed");
}
function Sf() {
  return `
    .ai-assistant-widget {
      position: fixed;
      z-index: 99999;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    }
    .ai-btn {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      transition: all 0.3s ease;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .ai-btn:hover {
      transform: scale(1.05);
      box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    .ai-btn:active { transform: scale(0.98); }
    .ai-btn:disabled { opacity: 0.7; cursor: not-allowed; }
    .ai-icon { width: 28px; height: 28px; color: white; }
    .ai-icon svg { width: 100%; height: 100%; }
    .is-recording .ai-btn {
      background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
      box-shadow: 0 4px 15px rgba(245, 87, 108, 0.5);
    }
    .is-connecting .ai-btn {
      background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    }
    .pulse-ring {
      position: absolute;
      width: 100%;
      height: 100%;
      border-radius: 50%;
      border: 2px solid rgba(245, 87, 108, 0.6);
      animation: pulse 1.5s ease-out infinite;
    }
    @keyframes pulse {
      0% { transform: scale(1); opacity: 1; }
      100% { transform: scale(1.8); opacity: 0; }
    }
    .spin { animation: spin 1s linear infinite; }
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .status-indicator {
      position: absolute;
      top: -30px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      white-space: nowrap;
    }
    .result-panel {
      position: absolute;
      bottom: 70px;
      right: 0;
      width: 300px;
      max-height: 400px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
      overflow: hidden;
    }
    .theme-dark .result-panel {
      background: #1e1e2e;
      color: #cdd6f4;
    }
    .result-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      font-weight: 600;
    }
    .theme-dark .result-header {
      border-bottom-color: rgba(255, 255, 255, 0.1);
    }
    .close-btn {
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      color: inherit;
      opacity: 0.6;
      transition: opacity 0.2s;
    }
    .close-btn:hover { opacity: 1; }
    .result-content {
      padding: 16px;
      max-height: 300px;
      overflow-y: auto;
    }
    .result-text {
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.5;
    }
    .result-placeholder {
      color: #888;
      text-align: center;
      padding: 20px;
    }
    .reconnect-overlay {
      position: absolute;
      bottom: 70px;
      right: 0;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 10px 16px;
      border-radius: 8px;
      font-size: 12px;
    }
    .reconnect-content {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .reconnect-spinner {
      width: 14px;
      height: 14px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
  `;
}
const Df = {
  init: Of,
  destroy: Cf,
  version: "1.0.0"
};
typeof window < "u" && (window.AIAssistant = Df);
export {
  Df as AIAssistant,
  Df as default
};
