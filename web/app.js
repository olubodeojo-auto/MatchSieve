'use strict';

const $ = (id) => document.getElementById(id);
const state = { fixtures: [], selectedFixture: null, selectedMarket: 'UNDER_4_5', filter: 'all', markets: [], latestMarkdown: '', ollamaEnabled: false };
const marketLabels = {
  UNDER_4_5: 'Under 4.5 goals', UNDER_3_5: 'Under 3.5 goals', OVER_2_5: 'Over 2.5 goals',
  BTTS: 'Both teams to score', DOUBLE_CHANCE: 'Double chance context', RESULT_1X2: 'Match result context', RESEARCH_BRIEF: 'Full contextual brief'
};

async function api(url, options = {}) {
  const opts = { ...options, headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) } };
  const response = await fetch(url, opts);
  const data = await response.json().catch(() => ({ error: 'The server returned an unreadable response.' }));
  if (!response.ok) throw new Error(data.error || data.message || `Request failed (${response.status})`);
  return data;
}
function esc(value) { return String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
function safeHttpUrl(value) {
  if (!value) return '';
  try { const url = new URL(String(value)); return ['http:', 'https:'].includes(url.protocol) ? url.href : ''; }
  catch { return ''; }
}
function shortDate(value) {
  if (!value) return 'Kickoff not provided';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? String(value) : new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(d);
}
function setMessage(id, message, kind = '') {
  const el = $(id); if (!el) return;
  el.textContent = message; el.className = `inline-message ${kind}`.trim();
}
function formatStatus(status) {
  return status === 'READY_FOR_REVIEW' ? 'Ready for review' : status === 'LIMITED_EVIDENCE' ? 'Limited evidence' : String(status || 'Unknown status').replaceAll('_', ' ').toLowerCase();
}
function updateSelected() {
  const f = state.selectedFixture;
  $('selectedTitle').textContent = f ? `${f.home_team} vs ${f.away_team}` : 'Select a fixture to continue';
  $('selectedMeta').textContent = f ? `${f.competition || 'Competition not set'} · ${shortDate(f.kickoff_utc)} · source ${f.source_primary || 'unknown'}` : 'Kickoff, competition and source will appear here.';
  $('researchBtn').disabled = !f;
  renderFixtures($('fixtureSearch').value);
}
function filteredFixtures(query = '') {
  const needle = query.trim().toLowerCase();
  return state.fixtures.filter((f) => {
    const matchQuery = !needle || `${f.home_team} ${f.away_team} ${f.competition}`.toLowerCase().includes(needle);
    const status = String(f.status || '').toLowerCase();
    const isFinished = ['finished', 'complete', 'completed', 'ft'].includes(status);
    const matchFilter = state.filter === 'all' || (state.filter === 'finished' ? isFinished : !isFinished);
    return matchQuery && matchFilter;
  }).slice(0, 80);
}
function renderFixtures(query = '') {
  const host = $('fixtureResults'); const fixtures = filteredFixtures(query);
  if (!fixtures.length) {
    const hasAny = state.fixtures.length > 0;
    host.innerHTML = `<div class="empty-state"><span class="empty-mark">${hasAny ? '⌕' : '＋'}</span><strong>${hasAny ? 'No fixture matches this search' : 'Your fixture archive is empty'}</strong><p>${hasAny ? 'Try another team name or change the status filter.' : 'Connect a permitted provider or import a historical-results CSV under Data setup to begin. No sample fixtures are being passed off as live data.'}</p></div>`;
    return;
  }
  host.innerHTML = fixtures.map((f) => {
    const active = state.selectedFixture?.id === f.id;
    const finished = ['finished', 'complete', 'completed', 'ft'].includes(String(f.status || '').toLowerCase());
    const score = f.home_score != null && f.away_score != null ? `<span class="fixture-score">${esc(f.home_score)}–${esc(f.away_score)}</span>` : '';
    return `<button class="fixture-card ${active ? 'active' : ''}" type="button" data-fixture-id="${Number(f.id)}" aria-pressed="${active}">
      <span class="fixture-card-top"><span class="competition-tag">${esc(f.competition || 'Competition')}</span><span class="fixture-state ${finished ? 'finished' : ''}">${finished ? 'Completed' : 'Scheduled'}</span></span>
      <span class="fixture-teams"><span>${esc(f.home_team)}</span><em>vs</em><span>${esc(f.away_team)}</span>${score}</span>
      <span class="fixture-meta">${esc(shortDate(f.kickoff_utc))} <b>·</b> ${esc(f.source_primary || 'unknown source')}</span>
    </button>`;
  }).join('');
  host.querySelectorAll('[data-fixture-id]').forEach((button) => button.addEventListener('click', () => {
    state.selectedFixture = state.fixtures.find((f) => f.id === Number(button.dataset.fixtureId)) || null;
    updateSelected();
  }));
}
function renderMarkets(markets) {
  state.markets = Array.isArray(markets) ? markets : [];
  const host = $('marketOptions');
  if (!state.markets.length) return;
  host.innerHTML = state.markets.map((m) => `<button class="market-option ${m.code === state.selectedMarket ? 'active' : ''}" data-market="${esc(m.code)}" type="button" aria-pressed="${m.code === state.selectedMarket}">
    <span class="market-check">✓</span><strong>${esc(m.label)}</strong><small>${esc(m.question)}</small></button>`).join('');
  host.querySelectorAll('[data-market]').forEach((button) => button.addEventListener('click', () => {
    state.selectedMarket = button.dataset.market;
    host.querySelectorAll('[data-market]').forEach((b) => { const active = b === button; b.classList.toggle('active', active); b.setAttribute('aria-pressed', String(active)); });
  }));
}
function markdownToSafeHtml(markdown) {
  // This is a deliberately small renderer. Escape input before adding formatting tokens.
  let html = esc(markdown || '');
  html = html.replace(/^### (.*)$/gm, '<h4>$1</h4>').replace(/^## (.*)$/gm, '<h3>$1</h3>').replace(/^# (.*)$/gm, '<h2>$1</h2>');
  html = html.replace(/^> (.*)$/gm, '<blockquote>$1</blockquote>').replace(/^\*\*(.*?)\*\*$/gm, '<strong>$1</strong>');
  html = html.replace(/^\- (.*)$/gm, '<li>$1</li>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/((?:<li>.*?<\/li>\s*)+)/gs, '<ul>$1</ul>').replace(/\n{2,}/g, '<br><br>').replace(/\n/g, '<br>');
  return html;
}
function renderSignalCard(title, list, type, empty) {
  const lines = Array.isArray(list) ? list : [];
  return `<section class="evidence-card ${type}"><div class="evidence-card-heading"><span class="evidence-icon">${type === 'support' ? '＋' : type === 'counter' ? '−' : '!'}</span><div><h3>${esc(title)}</h3><small>${lines.length} ${lines.length === 1 ? 'item' : 'items'}</small></div></div>${lines.length ? `<ul>${lines.map((item) => `<li>${esc(typeof item === 'string' ? item : item.detail || item.label || JSON.stringify(item))}</li>`).join('')}</ul>` : `<p class="no-evidence">${esc(empty)}</p>`}</section>`;
}
function renderReport(report) {
  const fixture = report.report?.fixture || report.fixture || state.selectedFixture || {};
  const evidence = report.report || report;
  const market = evidence.market || {};
  const label = market.label || report.market_label || marketLabels[report.market_code] || report.market_code || state.selectedMarket;
  state.latestMarkdown = report.markdown || report.markdown_content || '';
  $('reportHeading').textContent = `${fixture.home_team || 'Home'} vs ${fixture.away_team || 'Away'}`;
  $('reportSubtitle').textContent = `${fixture.competition || 'Competition not set'} · ${label} · Generated ${shortDate(evidence.generated_at || report.generated_at_utc)}`;
  const summary = report.summary || (evidence.status === 'READY_FOR_REVIEW' ? 'The archive contains a usable starting sample. Confirm current line-ups, injuries and market context before relying on the report.' : 'The archive is missing important evidence. This is a limited report, not a prediction or recommendation.');
  const support = evidence.supporting_signals || (report.supporting_evidence || []).map((x) => x.detail || x);
  const counter = evidence.counter_signals || (report.counter_evidence || []).map((x) => x.detail || x);
  const missing = evidence.missing_information || report.missing_data || [];
  const sources = evidence.sources || report.source_records || [];
  const home = evidence.home_form || report.home_form || {};
  const away = evidence.away_form || report.away_form || {};
  const recentLine = (team) => team?.sample_size ? `<div class="form-stats"><strong>${esc(team.sample_size)}</strong><small>matches</small><span>${esc(team.goals_for_avg ?? '—')} scored avg.</span><span>${esc(team.goals_against_avg ?? '—')} conceded avg.</span><span>${esc(team.five_plus_goals_count ?? 0)} with 5+ goals</span></div>` : '<p class="no-evidence">No completed historical results are stored for this team before the fixture.</p>';
  $('reportContent').innerHTML = `
    <div class="report-overview"><div><div class="report-chip-row"><span class="status-chip ${evidence.status === 'READY_FOR_REVIEW' ? 'ready' : 'limited'}">${esc(formatStatus(evidence.status || report.status))}</span><span class="market-chip">${esc(label)}</span><span class="report-id">REPORT #${esc(report.report_id || report.id || '—')}</span></div><p class="report-summary">${esc(summary)}</p></div><div class="overview-stamp"><span>DATA BASIS</span><strong>Stored records</strong><small>Not a live guarantee</small></div></div>
    <div class="team-form-grid"><article class="team-form-card"><div><span class="team-number">01</span><h3>${esc(home.team || fixture.home_team || 'Home team')}</h3></div>${recentLine(home)}</article><article class="team-form-card"><div><span class="team-number">02</span><h3>${esc(away.team || fixture.away_team || 'Away team')}</h3></div>${recentLine(away)}</article></div>
    <div class="evidence-grid">${renderSignalCard('Signals supporting the market', support, 'support', 'No supporting indicators could be calculated from the stored records.')}${renderSignalCard('Counter-signals & caution', counter, 'counter', 'No opposing indicator could be calculated from the stored records.')}</div>
    ${renderSignalCard('Missing or unverified information', missing, 'missing', 'No gaps were identified by this baseline check. This does not mean that every source was checked.')}
    <section class="source-card"><div class="source-heading"><div><p class="eyebrow">SOURCE PROVENANCE</p><h3>Where this evidence came from</h3></div><span class="source-count">${sources.length} record${sources.length === 1 ? '' : 's'}</span></div>${sources.length ? `<div class="source-list">${sources.map((s) => `<article class="source-row"><span class="source-mark">↗</span><div><strong>${esc(s.source_key || 'Unknown source')}</strong><small>Captured ${esc(shortDate(s.captured_at))} · ${esc(s.quality_label || 'quality not assessed')}</small><p>${esc(s.source_ref || 'No source reference attached.')}${safeHttpUrl(s.source_url) ? ` · <a href="${esc(safeHttpUrl(s.source_url))}" target="_blank" rel="noopener noreferrer">Open source</a>` : ''}${s.source_key === 'sportscore' ? ' · <a href="https://sportscore.com/" target="_blank" rel="noopener noreferrer">Powered by SportScore</a>' : ''}</p></div></article>`).join('')}</div>` : '<p class="no-evidence">No source snapshot is attached to this report.</p>'}</section>
    ${state.latestMarkdown ? `<details class="full-report-text"><summary>Open full report text</summary><div class="markdown-body">${markdownToSafeHtml(state.latestMarkdown)}</div></details>` : ''}
    <p class="method-note"><strong>Method and limits.</strong> ${esc(evidence.method_note || report.method_note || 'Counts describe the archive only; they are not calibrated probabilities or predictions.')}</p>`;
  $('reportSection').classList.remove('hidden');
  $('reportSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
}
async function loadStatus() {
  try {
    const data = await api('/api/status');
    $('fixtureCount').textContent = Number(data.counts?.fixtures || 0).toLocaleString();
    $('reportCount').textContent = Number(data.counts?.research_reports || 0).toLocaleString();
    $('snapshotCount').textContent = Number(data.counts?.source_snapshots || 0).toLocaleString();
    state.ollamaEnabled = Boolean(data.ollama_enabled);
    $('ollamaStatus').textContent = state.ollamaEnabled ? 'ON' : 'OFF';
    $('ollamaModel').textContent = state.ollamaEnabled ? (data.ollama_model || 'Configured local model') : 'Optional · disabled';
    $('ollamaPill').textContent = state.ollamaEnabled ? 'READY' : 'OFF';
    $('useOllama').disabled = !state.ollamaEnabled;
    $('connectionLabel').textContent = 'API CONNECTED';
    $('footerVersion').textContent = `MATCHSIEVE · API ${data.api_contract || '—'} · LOCAL FOUNDATION`;
  } catch (error) {
    $('connectionLabel').textContent = 'API OFFLINE';
    setMessage('intakeMessage', error.message, 'error');
  }
}
async function loadFixtures(query = '') {
  const previous = state.selectedFixture?.id;
  try {
    const params = new URLSearchParams({ q: query, limit: '250' });
    state.fixtures = await api(`/api/fixtures?${params.toString()}`);
    if (previous) state.selectedFixture = state.fixtures.find((f) => f.id === previous) || null;
    renderFixtures($('fixtureSearch').value);
    updateSelected();
  } catch (error) {
    $('fixtureResults').innerHTML = `<div class="empty-state"><strong>Could not load fixtures</strong><p>${esc(error.message)}</p></div>`;
  }
}
async function runResearch() {
  if (!state.selectedFixture) return;
  const button = $('researchBtn'); button.disabled = true; button.classList.add('loading'); button.querySelector('span').textContent = 'Assembling your report…';
  $('reportSection').classList.remove('hidden');
  $('reportContent').innerHTML = '<div class="working-state"><span class="spinner"></span><strong>Building the evidence map</strong><p>Reading stored results and source snapshots. Missing data will stay visible.</p></div>';
  $('reportHeading').textContent = `${state.selectedFixture.home_team} vs ${state.selectedFixture.away_team}`;
  try {
    const result = await api('/api/research', { method: 'POST', body: JSON.stringify({ fixture_id: state.selectedFixture.id, market: state.selectedMarket, ollama: $('useOllama').checked }) });
    renderReport(result);
    await Promise.all([loadStatus(), loadHistory()]);
  } catch (error) {
    $('reportContent').innerHTML = `<div class="error-state"><strong>Research could not be completed</strong><p>${esc(error.message)}</p><p>Check that the fixture exists and the selected market is supported.</p></div>`;
  } finally {
    button.classList.remove('loading'); button.querySelector('span').textContent = 'Generate research report'; button.disabled = !state.selectedFixture;
  }
}
async function loadHistory() {
  try {
    const rows = await api('/api/research/history?limit=24');
    const host = $('historyList');
    if (!rows.length) { host.innerHTML = '<div class="empty-state compact"><strong>No saved reports yet</strong><p>Generate a report and it will be saved here automatically.</p></div>'; return; }
    host.innerHTML = rows.map((r) => `<button class="history-card" type="button" data-report-id="${Number(r.id)}"><span class="history-date">${esc(shortDate(r.generated_at_utc || r.created_at))}</span><strong>${esc(r.fixture?.home_team || 'Home')} <em>vs</em> ${esc(r.fixture?.away_team || 'Away')}</strong><span class="history-meta"><span>${esc(r.market_label || marketLabels[r.market_code] || r.market_code)}</span><b>·</b><span class="status-dot-mini ${r.status === 'READY_FOR_REVIEW' ? 'ready' : ''}"></span>${esc(formatStatus(r.status))}</span><span class="history-open">Open report ↗</span></button>`).join('');
    host.querySelectorAll('[data-report-id]').forEach((button) => button.addEventListener('click', async () => {
      button.disabled = true;
      try { const report = await api(`/api/research/${Number(button.dataset.reportId)}`); renderReport(report); }
      catch (error) { setMessage('intakeMessage', error.message, 'error'); }
      finally { button.disabled = false; }
    }));
  } catch (error) {
    $('historyList').innerHTML = `<div class="empty-state compact"><strong>Could not load saved reports</strong><p>${esc(error.message)}</p></div>`;
  }
}
async function loadProviders() {
  try {
    const rows = await api('/api/providers');
    const list = Array.isArray(rows) ? rows : rows.providers || [];
    $('providerList').innerHTML = list.map((p) => {
      const status = String(p.status || 'catalogue_only');
      const hasAdapter = status.startsWith('adapter_available');
      const csvImport = status.startsWith('import_supported');
      const ready = hasAdapter || csvImport;
      const key = p.key || p.id || p.provider || p.label || 'provider';
      const label = p.label || p.name || key;
      const detail = p.note || p.notes || p.description || (hasAdapter ? 'Adapter exists; live validation still required.' : csvImport ? 'Historical import is supported; it is not a live schedule API.' : 'Catalogue entry only; adapter is not implemented here.');
      return `<div class="provider-row"><span class="provider-light ${ready ? 'implemented' : ''}"></span><div><strong>${esc(label)}</strong><small>${esc(detail)}</small></div><span class="provider-state">${hasAdapter ? 'ADAPTER' : csvImport ? 'CSV' : 'CATALOGUE'}</span></div>`;
    }).join('') || '<p class="muted">No providers listed.</p>';
  } catch (error) { $('providerList').textContent = error.message; }
}
async function importCsv() {
  const filename = $('csvFilename').value.trim();
  if (!filename) { setMessage('intakeMessage', 'Enter a CSV filename stored inside data/inbox/.', 'error'); return; }
  try {
    const result = await api('/api/import-csv', { method: 'POST', body: JSON.stringify({ filename, source_key: 'operator_csv' }) });
    const errors = Array.isArray(result.errors) ? result.errors.length : 0;
    setMessage('intakeMessage', `Import finished: ${result.imported ?? result.rows_imported ?? 0} row(s) imported; ${errors} row error(s).`, errors ? 'warning' : 'success');
    await Promise.all([loadFixtures(), loadStatus()]);
  } catch (error) { setMessage('intakeMessage', error.message, 'error'); }
}
async function addFixture() {
  const home_team = $('mHome').value.trim(), away_team = $('mAway').value.trim(), competition = $('mComp').value.trim();
  const kickoffValue = $('mKickoff').value;
  if (!home_team || !away_team || !kickoffValue) { setMessage('intakeMessage', 'Home team, away team and kickoff are required.', 'error'); return; }
  try {
    const result = await api('/api/fixture', { method: 'POST', body: JSON.stringify({ home_team, away_team, competition: competition || 'Unknown competition', kickoff: new Date(kickoffValue).toISOString(), source_key: 'manual', source_ref: $('mSource').value.trim() || 'entered by operator' }) });
    setMessage('intakeMessage', `Fixture saved as #${result.fixture_id}. Historical results are still needed for analysis.`, 'success');
    $('mHome').value = ''; $('mAway').value = ''; $('mComp').value = ''; $('mSource').value = '';
    await Promise.all([loadFixtures(), loadStatus()]);
  } catch (error) { setMessage('intakeMessage', error.message, 'error'); }
}
async function fetchProvider() {
  const provider = $('providerChoice').value;
  const payload = { provider, status: $('providerStatus').value };
  const from = $('providerDateFrom').value, to = $('providerDateTo').value;
  if (from) payload.date_from = from;
  if (to) payload.date_to = to;
  if (from) payload.date = from;
  payload.competition = $('providerCompetition').value.trim();
  payload.league = $('providerLeague').value.trim();
  payload.season = $('providerSeason').value.trim();
  $('providerFetchBtn').disabled = true;
  setMessage('providerFetchMessage', `Checking ${provider} configuration and attempting the selected fetch…`);
  try {
    const result = await api('/api/provider-fetch', { method: 'POST', body: JSON.stringify(payload) });
    if (result.status === 'success') {
      setMessage('providerFetchMessage', `${result.message || 'Provider fetch complete.'} Imported ${result.records_received ?? 0} record(s). Review source licence and coverage before production use.`, 'success');
      await Promise.all([loadFixtures($('fixtureSearch').value), loadStatus()]);
    } else {
      setMessage('providerFetchMessage', result.message || `Provider fetch returned status ${result.status}.`, 'warning');
    }
  } catch (error) {
    setMessage('providerFetchMessage', error.message, 'error');
  } finally { $('providerFetchBtn').disabled = false; }
}

async function searchKnowledge() {
  const query = $('kbQuery').value.trim();
  if (!query) { $('kbResults').textContent = 'Enter a search term.'; return; }
  try {
    const rows = await api(`/api/kb-search?q=${encodeURIComponent(query)}&limit=10`);
    $('kbResults').innerHTML = rows.length ? rows.map((r) => `<article class="kb-result"><strong>${esc(r.title)}</strong><small>${esc(r.doc_type)} · v${esc(r.version)} · ${esc(shortDate(r.updated_at))}</small><p>${esc(String(r.markdown || '').slice(0, 220))}${String(r.markdown || '').length > 220 ? '…' : ''}</p></article>`).join('') : '<p class="muted">No saved knowledge documents match that search.</p>';
  } catch (error) { $('kbResults').textContent = error.message; }
}
function downloadMarkdown() {
  if (!state.latestMarkdown) return;
  const blob = new Blob([state.latestMarkdown], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob); const a = document.createElement('a');
  a.href = url; a.download = `matchsieve-research-${Date.now()}.md`; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
}
async function copyMarkdown() {
  if (!state.latestMarkdown) return;
  try { await navigator.clipboard.writeText(state.latestMarkdown); $('copyReport').textContent = 'Copied ✓'; }
  catch { $('copyReport').textContent = 'Copy unavailable'; }
  setTimeout(() => { $('copyReport').textContent = 'Copy report'; }, 1800);
}

$('fixtureSearch').addEventListener('input', () => loadFixtures($('fixtureSearch').value));
$('clearSearch').addEventListener('click', () => { $('fixtureSearch').value = ''; loadFixtures(''); });
document.querySelectorAll('[data-filter]').forEach((button) => button.addEventListener('click', () => {
  state.filter = button.dataset.filter;
  document.querySelectorAll('[data-filter]').forEach((b) => b.classList.toggle('active', b === button));
  renderFixtures($('fixtureSearch').value);
}));
$('researchBtn').addEventListener('click', runResearch);
$('refreshHistory').addEventListener('click', loadHistory);
$('downloadReport').addEventListener('click', downloadMarkdown);
$('copyReport').addEventListener('click', copyMarkdown);
$('importCsvBtn').addEventListener('click', importCsv);
$('addFixtureBtn').addEventListener('click', addFixture);
$('kbSearchBtn').addEventListener('click', searchKnowledge);
$('providerFetchBtn').addEventListener('click', fetchProvider);
$('providerChoice').addEventListener('change', () => {
  const provider = $('providerChoice').value;
  document.querySelectorAll('[data-provider-fields]').forEach((el) => { el.classList.toggle('hidden', !el.dataset.providerFields.split(',').includes(provider)); });
});
$('kbQuery').addEventListener('keydown', (event) => { if (event.key === 'Enter') searchKnowledge(); });

async function boot() {
  const today = new Date().toISOString().slice(0, 10);
  $('providerDateFrom').value = today; $('providerDateTo').value = today;
  try {
    const [status, markets] = await Promise.all([api('/api/status'), api('/api/markets')]);
    $('fixtureCount').textContent = Number(status.counts?.fixtures || 0).toLocaleString();
    $('reportCount').textContent = Number(status.counts?.research_reports || 0).toLocaleString();
    $('snapshotCount').textContent = Number(status.counts?.source_snapshots || 0).toLocaleString();
    state.ollamaEnabled = Boolean(status.ollama_enabled);
    $('ollamaStatus').textContent = state.ollamaEnabled ? 'ON' : 'OFF';
    $('ollamaModel').textContent = state.ollamaEnabled ? status.ollama_model : 'Optional · disabled';
    $('ollamaPill').textContent = state.ollamaEnabled ? 'READY' : 'OFF';
    $('useOllama').disabled = !state.ollamaEnabled;
    $('connectionLabel').textContent = 'API CONNECTED';
    $('footerVersion').textContent = `MATCHSIEVE · API ${status.api_contract || '—'} · LOCAL FOUNDATION`;
    renderMarkets(markets);
  } catch (error) { $('connectionLabel').textContent = 'API OFFLINE'; console.error(error); }
  await Promise.all([loadFixtures(), loadHistory(), loadProviders()]);
}
boot();
