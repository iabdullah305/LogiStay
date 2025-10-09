async function fetchJSON(url) {
  const r = await fetch(url, { credentials: 'include' });
  if (!r.ok) throw new Error('Network error: ' + r.status);
  const j = await r.json();
  return j.message || j;
}

function card(title, childrenHTML = '') {
  return `
    <div class="bg-white shadow rounded p-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-lg font-semibold">${title}</h3>
      </div>
      <div>${childrenHTML}</div>
    </div>`;
}

function stat(label, value) {
  return `<div class="flex items-center justify-between py-1">
    <span class="text-sm text-gray-600">${label}</span>
    <span class="text-base font-medium">${value}</span>
  </div>`;
}

function listItem(it) {
  const amt = it.amount != null ? ` — ${it.amount}` : '';
  return `<li class="py-1 border-b"><a class="text-blue-600 hover:underline" href="/app/fuel-entry/${it.name}">${it.name}</a> — ${it.vehicle || ''} — ${it.posting_date}${amt}</li>`;
}

async function mountFleetPage() {
  const root = document.getElementById('fleet-page-root');
  if (!root) return;
  root.innerHTML = '<div class="text-gray-700">Loading...</div>';
  try {
    const counts = await fetchJSON('/api/method/logistay.api.get_counts');
    const fuelToday = await fetchJSON('/api/method/logistay.api.fuel_entries_today');

    const opsStats = [
      stat('Fleet Vehicle', counts.counts['Fleet Vehicle'] || 0),
      stat('Fleet Driver', counts.counts['Fleet Driver'] || 0),
      stat('Fuel Entry', counts.counts['Fuel Entry'] || 0),
      stat('Assignments', counts.counts['Driver Vehicle Assignment'] || 0),
    ].join('');

    const supplierStats = [
      stat('Supplier Master', counts.counts['Supplier Master'] || 0),
      stat('Supplier Contract', counts.counts['Supplier Contract'] || 0),
    ].join('');

    const quickList = `<ul>${(fuelToday.items || []).map(listItem).join('')}</ul>`;

    root.innerHTML = `
      <div class="container mx-auto px-4 py-6">
        <h1 class="text-2xl font-bold mb-4">Fleet Management</h1>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          ${card('Operations', opsStats)}
          ${card('Suppliers', supplierStats)}
          ${card('Fuel Entries Today', quickList)}
        </div>
        <div class="mt-6 text-sm text-gray-500">Updated at ${counts.timestamp}</div>
      </div>`;
  } catch (e) {
    root.innerHTML = `<div class="text-red-600">Error loading data: ${e.message}</div>`;
  }
}

document.addEventListener('DOMContentLoaded', mountFleetPage);