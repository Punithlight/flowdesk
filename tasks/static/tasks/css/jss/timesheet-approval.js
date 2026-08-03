const reports = [
  {
    employee: 'Aisha Patel',
    date: '2026-07-28',
    hours: '8.0',
    project: 'Website Redesign',
    tasks: 'Finalized homepage layout and updated hero visuals.',
    notes: 'Ready for review. Client requested the revised colors.',
    status: 'Pending',
    options: ['View full report', 'Download report', 'Share feedback'],
  },
  {
    employee: 'Jordan Kim',
    date: '2026-07-27',
    hours: '7.5',
    project: 'Support Portal',
    tasks: 'Closed three support tickets and updated knowledge base.',
    notes: 'One ticket escalated, follow up with QA tomorrow.',
    status: 'Pending',
    options: ['View full report', 'Request clarification', 'Add note'],
  },
  {
    employee: 'Mia Garcia',
    date: '2026-07-26',
    hours: '9.0',
    project: 'Mobile App',
    tasks: 'Completed login flow and tested biometric access.',
    notes: 'Works well on Android and iOS simulators.',
    status: 'Pending',
    options: ['View full report', 'Review test results', 'Send follow-up'],
  },
  {
    employee: 'Noah Brown',
    date: '2026-07-25',
    hours: '6.5',
    project: 'Analytics Dashboard',
    tasks: 'Added report filters and adjusted chart legends.',
    notes: 'Need data validation before approval.',
    status: 'Pending',
    options: ['View full report', 'Export summary', 'Flag issue'],
  },
];

const tableBody = document.querySelector('#reportTable tbody');
const reportCount = document.querySelector('#reportCount');
const reportTitle = document.querySelector('#reportTitle');
const reportMeta = document.querySelector('#reportMeta');
const reportOptions = document.querySelector('#reportOptions');
const dateFilterInput = document.querySelector('#sortDatePicker');
const resetBtn = document.querySelector('#resetBtn');
const toast = document.querySelector('#toast');

let selectedIndex = 0;
let allReports = [...reports];
let currentReports = [...allReports];

function formatDate(value) {
  const date = new Date(value);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function renderReportRows() {
  tableBody.innerHTML = '';
  currentReports.forEach((report, index) => {
    const row = document.createElement('tr');
    row.dataset.index = index;
    row.innerHTML = `
      <td><button type="button" class="employee-link">${report.employee}</button></td>
    `;

    row.querySelector('.employee-link').addEventListener('click', (event) => {
      event.stopPropagation();
      selectReport(index);
    });

    row.addEventListener('click', () => selectReport(index));
    row.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        selectReport(index);
      }
    });
    row.tabIndex = 0;
    if (index === selectedIndex) {
      row.classList.add('selected');
    }
    tableBody.appendChild(row);
  });

  reportCount.textContent = `${currentReports.length} total`;
}

function selectReport(index) {
  selectedIndex = index;
  const report = currentReports[index];

  const rows = Array.from(tableBody.querySelectorAll('tr'));
  rows.forEach((row) => row.classList.toggle('selected', Number(row.dataset.index) === index));

  reportTitle.textContent = `${report.employee}'s Daily Report`;
  reportMeta.innerHTML = `
    <span>Date: ${formatDate(report.date)}</span>
  `;
  document.querySelector('#reportTasks').textContent = report.tasks;
  renderReportOptions(report);
}

function renderReportOptions(report) {
  reportOptions.innerHTML = '';

  if (!report.options || report.options.length === 0) {
    reportOptions.innerHTML = '<span class="option-help">No manager options available for this report.</span>';
    return;
  }

  report.options.forEach((option) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'option-btn';
    button.textContent = option;
    button.addEventListener('click', () => {
      showToast(`Manager view: ${option}`);
    });
    reportOptions.appendChild(button);
  });
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(window.toastTimer);
  window.toastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, 2800);
}

function clearReportDetails() {
  reportTitle.textContent = 'No report selected';
  reportMeta.innerHTML = '<span>Date: -</span>';
  document.querySelector('#reportTasks').textContent = 'No employee reports available for the selected date.';
  reportOptions.innerHTML = '<span class="option-help">Select a report to see manager options.</span>';
}

function filterReportsByDate() {
  const selectedDate = dateFilterInput.value;

  if (!selectedDate) {
    currentReports = [...allReports];
  } else {
    currentReports = allReports.filter((report) => report.date === selectedDate);
  }

  selectedIndex = 0;
  renderReportRows();

  if (currentReports.length > 0) {
    selectReport(selectedIndex);
  } else {
    clearReportDetails();
  }
}

function resetOrder() {
  dateFilterInput.value = '';
  currentReports = [...allReports];
  selectedIndex = 0;
  renderReportRows();

  if (currentReports.length > 0) {
    selectReport(selectedIndex);
  } else {
    clearReportDetails();
  }
}

dateFilterInput.addEventListener('change', filterReportsByDate);
resetBtn.addEventListener('click', resetOrder);

renderReportRows();
selectReport(0);
