export function showModal(msg, onConfirm) {
  const modal = document.createElement('div');
  modal.className = 'ms-modal-mask';
  modal.innerHTML = `<div class="ms-modal"><div class="ms-modal-content">${msg}</div><div class="ms-modal-footer"><button class="ms-btn ms-primary" id="modalConfirmBtn">确定</button></div></div>`;
  document.body.appendChild(modal);
  document.getElementById('modalConfirmBtn').onclick = () => {
    document.body.removeChild(modal);
    if (onConfirm) onConfirm();
  };
}
