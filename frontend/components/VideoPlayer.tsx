"use client";
import { useRef, useState } from "react";

interface Props {
  src: string;
  title?: string;
}

export function VideoPlayer({ src, title }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);

  function toggle() {
    const v = videoRef.current;
    if (!v) return;
    if (v.paused) { v.play(); setPlaying(true); }
    else { v.pause(); setPlaying(false); }
  }

  return (
    <div className="relative w-full rounded-2xl overflow-hidden bg-black shadow-xl">
      <video
        ref={videoRef}
        src={src}
        className="w-full aspect-video"
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onEnded={() => setPlaying(false)}
        controls
        playsInline
      />
      {title && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent px-4 py-3 pointer-events-none">
          <p className="text-white text-sm font-medium">{title}</p>
        </div>
      )}
    </div>
  );
}
