/**
 * Video QR Generator - Dashboard Interactivity
 */

document.addEventListener('DOMContentLoaded', () => {
  initLiveSearch();
  initPreviewModals();
  initDeleteModals();
  initEditModals();
});

/* ==============================================================================
   Live Search Filter
   ============================================================================== */
function initLiveSearch() {
  const searchInput = document.getElementById('dashboard-search-input');
  const tableRows = document.querySelectorAll('.video-table-row');
  const emptyState = document.getElementById('search-empty-state');

  if (!searchInput || tableRows.length === 0) return;

  searchInput.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase().trim();
    let visibleCount = 0;

    tableRows.forEach(row => {
      const title = row.getAttribute('data-title') || '';
      const id = row.getAttribute('data-id') || '';
      const filename = row.getAttribute('data-filename') || '';

      const matches = title.toLowerCase().includes(term) ||
                      id.toLowerCase().includes(term) ||
                      filename.toLowerCase().includes(term);

      if (matches) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    if (emptyState) {
      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  });
}

/* ==============================================================================
   QR Preview Modal Trigger
   ============================================================================== */
function initPreviewModals() {
  document.querySelectorAll('[data-preview-qr]').forEach(btn => {
    btn.addEventListener('click', () => {
      const qrUrl = btn.getAttribute('data-preview-qr');
      const videoUrl = btn.getAttribute('data-video-url');
      const videoTitle = btn.getAttribute('data-title');
      const uniqueId = btn.getAttribute('data-id');

      const modalQrImg = document.getElementById('modal-qr-image');
      const modalTitle = document.getElementById('modal-qr-title');
      const modalUrlText = document.getElementById('modal-qr-url');
      const modalDownloadBtn = document.getElementById('modal-qr-download');
      const modalOpenBtn = document.getElementById('modal-qr-open');
      const modalCopyBtn = document.getElementById('modal-qr-copy');

      if (modalQrImg) modalQrImg.src = qrUrl;
      if (modalTitle) modalTitle.textContent = videoTitle;
      if (modalUrlText) modalUrlText.textContent = videoUrl;
      if (modalDownloadBtn) modalDownloadBtn.href = `/qr/${uniqueId}/download`;
      if (modalOpenBtn) modalOpenBtn.href = videoUrl;
      if (modalCopyBtn) modalCopyBtn.setAttribute('data-copy', videoUrl);

      openModal('qr-preview-modal');
    });
  });
}

/* ==============================================================================
   Delete Confirmation Modal
   ============================================================================== */
function initDeleteModals() {
  const deleteModal = document.getElementById('delete-confirm-modal');
  const deleteForm = document.getElementById('delete-video-form');
  const deleteTitleSpan = document.getElementById('delete-video-title');

  document.querySelectorAll('[data-delete-id]').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-delete-id');
      const title = btn.getAttribute('data-delete-title');

      if (deleteForm) deleteForm.action = `/admin/delete/${id}`;
      if (deleteTitleSpan) deleteTitleSpan.textContent = `"${title}"`;

      openModal('delete-confirm-modal');
    });
  });
}

/* ==============================================================================
   Edit Video Modal
   ============================================================================== */
function initEditModals() {
  const editModal = document.getElementById('edit-video-modal');
  const editForm = document.getElementById('edit-video-form');
  const editTitleInput = document.getElementById('edit-video-title-input');
  const editDescInput = document.getElementById('edit-video-desc-input');

  document.querySelectorAll('[data-edit-id]').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-edit-id');
      const title = btn.getAttribute('data-edit-title');
      const desc = btn.getAttribute('data-edit-desc') || '';

      if (editForm) editForm.action = `/admin/edit/${id}`;
      if (editTitleInput) editTitleInput.value = title;
      if (editDescInput) editDescInput.value = desc;

      openModal('edit-video-modal');
    });
  });
}
