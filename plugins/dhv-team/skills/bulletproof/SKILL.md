---
name: bulletproof
description: Pressure-test an idea or plan before building it - is this the best route, what are the alternatives (including buying instead of building), where is the logic thin, what was forgotten, and a keep/change/stop verdict. Use on /bulletproof, /bulletproof grill, "poke holes", "devil's advocate", "is this the right approach", "grill me", "תנקב חורים", "האם זה הכיוון הנכון".
argument-hint: [grill] [the idea, in a sentence] (default: the plan being discussed in this chat)
disable-model-invocation: true
---

# /bulletproof - is this the right path at all?

The failure this catches: a long conversation about *how* to build something that never asked
*whether* to build it, or whether something already owned or for sale does the job. Reply in the
person's language.

Two modes:
- **`/bulletproof`** (review): a written verdict. Steps 1-4.
- **`/bulletproof grill`**: an interview, one question at a time. Step 1, then step 5.

## 1. Write the brief
Subject: the argument if given, else the idea or plan under discussion in this chat, else the next step
in `HANDOFF.md`. Nothing to go on → ask for the idea in one sentence and stop.

Write it **neutrally**; the bias to fight is the chat's own momentum:

    Goal:        the outcome wanted, not the solution ("managers get meeting action items", not "build an AI summariser")
    Constraints: budget, deadline, who uses it, data it touches, what DHV already owns (monday.com, Microsoft 365...),
                 what IT or security already approved (unknown → "unknown")
    Options:     the favoured path, as ONE option among the others known so far
    Walls:       every "X can't do Y" found so far
    Decided:     anything already ruled out, and why

Show it in about 3 lines ("Reviewing this - correct me if the goal is wrong") and carry on.

## 2. A fresh reviewer
Where you can start a helper agent, give it the brief and steps 3-4 as its instructions, not the chat
history: it has not spent an hour agreeing with the plan. Otherwise do steps 3-4 yourself, arguing for
the strongest alternative before judging the favoured one. "Keep it" is a fair verdict: do not invent
objections.

## 3. The alternatives ladder
Top to bottom; the first rung that meets the goal is the benchmark everything below must beat:
1. **Do nothing:** what breaks if this never happens?
2. **Change the process:** a template, a rule, a meeting format.
3. **Something already owned:** a feature in monday.com, Microsoft 365 / Teams / Copilot, Outlook, Excel,
   or a DHV tool someone already built.
4. **Buy:** search the web for products sold for this need, across the different names it is sold under,
   and name real products. Skip for pure logic choices.
5. **Build:** only now. Say what it gives that rungs 1-4 don't.

## 4. The angles, then the report
Check each; report only real findings: cost over 1-3 years (licences, hours to maintain); who maintains
it after the builder moves on; will the people it is for actually use it; privacy and client data
(personal data, recordings, client documents going to an outside service); what if the vendor changes
price or disappears; how success is measured; what happens when it is wrong and who notices; who was
not asked (IT, security, the users, the person who pays); logic holes.

Report, fitting a phone screen:
1. **Verdict:** Keep / Change / Stop, and the one-sentence reason.
2. **Top holes:** at most 3, each: what is wrong, its effect, the fix.
3. **Alternatives:** a table: option / pros / cons / rough cost. Only viable rungs.
4. **Only you can answer:** at most 3 questions no search can settle. End with "Want me to grill you on these?"

## 5. Grill mode
One question per message, multiple choice (2-4 options, the one you would pick first marked
"(Recommended)"). Never ask what can be looked up. Move across angles; push back once on a weak answer,
then accept it. Stop when two rounds change nothing, or on "enough", and close with the step 4 report.
