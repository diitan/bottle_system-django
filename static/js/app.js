function showPanel(name){
  const intro = document.getElementById("panel-intro");
  const pricing = document.getElementById("panel-pricing");
  const contact = document.getElementById("panel-contact");

  if(!intro || !pricing || !contact) return;

  intro.className = "panel panel-hide";
  pricing.className = "panel panel-hide";
  contact.className = "panel panel-hide";

  if(name === "pricing") pricing.className = "panel panel-show";
  else if(name === "contact") contact.className = "panel panel-show";
  else intro.className = "panel panel-show";
}

document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-show]");
  if(!btn) return;
  showPanel(btn.getAttribute("data-show"));
});

function openModal(id){
  const el = document.getElementById(id);
  if(!el) return;
  el.classList.add('show', 'is-open');
  el.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeModal(id){
  const el = document.getElementById(id);
  if(!el) return;
  el.classList.remove('show', 'is-open');
  el.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

// Click nút đóng (x) hoặc nút có data-close-modal
document.addEventListener('click', (e) => {
  const closeBtn = e.target.closest('[data-close-modal]');
  if(closeBtn){
    closeModal(closeBtn.getAttribute('data-close-modal'));
    return;
  }

  // click ra ngoài backdrop để đóng
const backdrop = e.target.classList.contains('modal-backdrop') ? e.target : null;
if(backdrop){
  const id = backdrop.dataset.modalId || backdrop.id;
  if(id) closeModal(id);
}


  // mở modal bằng data-open-modal
  const openBtn = e.target.closest('[data-open-modal]');
  if (openBtn) {
    e.preventDefault(); // <- thêm dòng này
    const openId = openBtn.getAttribute("data-open-modal");
    openModal(openId);
  }
});

// ESC để đóng tất cả modal
document.addEventListener('keydown', (e) => {
  if(e.key === 'Escape'){
    document.querySelectorAll('.modal-backdrop.show').forEach(m => m.classList.remove('show'));
    document.body.style.overflow = '';
  }
});
