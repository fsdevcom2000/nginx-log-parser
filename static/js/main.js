// log rendering
window.renderLogs = function(logs) {
  const table = document.getElementById('log-table');
  if (!logs?.length) {
    table.innerHTML = `<tr><td colspan="6" class="text-center py-5 text-muted">Нет данных</td></tr>`;
    return;
  }

  const rows = logs.map(log => `
    <tr>
      <td><span class="badge level-${log.level}">${log.level}</span></td>
      <td><small class="text-muted">${formatTime(log.time)}</small></td>
      <td><code>${escape(log.ip || log.method || '-')}</code></td>
      <td><code>${escape(log.status || '-')}</code></td>
      <td><code>${escape(log.request?.split(' ')[1] || '-')}</code></td>
      <td>
        <details class="dropdown">
          <summary class="text-primary" style="cursor:pointer">raw</summary>
          <div class="raw-log mt-2">${escape(log.raw)}</div>
        </details>
      </td>
    </tr>
  `).join('');

  table.innerHTML = `
    <thead class="table-light">
      <tr>
        <th>Level</th><th>Time</th><th>IP/Method</th><th>Status</th><th>Path</th><th>Raw</th>
      </tr>
    </thead>
    <tbody>${rows}</tbody>
  `;
};

function escape(str) {
  if (!str) return '-';
  return String(str).replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[m]);
}

function formatTime(t) {
  if (!t || t === 'N/A') return '—';
  try {
    const d = new Date(t);
    return d.toLocaleString('ru-RU');
  } catch {
    return t;
  }
}

// drag & drop
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('upload-form');
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(ev => {
    form.addEventListener(ev, e => e.preventDefault());
  });
  ['dragenter', 'dragover'].forEach(ev => {
    form.addEventListener(ev, () => form.classList.add('dragover'));
  });
  ['dragleave', 'drop'].forEach(ev => {
    form.addEventListener(ev, () => form.classList.remove('dragover'));
  });
});