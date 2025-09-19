
(function(){
  const state = { data: [], ready:false };
  function escapeHTML(s){ return s.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m])) }
  function highlight(haystack,q){
    const i = haystack.toLowerCase().indexOf(q.toLowerCase());
    if(i<0) return escapeHTML(haystack);
    return escapeHTML(haystack.slice(0,i)) + "<mark>" + escapeHTML(haystack.slice(i,i+q.length)) + "</mark>" + escapeHTML(haystack.slice(i+q.length));
  }
  function score(item, q){
    const t = (item.title||"") + " " + (item.h1||"") + " " + (item.desc||"");
    const idx = t.toLowerCase().indexOf(q.toLowerCase());
    let base = idx<0 ? 9999 : idx;
    // tiny bonus if query matches path segments
    if(item.path.toLowerCase().includes(q.toLowerCase())) base -= 5;
    return base;
  }
  function render(list, q){
    const box = document.getElementById("tb-suggest");
    if(!box) return;
    box.innerHTML = "";
    if(!q){ box.hidden = true; return; }
    const items = state.data
      .map(x=>[x, score(x,q)])
      .filter(([_,s])=>s<9999)
      .sort((a,b)=>a[1]-b[1])
      .slice(0,10)
      .map(([x,_])=>x);
    if(items.length===0){ box.hidden = true; return; }
    items.forEach((it, idx)=>{
      const d = document.createElement("div");
      d.className = "suggestion-item";
      d.setAttribute("role","option");
      d.setAttribute("data-path", it.path);
      if(idx===0) d.setAttribute("aria-selected","true");
      d.innerHTML = `<div class="suggestion-body">
        <div class="suggestion-title">${highlight(it.title||it.h1||it.path, q)}</div>
        <div class="suggestion-path">${escapeHTML(it.path)}</div>
        ${it.desc?`<div class="suggestion-desc">${escapeHTML(it.desc.slice(0,120))}</div>`:""}
      </div>`;
      d.addEventListener("mousedown", (e)=>{ e.preventDefault(); window.location.href = it.path; });
      box.appendChild(d);
    });
    box.hidden = false;
  }
  function moveActive(dir){
    const box = document.getElementById("tb-suggest");
    if(!box || box.hidden) return;
    const items = Array.from(box.querySelectorAll(".suggestion-item"));
    let idx = items.findIndex(el=>el.getAttribute("aria-selected")==="true");
    if(idx<0) idx = 0;
    items.forEach(el=>el.removeAttribute("aria-selected"));
    idx = (idx + dir + items.length) % items.length;
    items[idx].setAttribute("aria-selected","true");
  }
  function goActive(){
    const box = document.getElementById("tb-suggest");
    if(!box || box.hidden) return;
    const el = box.querySelector(".suggestion-item[aria-selected='true']") || box.querySelector(".suggestion-item");
    if(el){ window.location.href = el.getAttribute("data-path"); }
  }

  function init(){
    const input = document.getElementById("tb-search");
    const box = document.getElementById("tb-suggest");
    if(!input || !box) return;
    // fetch index on first focus
    let fetched = false;
    function ensure(){
      if(fetched) return Promise.resolve();
      fetched = true;
      return fetch("/assets/search-index.json").then(r=>r.json()).then(d=>{ state.data = d; state.ready = true; }).catch(console.error);
    }
    let t = null;
    input.addEventListener("input", function(){
      const q = this.value.trim();
      clearTimeout(t);
      t = setTimeout(()=>{ ensure().then(()=>render(state.data, q)); }, 80);
    });
    input.addEventListener("focus", function(){
      if(this.value.trim()){ ensure().then(()=>render(state.data, this.value.trim())); }
    });
    input.addEventListener("keydown", function(e){
      if(e.key==="ArrowDown"){ e.preventDefault(); moveActive(1); }
      else if(e.key==="ArrowUp"){ e.preventDefault(); moveActive(-1); }
      else if(e.key==="Enter"){ e.preventDefault(); goActive(); }
      else if(e.key==="Escape"){ document.getElementById("tb-suggest").hidden = true; }
    });
    document.addEventListener("click", function(e){
      if(!e.target.closest(".site-search")){ box.hidden = true; }
    });
  }

  // public init for when header is injected dynamically
  window.__TB_INIT_SEARCH__ = init;
})();
