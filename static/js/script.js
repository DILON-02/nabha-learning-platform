/* ============================================================
   DIGITAL LEARNING PLATFORM — NABHA
   Custom JavaScript
   ============================================================ */

'use strict';

/* ============================================================
   1. DOM READY
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {
  initNavbarScroll();
  initFlashMessages();
  initQuizSystem();
  initScrollAnimations();
  initAdminSidebar();
  initSearchFilter();
  initCounterAnimation();
  initTooltips();
  initConfirmDialogs();
  initPasswordToggle();
  initFormValidation();
  initSmoothScroll();
  initActiveNavLink();
});


/* ============================================================
   2. NAVBAR — Scroll Effect
   Changes navbar background on scroll
   ============================================================ */
function initNavbarScroll() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;

  function handleScroll() {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
      navbar.style.padding = '0.6rem 0';
      navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.4)';
    } else {
      navbar.classList.remove('scrolled');
      navbar.style.padding = '1rem 0';
      navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.3)';
    }
  }

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll(); // Run on load
}


/* ============================================================
   3. FLASH MESSAGES — Auto Dismiss
   Dismisses flash alerts after 5 seconds
   ============================================================ */
function initFlashMessages() {
  const flashAlerts = document.querySelectorAll('.flash-alert');
  if (!flashAlerts.length) return;

  flashAlerts.forEach(function (alert, index) {
    // Stagger appearance
    setTimeout(function () {
      alert.style.opacity = '1';
      alert.style.transform = 'translateX(0)';
    }, index * 150);

    // Auto dismiss after 5 seconds
    setTimeout(function () {
      dismissAlert(alert);
    }, 5000 + (index * 500));

    // Manual close button
    const closeBtn = alert.querySelector('.btn-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        dismissAlert(alert);
      });
    }
  });

  function dismissAlert(alert) {
    alert.style.transition = 'all 0.4s ease';
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(100%)';
    setTimeout(function () {
      if (alert.parentNode) {
        alert.parentNode.removeChild(alert);
      }
    }, 400);
  }
}


/* ============================================================
   4. QUIZ SYSTEM
   Handles option selection, validation, timer
   ============================================================ */
function initQuizSystem() {
  const quizForm = document.getElementById('quizForm');
  if (!quizForm) return;

  // --- Option Selection ---
  const quizOptions = document.querySelectorAll('.quiz-option');
  quizOptions.forEach(function (option) {
    option.addEventListener('click', function () {
      const questionCard = this.closest('.question-card');
      const radio        = this.querySelector('input[type="radio"]');

      // Deselect all options in this question
      questionCard.querySelectorAll('.quiz-option').forEach(function (opt) {
        opt.classList.remove('selected');
        opt.style.transform = '';
      });

      // Select clicked option
      this.classList.add('selected');
      this.style.transform = 'scale(1.02)';
      if (radio) radio.checked = true;

      // Update progress
      updateQuizProgress();

      // Brief bounce animation
      setTimeout(function () {
        option.style.transform = '';
      }, 200);
    });
  });

  // --- Progress Tracker ---
  function updateQuizProgress() {
    const totalQuestions    = document.querySelectorAll('.question-card').length;
    const answeredQuestions = document.querySelectorAll('.quiz-option.selected').length;
    const progressBar       = document.getElementById('quizProgressBar');
    const progressText      = document.getElementById('quizProgressText');

    if (progressBar) {
      const percent = totalQuestions > 0
        ? Math.round((answeredQuestions / totalQuestions) * 100)
        : 0;
      progressBar.style.width = percent + '%';
      progressBar.setAttribute('aria-valuenow', percent);
    }

    if (progressText) {
      progressText.textContent = answeredQuestions + ' of ' + totalQuestions + ' answered';
    }
  }

  // --- Quiz Timer ---
  const timerDisplay = document.getElementById('quizTimer');
  if (timerDisplay) {
    const totalQuestions  = document.querySelectorAll('.question-card').length;
    let   timeLimit       = totalQuestions * 60; // 1 minute per question
    let   timeRemaining   = timeLimit;

    const timerInterval = setInterval(function () {
      timeRemaining--;
      const minutes = Math.floor(timeRemaining / 60);
      const seconds = timeRemaining % 60;
      timerDisplay.textContent =
        String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');

      // Warning colors
      if (timeRemaining <= 60) {
        timerDisplay.style.color = '#ef4444';
        timerDisplay.style.fontWeight = '800';
      } else if (timeRemaining <= 120) {
        timerDisplay.style.color = '#f59e0b';
      }

      // Time's up — auto submit
      if (timeRemaining <= 0) {
        clearInterval(timerInterval);
        timerDisplay.textContent = '00:00';
        showTimeUpModal();
      }
    }, 1000);

    // Clear timer on form submit
    quizForm.addEventListener('submit', function () {
      clearInterval(timerInterval);
    });
  }

  // --- Time Up Modal ---
  function showTimeUpModal() {
    const existingModal = document.getElementById('timeUpModal');
    if (existingModal) {
      const modal = new bootstrap.Modal(existingModal);
      modal.show();
    } else {
      // Auto-submit if no modal
      quizForm.submit();
    }
  }

  // --- Submit Validation ---
  quizForm.addEventListener('submit', function (e) {
    const totalQuestions    = document.querySelectorAll('.question-card').length;
    const answeredQuestions = document.querySelectorAll('.question-card').length > 0
      ? countAnsweredQuestions()
      : 0;
    const unanswered = totalQuestions - answeredQuestions;

    if (unanswered > 0) {
      e.preventDefault();
      showUnansweredWarning(unanswered);
      return false;
    }

    // Show loading state on submit button
    const submitBtn = quizForm.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';
    }
  });

  function countAnsweredQuestions() {
    let count = 0;
    document.querySelectorAll('.question-card').forEach(function (card) {
      const selected = card.querySelector('input[type="radio"]:checked');
      if (selected) count++;
    });
    return count;
  }

  function showUnansweredWarning(unanswered) {
    // Remove existing warning if any
    const existing = document.getElementById('unansweredWarning');
    if (existing) existing.remove();

    const warning = document.createElement('div');
    warning.id = 'unansweredWarning';
    warning.className = 'alert alert-warning d-flex align-items-center gap-2 mt-3 animate-fade-up';
    warning.innerHTML =
      '<i class="fas fa-exclamation-triangle"></i>' +
      '<span>You have <strong>' + unanswered + ' unanswered question(s)</strong>. ' +
      'Please answer all questions before submitting.</span>';

    const submitArea = document.getElementById('quizSubmitArea');
    if (submitArea) {
      submitArea.parentNode.insertBefore(warning, submitArea);
    } else {
      quizForm.appendChild(warning);
    }

    // Scroll to first unanswered
    scrollToFirstUnanswered();

    // Auto remove after 4 seconds
    setTimeout(function () {
      if (warning.parentNode) warning.remove();
    }, 4000);
  }

  function scrollToFirstUnanswered() {
    const cards = document.querySelectorAll('.question-card');
    for (let i = 0; i < cards.length; i++) {
      const answered = cards[i].querySelector('input[type="radio"]:checked');
      if (!answered) {
        cards[i].scrollIntoView({ behavior: 'smooth', block: 'center' });
        cards[i].style.borderColor = '#f59e0b';
        cards[i].style.boxShadow   = '0 0 0 3px rgba(245,158,11,0.2)';
        setTimeout(function () {
          cards[i].style.borderColor = '';
          cards[i].style.boxShadow   = '';
        }, 2000);
        break;
      }
    }
  }
}


/* ============================================================
   5. SCROLL ANIMATIONS
   Animates elements when they enter the viewport
   ============================================================ */
function initScrollAnimations() {
  const animateElements = document.querySelectorAll(
    '.feature-card, .course-card, .stat-card, .video-card, .note-card, ' +
    '.testimonial-card, .animate-on-scroll'
  );

  if (!animateElements.length) return;

  // Set initial state
  animateElements.forEach(function (el) {
    el.style.opacity  = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  });

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry, i) {
        if (entry.isIntersecting) {
          setTimeout(function () {
            entry.target.style.opacity   = '1';
            entry.target.style.transform = 'translateY(0)';
          }, i * 80);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
  );

  animateElements.forEach(function (el) {
    observer.observe(el);
  });
}


/* ============================================================
   6. ADMIN SIDEBAR TOGGLE (Mobile)
   ============================================================ */
function initAdminSidebar() {
  const sidebar    = document.getElementById('adminSidebar');
  const toggleBtn  = document.getElementById('sidebarToggle');
  const overlay    = document.getElementById('sidebarOverlay');

  if (!sidebar || !toggleBtn) return;

  toggleBtn.addEventListener('click', function () {
    sidebar.classList.toggle('show');
    if (overlay) overlay.classList.toggle('show');
    document.body.style.overflow =
      sidebar.classList.contains('show') ? 'hidden' : '';
  });

  if (overlay) {
    overlay.addEventListener('click', function () {
      sidebar.classList.remove('show');
      overlay.classList.remove('show');
      document.body.style.overflow = '';
    });
  }

  // Mark active nav link in admin panel
  const currentPath = window.location.pathname;
  const adminLinks  = document.querySelectorAll('.admin-nav-link');
  adminLinks.forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });
}


/* ============================================================
   7. SEARCH & FILTER
   Live search filter for cards/rows
   ============================================================ */
function initSearchFilter() {
  const liveSearch = document.getElementById('liveSearch');
  if (!liveSearch) return;

  liveSearch.addEventListener('input', function () {
    const query    = this.value.toLowerCase().trim();
    const target   = this.getAttribute('data-target') || '.searchable-item';
    const items    = document.querySelectorAll(target);
    let   visible  = 0;

    items.forEach(function (item) {
      const text = item.textContent.toLowerCase();
      if (text.includes(query)) {
        item.style.display = '';
        item.style.animation = 'fadeInUp 0.3s ease';
        visible++;
      } else {
        item.style.display = 'none';
      }
    });

    // Show/hide no results message
    const noResults = document.getElementById('noResults');
    if (noResults) {
      noResults.style.display = visible === 0 ? 'block' : 'none';
    }
  });
}


/* ============================================================
   8. COUNTER ANIMATION
   Animates stat numbers counting up
   ============================================================ */
function initCounterAnimation() {
  const counters = document.querySelectorAll('.counter-animate');
  if (!counters.length) return;

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.5 }
  );

  counters.forEach(function (counter) {
    observer.observe(counter);
  });

  function animateCounter(el) {
    const target   = parseInt(el.getAttribute('data-target') || el.textContent, 10);
    const duration = 2000;
    const step     = target / (duration / 16);
    let   current  = 0;

    const timer = setInterval(function () {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = Math.floor(current).toLocaleString();
    }, 16);
  }
}


/* ============================================================
   9. BOOTSTRAP TOOLTIPS
   ============================================================ */
function initTooltips() {
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(function (el) {
    new bootstrap.Tooltip(el, { trigger: 'hover' });
  });
}


/* ============================================================
   10. CONFIRM DIALOGS
   Replaces browser confirm() with a better UX pattern
   ============================================================ */
function initConfirmDialogs() {
  const deleteLinks = document.querySelectorAll('[data-confirm]');
  deleteLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const message  = this.getAttribute('data-confirm') || 'Are you sure?';
      const href     = this.getAttribute('href');
      showConfirmModal(message, href);
    });
  });
}

function showConfirmModal(message, actionUrl) {
  // Remove existing confirm modal
  const existingModal = document.getElementById('confirmModal');
  if (existingModal) existingModal.remove();

  const modalHtml = `
    <div class="modal fade" id="confirmModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header border-0 pb-0">
            <div class="d-flex align-items-center gap-2">
              <div style="width:40px;height:40px;background:#fee2e2;border-radius:10px;
                          display:flex;align-items:center;justify-content:center;color:#ef4444;font-size:1.2rem;">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <h5 class="modal-title mb-0 fw-bold">Confirm Action</h5>
            </div>
          </div>
          <div class="modal-body">
            <p class="text-muted mb-0">${message}</p>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <a href="${actionUrl}" class="btn btn-danger" id="confirmActionBtn">
              <i class="fas fa-trash me-1"></i> Yes, Delete
            </a>
          </div>
        </div>
      </div>
    </div>`;

  document.body.insertAdjacentHTML('beforeend', modalHtml);
  const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
  modal.show();
}


/* ============================================================
   11. PASSWORD TOGGLE
   Show/hide password in input fields
   ============================================================ */
function initPasswordToggle() {
  const toggleBtns = document.querySelectorAll('.password-toggle');
  toggleBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input    = document.getElementById(targetId);
      const icon     = this.querySelector('i');

      if (!input) return;

      if (input.type === 'password') {
        input.type    = 'text';
        if (icon) {
          icon.classList.remove('fa-eye');
          icon.classList.add('fa-eye-slash');
        }
        this.setAttribute('title', 'Hide password');
      } else {
        input.type = 'password';
        if (icon) {
          icon.classList.remove('fa-eye-slash');
          icon.classList.add('fa-eye');
        }
        this.setAttribute('title', 'Show password');
      }
    });
  });
}


/* ============================================================
   12. FORM VALIDATION
   Client-side validation for register and profile forms
   ============================================================ */
function initFormValidation() {
  // Register form
  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    registerForm.addEventListener('submit', function (e) {
      const password = document.getElementById('password');
      const confirm  = document.getElementById('confirm_password');
      const phone    = document.getElementById('phone');

      clearValidation(registerForm);
      let valid = true;

      // Password length
      if (password && password.value.length < 6) {
        showFieldError(password, 'Password must be at least 6 characters.');
        valid = false;
      }

      // Password match
      if (password && confirm && password.value !== confirm.value) {
        showFieldError(confirm, 'Passwords do not match.');
        valid = false;
      }

      // Phone format
      if (phone && !/^\d{10}$/.test(phone.value.trim())) {
        showFieldError(phone, 'Phone number must be exactly 10 digits.');
        valid = false;
      }

      if (!valid) {
        e.preventDefault();
        // Scroll to first error
        const firstError = registerForm.querySelector('.is-invalid');
        if (firstError) {
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    });
  }

  // Profile update form
  const profileForm = document.getElementById('profileForm');
  if (profileForm) {
    profileForm.addEventListener('submit', function (e) {
      const phone = document.getElementById('phone');
      clearValidation(profileForm);

      if (phone && !/^\d{10}$/.test(phone.value.trim())) {
        e.preventDefault();
        showFieldError(phone, 'Phone number must be exactly 10 digits.');
      }
    });
  }

  function showFieldError(input, message) {
    input.classList.add('is-invalid');
    let feedback = input.nextElementSibling;
    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
      feedback = document.createElement('div');
      feedback.className = 'invalid-feedback';
      input.parentNode.insertBefore(feedback, input.nextSibling);
    }
    feedback.textContent = message;
  }

  function clearValidation(form) {
    form.querySelectorAll('.is-invalid').forEach(function (el) {
      el.classList.remove('is-invalid');
    });
  }
}


/* ============================================================
   13. SMOOTH SCROLL
   Smooth scroll for anchor links
   ============================================================ */
function initSmoothScroll() {
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;

      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        const navbarHeight = document.querySelector('.navbar')
          ? document.querySelector('.navbar').offsetHeight
          : 0;
        const offsetTop = target.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;
        window.scrollTo({ top: offsetTop, behavior: 'smooth' });
      }
    });
  });
}


/* ============================================================
   14. ACTIVE NAV LINK
   Highlights the current page nav link
   ============================================================ */
function initActiveNavLink() {
  const currentPath = window.location.pathname;
  const navLinks    = document.querySelectorAll('.navbar-nav .nav-link');

  navLinks.forEach(function (link) {
    const href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    } else if (href === '/' && currentPath === '/') {
      link.classList.add('active');
    }
  });
}


/* ============================================================
   15. IMAGE PREVIEW
   Preview image before uploading in admin forms
   ============================================================ */
function previewImage(input, previewId) {
  const preview = document.getElementById(previewId);
  if (!preview) return;

  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src             = e.target.result;
      preview.style.display   = 'block';
      preview.style.maxHeight = '200px';
      preview.style.borderRadius = '12px';
      preview.style.marginTop    = '0.75rem';
      preview.style.boxShadow    = '0 4px 16px rgba(0,0,0,0.1)';
    };
    reader.readAsDataURL(input.files[0]);
  }
}

// Attach image preview to file inputs
document.addEventListener('DOMContentLoaded', function () {
  const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
  imageInputs.forEach(function (input) {
    input.addEventListener('change', function () {
      const previewId = this.getAttribute('data-preview');
      if (previewId) previewImage(this, previewId);
    });
  });
});


/* ============================================================
   16. PDF FILE NAME DISPLAY
   Shows filename when PDF is selected for upload
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {
  const pdfInputs = document.querySelectorAll('input[type="file"][accept=".pdf"]');
  pdfInputs.forEach(function (input) {
    input.addEventListener('change', function () {
      const label = this.nextElementSibling;
      if (label && this.files[0]) {
        const fileName = this.files[0].name;
        const fileSize = (this.files[0].size / 1024 / 1024).toFixed(2);

        if (fileSize > 16) {
          showFileError(this, 'File size exceeds 16MB limit.');
          this.value = '';
        } else {
          if (label.tagName === 'LABEL') {
            label.textContent = fileName + ' (' + fileSize + ' MB)';
          }
          showFileSuccess(this, fileName + ' selected (' + fileSize + ' MB)');
        }
      }
    });
  });

  function showFileError(input, message) {
    removeFileMessage(input);
    const msg = document.createElement('small');
    msg.className   = 'text-danger d-block mt-1 file-message';
    msg.textContent = '✗ ' + message;
    input.parentNode.insertBefore(msg, input.nextSibling);
  }

  function showFileSuccess(input, message) {
    removeFileMessage(input);
    const msg = document.createElement('small');
    msg.className   = 'text-success d-block mt-1 file-message';
    msg.textContent = '✓ ' + message;
    input.parentNode.insertBefore(msg, input.nextSibling);
  }

  function removeFileMessage(input) {
    const existing = input.parentNode.querySelector('.file-message');
    if (existing) existing.remove();
  }
});


/* ============================================================
   17. BACK TO TOP BUTTON
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {
  // Create button
  const btn = document.createElement('button');
  btn.id        = 'backToTop';
  btn.innerHTML = '<i class="fas fa-arrow-up"></i>';
  btn.setAttribute('title', 'Back to top');
  btn.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 46px;
    height: 46px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    border-radius: 50%;
    font-size: 1rem;
    cursor: pointer;
    display: none;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px rgba(37,99,235,0.4);
    transition: all 0.3s ease;
    z-index: 9000;
  `;
  document.body.appendChild(btn);

  // Show/hide on scroll
  window.addEventListener('scroll', function () {
    if (window.scrollY > 400) {
      btn.style.display = 'flex';
    } else {
      btn.style.display = 'none';
    }
  }, { passive: true });

  // Scroll to top on click
  btn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  btn.addEventListener('mouseenter', function () {
    this.style.transform = 'translateY(-4px)';
    this.style.boxShadow = '0 8px 24px rgba(37,99,235,0.5)';
  });

  btn.addEventListener('mouseleave', function () {
    this.style.transform = '';
    this.style.boxShadow = '0 4px 16px rgba(37,99,235,0.4)';
  });
});


/* ============================================================
   18. COURSE FILTER (Videos & Notes pages)
   Updates URL with selected course filter
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {
  const courseFilter = document.getElementById('courseFilter');
  if (!courseFilter) return;

  courseFilter.addEventListener('change', function () {
    const url    = new URL(window.location.href);
    const value  = this.value;

    if (value) {
      url.searchParams.set('course_id', value);
    } else {
      url.searchParams.delete('course_id');
    }

    // Keep search query if present
    const searchInput = document.getElementById('searchInput');
    if (searchInput && searchInput.value.trim()) {
      url.searchParams.set('search', searchInput.value.trim());
    }

    window.location.href = url.toString();
  });
});


/* ============================================================
   19. TABLE ROW HIGHLIGHT
   Highlights table row on hover in admin panels
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {
  const tableRows = document.querySelectorAll('.table-custom tbody tr');
  tableRows.forEach(function (row) {
    row.style.transition = 'background 0.2s ease';
    row.addEventListener('mouseenter', function () {
      this.style.background = '#eff6ff';
    });
    row.addEventListener('mouseleave', function () {
      this.style.background = '';
    });
  });
});


/* ============================================================
   20. QUIZ RESULT — Scroll to Summary
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {
  const resultHero = document.querySelector('.result-hero');
  if (resultHero) {
    // Animate score circle
    const scoreCircle = document.querySelector('.result-score-circle');
    if (scoreCircle) {
      scoreCircle.style.animation = 'pulse 2s ease-in-out 3';
    }

    // Add keyframe for pulse if needed
    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50%       { transform: scale(1.05); }
      }
    `;
    document.head.appendChild(style);
  }
});


/* ============================================================
   21. GLOBAL UTILITY FUNCTIONS
   ============================================================ */

/**
 * Show a toast notification
 * @param {string} message
 * @param {string} type - 'success' | 'danger' | 'warning' | 'info'
 */
function showToast(message, type) {
  type = type || 'info';
  const iconMap = {
    success: 'fa-check-circle',
    danger:  'fa-times-circle',
    warning: 'fa-exclamation-triangle',
    info:    'fa-info-circle'
  };

  const toast = document.createElement('div');
  toast.className = 'flash-alert alert alert-' + type;
  toast.innerHTML =
    '<i class="fas ' + (iconMap[type] || 'fa-info-circle') + '"></i>' +
    '<span>' + message + '</span>' +
    '<button type="button" class="btn-close ms-auto" aria-label="Close"></button>';

  let container = document.querySelector('.flash-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'flash-container';
    document.body.appendChild(container);
  }

  container.appendChild(toast);

  // Close button
  toast.querySelector('.btn-close').addEventListener('click', function () {
    toast.remove();
  });

  // Auto dismiss
  setTimeout(function () {
    toast.style.opacity   = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(function () { toast.remove(); }, 400);
  }, 4000);
}


/**
 * Format a number with commas
 * @param {number} num
 * @returns {string}
 */
function formatNumber(num) {
  return num.toLocaleString();
}


/**
 * Capitalize the first letter of a string
 * @param {string} str
 * @returns {string}
 */
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
