# How Tap-to-Pay Wakes a Card With No Battery

*You tap. It says "Approved." Your card has no battery, no charger, no power button. So what just woke it up — and how did it talk back?*

---

You hold your card near the reader. It beeps. *Approved.*

You didn't slide anything into a slot. You didn't even touch the thing — you just floated the card a centimetre away and a transaction settled between you, a shop, and a bank on the other side of the city. The whole exchange took less time than a blink.

Now turn the card over and look at it. There's no battery. No little gold contacts to charge it. No power button, no screen, nothing that could possibly be holding a charge. You've owned it for years and never plugged it in. By every reasonable measure, this card is an inert rectangle of plastic.

And yet, for about half a second, it ran a computer, did some cryptography, and held a conversation. Something woke it up. The question is what.

---

The answer is that the reader is shouting, and your card is listening with an antenna you can't see.

Inside your card, looped around the very edge of the plastic, is a flat coil of wire — several turns of it, running the full perimeter. You'd never know it's there. Inside the payment terminal is a second coil, doing one thing constantly, whether or not anyone is paying: pushing an alternating current back and forth through itself `13.56 million` times a second, which throws off an invisible magnetic field that pulses at exactly that rate. The terminal is always broadcasting. It's been broadcasting all day.

When you bring your card into that field, physics does you a favour. A magnetic field that's changing — flipping direction `13.56M` times a second — will shove electrons around in any nearby loop of wire. Your card's coil sits in the field, the field flips, and a current starts flowing in the coil that wasn't there a moment ago. The card didn't bring power. The reader handed it power, through thin air, the instant the two coils got close enough.

> Two coils, no wire between them. That's a transformer — the same trick humming inside every phone charger, except here the second half of it is in your wallet.

This is *inductive coupling*, and the chip in your card runs on nothing else. The current the reader induces is alternating — sloshing back and forth — so the chip first sends it through a *rectifier*, a tiny circuit that bends the back-and-forth into steady one-way power, then smooths it and feeds it to the processor. Cross the gap, and the chip boots. Pull away, and it goes dark mid-thought. There is no in-between, because there is nothing stored. The power exists only while you're holding the card in the field.

[INSERT DIAGRAM: How the reader powers the card across an air gap — copy from HTML]

---

This is also why you have to get so close. You've felt it — hold the card a hand's width away and nothing happens; bring it within a couple of centimetres and it springs to life. That's not the terminal being fussy. It's the kind of field it is.

A magnetic field like this one is *near-field* — it doesn't radiate across a room the way a radio station does. Its strength falls off brutally with distance, fading to nothing within a few centimetres of the coil. The standard that governs your card, an international rulebook called *ISO 14443*, is built around a working range of roughly `4 cm`. Beyond that, there simply isn't enough field left to power the chip.

The short range is doing security work for free. A card that can only be powered from four centimetres away is a card that can't be quietly energised by someone standing behind you in line. To wake your card, you have to almost touch it to the reader — which is exactly the gesture you already make, and exactly the gesture a pickpocket can't make from across the aisle.

---

So the card is awake. Now it has to answer. And here's the part that turns the whole thing on its head.

Your card has no transmitter. Broadcasting a radio signal of its own would take real power — power it doesn't have, because every drop it owns is being spent just staying on. It cannot shout back. So it doesn't. Instead, it does something far stranger: it talks by getting heavier and lighter.

Remember, the card is drawing power out of the reader's field, like a straw drawing from a glass. The chip can choose, thousands of times a second, to sip harder or sip softer — switching a small load on and off inside itself. And the reader, on the other end of that same field, can *feel* the difference. Every time the card draws a little more, the reader's own circuit dips a little. The card isn't sending a signal. It's tugging on the reader's signal, and the reader reads the tugs.

This is *load modulation*, and it's the quiet genius of the whole system. The card switches its load on and off at `847.5 kHz` — a rhythm fast enough to ride on top of the reader's `13.56 MHz` hum without getting lost in it — and the pattern of heavier and lighter spells out bits, around `106 kbit/s` of them. The reader feels a faint shudder in its own field and decodes your card's reply out of it. Two devices, one of them with no power source and no transmitter, holding a full conversation across a few centimetres of air.

---

And that conversation is not your card reciting its number into the void. If it were, anyone who overheard one tap could replay it forever. That's the trap the magnetic-stripe cards fell into for decades — the stripe held the same fixed data every time, so a single skim was enough to clone it.

Your contactless card slams that door. When it talks back, the chip uses a secret key — one baked into it at the factory, one that *never* leaves the chip and is known only to it and your bank — to compute a fresh one-time code for this exact purchase. The amount, the moment, a counter that ticks up every single tap: all of it gets stirred into a cryptographic signature called an *ARQC*, an Authorisation Request Cryptogram. The terminal can't fake it. The terminal never even sees the key. It just relays the cryptogram to your bank, which holds the matching secret, recomputes the same code, and checks that the two agree.

> Eavesdrop on a tap and all you capture is a code that was already spent the instant it was made. Replay it and the bank sees a counter that already ticked past, and says no.

That's why a contactless card is so much harder to clone than the old stripe. There's nothing static worth stealing. The card doesn't hand over a secret; it proves it knows one, in a way that's useless to anyone the moment it's spoken. And it does all of this — power up, select the payment app, sign the cryptogram, reply — inside a budget the standard caps at half a second. The card is meant to be in the field for no more than `500 ms`: roughly `100 ms` for the reader's side of the talk, and up to `400 ms` for the card's.

This is also why a tap occasionally fails. Sweep the card past too fast and you yank it out of the field before the chip finishes signing — the power collapses mid-sentence, the cryptogram never lands, and the terminal, hearing only half an answer, declines. The fix is the thing the cashier always tells you: hold it still, a moment longer.

[INSERT DIAGRAM: One tap from field entry to Approved — copy from HTML]

---

The reader beeps. The card goes dark.

It's back to being an inert rectangle in your wallet, holding no charge, doing nothing, waiting for the next field to lend it half a second of life. You didn't think about the coil, or the borrowed current, or the load it tugged to speak, or the one-time code that's already worthless.

You just held it near the reader. It said yes.

Tomorrow you'll do it again, and now you'll feel the half-second.

## Sources

- Near-field communication overview (ISM band, inductive coupling): en.wikipedia.org/wiki/Near-field_communication
- ISO/IEC 14443 — 13.56 MHz, induction-powered PICC, rectifier, ~10 cm physical limit: en.wikipedia.org/wiki/ISO/IEC_14443 ; gototags.com/help/nfc/standards/iso-14443
- Contactless EMV transaction timing (500 ms budget) and ~4 cm working range: emvco.com EMV Contactless specifications; infishark.com/blogs/learn/contactless-payment-security
- Load modulation, 847.5 kHz subcarrier (13.56 MHz / 16), 106 kbit/s Manchester coding: mathworks.com/help/comm/ug/near-field-communication-nfc.html
- Dynamic ARQC cryptogram and why contactless cards resist cloning: cryptomathic.com/blog/reducing-payment-card-fraud-by-shifting-over-to-emv-chip-technology
