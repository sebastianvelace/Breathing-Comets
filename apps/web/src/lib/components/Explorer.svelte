<script lang="ts">
  import { onMount } from 'svelte';
  import { wrap, proxy } from 'comlink';
  import { page } from '$app/state';
  import { replaceState } from '$app/navigation';
  import { getLocale, localizeHref } from '#lib/paraglide/runtime.js';
  import * as m from '#lib/paraglide/messages.js';
  import { view } from '#lib/state/view.svelte.js';
  import { parseView, serializeView, nearestFrame, type Mode } from '#lib/state/view.js';
  import type { Frame, Header, Stack, Manifest, GaiaStar, SpectrumPoint } from '#lib/data/types.js';
  import type { StackService } from '#lib/workers/stack.worker.js';
  import SpxViewer from './SpxViewer.svelte';
  import Timeline from './Timeline.svelte';
  import ModeSwitch from './ModeSwitch.svelte';
  import FieldNotes from './FieldNotes.svelte';
  import SpectrumPlot from './SpectrumPlot.svelte';

  let { embed = false }: { embed?: boolean } = $props();
  const targets = [{slug:'barnard',name:"Barnard’s Star"},{slug:'eps-indi-b',name:'ε Indi B'},{slug:'wise-0855',name:'WISE 0855−0714'},{slug:'rw-aur',name:'RW Aurigae'},{slug:'r-dra',name:'R Draconis'}];
  let ready = $state(false), manifest = $state.raw<Manifest>(), base = $state.raw<Stack>(), diff = $state.raw<Stack>();
  let gaia = $state.raw<GaiaStar[]>([]), spectrum = $state.raw<SpectrumPoint[]>([]);
  let index = $state(0), a = $state(0), b = $state(0), playing = $state(false), speed = $state(4), blend = $state(0);
  let error = $state(''), diffError = $state(''), gaiaError = $state(false), retry = $state(0), copied = $state(false), search = $state(''), searchError = $state(false);
  let shareLink = $state(''), selected = $state<[number,number]>(), livePoints = $state.raw<SpectrumPoint[]>([]), spectrumStatus = $state('');
  let urlTimer: ReturnType<typeof setTimeout> | undefined;
  const active = $derived(view.mode === 'diff' ? diff : base);
  const shownIndex = $derived(view.mode === 'blink' ? (blend >= .5 ? b : a) : index);
  const current = $derived(base?.header.frames[Math.min(shownIndex,Math.max(0,(base?.frames.length??1)-1))]);
  const star = $derived(gaia.find(s=>s.source_id===manifest?.gaia_target_id));
  const availableDiff = $derived(view.mode !== 'diff' || !!diff?.header.frames[index]?.diff_available);
  const languageHref = $derived(localizeHref(page.url.pathname+page.url.search,{locale:getLocale()==='en'?'es':'en'}));

  onMount(() => {
    Object.assign(view,parseView(page.url.searchParams)); view.lang=getLocale();
    if (!page.url.searchParams.has('det')) view.det=view.target==='barnard'?4:6;
    ready=true;
    const pop = () => { Object.assign(view,parseView(new URL(location.href).searchParams)); index=nearestFrame(base?.header.frames.map(f=>f.mjd)??[],view.t); playing=false; };
    window.addEventListener('popstate',pop);
    return () => { window.removeEventListener('popstate',pop); clearTimeout(urlTimer); };
  });
  function writeUrl(immediate=false) {
    clearTimeout(urlTimer);
    const write=()=>{if(!base||!manifest)return;view.ra=manifest.ra;view.dec=manifest.dec;view.fov=manifest.fov_deg;view.t=base.header.frames[index]?.mjd;view.ch=base.header.frames[index]?.lam_um;view.a=base.header.frames[a]?.mjd;view.b=base.header.frames[b]?.mjd;view.lang=getLocale();const url=new URL(page.url.href);url.search=serializeView(view).toString();replaceState(url,{});shareLink=url.href;};
    if(immediate)write();else urlTimer=setTimeout(write,150);
  }
  $effect(()=>{
    if(!ready)return;
    const slug=view.target,det=view.det,attempt=retry;
    void attempt;
    const abort=new AbortController();let worker:Worker|undefined,alive=true;
    base=undefined;diff=undefined;gaia=[];spectrum=[];error='';diffError='';gaiaError=false;manifest=undefined;playing=false;selected=undefined;livePoints=[];spectrumStatus='';
    const root=`/data/targets/${encodeURIComponent(slug)}/`;
    (async()=>{
      const response=await fetch(root+'manifest.json',{signal:abort.signal});if(!response.ok)throw Error(`Manifest HTTP ${response.status}`);
      const data:Manifest=await response.json();if(!alive)return;manifest=data;
      if(!data.stacks[String(det)])throw Error('Detector unavailable');
      fetch(root+data.gaia,{signal:abort.signal}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(list=>{if(alive)gaia=list;}).catch(()=>{if(alive)gaiaError=true;});
      fetch(`/data/targets/${encodeURIComponent(slug)}.json`,{signal:abort.signal}).then(r=>r.json()).then(d=>{if(alive)spectrum=d.spectrum??[];}).catch(()=>{});
      worker=new Worker(new URL('../workers/stack.worker.ts',import.meta.url),{type:'module'});
      const remote=wrap<StackService>(worker);
      let desired=0;
      await remote.load(root+data.stacks[String(det)],proxy((header:Header)=>{if(!alive)return;desired=nearestFrame(header.frames.map(f=>f.mjd),view.t);a=nearestFrame(header.frames.map(f=>f.mjd),view.a);b=view.b===undefined?header.frames.length-1:nearestFrame(header.frames.map(f=>f.mjd),view.b);index=0;blend=0;base={header,frames:[]};}),proxy((frame:Frame,i:number)=>{if(!alive||!base)return;base={header:base.header,frames:[...base.frames,frame]};index=Math.min(desired,i);}));
      if(alive)writeUrl(true);
    })().catch(e=>{if(alive&&!abort.signal.aborted)error=String(e);});
    return()=>{alive=false;abort.abort();worker?.terminate();};
  });
  $effect(()=>{
    if(view.mode!=='diff'||!manifest)return;
    const root=`/data/targets/${manifest.slug}/`, filename=manifest.diff[String(view.det)];
    if(!filename){diffError=m.diff_detector();return;}
    const worker=new Worker(new URL('../workers/stack.worker.ts',import.meta.url),{type:'module'});let alive=true;
    wrap<StackService>(worker).load(root+filename,proxy((header:Header)=>{if(alive)diff={header,frames:[]};}),proxy((frame:Frame)=>{if(alive&&diff)diff={header:diff.header,frames:[...diff.frames,frame]};})).catch(e=>{if(alive)diffError=String(e);});
    return()=>{alive=false;worker.terminate();};
  });
  $effect(()=>{
    if(!playing||!base?.frames.length)return;
    const count=base.frames.length, mode=view.mode, fps=speed, reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
    let id=0,start=0,last=0;
    function tick(time:number){if(!start)start=time;if(mode==='blink'){const phase=(time-start)%1000;const target=phase>=500?1:0;const elapsed=phase%500;blend=reduced?target:target?Math.min(1,elapsed/80):1-Math.min(1,elapsed/80);}else if(time-last>=1000/fps){index=(index+1)%count;last=time;}id=requestAnimationFrame(tick);}
    id=requestAnimationFrame(tick);return()=>cancelAnimationFrame(id);
  });
  function modeChange(value:string){view.mode=value as Mode;playing=false;blend=0;writeUrl();}
  function choose(slug:string){if(!targets.some(t=>t.slug===slug))return;view.target=slug;view.det=slug==='barnard'?4:6;view.mode='epoch';view.t=undefined;view.a=undefined;view.b=undefined;search='';searchError=false;}
  function submitSearch(e:SubmitEvent){e.preventDefault();const q=search.trim().toLowerCase(),target=targets.find(t=>t.slug===q||t.name.toLowerCase().includes(q));if(target&&q)choose(target.slug);else searchError=true;}
  function compare(){view.mode='blink';a=0;b=(base?.frames.length??1)-1;blend=0;playing=true;writeUrl();}
  async function share(){writeUrl(true);try{await navigator.clipboard.writeText(shareLink);copied=true;setTimeout(()=>copied=false,2500);}catch{copied=false;}}
  async function pick(ra:number,dec:number){selected=[ra,dec];livePoints=[];spectrumStatus=m.spectrum_pending();}
</script>

<svelte:head><title>{manifest?.name??'Explore'} · Breathing Comets</title><meta name="description" content="Compare real SPHEREx survey images across dates and infrared wavelengths." /></svelte:head>

{#if !embed}<header class="site-header"><a class="brand" href={localizeHref('/')}>BREATHING COMETS</a><nav><a href={languageHref} aria-label={m.language()}>{getLocale()==='en'?'ES':'EN'}</a><button onclick={share}>{copied?m.copied():m.share()} ↗</button></nav></header>{/if}
<main class:embedded={embed}>
  {#if !embed}<section class="search-section"><form onsubmit={submitSearch}><label class="sr-only" for="sky-search">{m.search_sky()}</label><input id="sky-search" type="search" list="target-list" bind:value={search} placeholder={m.search_sky()} autocomplete="off"/><datalist id="target-list">{#each targets as target}<option value={target.name}></option>{/each}</datalist><button aria-label={m.search_submit()}>{m.search_submit()} →</button></form>{#if searchError}<p role="status" class="mono">{m.no_target()}</p>{/if}<div class="target-links">{#each targets as target}<button class:chosen={view.target===target.slug} aria-pressed={view.target===target.slug} onclick={()=>choose(target.slug)}>{target.name}</button>{/each}</div></section>{/if}
  <div class="explorer-grid">
    <section class="observation">
      <div class="toolbar"><ModeSwitch value={view.mode} onchange={modeChange}/><label class="mono">{m.detector()} <select aria-label={m.detector()} bind:value={view.det} onchange={()=>{view.t=undefined;playing=false;}}>{#each [1,2,3,4,5,6] as det}<option value={det}>D{det}</option>{/each}</select></label><label class="gaia-toggle mono"><input type="checkbox" checked={view.layers.includes('gaia')} onchange={e=>{view.layers=e.currentTarget.checked?['gaia']:[];writeUrl();}}/> Gaia</label></div>
      {#if active&&manifest&&active.frames.length&&availableDiff}
        {#key `${manifest.slug}/${view.det}/${view.mode==='diff'}`}<SpxViewer stack={active} {index} {a} {b} mode={view.mode} {blend} {manifest} {star} showGaia={view.layers.includes('gaia')} onpick={pick}/>{/key}
      {:else}<div class="empty-plate" role="status"><span class="mono">{error?m.load_failed():diffError||(!availableDiff?m.diff_unavailable():m.loading())}</span>{#if error}<button onclick={()=>retry++}>{m.retry()}</button><small>{error}</small>{/if}</div>{/if}
      {#if base&&base.frames.length}
        <Timeline frames={base.header.frames} bind:index loaded={base.frames.length} {playing} bind:speed ontoggle={()=>playing=!playing} onmanual={()=>playing=false} oncommit={()=>writeUrl()}/>
        {#if view.mode==='blink'}<div class="compare-dates"><label>{m.date_a()}<select aria-label={m.date_a()} bind:value={a} onchange={()=>writeUrl()}>{#each base.header.frames.slice(0,base.frames.length) as frame,i}<option value={i}>{frame.date.slice(0,10)} · {frame.lam_um.toFixed(3)} µm</option>{/each}</select></label><span>↔</span><label>{m.date_b()}<select aria-label={m.date_b()} bind:value={b} onchange={()=>writeUrl()}>{#each base.header.frames.slice(0,base.frames.length) as frame,i}<option value={i}>{frame.date.slice(0,10)} · {frame.lam_um.toFixed(3)} µm</option>{/each}</select></label></div>{/if}
        <div class="metadata mono" data-testid="frame-metadata"><span>D{view.det} · {current?.lam_um.toFixed(3)} µm · {current?.date.replace('T',' ').slice(0,19)} UTC</span><span>MJD {current?.mjd.toFixed(3)} · {m.visit()} {(current?.visit??0)+1} · {m.frame()} {shownIndex+1}/{base.header.frames.length}</span><span>{current?.obs_id}</span></div>
        <p class="stretch-note mono">{m.whole_stack()}</p>
        <p class="explanation">{view.mode==='diff'?m.diff_explain():view.mode==='blink'?m.blink_explain():m.same_stretch()}</p>
        {#if gaiaError}<p class="mono" role="status">{m.loading_gaia()} <button onclick={()=>retry++}>{m.retry()}</button></p>{:else if !star}<p class="mono muted">{m.no_gaia_target()}</p>{/if}
        {#if selected}<section class="selected-spectrum"><h2>{m.live_spectrum()}</h2><p class="mono">{m.pixel_selected()}: {selected[0].toFixed(6)}, {selected[1].toFixed(6)}</p><p role="status">{spectrumStatus}</p>{#if livePoints.length}<SpectrumPlot points={livePoints} label={m.live_spectrum()}/>{/if}</section>{/if}
      {/if}
      {#if base}<p class="loading-progress mono" role="status">{m.frame_count({loaded:String(base.frames.length),total:String(base.header.frames.length)})}</p>{/if}
    </section>
    {#if !embed&&manifest}<FieldNotes {manifest} {spectrum} oncompare={compare} onplay={()=>playing=!playing}/>{/if}
  </div>
  {#if embed}<a class="embed-brand mono" href={localizeHref('/explore')+'?'+serializeView(view)} target="_blank" rel="noopener">BREATHING COMETS ↗ · {m.embed_full()}</a>{:else}<details class="share-details"><summary>{m.share()}</summary><label class="mono" for="share-link">URL</label><input id="share-link" readonly value={shareLink||page.url.href}/><button onclick={share}>{copied?m.copied():m.copy_link()}</button></details>{/if}
</main>
{#if !embed}<footer class="mono">{m.credits()}</footer>{/if}

<style>
  .site-header{padding:20px var(--gutter);display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--rule);gap:18px}.site-header nav{display:flex;align-items:center;gap:24px}.site-header nav a{font:12px var(--font-data)}main{padding:30px var(--gutter) 48px;max-width:1800px;margin:auto}.search-section{margin-bottom:32px}form{display:flex;border-bottom:1px solid var(--ink);align-items:center}form input{font:italic clamp(21px,2.5vw,36px) var(--font-display);width:100%;padding:10px 0 14px;border:0;background:transparent}form button{border:0;white-space:nowrap}.target-links{display:flex;gap:22px;flex-wrap:wrap;margin-top:16px}.target-links button{padding:0 0 6px;border:0;border-bottom:1px solid transparent;font-size:13px;min-height:28px;color:var(--graphite);background:none}.target-links button.chosen{color:var(--co2);border-bottom-color:var(--co2)}.explorer-grid{display:grid;grid-template-columns:minmax(0,3fr) minmax(250px,1fr);gap:0}.observation{min-width:0}.toolbar{display:flex;align-items:center;gap:20px;margin-bottom:14px}.toolbar label{display:flex;align-items:center;gap:6px}.toolbar select{padding:4px}.gaia-toggle{margin-left:auto}.empty-plate{aspect-ratio:1.47;background:var(--plate);color:var(--plate-ink);border:1px solid var(--rule);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;padding:28px;text-align:center}.empty-plate small{max-width:100%;overflow-wrap:anywhere}.compare-dates{display:flex;gap:12px;align-items:center;padding:12px 0;border-bottom:1px solid var(--rule);flex-wrap:wrap}.compare-dates label{font:11px var(--font-data);display:flex;gap:9px;align-items:center}.compare-dates select{max-width:100%;font-size:11px}.metadata{display:flex;gap:8px 20px;flex-wrap:wrap;padding:15px 0;color:var(--ink-2);overflow-wrap:anywhere}.stretch-note{color:var(--graphite);font-size:10px}.explanation{font:20px/1.4 var(--font-display);max-width:650px;color:var(--ink-2)}.loading-progress{color:var(--graphite);font-size:10px}.share-details{border-top:1px solid var(--rule);padding-top:18px;margin-top:35px}.share-details input{display:block;width:100%;font:12px var(--font-data);margin:12px 0}.share-details summary{font-size:13px;cursor:pointer}.selected-spectrum{max-width:650px;border-top:1px solid var(--rule);padding-top:24px}.embedded{padding:0}.embedded .explorer-grid{display:block}.embed-brand{display:block;text-decoration:none;text-align:right;padding:8px}.embedded .toolbar{padding:8px;margin:0}.embedded .metadata,.embedded :global(.timeline){padding:10px}.embedded .explanation,.embedded .stretch-note{display:none}@media(max-width:1000px){.explorer-grid{grid-template-columns:minmax(0,2.3fr) minmax(240px,1fr)}.toolbar{gap:10px}}@media(max-width:767px){main{padding-top:20px}.site-header{padding:14px 16px}.site-header .brand{font-size:11px;letter-spacing:.10em}.site-header nav{gap:12px}.site-header nav button{font-size:11px;padding:6px}.explorer-grid{display:block}.target-links{gap:10px 18px}.search-section{margin-bottom:24px}.toolbar{flex-wrap:wrap;gap:10px}.toolbar :global(button){font-size:13px;padding:7px 12px}.gaia-toggle{margin-left:0}.empty-plate{aspect-ratio:1}.compare-dates{gap:6px}.compare-dates label{flex:1;display:block;min-width:0}.compare-dates select{display:block;width:100%;margin-top:5px}.metadata{font-size:10px;gap:6px}footer{font-size:10px}}
</style>
