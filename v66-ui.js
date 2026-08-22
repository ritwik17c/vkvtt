/* VKV Nalbari · Version 66.0 shared interface enhancements */
(function () {
  'use strict';

  document.documentElement.classList.add('v66-ui');

  const ICONS = {
    home: '<path d="M3 10.8 12 3l9 7.8"/><path d="M5.5 9.5V21h13V9.5"/><path d="M9.5 21v-6h5v6"/>',
    calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/><path d="M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    people: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    building: '<path d="M3 21h18M5 21V8l7-4 7 4v13M9 21v-4h6v4"/><path d="M9 10h.01M15 10h.01M9 13h.01M15 13h.01"/>',
    book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13Z"/><path d="M4 6.5A2.5 2.5 0 0 1 6.5 9H20"/>',
    file: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    swap: '<path d="m17 3 4 4-4 4M3 7h18M7 21l-4-4 4-4M21 17H3"/>',
    pin: '<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V21h-4v-.08A1.7 1.7 0 0 0 8.97 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.52-1H3v-4h.08A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.88L4.2 7.06l2.83-2.83.06.06A1.7 1.7 0 0 0 8.97 4.6 1.7 1.7 0 0 0 10 3.08V3h4v.08A1.7 1.7 0 0 0 15.03 4.6a1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.4 9c.12.62.65 1.03 1.52 1.03H21v4h-.08A1.7 1.7 0 0 0 19.4 15Z"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    chart: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    download: '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
    upload: '<path d="M12 16V4M7 9l5-5 5 5M5 21h14"/>',
    database: '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"/>',
    lock: '<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    flask: '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4a2 2 0 0 0 1.8-3l-5-9V3"/><path d="M8 15h8"/>',
    arrow: '<path d="M19 12H5M12 19l-7-7 7-7"/>',
    dots: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>'
  };

  function iconName(text) {
    const t = String(text || '').toLowerCase();
    if (/return|back|home|reset/.test(t)) return 'home';
    if (/calendar|date|day wise|annual/.test(t)) return 'calendar';
    if (/history|past|schedule|period|time/.test(t)) return 'clock';
    if (/teacher|staff|member|proxy|supervision/.test(t)) return /proxy|supervision/.test(t) ? 'swap' : 'people';
    if (/class|section|room|venue|school/.test(t)) return 'building';
    if (/timetable|subject|workload/.test(t)) return 'book';
    if (/leave|assignment|record|document/.test(t)) return 'file';
    if (/attendance|geofence|where now|location|on duty/.test(t)) return 'pin';
    if (/integrity|verify|approved|security/.test(t)) return 'shield';
    if (/admin|setting|configuration|manage/.test(t)) return 'settings';
    if (/access|role|account|sign in|profile/.test(t)) return 'lock';
    if (/overview|summary|report|metric/.test(t)) return 'chart';
    if (/export|download|share|print/.test(t)) return 'download';
    if (/import|upload|restore/.test(t)) return 'upload';
    if (/backup|database|cloud|sync/.test(t)) return 'database';
    if (/edit|correction|update|master/.test(t)) return 'edit';
    if (/test|mock|trial/.test(t)) return 'flask';
    if (/save|finali[sz]e|accept|working/.test(t)) return 'check';
    if (/user|my /.test(t)) return 'user';
    return 'dots';
  }

  function makeIcon(name) {
    const span = document.createElement('span');
    span.className = 'v66-icon';
    span.setAttribute('aria-hidden', 'true');
    span.innerHTML = '<svg viewBox="0 0 24 24">' + (ICONS[name] || ICONS.dots) + '</svg>';
    return span;
  }

  function firstTextNode(root) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) { return node.nodeValue && node.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP; }
    });
    return walker.nextNode();
  }

  function replaceLeadingEmoji(target) {
    if (!target || target.querySelector(':scope > .v66-icon')) return;
    const node = firstTextNode(target);
    if (!node) return;
    const original = node.nodeValue;
    const cleaned = original.replace(/^\s*(?:(?:\p{Extended_Pictographic}|[←↻↩︎↪︎✦✓✕＋])(?:\uFE0F|\u200D|\p{Emoji_Modifier})*\s*)+/u, '');
    if (cleaned === original) return;
    node.nodeValue = cleaned;
    const host = node.parentElement || target;
    host.insertBefore(makeIcon(iconName(target.textContent)), node);
  }

  function setLoadingState(el) {
    if (!el) return;
    const loading = /checking|loading|connecting|please wait|verifying|preparing/i.test(el.textContent || '');
    el.classList.toggle('is-loading', loading);
    if (loading) el.setAttribute('aria-busy', 'true');
    else el.removeAttribute('aria-busy');
  }

  function enhance() {
    const file = (location.pathname.split('/').pop() || 'index.html').replace(/\.html$/i, '') || 'index';
    document.body.dataset.page = file;

    const pageHeading = document.querySelector('body > header:not(.topbar) h1');
    if (pageHeading && !pageHeading.parentElement.querySelector('.v66-eyebrow')) {
      const eyebrow = document.createElement('div');
      eyebrow.className = 'v66-eyebrow';
      eyebrow.textContent = file.startsWith('admin-') ? 'Administration workspace' : (file === 'attendance' ? 'Staff self-service' : 'School operations');
      pageHeading.parentElement.insertBefore(eyebrow, pageHeading);
    }

    const main = document.querySelector('main');
    if (main) {
      if (!main.id) main.id = 'main-content';
      const skip = document.createElement('a');
      skip.className = 'v66-skip-link';
      skip.href = '#' + main.id;
      skip.textContent = 'Skip to main content';
      document.body.insertBefore(skip, document.body.firstChild);
    }

    document.querySelectorAll('button, a.btn, .tile b, .myAreaTitle, .opsTitle').forEach(replaceLeadingEmoji);

    document.querySelectorAll('.tile').forEach(tile => {
      if (tile.tabIndex < 0) tile.tabIndex = 0;
      if (!tile.hasAttribute('role')) tile.setAttribute('role', 'button');
      tile.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          tile.click();
        }
      });
    });

    document.querySelectorAll('button').forEach(button => {
      if (/delete|remove|archive/i.test(button.textContent || '')) button.dataset.tone = 'destructive';
    });

    const liveRegions = document.querySelectorAll('.status, [id$="Msg"], [id$="Message"], [id$="Status"]');
    liveRegions.forEach(el => {
      if (!el.hasAttribute('aria-live')) el.setAttribute('aria-live', 'polite');
      setLoadingState(el);
    });
    const observer = new MutationObserver(records => {
      records.forEach(record => setLoadingState(record.target.nodeType === 1 ? record.target : record.target.parentElement));
    });
    liveRegions.forEach(el => observer.observe(el, { childList: true, characterData: true, subtree: true }));

    if (!document.querySelector('.v66-product-footer')) {
      const footer = document.createElement('footer');
      footer.className = 'v66-product-footer';
      footer.textContent = 'VKV Nalbari · Secure school operations workspace · Version 66.0';
      document.body.appendChild(footer);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhance, { once: true });
  else enhance();
}());
