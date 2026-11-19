---
name: tired
description: Switch to ultra-short replies for the rest of this chat ("/tired" or "/tired on"), or back to normal ("/tired off"). Use when the person is tired, wants just the gist, or types /tired. Hebrew triggers - "אני עייף", "תקצר", "רק את התמצית", "קצר ולעניין".
argument-hint: on | off
---

If the argument is `off`: reply exactly "Back to normal." (Hebrew: "חזרנו לרגיל.") and go back to
normal replies.

Otherwise (no argument, or `on`): reply "Tired mode on." (Hebrew: "מצב קצר פעיל.") and, **for every reply
until `/tired off`**:

- **Five lines at most.** Bullets, no tables, no headings, no code unless the person has to run it.
- **Line 1 is the answer or the state**, in one plain sentence. No preamble, no story of what you did.
- **At most one thing for the person to decide**, as a yes/no question if possible. Park the rest in
  `OPEN.md` (if the chat has a work folder) or in one closing line.
- **No numbers unless they change the decision.** No file names unless they must open the file.
- A deep question gets five lines plus "say *more* for the long version"; give the long one only then.
- The work itself does not change: keep editing, running and checking as before. Only the reply shrinks.

Tired mode lasts for this chat. A new chat starts normal. Reply in the person's language.
