const requests = [
  {
    name: 'Sophia Liu',
    title: "Sophia Liu's Leave Request",
    summary: 'Requested leave for personal reasons from May 10 to May 14.',
    duration: '5 days',
    type: 'Paid leave',
    department: 'HR',
    submitted: 'May 2',
    notes: 'Please review her leave dates and check availability of coverage.',
    status: 'Pending',
  },
  {
    name: 'Marcus Allen',
    title: "Marcus Allen's Leave Request",
    summary: 'Requested leave for medical appointment on May 18.',
    duration: '1 day',
    type: 'Medical leave',
    department: 'Operations',
    submitted: 'May 4',
    notes: 'Needs approval quickly to arrange his appointment.',
    status: 'Pending',
  },
  {
    name: 'Priya Singh',
    title: "Priya Singh's Leave Request",
    summary: 'Requested leave for family event from May 20 to May 23.',
    duration: '4 days',
    type: 'Personal leave',
    department: 'Sales',
    submitted: 'May 5',
    notes: 'Ensure sales coverage is in place before approving.',
    status: 'Pending',
  },
];

const requestCards = Array.from(document.querySelectorAll('.request-card'));
const requestTitle = document.querySelector('.detail-card h2');
const requestMeta = document.querySelector('.request-meta');
const requestDescription = document.querySelector('#request-description');
const approveButton = document.querySelector('.action-btn.approve');
const rejectButton = document.querySelector('.action-btn.reject');
const toast = document.querySelector('#toast');

let selectedIndex = 0;

function renderSelectedRequest(index) {
  selectedIndex = index;
  const request = requests[index];

  requestCards.forEach((card) => {
    card.classList.toggle('selected', Number(card.dataset.index) === index);
  });

  requestTitle.textContent = request.title;
  requestMeta.innerHTML = `
    <span>Duration: ${request.duration}</span>
    <span>Type: ${request.type}</span>
    <span>Department: ${request.department}</span>
    <span>Submitted: ${request.submitted}</span>
  `;
  requestDescription.value = request.notes;
  updateRequestStatusChip(index, request.status);
}

function updateRequestStatusChip(index, status) {
  const card = requestCards[index];
  const statusChip = card.querySelector('.chip');
  statusChip.textContent = `Status: ${status}`;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(window.toastTimer);
  window.toastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, 2800);
}

function approveRequest() {
  requests[selectedIndex].status = 'Approved';
  updateRequestStatusChip(selectedIndex, 'Approved');
  showToast('Request has been approved.');
}

function rejectRequest() {
  requests[selectedIndex].status = 'Rejected';
  updateRequestStatusChip(selectedIndex, 'Rejected');
  showToast('Request has been rejected.');
}

function handleSelection(event) {
  const card = event.currentTarget;
  const index = Number(card.dataset.index);
  renderSelectedRequest(index);
}

requestCards.forEach((card) => {
  card.addEventListener('click', handleSelection);
  card.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleSelection(event);
    }
  });
});

requestDescription.addEventListener('input', () => {
  requests[selectedIndex].notes = requestDescription.value;
});
approveButton.addEventListener('click', approveRequest);
rejectButton.addEventListener('click', rejectRequest);

renderSelectedRequest(0);
