(function(){
  const byId = id => document.getElementById(id);
  const totalMembers = byId('totalMembers');

  const overlay = byId('modalOverlay');
  const closeBtn = byId('closeModal');
  const addBtn = byId('addTLBtn');
  const nameInput = byId('addTLName');
  const deptInput = byId('addTLDept');
  const listEl = byId('teamLeadList');

  const detailsPanel = byId('teamLeadDetails');
  const detailName = byId('detailName');
  const detailDept = byId('detailDept');
  const detailActive = byId('detailActive');
  const detailCompleted = byId('detailCompleted');
  const detailPending = byId('detailPending');
  const closeDetailsBtn = byId('closeDetails');

  const deptOverlay = byId('deptModalOverlay');
  const deptModalClose = byId('closeDeptModal');
  const deptListEl = byId('deptList');

  const deptDetailsPanel = byId('deptDetails');
  const deptNameEl = byId('deptName');
  const deptLeadEl = byId('deptLead');
  const deptMemberTbody = byId('deptMemberTbody');
  const closeDeptDetailsBtn = byId('closeDeptDetails');

  const deptFilterInput = byId('deptFilterInput');
  const deptAddName = byId('deptAddName');
  const deptAddRole = byId('deptAddRole');
  const deptAddBtn = byId('deptAddBtn');
  const sortByNameBtn = byId('sortByName');
  const sortByRoleBtn = byId('sortByRole');

  const employeeProfileOverlay = byId('employeeProfileOverlay');
  const closeProfileModal = byId('closeProfileModal');
  const profileNameEl = byId('profileName');
  const profileRoleEl = byId('profileRole');
  const profileDepartmentEl = byId('profileDepartment');
  const profileEmployeeIdEl = byId('profileEmployeeId');
  const profileEmailEl = byId('profileEmail');
  const profilePhoneEl = byId('profilePhone');
  const openFullProfileBtn = byId('openFullProfileBtn');

  const departments = ['Python Team','Java Team','Devops Team','Frontend Team','UI/UX Team'];

  const defaultDeptMembers = {
      };

  const raw = localStorage.getItem('teamLeads');
  let teamLeads = [];
  try {
    const parsed = raw ? JSON.parse(raw) : [];
    if(Array.isArray(parsed)){
      teamLeads = parsed.map(item => {
        if(item && typeof item === 'object') return { name: item.name||'', dept: item.dept||'', active: item.active||0, completed: item.completed||0, pending: item.pending||0 };
        return { name: String(item||''), dept: '', active:0, completed:0, pending:0 };
      }).filter(t => t.name);
    }
  } catch(e){ teamLeads = []; }

  const rawMembers = localStorage.getItem('departmentMembers');
  let departmentMembers = {};
  try {
    const parsed = rawMembers ? JSON.parse(rawMembers) : null;
    if(parsed && typeof parsed === 'object') departmentMembers = parsed;
    else departmentMembers = Object.assign({}, defaultDeptMembers);
  } catch(e){ departmentMembers = Object.assign({}, defaultDeptMembers); }

  const normalize = s => (s||'').toString().trim().toLowerCase();

  function saveLeads(){ localStorage.setItem('teamLeads', JSON.stringify(teamLeads)); }

  function updateMemberCount(){
    let total = 0;
    Object.keys(departmentMembers).forEach(k => {
      const arr = departmentMembers[k];
      if(Array.isArray(arr)) total += arr.length;
    });
    if(totalMembers) totalMembers.textContent = String(total);
  }

  function saveDeptMembers(){ localStorage.setItem('departmentMembers', JSON.stringify(departmentMembers)); updateMemberCount(); }

  let selectedIndex = -1;

  function showOverlay(){ overlay.style.display = 'flex'; renderLeadList(); setTimeout(()=>nameInput.focus(),50); }
  function hideOverlay(){ overlay.style.display = 'none'; }

  function renderLeadList(){
    listEl.innerHTML = '';
    if(teamLeads.length===0){
      const li=document.createElement('li');
      li.textContent='No team leads added yet.';
      li.className='small';
      listEl.appendChild(li);
      return;
    }
    teamLeads.forEach((tl,idx)=>{
      const li=document.createElement('li');
      li.style.display='flex'; li.style.justifyContent='space-between'; li.style.alignItems='center'; li.style.padding='8px 0';
      const left=document.createElement('div');
      left.style.display='flex'; left.style.flexDirection='column';
      const nameSpan=document.createElement('span');
      nameSpan.textContent=tl.name; nameSpan.style.fontWeight='600'; nameSpan.style.cursor='pointer'; nameSpan.title='Click to view details';
      nameSpan.addEventListener('click',()=>{ showDetails(idx); });
      const deptSpan=document.createElement('span');
      deptSpan.textContent=tl.dept||'No department'; deptSpan.className='small'; deptSpan.style.color='var(--muted)'; deptSpan.style.fontSize='0.85rem';
      left.appendChild(nameSpan); left.appendChild(deptSpan);
      const right=document.createElement('div');
      right.style.display='flex'; right.style.gap='8px';
      const rm=document.createElement('button');
      rm.textContent='Remove'; rm.className='btn btn-secondary';
      rm.addEventListener('click',()=>{ teamLeads.splice(idx,1); saveLeads(); renderLeadList(); if(selectedIndex===idx) hideDetails(); });
      right.appendChild(rm); li.appendChild(left); li.appendChild(right); listEl.appendChild(li);
    });
  }

  function showDetails(idx){
    const tl=teamLeads[idx];
    if(!tl) return;
    selectedIndex=idx;
    detailName.textContent=tl.name; detailDept.textContent=tl.dept||'No department';
    detailActive.textContent=String(tl.active||0); detailCompleted.textContent=String(tl.completed||0); detailPending.textContent=String(tl.pending||0);
    detailsPanel.style.display='block'; hideOverlay();
    detailsPanel.scrollIntoView({behavior:'smooth',block:'center'});
  }

  function hideDetails(){ selectedIndex=-1; detailsPanel.style.display='none'; }

  closeBtn.addEventListener('click', hideOverlay);
  overlay.addEventListener('click',(e)=>{ if(e.target===overlay) hideOverlay(); });
  addBtn.addEventListener('click',()=>{
    const name=(nameInput.value||'').trim(); const dept=(deptInput.value||'').trim();
    if(!name) return;
    teamLeads.push({name,dept,active:0,completed:0,pending:0}); nameInput.value=''; deptInput.value=''; saveLeads(); renderLeadList(); nameInput.focus();
  });
  nameInput.addEventListener('keydown',(e)=>{ if(e.key==='Enter'){ e.preventDefault(); addBtn.click(); } });
  deptInput.addEventListener('keydown',(e)=>{ if(e.key==='Enter'){ e.preventDefault(); addBtn.click(); } });
  document.addEventListener('keydown',(e)=>{ if(e.key==='Escape'){ hideOverlay(); hideDetails(); hideDeptDetails(); hideDeptModal(); hideEmployeeProfile(); } });
  closeDetailsBtn.addEventListener('click', hideDetails);

  function showDeptModal(){ deptOverlay.style.display='flex'; renderDeptList(); }
  function hideDeptModal(){ deptOverlay.style.display='none'; }

  function renderDeptList(){
    deptListEl.innerHTML='';
    departments.forEach(d=>{
      const li=document.createElement('li');
      li.style.padding='8px 4px'; li.style.cursor='pointer'; li.style.borderBottom='1px solid rgba(0,0,0,0.04)';
      li.textContent=d;
      li.addEventListener('click',()=>{ showDeptDetails(d); });
      deptListEl.appendChild(li);
    });
  }

  let currentDeptKey = null;
  let currentSort = { key: 'name', asc: true };

  function renderDeptMembersTable(members){
    deptMemberTbody.innerHTML = '';
    if(!members || members.length === 0){
      const tr=document.createElement('tr'); const td=document.createElement('td');
      td.colSpan=4; td.textContent='No members in this department.'; td.className='small'; td.style.padding='10px'; td.style.border='1px solid #e6e6e6';
      tr.appendChild(td); deptMemberTbody.appendChild(tr); return;
    }
    const original = departmentMembers[currentDeptKey] || [];
    members.forEach((m,i)=>{
      const tr=document.createElement('tr');
      const tdIndex=document.createElement('td'); tdIndex.textContent=String(i+1); tdIndex.style.padding='8px 10px'; tdIndex.style.border='1px solid #e6e6e6'; tdIndex.style.fontWeight='600';
      const tdName=document.createElement('td'); tdName.style.padding='8px 10px'; tdName.style.border='1px solid #e6e6e6';
      const nameDiv=document.createElement('div'); nameDiv.textContent=m.name||''; nameDiv.className='employee-link'; nameDiv.style.fontWeight='600'; nameDiv.title='Click to view employee profile';
      nameDiv.addEventListener('click',()=>{
        const departmentName=deptNameEl?deptNameEl.textContent:'';
        showEmployeeProfile({ name:m.name||'Unknown', role:m.role||'Member', department:departmentName||currentDeptKey||'Unknown', email:generateEmployeeEmail(m.name), phone:generateEmployeePhone(i), employeeId:generateEmployeeId(m.name) });
      });
      tdName.appendChild(nameDiv);
      const tdRole=document.createElement('td'); tdRole.style.padding='8px 10px'; tdRole.style.border='1px solid #e6e6e6';
      const roleDiv=document.createElement('div'); roleDiv.textContent=m.role||'Member'; roleDiv.className='small'; roleDiv.style.color='var(--muted)'; tdRole.appendChild(roleDiv);
      const tdActions=document.createElement('td'); tdActions.style.textAlign='right'; tdActions.style.padding='8px 10px'; tdActions.style.border='1px solid #e6e6e6';
      const editBtn=document.createElement('button'); editBtn.textContent='Edit'; editBtn.className='btn btn-secondary edit-btn';
      editBtn.addEventListener('click',()=>{
        const newRole=prompt('Edit role for '+(m.name||'')+':',m.role||'Member');
        if(newRole!==null){ m.role=newRole.trim()||'Member'; saveDeptMembers(); applyDeptFiltersAndRender(); }
      });
      const removeBtn=document.createElement('button'); removeBtn.textContent='Remove'; removeBtn.className='btn btn-secondary remove-btn';
      removeBtn.addEventListener('click',()=>{
        if(!currentDeptKey) return;
        if(!confirm('Remove '+(m.name||'')+' from this department?')) return;
        const idx=original.indexOf(m);
        if(idx!==-1){ original.splice(idx,1); saveDeptMembers(); applyDeptFiltersAndRender(); }
      });
      const actionGroup=document.createElement('div'); actionGroup.className='action-buttons'; actionGroup.appendChild(editBtn); actionGroup.appendChild(removeBtn); tdActions.appendChild(actionGroup);
      tr.appendChild(tdIndex); tr.appendChild(tdName); tr.appendChild(tdRole); tr.appendChild(tdActions); deptMemberTbody.appendChild(tr);
    });
  }

  function showEmployeeProfile(employee){
    if(!employee||!employee.name) return;
    profileNameEl.textContent=employee.name; profileRoleEl.textContent=employee.role||'Member';
    profileDepartmentEl.textContent=employee.department||'Unknown'; profileEmployeeIdEl.textContent=employee.employeeId||'EMP-0000';
    profileEmailEl.textContent=employee.email||'not.available@example.com'; profilePhoneEl.textContent=employee.phone||'N/A';
    openFullProfileBtn.onclick=function(){
      const storedProfile={ name:employee.name, designation:employee.role||'Member', employeeId:employee.employeeId||'EMP-0000', department:employee.department||'Unknown', email:employee.email||'', mobile:employee.phone||'' };
      localStorage.setItem('employeeProfile', JSON.stringify(storedProfile));
      window.location.href='/teamlprofile/';
    };
    employeeProfileOverlay.style.display='flex';
  }

  function hideEmployeeProfile(){ employeeProfileOverlay.style.display='none'; }

  function generateEmployeeId(name){ const key=(name||'EMP').toString().trim().toUpperCase().replace(/\s+/g,'').slice(0,3); return 'EMP-'+key+String(Math.floor(1000+Math.random()*9000)); }
  function generateEmployeeEmail(name){ const user=(name||'employee').toString().trim().toLowerCase().replace(/\s+/g,'.'); return `${user}@example.com`; }
  function generateEmployeePhone(index){ const base=7000000000+(index*13); return '+91 '+String(base).slice(0,5)+' '+String(base).slice(5); }

  function applyDeptFiltersAndRender(){
    if(!currentDeptKey) return;
    const all=departmentMembers[currentDeptKey]||[];
    const filter=(deptFilterInput.value||'').trim().toLowerCase();
    let filtered=all.filter(m=>(m.name||'').toLowerCase().includes(filter)||(m.role||'').toLowerCase().includes(filter));
    filtered.sort((a,b)=>{
      const ka=currentSort.key==='role'?(a.role||'').toLowerCase():(a.name||'').toLowerCase();
      const kb=currentSort.key==='role'?(b.role||'').toLowerCase():(b.name||'').toLowerCase();
      if(ka<kb) return currentSort.asc?-1:1; if(ka>kb) return currentSort.asc?1:-1; return 0;
    });
    renderDeptMembersTable(filtered);
  }

  function showDeptDetails(deptDisplayName){
    const key=normalize(deptDisplayName); currentDeptKey=key;
    const leads=teamLeads.filter(t=>normalize(t.dept)===key).map(t=>t.name);
    deptNameEl.textContent=deptDisplayName; deptLeadEl.textContent=leads.length?'Lead: '+leads.join(', '):'No lead assigned';
    deptFilterInput.value=''; currentSort={key:'name',asc:true};
    applyDeptFiltersAndRender(); deptDetailsPanel.style.display='block'; hideDeptModal();
    deptDetailsPanel.scrollIntoView({behavior:'smooth',block:'center'});
  }

  deptAddBtn.addEventListener('click',()=>{
    if(!currentDeptKey) return;
    const name=(deptAddName.value||'').trim(); const role=(deptAddRole.value||'').trim()||'Member';
    if(!name) return alert('Please enter a member name');
    departmentMembers[currentDeptKey]=departmentMembers[currentDeptKey]||[];
    departmentMembers[currentDeptKey].push({name,role}); saveDeptMembers(); deptAddName.value=''; deptAddRole.value=''; applyDeptFiltersAndRender();
  });

  deptFilterInput.addEventListener('input',()=>applyDeptFiltersAndRender());
  sortByNameBtn.addEventListener('click',()=>{ if(currentSort.key==='name') currentSort.asc=!currentSort.asc; else { currentSort.key='name'; currentSort.asc=true; } applyDeptFiltersAndRender(); });
  sortByRoleBtn.addEventListener('click',()=>{ if(currentSort.key==='role') currentSort.asc=!currentSort.asc; else { currentSort.key='role'; currentSort.asc=true; } applyDeptFiltersAndRender(); });

  function hideDeptDetails(){ deptDetailsPanel.style.display='none'; }

  totalMembers.style.cursor='pointer'; totalMembers.title='Click to view departments';
  totalMembers.addEventListener('click', showDeptModal);
  deptModalClose.addEventListener('click', hideDeptModal);
  deptOverlay.addEventListener('click',(e)=>{ if(e.target===deptOverlay) hideDeptModal(); });
  closeProfileModal.addEventListener('click', hideEmployeeProfile);
  employeeProfileOverlay.addEventListener('click',(e)=>{ if(e.target===employeeProfileOverlay) hideEmployeeProfile(); });
  closeDeptDetailsBtn.addEventListener('click', hideDeptDetails);

  // Normalize and save default dept members
  const normalizedMembers = {};
  Object.keys(departmentMembers).forEach(k=>{ normalizedMembers[normalize(k)]=departmentMembers[k]; });
  Object.keys(defaultDeptMembers).forEach(k=>{ const nk=normalize(k); if(!normalizedMembers[nk]) normalizedMembers[nk]=defaultDeptMembers[k]; });
  departmentMembers = normalizedMembers;
  saveDeptMembers();
})();
