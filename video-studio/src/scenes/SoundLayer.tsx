import React from "react";
import { Sfx } from "../components/Sfx";
import { cutFrames, Shot } from "../components/Timeline";
import { soundMap } from "../data/sound-map";

/** A whoosh on every moving cut, peak aligned to the cut frame. */
export const WhooshOnCuts: React.FC<{ shots: Shot[] }> = ({ shots }) => (
  <>
    {cutFrames(shots).map((c) => (
      <Sfx
        key={c.frame}
        src={soundMap.whoosh.src}
        atFrame={c.frame}
        peakSec={soundMap.whoosh.peakSec}
        gainDb={soundMap.whoosh.gainDb}
      />
    ))}
  </>
);
