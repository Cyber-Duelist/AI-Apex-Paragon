const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%&*<>/\\|{}[]';

export function scrambleText(
  element: HTMLElement,
  finalText: string,
  duration = 1.4,
  onComplete?: () => void,
): () => void {
  const length = finalText.length;
  const resolved = new Array<boolean>(length).fill(false);
  let frame = 0;
  const totalFrames = Math.ceil(duration * 60);
  const resolveInterval = Math.max(1, Math.floor(totalFrames / length));

  const tick = () => {
    frame++;
    const resolveCount = Math.min(length, Math.floor(frame / resolveInterval));

    for (let i = 0; i < resolveCount; i++) {
      resolved[i] = true;
    }

    let output = '';
    for (let i = 0; i < length; i++) {
      const char = finalText[i] ?? '';
      if (resolved[i] || char === ' ') {
        output += char;
      } else {
        output += GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
      }
    }

    element.textContent = output;

    if (frame >= totalFrames) {
      element.textContent = finalText;
      onComplete?.();
      return;
    }

    requestAnimationFrame(tick);
  };

  requestAnimationFrame(tick);

  return () => {
    element.textContent = finalText;
  };
}
