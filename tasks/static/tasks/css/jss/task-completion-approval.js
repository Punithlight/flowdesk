const reviews = [
  {
    employee: 'Aisha Patel',
    task: 'Website Redesign Homepage',
    status: 'Pending',
    summary: 'Completed homepage layout refinements and polished the hero section for launch readiness.',
    notes: 'Client requested final visual adjustments before submission.',
  },
  {
    employee: 'Jordan Kim',
    task: 'Support Portal FAQ Update',
    status: 'Pending',
    summary: 'Added updated help articles and resolved the top recurring support tickets.',
    notes: 'The QA team confirmed the new flow is working as expected.',
  },
  {
    employee: 'Mia Garcia',
    task: 'Mobile App Login Flow',
    status: 'Pending',
    summary: 'Finished the biometric authentication flow and tested it on both Android and iOS.',
    notes: 'Ready for manager approval and release review.',
  },
];

const reviewList = document.querySelector('#reviewList');
const reviewCount = document.querySelector('#reviewCount');
const reviewTitle = document.querySelector('#reviewTitle');
const reviewMeta = document.querySelector('#reviewMeta');
const reviewSummary = document.querySelector('#reviewSummary');
const reviewNotes = document.querySelector('#reviewNotes');
const noteTypeSelect = document.querySelector('#noteType');
const approveBtn = document.querySelector('#approveBtn');
const toast = document.querySelector('#toast');

let selectedReviewIndex = 0;
let currentReviews = [...reviews];

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(window.toastTimer);
  window.toastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, 2800);
}

function renderReviewList() {
  reviewList.innerHTML = '';

  currentReviews.forEach((review, index) => {
    const card = document.createElement('article');
    card.className = 'request-card';
    if (index === selectedReviewIndex) {
      card.classList.add('selected');
    }

    card.innerHTML = `
      <h4>${review.employee}</h4>
      <p>${review.task}</p>
      <p><strong>Status:</strong> ${review.status}</p>
    `;

    card.addEventListener('click', () => selectReview(index));
    reviewList.appendChild(card);
  });

  reviewCount.textContent = `${currentReviews.length} pending`;
}

function selectReview(index) {
  selectedReviewIndex = index;
  const review = currentReviews[index];

  renderReviewList();
  reviewTitle.textContent = `${review.employee}'s Review`;
  reviewMeta.innerHTML = `
    <span>Employee: ${review.employee}</span>
    <span>Status: ${review.status}</span>
  `;
  reviewSummary.textContent = review.summary;
  reviewNotes.value = `${noteTypeSelect.value}: ${review.notes}`;
}

function approveSelectedReview() {
  const review = currentReviews[selectedReviewIndex];
  if (!review) {
    showToast('No review selected');
    return;
  }

  review.status = 'Approved';
  currentReviews.splice(selectedReviewIndex, 1);

  if (currentReviews.length === 0) {
    reviewTitle.textContent = 'No review selected';
    reviewMeta.innerHTML = '<span>Employee: -</span><span>Status: Pending</span>';
    reviewSummary.textContent = 'All reviews have been approved.';
    reviewNotes.textContent = 'No pending reviews remain.';
    reviewList.innerHTML = '<p class="option-help">No pending reviews.</p>';
    reviewCount.textContent = '0 pending';
    showToast('Review approved successfully');
    return;
  }

  selectedReviewIndex = Math.min(selectedReviewIndex, currentReviews.length - 1);
  renderReviewList();
  selectReview(selectedReviewIndex);
  showToast(`Approved ${review.employee}'s review`);
}

noteTypeSelect.addEventListener('change', () => {
  const review = currentReviews[selectedReviewIndex];
  if (review) {
    reviewNotes.value = `${noteTypeSelect.value}: ${review.notes}`;
  }
});

approveBtn.addEventListener('click', approveSelectedReview);
renderReviewList();
selectReview(0);
