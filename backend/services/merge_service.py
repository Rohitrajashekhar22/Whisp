from typing import List, Dict


# =====================================================
# MERGE WHISPER + DIARIZATION
# =====================================================

class MergeService:

    def assign_speakers(
        self,
        whisper_segments: List[Dict],
        diarization_segments: List[Dict]
    ) -> List[Dict]:
        """
        Output:
        [
            {
                "speaker": "Speaker 1",
                "text": "...",
                "start": 0.0,
                "end": 2.3
            }
        ]
        """

        merged_output = []

        for w_seg in whisper_segments:

            w_start = w_seg.get("start", 0)
            w_end = w_seg.get("end", 0)
            w_text = w_seg.get("text", "")

            speaker = self._find_speaker(
                w_start,
                w_end,
                diarization_segments
            )

            merged_output.append({
                "speaker": speaker,
                "text": w_text,
                "start": w_start,
                "end": w_end
            })

        return merged_output

    # -------------------------------------------------
    # FIND BEST MATCHING SPEAKER
    # -------------------------------------------------
    def _find_speaker(
        self,
        start: float,
        end: float,
        diarization_segments: List[Dict]
    ) -> str:

        best_speaker = "Unknown"
        max_overlap = 0

        for seg in diarization_segments:

            d_start = seg["start"]
            d_end = seg["end"]
            speaker = seg["speaker"]

            overlap = self._calculate_overlap(
                start, end, d_start, d_end
            )

            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = speaker

        return best_speaker

    # -------------------------------------------------
    # OVERLAP CALCULATION
    # -------------------------------------------------
    def _calculate_overlap(
        self,
        s1, e1,
        s2, e2
    ) -> float:

        start = max(s1, s2)
        end = min(e1, e2)

        return max(0, end - start)