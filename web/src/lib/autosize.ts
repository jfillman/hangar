// Grow each same-origin iframe to its document height so the page, not the frame, scrolls.
function fit(frame: HTMLIFrameElement) {
  const doc = frame.contentDocument;
  if (!doc?.documentElement) return;
  frame.style.height = `${doc.documentElement.scrollHeight}px`;
}

for (const frame of document.querySelectorAll<HTMLIFrameElement>('iframe[data-autosize]')) {
  const attach = () => {
    fit(frame);
    const body = frame.contentDocument?.body;
    if (body) new ResizeObserver(() => fit(frame)).observe(body);
    frame.contentDocument?.fonts?.ready.then(() => fit(frame));
  };
  frame.addEventListener('load', attach);
  if (frame.contentDocument?.readyState === 'complete') attach();
}
