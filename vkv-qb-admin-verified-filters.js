// Read-only filter helper for the already-rendered Verified Contribution view.
// No Firestore/network access and no ranking recalculation.
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function parseLeader(card){
  const text=String(card?.textContent||'');
  const verified=text.match(/Verified:\s*(\d+)\s*of\s*(\d+)\s*submitted/i);
  const returned=text.match(/Returned for revision:\s*(\d+)/i);
  return{verified:Number(verified?.[1]||0),submitted:Number(verified?.[2]||0),returned:Number(returned?.[1]||0)};
}
function apply(){
  const list=document.getElementById('verifiedContributionList'),select=document.getElementById('vCFollowupView'),status=document.getElementById('vCFollowupStatus');
  if(!list||!select||!status)return;
  const cards=[...list.querySelectorAll('.leader')];
  if(!cards.length){status.textContent='';return}
  let shown=0;
  for(const card of cards){
    const x=parseLeader(card),mode=select.value;
    const visible=mode==='all'||(mode==='revision'&&x.returned>0)||(mode==='small'&&x.submitted>0&&x.submitted<5)||(mode==='zero'&&x.submitted>0&&x.verified===0);
    card.style.display=visible?'':'none';if(visible)shown++;
  }
  status.textContent=`Showing ${shown} of ${cards.length} contributors. Existing ranks are preserved; this view filter does not recalculate ranking.`;
}
async function init(){
  for(let i=0;i<60&&!document.getElementById('verifiedContribution');i++)await wait(100);
  const panel=document.getElementById('verifiedContribution');if(!panel||document.getElementById('vCFollowupView'))return;
  const rank=document.getElementById('vCRankMode');if(!rank)return;
  const wrap=document.createElement('div');wrap.style.cssText='margin-top:10px;max-width:420px';
  wrap.innerHTML='<label>Follow-up view</label><select id="vCFollowupView"><option value="all">All contributors</option><option value="revision">Revision follow-up (currently returned)</option><option value="small">Small sample (&lt;5 submitted)</option><option value="zero">No verified yet</option></select><div id="vCFollowupStatus" class="small" style="margin-top:5px"></div><div class="small" style="margin-top:3px">View-only filter. Copy Summary and CSV continue to use the full calculated cohort.</div>';
  rank.parentElement?.insertAdjacentElement('afterend',wrap);
  document.getElementById('vCFollowupView').addEventListener('change',apply);
  const list=document.getElementById('verifiedContributionList');if(list)new MutationObserver(apply).observe(list,{childList:true,subtree:false});
  apply();
}
init().catch(e=>console.warn('QB verified contribution filters:',e));
