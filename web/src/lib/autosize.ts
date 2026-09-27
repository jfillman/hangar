// Same-origin iframes (the diagrams): grow each to its document height so the page, not the
// frame, scrolls, and keep its theme in step with the page's.
function fit(frame: HTMLIFrameElement) {
  const doc = frame.contentDocument;
  if (!doc?.documentElement) return;
  frame.style.height = `${doc.documentElement.scrollHeight}px`;
}

function syncTheme(frame: HTMLIFrameElement) {
  const root = frame.contentDocument?.documentElement;
  if (!root) return;
  const theme = document.documentElement.dataset.theme;
  if (theme) root.dataset.theme = theme;
  else delete root.dataset.theme;
}

const frames = [...document.querySelectorAll<HTMLIFrameElement>('iframe[data-autosize]')];
for (const frame of frames) {
  const attach = () => {
    syncTheme(frame);
    fit(frame);
    const body = frame.contentDocument?.body;
    if (body) new ResizeObserver(() => fit(frame)).observe(body);
    frame.contentDocument?.fonts?.ready.then(() => fit(frame));
  };
  frame.addEventListener('load', attach);
  if (frame.contentDocument?.readyState === 'complete') attach();
}

document.addEventListener('themechange', () => frames.forEach(syncTheme));
