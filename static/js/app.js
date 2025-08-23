// Clear old service worker caches
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(function(registrations) {
    for(let registration of registrations) {
      registration.unregister();
    }
  });
  
  // Clear old caches
  if ('caches' in window) {
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName.includes('solo-todo')) {
            return caches.delete(cacheName);
          }
        })
      );
    });
  }
}

// Prevent form submission on Enter for quick-add
document.addEventListener('DOMContentLoaded', function() {
  const quickAddForm = document.querySelector('form[action*="quick-add"]');
  if (quickAddForm) {
    const input = quickAddForm.querySelector('input[name="text"]');
    if (input) {
      input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          quickAddForm.submit();
        }
      });
    }
  }

  // Initialize tooltips and other UI enhancements
  initializeUI();
});

function initializeUI() {
  // Add loading states to buttons (excluding login form) without blocking submit
  const buttons = document.querySelectorAll('button[type="submit"]');
  buttons.forEach(button => {
    const form = button.closest('form');
    if (form && (form.action.includes('login') || form.id === 'loginForm')) {
      return;
    }

    if (form) {
      form.addEventListener('submit', function() {
        if (!button.disabled) {
          // Defer disabling until submit is already in progress
          setTimeout(() => {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
          }, 0);
        }
      });
    }
  });

  // Add keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N for new task
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
      e.preventDefault();
      window.location.href = '/tasks/new/';
    }
    
    // Ctrl/Cmd + K for quick add
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      openQuickAdd();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
      const modals = document.querySelectorAll('.modal, [id$="Modal"]');
      modals.forEach(modal => {
        if (!modal.classList.contains('hidden')) {
          modal.classList.add('hidden');
        }
      });
    }
  });

  // Add hover effects for task cards
  const taskCards = document.querySelectorAll('.task-card');
  taskCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-2px)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });

  // Add priority color indicators
  const priorityElements = document.querySelectorAll('[data-priority]');
  priorityElements.forEach(element => {
    const priority = element.dataset.priority;
    element.style.borderLeftColor = getPriorityColor(priority);
  });
}

function getPriorityColor(priority) {
  const colors = {
    '1': '#dc2626', // Red
    '2': '#ea580c', // Orange
    '3': '#ca8a04', // Yellow
    '4': '#0284c7', // Blue
    '5': '#64748b'  // Gray
  };
  return colors[priority] || colors['3'];
}

// Enhanced quick add functionality
function openQuickAdd() {
  const modal = document.getElementById('quickAddModal');
  const input = document.getElementById('quickAddInput');
  
  if (modal && input) {
    modal.classList.remove('hidden');
    input.focus();
    
    // Add animation
    modal.style.opacity = '0';
    modal.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
      modal.style.opacity = '1';
      modal.style.transform = 'scale(1)';
    }, 10);
  }
}

function closeQuickAdd() {
  const modal = document.getElementById('quickAddModal');
  
  if (modal) {
    modal.style.opacity = '0';
    modal.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
      modal.classList.add('hidden');
    }, 150);
  }
}

// Task completion with animation
function completeTask(taskId) {
  const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
  if (taskElement) {
    taskElement.style.transition = 'all 0.3s ease';
    taskElement.style.opacity = '0.5';
    taskElement.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
      taskElement.remove();
    }, 300);
  }
}

// Snooze task with confirmation
function snoozeTask(taskId) {
  const minutes = prompt('Snooze for how many minutes?', '30');
  if (minutes && !isNaN(minutes)) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/tasks/${taskId}/snooze/`;
    
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    const minutesInput = document.createElement('input');
    minutesInput.type = 'hidden';
    minutesInput.name = 'minutes';
    minutesInput.value = minutes;
    
    form.appendChild(csrfInput);
    form.appendChild(minutesInput);
    document.body.appendChild(form);
    form.submit();
  }
}

// Start focus session
function startFocusSession(taskId) {
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = '/focus/start/';
  
  const csrfInput = document.createElement('input');
  csrfInput.type = 'hidden';
  csrfInput.name = 'csrfmiddlewaretoken';
  csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  const kindInput = document.createElement('input');
  kindInput.type = 'hidden';
  kindInput.name = 'kind';
  kindInput.value = 'work';
  
  const taskInput = document.createElement('input');
  taskInput.type = 'hidden';
  taskInput.name = 'task_id';
  taskInput.value = taskId;
  
  form.appendChild(csrfInput);
  form.appendChild(kindInput);
  form.appendChild(taskInput);
  document.body.appendChild(form);
  form.submit();
}

// Add floating action button for mobile
function addFloatingActionButton() {
  if (window.innerWidth <= 768) {
    const fab = document.createElement('button');
    fab.innerHTML = '<i class="fas fa-plus"></i>';
    fab.className = 'fixed bottom-6 right-6 w-14 h-14 bg-sky-600 hover:bg-sky-700 text-white rounded-full shadow-lg z-50 flex items-center justify-center transition-colors';
    fab.onclick = openQuickAdd;
    
    document.body.appendChild(fab);
  }
}

// Initialize floating action button
document.addEventListener('DOMContentLoaded', addFloatingActionButton);
window.addEventListener('resize', addFloatingActionButton); 