function t(t,e,i,s){var o,n=arguments.length,r=n<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)r=Reflect.decorate(t,e,i,s);else for(var a=t.length-1;a>=0;a--)(o=t[a])&&(r=(n<3?o(r):n>3?o(e,i,r):o(e,i))||r);return n>3&&r&&Object.defineProperty(e,i,r),r}"function"==typeof SuppressedError&&SuppressedError;
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const e=globalThis,i=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),o=new WeakMap;let n=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(i&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=o.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&o.set(e,t))}return t}toString(){return this.cssText}};const r=(t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new n(i,t,s)},a=i?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new n("string"==typeof t?t:t+"",void 0,s))(e)})(t):t,{is:l,defineProperty:c,getOwnPropertyDescriptor:h,getOwnPropertyNames:d,getOwnPropertySymbols:p,getPrototypeOf:u}=Object,f=globalThis,g=f.trustedTypes,m=g?g.emptyScript:"",_=f.reactiveElementPolyfillSupport,$=(t,e)=>t,v={toAttribute(t,e){switch(e){case Boolean:t=t?m:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},y=(t,e)=>!l(t,e),w={attribute:!0,type:String,converter:v,reflect:!1,useDefault:!1,hasChanged:y};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */Symbol.metadata??=Symbol("metadata"),f.litPropertyMetadata??=new WeakMap;let b=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=w){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(t,i,e);void 0!==s&&c(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:o}=h(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:s,set(e){const n=s?.call(this);o?.call(this,e),this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??w}static _$Ei(){if(this.hasOwnProperty($("elementProperties")))return;const t=u(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty($("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty($("properties"))){const t=this.properties,e=[...d(t),...p(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(a(t))}else void 0!==t&&e.push(a(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,s)=>{if(i)t.adoptedStyleSheets=s.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const i of s){const s=document.createElement("style"),o=e.litNonce;void 0!==o&&s.setAttribute("nonce",o),s.textContent=i.cssText,t.appendChild(s)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(void 0!==s&&!0===i.reflect){const o=(void 0!==i.converter?.toAttribute?i.converter:v).toAttribute(e,i.type);this._$Em=t,null==o?this.removeAttribute(s):this.setAttribute(s,o),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(void 0!==s&&this._$Em!==s){const t=i.getPropertyOptions(s),o="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:v;this._$Em=s;const n=o.fromAttribute(e,t.type);this[s]=n??this._$Ej?.get(s)??n,this._$Em=null}}requestUpdate(t,e,i,s=!1,o){if(void 0!==t){const n=this.constructor;if(!1===s&&(o=this[t]),i??=n.getPropertyOptions(t),!((i.hasChanged??y)(o,e)||i.useDefault&&i.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:s,wrapped:o},n){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),!0!==o||void 0!==n)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===s&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,s=this[e];!0!==t||this._$AL.has(e)||void 0===s||this.C(e,void 0,i,s)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};b.elementStyles=[],b.shadowRootOptions={mode:"open"},b[$("elementProperties")]=new Map,b[$("finalized")]=new Map,_?.({ReactiveElement:b}),(f.reactiveElementVersions??=[]).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const x=globalThis,A=t=>t,E=x.trustedTypes,C=E?E.createPolicy("lit-html",{createHTML:t=>t}):void 0,S="$lit$",k=`lit$${Math.random().toFixed(9).slice(2)}$`,P="?"+k,R=`<${P}>`,T=document,M=()=>T.createComment(""),U=t=>null===t||"object"!=typeof t&&"function"!=typeof t,O=Array.isArray,H="[ \t\n\f\r]",N=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,L=/-->/g,j=/>/g,z=RegExp(`>|${H}(?:([^\\s"'>=/]+)(${H}*=${H}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),D=/'/g,I=/"/g,V=/^(?:script|style|textarea|title)$/i,B=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),W=Symbol.for("lit-noChange"),q=Symbol.for("lit-nothing"),G=new WeakMap,K=T.createTreeWalker(T,129);function Y(t,e){if(!O(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==C?C.createHTML(e):e}const F=(t,e)=>{const i=t.length-1,s=[];let o,n=2===e?"<svg>":3===e?"<math>":"",r=N;for(let e=0;e<i;e++){const i=t[e];let a,l,c=-1,h=0;for(;h<i.length&&(r.lastIndex=h,l=r.exec(i),null!==l);)h=r.lastIndex,r===N?"!--"===l[1]?r=L:void 0!==l[1]?r=j:void 0!==l[2]?(V.test(l[2])&&(o=RegExp("</"+l[2],"g")),r=z):void 0!==l[3]&&(r=z):r===z?">"===l[0]?(r=o??N,c=-1):void 0===l[1]?c=-2:(c=r.lastIndex-l[2].length,a=l[1],r=void 0===l[3]?z:'"'===l[3]?I:D):r===I||r===D?r=z:r===L||r===j?r=N:(r=z,o=void 0);const d=r===z&&t[e+1].startsWith("/>")?" ":"";n+=r===N?i+R:c>=0?(s.push(a),i.slice(0,c)+S+i.slice(c)+k+d):i+k+(-2===c?e:d)}return[Y(t,n+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),s]};class Z{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let o=0,n=0;const r=t.length-1,a=this.parts,[l,c]=F(t,e);if(this.el=Z.createElement(l,i),K.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(s=K.nextNode())&&a.length<r;){if(1===s.nodeType){if(s.hasAttributes())for(const t of s.getAttributeNames())if(t.endsWith(S)){const e=c[n++],i=s.getAttribute(t).split(k),r=/([.?@])?(.*)/.exec(e);a.push({type:1,index:o,name:r[2],strings:i,ctor:"."===r[1]?et:"?"===r[1]?it:"@"===r[1]?st:tt}),s.removeAttribute(t)}else t.startsWith(k)&&(a.push({type:6,index:o}),s.removeAttribute(t));if(V.test(s.tagName)){const t=s.textContent.split(k),e=t.length-1;if(e>0){s.textContent=E?E.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],M()),K.nextNode(),a.push({type:2,index:++o});s.append(t[e],M())}}}else if(8===s.nodeType)if(s.data===P)a.push({type:2,index:o});else{let t=-1;for(;-1!==(t=s.data.indexOf(k,t+1));)a.push({type:7,index:o}),t+=k.length-1}o++}}static createElement(t,e){const i=T.createElement("template");return i.innerHTML=t,i}}function J(t,e,i=t,s){if(e===W)return e;let o=void 0!==s?i._$Co?.[s]:i._$Cl;const n=U(e)?void 0:e._$litDirective$;return o?.constructor!==n&&(o?._$AO?.(!1),void 0===n?o=void 0:(o=new n(t),o._$AT(t,i,s)),void 0!==s?(i._$Co??=[])[s]=o:i._$Cl=o),void 0!==o&&(e=J(t,o._$AS(t,e.values),o,s)),e}class Q{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??T).importNode(e,!0);K.currentNode=s;let o=K.nextNode(),n=0,r=0,a=i[0];for(;void 0!==a;){if(n===a.index){let e;2===a.type?e=new X(o,o.nextSibling,this,t):1===a.type?e=new a.ctor(o,a.name,a.strings,this,t):6===a.type&&(e=new ot(o,this,t)),this._$AV.push(e),a=i[++r]}n!==a?.index&&(o=K.nextNode(),n++)}return K.currentNode=T,s}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class X{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=q,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=J(this,t,e),U(t)?t===q||null==t||""===t?(this._$AH!==q&&this._$AR(),this._$AH=q):t!==this._$AH&&t!==W&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>O(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==q&&U(this._$AH)?this._$AA.nextSibling.data=t:this.T(T.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=Z.createElement(Y(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const t=new Q(s,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=G.get(t.strings);return void 0===e&&G.set(t.strings,e=new Z(t)),e}k(t){O(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const o of t)s===e.length?e.push(i=new X(this.O(M()),this.O(M()),this,this.options)):i=e[s],i._$AI(o),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=A(t).nextSibling;A(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class tt{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,o){this.type=1,this._$AH=q,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=q}_$AI(t,e=this,i,s){const o=this.strings;let n=!1;if(void 0===o)t=J(this,t,e,0),n=!U(t)||t!==this._$AH&&t!==W,n&&(this._$AH=t);else{const s=t;let r,a;for(t=o[0],r=0;r<o.length-1;r++)a=J(this,s[i+r],e,r),a===W&&(a=this._$AH[r]),n||=!U(a)||a!==this._$AH[r],a===q?t=q:t!==q&&(t+=(a??"")+o[r+1]),this._$AH[r]=a}n&&!s&&this.j(t)}j(t){t===q?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class et extends tt{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===q?void 0:t}}class it extends tt{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==q)}}class st extends tt{constructor(t,e,i,s,o){super(t,e,i,s,o),this.type=5}_$AI(t,e=this){if((t=J(this,t,e,0)??q)===W)return;const i=this._$AH,s=t===q&&i!==q||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,o=t!==q&&(i===q||s);s&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class ot{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){J(this,t)}}const nt=x.litHtmlPolyfillSupport;nt?.(Z,X),(x.litHtmlVersions??=[]).push("3.3.3");const rt=globalThis;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */class at extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const s=i?.renderBefore??e;let o=s._$litPart$;if(void 0===o){const t=i?.renderBefore??null;s._$litPart$=o=new X(e.insertBefore(M(),t),t,void 0,i??{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return W}}at._$litElement$=!0,at.finalized=!0,rt.litElementHydrateSupport?.({LitElement:at});const lt=rt.litElementPolyfillSupport;lt?.({LitElement:at}),(rt.litElementVersions??=[]).push("4.2.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const ct=t=>(e,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)},ht={attribute:!0,type:String,converter:v,reflect:!1,hasChanged:y},dt=(t=ht,e,i)=>{const{kind:s,metadata:o}=i;let n=globalThis.litPropertyMetadata.get(o);if(void 0===n&&globalThis.litPropertyMetadata.set(o,n=new Map),"setter"===s&&((t=Object.create(t)).wrapped=!0),n.set(i.name,t),"accessor"===s){const{name:s}=i;return{set(i){const o=e.get.call(this);e.set.call(this,i),this.requestUpdate(s,o,t,!0,i)},init(e){return void 0!==e&&this.C(s,void 0,t,e),e}}}if("setter"===s){const{name:s}=i;return function(i){const o=this[s];e.call(this,i),this.requestUpdate(s,o,t,!0,i)}}throw Error("Unsupported decorator location: "+s)};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function pt(t){return(e,i)=>"object"==typeof i?dt(t,e,i):((t,e,i)=>{const s=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),s?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function ut(t){return pt({...t,state:!0,attribute:!1})}let ft=class extends at{constructor(){super(...arguments),this.language="en",this._now=Date.now()}connectedCallback(){super.connectedCallback(),this._interval=window.setInterval(()=>{this._now=Date.now()},1e3)}disconnectedCallback(){super.disconnectedCallback(),void 0!==this._interval&&(window.clearInterval(this._interval),this._interval=void 0)}_format(t){const e="nl"===this.language;if(t<=0)return e?"vertrokken":"departed";const i=Math.floor(t/3600),s=Math.floor(t%3600/60),o=e?"over":"in";return i>0?`${o} ${i}${e?"u":"h"} ${s}m`:`${o} ${s} min`}render(){if(!this.arrival)return B``;const t=new Date(this.arrival).getTime();if(Number.isNaN(t))return B``;const e=Math.round((t-this._now)/1e3);return B`<span class="countdown ${e<=0?"departed":""}"
      >${this._format(e)}</span
    >`}};ft.styles=r`
    .countdown {
      font-weight: 600;
    }
    .departed {
      opacity: 0.6;
    }
  `,t([pt({attribute:!1})],ft.prototype,"arrival",void 0),t([pt({attribute:!1})],ft.prototype,"language",void 0),t([ut()],ft.prototype,"_now",void 0),ft=t([ct("google-transit-countdown")],ft);const gt={BUS:"mdi:bus",TRAM:"mdi:tram",SUBWAY:"mdi:subway",HEAVY_RAIL:"mdi:train",RAIL:"mdi:train",COMMUTER_TRAIN:"mdi:train",LIGHT_RAIL:"mdi:tram",FERRY:"mdi:ferry",WALK:"mdi:walk"};function mt(t){const e=Math.floor(t%60),i=Math.floor(t/60),s=i%60,o=Math.floor(i/60),n=e>0?`${e}s`:"";return o>0?`${o}h${s}m${n}`:s>0?`${s}m${n}`:n||"0s"}let _t=class extends at{constructor(){super(...arguments),this.legs=[],this.expanded=!1,this.language="en"}render(){if(!this.legs?.length)return B``;const t=this.legs.map(t=>this._spanSeconds(t)),e=t.reduce((t,e)=>t+e,0)||1,i=t.map(t=>Math.max(t/e*100,6)),s=i.map(t=>`minmax(0, ${t}fr)`).join(" ");return B`
      <div class="bar" style="grid-template-columns: ${s}">
        ${this.legs.map((e,i)=>{const s="WALK"===e.mode,o=gt[e.mode]??"mdi:map-marker-path",n=e.line_color||"var(--secondary-text-color, #727272)",r=Math.min(e.duration||0,t[i]),a=t[i]-r;return B`
            <div
              class="segment ${s?"walk":"transit"}"
              style=${s?"":`background: ${n};`}
              title=${e.line_full_name||e.mode}
            >
              ${s?B`
                    <div
                      class="walk-part"
                      style="flex-grow: ${Math.max(r,1)}"
                    >
                      <ha-icon icon="mdi:walk"></ha-icon>
                    </div>
                    ${a>0?B`<div
                          class="wait-part"
                          style="flex-grow: ${a}"
                          title="Waiting"
                        >
                          <ha-icon icon="mdi:human"></ha-icon>
                        </div>`:q}
                  `:B`<ha-icon icon=${o}></ha-icon
                    ><span class="line-name">${e.line_name}</span>`}
            </div>
          `})}
      </div>
      <div class="times" style="grid-template-columns: ${s}">
        ${this.legs.map((e,i)=>B`<span>${this._legTimeLabel(e,t[i])}</span>`)}
      </div>
      ${this.expanded?B`<div class="leg-details">
            ${this.legs.map(t=>{const e=this._legDetailLabel(t);return e?B`<div class="leg-detail-row">
                    <ha-icon
                      icon=${gt[t.mode]??"mdi:map-marker-path"}
                    ></ha-icon>
                    <span>${e}</span>
                  </div>`:q})}
          </div>`:q}
    `}_legTimeLabel(t,e){return t.departure_time_local?e>0?`${t.departure_time_local} (${mt(e)})`:t.departure_time_local:""}_legDetailLabel(t){if("WALK"===t.mode||!t.departure_stop||!t.arrival_stop)return"";const e="nl"===this.language,i=t.stop_count?` · ${t.stop_count} ${e?1===t.stop_count?"halte":"haltes":1===t.stop_count?"stop":"stops"}`:"";return`${this._stripCityPrefix(t.departure_stop)} → ${this._stripCityPrefix(t.arrival_stop)}${i}`}_stripCityPrefix(t){const e=t.indexOf(",");return-1===e?t:t.slice(e+1).trim()}_spanSeconds(t){if(t.departure_time&&t.arrival_time){const e=new Date(t.arrival_time).getTime()-new Date(t.departure_time).getTime();if(!Number.isNaN(e)&&e>=0)return Math.round(e/1e3)}return t.duration||0}};_t.styles=r`
    .bar {
      display: grid;
      grid-auto-flow: column;
      height: 26px;
      border-radius: 13px;
      overflow: hidden;
      margin: 6px 0 2px;
    }

    .segment {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 3px;
      color: #fff;
      font-size: 0.72em;
      overflow: hidden;
    }

    .segment.walk {
      /* .walk-part / .wait-part fill this — no background of its own. */
      gap: 0;
      overflow: hidden;
    }

    .walk-part {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      min-width: 16px;
      background: repeating-linear-gradient(
        45deg,
        var(--disabled-text-color, #9e9e9e),
        var(--disabled-text-color, #9e9e9e) 4px,
        var(--secondary-background-color, #e0e0e0) 4px,
        var(--secondary-background-color, #e0e0e0) 8px
      );
    }

    /* Flat, unstriped fill: visually distinct from the walking stripe so a
       waiting stretch doesn't read as "more walking". */
    .wait-part {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      min-width: 16px;
      background: var(--secondary-background-color, #e0e0e0);
    }

    .segment ha-icon {
      --mdc-icon-size: 15px;
      color: #fff;
    }

    .walk-part ha-icon,
    .wait-part ha-icon {
      --mdc-icon-size: 13px;
      color: #fff;
      background: var(--disabled-text-color, #9e9e9e);
      border-radius: 50%;
      padding: 2px;
    }

    .line-name {
      font-weight: 700;
    }

    .times {
      display: grid;
      grid-auto-flow: column;
      font-size: 0.72em;
      color: var(--secondary-text-color, #727272);
    }

    .times span {
      overflow: visible;
      white-space: nowrap;
      text-align: left;
    }

    .leg-details {
      display: flex;
      flex-direction: column;
      gap: 2px;
      font-size: 0.72em;
      font-style: italic;
      color: var(--secondary-text-color, #727272);
      margin-top: 4px;
    }

    .leg-detail-row {
      display: flex;
      align-items: flex-start;
      gap: 4px;
    }

    .leg-detail-row ha-icon {
      --mdc-icon-size: 13px;
      flex-shrink: 0;
      margin-top: 1px;
    }

    .leg-detail-row span {
      white-space: normal;
      overflow-wrap: break-word;
    }
  `,t([pt({attribute:!1})],_t.prototype,"legs",void 0),t([pt({attribute:!1})],_t.prototype,"expanded",void 0),t([pt({attribute:!1})],_t.prototype,"language",void 0),_t=t([ct("google-transit-journey-bar")],_t);const $t=r`
  :host {
    display: block;
  }

  ha-card {
    padding: 16px;
  }

  .card-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .card-content.compact {
    gap: 8px;
  }

  .route-row {
    cursor: pointer;
    padding: 12px 16px;
    border-radius: 12px;
    background: var(--ha-card-background, var(--card-background-color, #fff));
    border: 1px solid var(--divider-color, #e0e0e0);
    transition: opacity 0.3s ease;
  }

  .compact .route-row {
    padding: 8px 12px;
  }

  .route-row.departed {
    opacity: 0.4;
  }

  .route-row.unavailable {
    opacity: 0.6;
    font-style: italic;
  }

  .route-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.3em;
    font-weight: 600;
    color: var(--primary-text-color);
  }

  .compact .route-header {
    font-size: 1.05em;
  }

  .route-header ha-icon {
    color: var(--state-icon-color, var(--paper-item-icon-color, #44739e));
    --mdc-icon-size: 28px;
  }

  .route-name {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .arrival {
    font-size: 0.85em;
    color: var(--secondary-text-color);
    white-space: nowrap;
  }

  .route-sub {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.15em;
    margin-top: 2px;
  }

  .compact .route-sub {
    font-size: 0.95em;
  }

  .expand-arrow {
    color: var(--secondary-text-color);
    transition: transform 0.2s ease;
  }

  .expand-arrow.open {
    transform: rotate(180deg);
  }

  .alternatives {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed var(--divider-color, #e0e0e0);
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 0.9em;
    color: var(--secondary-text-color);
  }

  .alternatives-label {
    color: var(--primary-text-color);
    font-size: 0.95em;
  }

  .alternative-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }

  .alt-legs {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 4px;
  }

  .alt-leg {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    white-space: nowrap;
  }

  .alt-line-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 20px;
    padding: 1px 4px;
    border-radius: 4px;
    color: #fff;
    font-weight: 700;
    font-size: 0.95em;
  }

  .alt-mode-icon,
  .alt-walk-icon {
    --mdc-icon-size: 15px;
  }

  .alt-mode-icon {
    color: var(--secondary-text-color, #727272);
  }

  .alt-walk-icon {
    color: #fff;
    background: var(--disabled-text-color, #9e9e9e);
    border-radius: 50%;
    padding: 2px;
  }

  /* Explicit theme overrides for theme: "light" / "dark" (theme: "auto" just
     inherits the ambient Home Assistant theme variables, no override needed). */
  :host(.force-light) {
    --card-background-color: #ffffff;
    --primary-text-color: #212121;
    --secondary-text-color: #727272;
    --divider-color: #e0e0e0;
    --disabled-text-color: #9e9e9e;
  }

  :host(.force-dark) {
    --card-background-color: #1c1c1c;
    --primary-text-color: #e1e1e1;
    --secondary-text-color: #a3a3a3;
    --divider-color: #383838;
    --disabled-text-color: #6c6c6c;
  }
`,vt=new Set(["BUS","TRAM","SUBWAY","LIGHT_RAIL"]);console.info("%c GOOGLE-TRANSIT-ROUTES-CARD %c v0.1.0 ","color: white; background: #1a73e8; font-weight: 700;","color: #1a73e8; background: white; font-weight: 700;");let yt=class extends at{constructor(){super(...arguments),this._expanded=new Set}static async getConfigElement(){return await Promise.resolve().then(function(){return xt}),document.createElement("google-transit-routes-card-editor")}static getStubConfig(){return{type:"custom:google-transit-routes-card",title:"Reistijden",entities:[],show_alternatives:!0,show_legs:!0,show_countdown:!0,refresh_interval:0,theme:"auto",compact:!1}}setConfig(t){if(!t.entities||!Array.isArray(t.entities))throw new Error("google-transit-routes-card: 'entities' is required");this._config={show_alternatives:!0,show_legs:!0,show_countdown:!0,refresh_interval:0,theme:"auto",compact:!1,...t}}getCardSize(){return 1+3*(this._config?.entities?.length||1)}connectedCallback(){super.connectedCallback(),this._scheduleRefresh()}disconnectedCallback(){super.disconnectedCallback(),this._clearRefresh()}updated(t){t.has("_config")&&(this._scheduleRefresh(),this._applyThemeClass())}_applyThemeClass(){this.classList.remove("force-light","force-dark"),"light"===this._config?.theme?this.classList.add("force-light"):"dark"===this._config?.theme&&this.classList.add("force-dark")}_clearRefresh(){void 0!==this._refreshTimer&&(window.clearInterval(this._refreshTimer),this._refreshTimer=void 0)}_scheduleRefresh(){this._clearRefresh();const t=1e3*(this._config?.refresh_interval??0);t&&(this._refreshTimer=window.setInterval(()=>this._refreshEntities(),t))}_refreshEntities(){if(!this.hass||!this._config)return;const t=this._config.entities.map(t=>t.entity).filter(Boolean);t.length&&this.hass.callService("homeassistant","update_entity",{entity_id:t})}_toggleExpanded(t){const e=new Set(this._expanded);e.has(t)?e.delete(t):e.add(t),this._expanded=e}render(){if(!this._config||!this.hass)return B``;const t=this._config.compact;return B`
      <ha-card .header=${this._config.title}>
        <div class="card-content ${t?"compact":""}">
          ${this._config.entities.map(t=>this._renderRoute(t))}
        </div>
      </ha-card>
    `}_renderRoute(t){const e=this.hass,i=this._config,s=t.entity?e.states[t.entity]:void 0,o=e.locale?.language||"en",n="nl"===o;if(!s)return B`
        <div class="route-row unavailable">
          <div class="route-header">
            <ha-icon icon=${t.icon||"mdi:bus-clock"}></ha-icon>
            <span class="route-name">${t.name||t.entity}</span>
            <span class="arrival"
              >${n?"entiteit niet gevonden":"entity not found"}</span
            >
          </div>
        </div>
      `;const r=s.attributes,a=r.arrival_time,l=r.arrival_time_local,c=r.legs||[],h=r.alternative_routes||[],d=t.name||r.friendly_name||t.entity,p=this._expanded.has(t.entity),u=!!a&&new Date(a).getTime()<Date.now(),f=i.show_alternatives&&h.length>0;return B`
      <div
        class="route-row ${u?"departed":""}"
        @click=${f?()=>this._toggleExpanded(t.entity):void 0}
      >
        <div class="route-header">
          <ha-icon icon=${t.icon||"mdi:bus-clock"}></ha-icon>
          <span class="route-name">${d}</span>
          <span class="arrival">
            ${l?B`${n?"aankomst":"arrival"} ${l}`:n?"geen route gevonden":"no route found"}
          </span>
        </div>

        <div class="route-sub">
          ${i.show_countdown&&a?B`<google-transit-countdown
                .arrival=${a}
                .language=${o}
              ></google-transit-countdown>`:B`<span></span>`}
          ${f?B`<ha-icon
                class="expand-arrow ${p?"open":""}"
                icon="mdi:chevron-down"
              ></ha-icon>`:q}
        </div>

        ${i.show_legs&&c.length?B`<google-transit-journey-bar
              .legs=${c}
              .expanded=${p}
              .language=${o}
            ></google-transit-journey-bar>`:q}
        ${f&&p?B`
              <div class="alternatives">
                <strong class="alternatives-label"
                  >${n?"Alternatieven:":"Alternatives:"}</strong
                >
                ${h.slice(0,3).map(t=>B`
                    <div class="alternative-row">
                      <span>
                        ${t.departure_time_local} → ${t.arrival_time_local}
                        (${t.duration_text})
                      </span>
                      <span class="alt-legs">
                        ${(t.legs||[]).map((t,e)=>B`${e>0?", ":""}${this._renderAltLeg(t)}`)}
                      </span>
                    </div>
                  `)}
              </div>
            `:q}
      </div>
    `}_renderAltLeg(t){const e=mt(t.duration||0);if(vt.has(t.mode)&&t.line_name){const i=t.line_color||"var(--secondary-text-color, #727272)";return B`<span class="alt-leg"
        ><span class="alt-line-badge" style="background: ${i}"
          >${t.line_name}</span
        >
        (${e})</span
      >`}const i="WALK"===t.mode,s=gt[t.mode]??"mdi:map-marker-path";return B`<span class="alt-leg"
      ><ha-icon
        class=${i?"alt-walk-icon":"alt-mode-icon"}
        icon=${s}
      ></ha-icon>
      (${e})</span
    >`}};yt.styles=$t,t([pt({attribute:!1})],yt.prototype,"hass",void 0),t([ut()],yt.prototype,"_config",void 0),t([ut()],yt.prototype,"_expanded",void 0),yt=t([ct("google-transit-routes-card")],yt),window.customCards=window.customCards||[],window.customCards.push({type:"google-transit-routes-card",name:"Google Transit Routes Card",description:"Wall-mounted dashboard card showing saved Google Transit routes with live countdowns, journey bars and alternative departures.",preview:!0});const wt={show_alternatives:!0,show_legs:!0,show_countdown:!0,refresh_interval:0,theme:"auto",compact:!1};let bt=class extends at{setConfig(t){this._config={...wt,...t}}_fireChanged(t){this._config=t,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:t},bubbles:!0,composed:!0}))}_valueChanged(t){if(!this._config)return;const e=t.target,i=e.configValue;if(!i)return;let s="checkbox"===e.type?e.checked:e.value;"refresh_interval"===i&&(s=Number(s)||0),this._fireChanged({...this._config,[i]:s})}_themeChanged(t){if(!this._config)return;const e=t.target.value;this._fireChanged({...this._config,theme:e})}_entityChanged(t,e,i){if(!this._config)return;const s=[...this._config.entities];s[t]={...s[t],[e]:i},this._fireChanged({...this._config,entities:s})}_addEntity(){if(!this._config)return;const t=[...this._config.entities||[],{entity:""}];this._fireChanged({...this._config,entities:t})}_removeEntity(t){if(!this._config)return;const e=this._config.entities.filter((e,i)=>i!==t);this._fireChanged({...this._config,entities:e})}render(){return this._config&&this.hass?B`
      <div class="card-config">
        <ha-textfield
          label="Title"
          .value=${this._config.title||""}
          .configValue=${"title"}
          @input=${this._valueChanged}
        ></ha-textfield>

        <h3>Routes</h3>
        ${this._config.entities.map((t,e)=>B`
            <div class="entity-row">
              <ha-entity-picker
                .hass=${this.hass}
                .value=${t.entity}
                .includeDomains=${["sensor"]}
                @value-changed=${t=>this._entityChanged(e,"entity",t.detail.value)}
              ></ha-entity-picker>
              <ha-textfield
                label="Name"
                .value=${t.name||""}
                @input=${t=>this._entityChanged(e,"name",t.target.value)}
              ></ha-textfield>
              <ha-icon-picker
                label="Icon (optional)"
                .hass=${this.hass}
                .value=${t.icon||""}
                @value-changed=${t=>this._entityChanged(e,"icon",t.detail.value)}
              ></ha-icon-picker>
              <ha-icon-button
                .path=${"M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"}
                @click=${()=>this._removeEntity(e)}
              ></ha-icon-button>
            </div>
          `)}
        <mwc-button @click=${this._addEntity}>+ Add route</mwc-button>

        <h3>Display options</h3>
        <div class="switch-row">
          <ha-formfield label="Show alternative routes">
            <ha-switch
              .checked=${this._config.show_alternatives??!0}
              .configValue=${"show_alternatives"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
          <ha-formfield label="Show journey bar (legs)">
            <ha-switch
              .checked=${this._config.show_legs??!0}
              .configValue=${"show_legs"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
          <ha-formfield label="Show live countdown">
            <ha-switch
              .checked=${this._config.show_countdown??!0}
              .configValue=${"show_countdown"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
          <ha-formfield label="Compact mode">
            <ha-switch
              .checked=${this._config.compact??!1}
              .configValue=${"compact"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
        </div>

        <ha-textfield
          label="Refresh interval in seconds (0 = off, no automatic API calls)"
          helper="Each refresh calls the Google Routes API for every route on this card. Leave at 0 unless you understand the quota cost — see the API quota section in the README."
          helper-persistent
          type="number"
          .value=${String(this._config.refresh_interval??0)}
          .configValue=${"refresh_interval"}
          @input=${this._valueChanged}
        ></ha-textfield>

        <label class="theme-label">
          Theme
          <select .value=${this._config.theme||"auto"} @change=${this._themeChanged}>
            <option value="auto">Auto (follow Home Assistant theme)</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </label>
      </div>
    `:B``}};bt.styles=r`
    .card-config {
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 8px 0;
    }
    h3 {
      margin: 8px 0 0;
      font-size: 1em;
      color: var(--secondary-text-color);
    }
    .entity-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .entity-row ha-entity-picker {
      flex: 2;
    }
    .entity-row ha-textfield {
      flex: 1;
    }
    .switch-row {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .theme-label {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 0.9em;
      color: var(--secondary-text-color);
    }
  `,t([pt({attribute:!1})],bt.prototype,"hass",void 0),t([ut()],bt.prototype,"_config",void 0),bt=t([ct("google-transit-routes-card-editor")],bt);var xt=Object.freeze({__proto__:null,get GoogleTransitRoutesCardEditor(){return bt}});export{yt as GoogleTransitRoutesCard};
