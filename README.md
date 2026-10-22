# evidence-packet

**Turn a messy folder of dispute evidence into a clean packet a company, bank, regulator, or court can actually follow.**

Every consumer dispute ends up the same way: 40 screenshots named `IMG_2041.png`, three email threads, a receipt in a downloads folder, and a story nobody can reconstruct. evidence-packet fixes the packaging. Point it at the folder and it produces:

- `files/` — every piece of evidence copied in unchanged, keeping its folder structure
- `INDEX.md` — a cover index with the date, size, and SHA-256 hash of every file, sorted by date, with a section for your timeline
- `index.csv` — the same index as a spreadsheet

The hashes matter: they let a recipient verify the copies match your originals, so "you edited that screenshot" stops being an argument.

## Install

```bash
pip install -e .
```

Or just run the module directly, it is a single file with no dependencies beyond Python 3.10+.

## Use

```bash
evidence-packet build ./my-dispute-folder ./packet --title "Best Buy return dispute, order BBY01-..." --claimant "Your Name"
```

Then open `packet/INDEX.md`, write the timeline under Notes (one line per event, citing file numbers), and send the packet folder, or zip it first:

```bash
zip -r packet.zip packet
```

## Why

Built by someone who has filed complaints with two state attorneys general, a federal regulator, and more corporate executive offices than he cares to count. The packet that gets answered is the one that reads in five minutes.

## License

MIT. See [LICENSE](LICENSE).
