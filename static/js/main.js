
function prefillBooking(type, notes){
  const sel = document.getElementById('event_type');
  if(sel){
    for (let i=0;i<sel.options.length;i++){
      if(sel.options[i].value.toLowerCase() === type.toLowerCase()){
        sel.selectedIndex = i;
        break;
      }
    }
  }
  const notesEl = document.getElementById('notes');
  if(notesEl){ notesEl.value = notes; }
  window.location.hash = 'book';
}

function validateBooking(){
  // basic client validation
  return true;
}

async function sendEnquiry(e){
  e.preventDefault();
  const form = document.getElementById('enquiry-form');
  const fd = new FormData(form);
  const res = await fetch('/api/enquiry', { method: 'POST', body: fd });
  const data = await res.json();
  if(data.ok){
    alert('Thanks! We will contact you shortly.');
    form.reset();
  }else{
    alert('Error: ' + (data.error || 'Something went wrong'));
  }
}
window.addEventListener('scroll', function() {
    document.querySelectorAll('.fade-in').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 100) {
            el.classList.add('visible');
        }
    });
});
