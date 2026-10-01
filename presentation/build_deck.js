// PRAVAAH — QUB GIFT City Datathon 2026 executive deck (7 slides + 3 appendix)
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";            // 13.33 x 7.5 in
p.author = "PRAVAAH team";
p.title = "Tourism for Inclusive Growth in Gujarat";

const W = 13.33, H = 7.5, M = 0.7;
const DARK = "0E4D45", INK = "16241F", WHITE = "FFFFFF", ICE = "BFE3DA", MUTE = "6B7280",
      LINE = "DDE5E1", CARD = "F3F7F5", TEAL = "1D9E75", BLUE = "2F7FD0", AMBER = "BA7517",
      GOLD = "D99A2B", SKILL = "0F766E";
const HEAD = "Georgia", BODY = "Calibri";
const FIG = "/Users/shreyashprajapati/Downloads/QUB_Datathon/analysis/outputs/figures/";
const RATIO = { allocation: 1.794, choropleth: 1.438, frontier: 1.313, lever: 3.102, quadrant: 1.430, robustness: 1.736 };

function img(s, name, bx, by, bw, bh) {
  const r = RATIO[name]; let w = bw, h = w / r;
  if (h > bh) { h = bh; w = h * r; }
  s.addImage({ path: FIG + "fig_" + name + ".png", x: bx + (bw - w) / 2, y: by + (bh - h) / 2, w, h });
}
function kicker(s, t, x, y, color) {
  s.addText(t.toUpperCase(), { x, y, w: 9, h: 0.3, margin: 0, fontFace: BODY, fontSize: 12.5, bold: true, color, charSpacing: 3 });
}
function dot(s, x, y, c) { s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.16, h: 0.16, fill: { color: c }, line: { type: "none" } }); }
function title(s, t, color) { s.addText(t, { x: M, y: 0.95, w: 12, h: 0.8, fontFace: HEAD, fontSize: 33, bold: true, color: color || INK }); }

// ============================================================ 1 — CHALLENGE (title)
let s = p.addSlide(); s.background = { color: DARK };
dot(s, M, 0.78, TEAL); dot(s, M + 0.22, 0.78, BLUE); dot(s, M + 0.44, 0.78, AMBER);
kicker(s, "QUB GIFT City Datathon 2026", M + 0.66, 0.78, GOLD);
s.addText([{ text: "Where should Gujarat invest", options: { breakLine: true } }, { text: "₹6,500 crore in tourism?" }],
  { x: M, y: 2.05, w: 12, h: 2.2, fontFace: HEAD, fontSize: 46, bold: true, color: WHITE, lineSpacingMultiple: 1.04 });
s.addText("An evidence-based allocation for economic growth, jobs, regional inclusion and sustainability.",
  { x: M, y: 4.35, w: 10.6, h: 0.7, fontFace: BODY, fontSize: 20, color: ICE });
[["₹6,500 cr", "budget"], ["33", "districts"], ["4", "objectives"], ["~143k", "jobs modelled"]].forEach((c, i) => {
  const x = M + i * 3.0;
  s.addText(c[0], { x, y: 5.95, w: 2.7, h: 0.55, margin: 0, fontFace: HEAD, fontSize: 26, bold: true, color: WHITE });
  s.addText(c[1], { x, y: 6.5, w: 2.7, h: 0.35, margin: 0, fontFace: BODY, fontSize: 13, color: ICE });
});
s.addNotes("[~20s] The question is simple but the stakes are high: Gujarat — India's third-largest foreign-tourist destination, in its declared Year of Tourism — must place ₹6,500 crore to maximise four goals at once: growth, jobs, regional inclusion, and sustainability. We built a transparent engine to answer exactly where. In five minutes: the opportunity, our method, the allocation, where it lands, why it's robust, and what to do Monday morning.");

// ============================================================ 2 — OPPORTUNITY GAP
s = p.addSlide(); s.background = { color: WHITE };
kicker(s, "The opportunity gap", M, 0.62, TEAL);
title(s, "Follow the gap, not the crowd");
img(s, "quadrant", 6.4, 1.85, 6.5, 5.2);
[["3", "of the top-10 footfall districts have", "zero hotels in the data — a literal blank canvas."],
 ["310,000", "visits per hotel in Banaskantha (Ambaji) —", "the state's least-literate district."],
 ["−0.25", "correlation of footfall with hotel quality —", "the busiest hubs deliver the worst experience."]].forEach((f, i) => {
  const y = 2.15 + i * 1.5;
  s.addText(f[0], { x: M, y, w: 5.4, h: 0.6, margin: 0, fontFace: HEAD, fontSize: 30, bold: true, color: TEAL });
  s.addText([{ text: f[1] + " " }, { text: f[2], options: { bold: true, color: INK } }],
    { x: M, y: y + 0.62, w: 5.4, h: 0.7, margin: 0, fontFace: BODY, fontSize: 14.5, color: MUTE });
});
s.addNotes("[~50s] Most teams will chase footfall. That's a trap. Plot demand against supply and the story flips. Three districts — Panchmahal, Kheda, Mehsana — are top-ten for footfall yet have zero hotels in the data. Banaskantha, home to the Ambaji temple, absorbs 310,000 visits per hotel — and it's the least-literate district in Gujarat. And footfall is negatively correlated with hotel quality: the busiest places give the worst experience, exactly the on-the-ground problem the brief flags. The opportunity isn't where tourists already are — it's where demand outruns supply in districts that also need development.");

// ============================================================ 3 — PRAVAAH FRAMEWORK
s = p.addSlide(); s.background = { color: WHITE };
kicker(s, "The framework", M, 0.62, BLUE);
title(s, "PRAVAAH — a transparent allocation engine");
const steps = [["1", "SCORE", "every district on four objectives"], ["2", "CONSTRAIN", "inclusion floor + carrying-capacity cap"],
               ["3", "ALLOCATE", "₹6,500 cr across districts & levers"], ["4", "STRESS-TEST", "500 weightings + frontier"]];
const bw = 2.78, gap = 0.36, y0 = 2.25, bh = 1.7;
steps.forEach((st, i) => {
  const x = M + i * (bw + gap);
  s.addShape(p.shapes.RECTANGLE, { x, y: y0, w: bw, h: bh, fill: { color: CARD }, line: { color: LINE, width: 1 } });
  s.addText(st[0], { x: x + 0.18, y: y0 + 0.16, w: 0.8, h: 0.7, margin: 0, fontFace: HEAD, fontSize: 30, bold: true, color: i < 3 ? TEAL : GOLD });
  s.addText(st[1], { x: x + 0.18, y: y0 + 0.82, w: bw - 0.36, h: 0.35, margin: 0, fontFace: BODY, fontSize: 15, bold: true, color: INK, charSpacing: 1 });
  s.addText(st[2], { x: x + 0.18, y: y0 + 1.16, w: bw - 0.36, h: 0.5, margin: 0, fontFace: BODY, fontSize: 12.5, color: MUTE });
  if (i < 3) s.addText("→", { x: x + bw - 0.02, y: y0 + 0.55, w: gap + 0.04, h: 0.5, margin: 0, align: "center", fontFace: BODY, fontSize: 20, color: MUTE });
});
[["Economic", TEAL, "yield-adjusted"], ["Employment", BLUE, "jobs / crore"], ["Inclusion", AMBER, "inverse literacy"], ["Sustainability", SKILL, "congestion + eco"]].forEach((o, i) => {
  const x = M + i * (bw + gap);
  s.addShape(p.shapes.RECTANGLE, { x, y: 4.35, w: bw, h: 0.95, fill: { color: WHITE }, line: { color: o[1], width: 1.5 } });
  dot(s, x + 0.18, 4.55, o[1]);
  s.addText(o[0], { x: x + 0.42, y: 4.47, w: bw - 0.5, h: 0.35, margin: 0, fontFace: BODY, fontSize: 14, bold: true, color: INK });
  s.addText(o[2], { x: x + 0.42, y: 4.82, w: bw - 0.5, h: 0.35, margin: 0, fontFace: BODY, fontSize: 11.5, color: MUTE });
});
s.addText("Four objectives, scored at step 1 — every parameter cited and tunable. No black box.",
  { x: M, y: 5.7, w: 12, h: 0.5, fontFace: BODY, fontSize: 15, italic: true, color: MUTE });
s.addNotes("[~40s] Our framework, PRAVAAH, is deliberately a glass box, not a black box — judges trust what they can audit. Four steps. One: score every district on four objectives — economic value (yield-adjusted, because a pilgrim day-tripper is not a premium eco-tourist), employment, inclusion, and sustainability. Two: constrain — a 30% floor for the least-literate districts and a carrying-capacity cap so we never overload a fragile eco-zone. Three: allocate the budget across districts and four investment levers. Four: stress-test against 500 weightings. Every number is sourced from WTTC, the Tourism Satellite Account, and the Census.");

// ============================================================ 4 — ALLOCATION RECOMMENDATION
s = p.addSlide(); s.background = { color: WHITE };
kicker(s, "The recommendation", M, 0.62, AMBER);
title(s, "Three moves, four levers");
[["BUILD THE WHITE SPACE", "₹2.3k cr", TEAL, "Panchmahal, Kheda, Mehsana — new capacity + connectivity where demand has no supply."],
 ["LIFT THE LEFT-BEHIND", "₹1.0k cr", BLUE, "Banaskantha & Dahod — inclusive flagship: skilling, decongest Ambaji, raise quality."],
 ["PROTECT & DISPERSE", "₹0.7k cr", AMBER, "Dwarka & Gir Somnath — cap new build in eco-zones, spread visitors, manage carrying capacity."]].forEach((mv, i) => {
  const x = M + i * 4.07, y = 2.05, cw = 3.8;
  s.addShape(p.shapes.RECTANGLE, { x, y, w: cw, h: 2.9, fill: { color: CARD }, line: { color: LINE, width: 1 } });
  s.addShape(p.shapes.RECTANGLE, { x, y, w: cw, h: 0.13, fill: { color: mv[2] }, line: { type: "none" } });
  s.addText(mv[0], { x: x + 0.28, y: y + 0.32, w: cw - 0.56, h: 0.7, margin: 0, fontFace: BODY, fontSize: 15, bold: true, color: INK, charSpacing: 0.5 });
  s.addText(mv[1], { x: x + 0.28, y: y + 1.05, w: cw - 0.56, h: 0.6, margin: 0, fontFace: HEAD, fontSize: 28, bold: true, color: mv[2] });
  s.addText(mv[3], { x: x + 0.28, y: y + 1.7, w: cw - 0.56, h: 1.1, margin: 0, fontFace: BODY, fontSize: 13.5, color: MUTE });
});
s.addText("Across four levers:", { x: M, y: 5.35, w: 2.4, h: 0.5, margin: 0, fontFace: BODY, fontSize: 14, bold: true, color: INK });
[["Build", "₹2,122 cr", TEAL], ["Upgrade", "₹1,685 cr", BLUE], ["Protect & disperse", "₹1,500 cr", AMBER], ["Skilling & sustainability", "₹1,194 cr", SKILL]].forEach((l, i) => {
  const x = 2.9 + i * 2.55;
  dot(s, x, 5.45, l[2]);
  s.addText(l[1], { x: x + 0.26, y: 5.32, w: 2.3, h: 0.35, margin: 0, fontFace: HEAD, fontSize: 16, bold: true, color: INK });
  s.addText(l[0], { x: x + 0.26, y: 5.66, w: 2.3, h: 0.3, margin: 0, fontFace: BODY, fontSize: 11.5, color: MUTE });
});
s.addNotes("[~50s] Run the engine and here is what it recommends — three moves. One — build the white space: 2.3 thousand crore into Panchmahal, Kheda and Mehsana, where demand has no supply, paired with connectivity so the rooms get used. Two — lift the left-behind: a thousand crore into Banaskantha and Dahod, the inclusion flagship, with skilling, decongestion at Ambaji and quality upgrades. Three — protect and disperse: 700 crore at Dwarka and Gir Somnath to cap new build in eco-zones and spread visitors. And it's not all hotels — across four levers, the largest slice after build is upgrading the experience, and a quarter goes to skilling and sustainability, which is where inclusion and jobs actually land.");

// ============================================================ 5 — GEOGRAPHIC ALLOCATION
s = p.addSlide(); s.background = { color: WHITE };
kicker(s, "Geographic allocation", M, 0.62, TEAL);
title(s, "₹6,500 crore, on the map");
img(s, "choropleth", M - 0.1, 1.7, 7.2, 5.4);
[["~143,000", "jobs created (98k–228k)", TEAL], ["37%", "of budget to low-literacy districts", AMBER],
 ["₹895 cr", "to Panchmahal — zero hotels today", BLUE]].forEach((k, i) => {
  const x = 7.7, y = 1.95 + i * 1.45;
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 4.9, h: 1.25, fill: { color: CARD }, line: { color: LINE, width: 1 } });
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.13, h: 1.25, fill: { color: k[2] }, line: { type: "none" } });
  s.addText(k[0], { x: x + 0.35, y: y + 0.16, w: 4.4, h: 0.65, margin: 0, fontFace: HEAD, fontSize: 32, bold: true, color: k[2] });
  s.addText(k[1], { x: x + 0.35, y: y + 0.82, w: 4.4, h: 0.35, margin: 0, fontFace: BODY, fontSize: 14, color: INK });
});
s.addText("85% to evidenced districts · 15% ring-fenced for data-blind districts.",
  { x: 7.7, y: 6.35, w: 4.9, h: 0.4, margin: 0, fontFace: BODY, fontSize: 12.5, italic: true, color: MUTE });
s.addNotes("[~55s] Geographically, here is where it lands. The budget flows east and into the under-served interior, not just the big cities. Panchmahal leads at 895 crore — a UNESCO World Heritage site, Champaner-Pavagadh, with zero formal hotels today. Kheda and Mehsana follow on the same logic. Ahmedabad still gets money, but for quality upgrades, not new build. The headline: about 143,000 jobs — a sourced range, not a single hopeful number — and 37% of every rupee reaching the least-literate districts, which the model produced on merit before the equity floor even bound. And we're honest about the data: 85% goes where we have footfall evidence; 15% is ring-fenced to explore the districts we're blind on.");

// ============================================================ 6 — ROBUSTNESS
s = p.addSlide(); s.background = { color: WHITE };
kicker(s, "Robustness", M, 0.62, BLUE);
title(s, "The recommendation holds under any weighting");
img(s, "robustness", M - 0.1, 1.75, 8.0, 5.3);
[["100%", "Panchmahal stays top-5 across 500 random weightings", TEAL], ["5.1%", "allocation variation within plausible policy bands", BLUE]].forEach((k, i) => {
  const x = 8.4, y = 2.3 + i * 1.7;
  s.addText(k[0], { x, y, w: 4.4, h: 0.7, margin: 0, fontFace: HEAD, fontSize: 40, bold: true, color: k[2] });
  s.addText(k[1], { x, y: y + 0.75, w: 4.3, h: 0.8, margin: 0, fontFace: BODY, fontSize: 15, color: INK });
});
s.addText("Weight-invariant — not cherry-picked.", { x: 8.4, y: 6.1, w: 4.3, h: 0.4, margin: 0, fontFace: BODY, fontSize: 14, italic: true, color: MUTE });
s.addNotes("[~40s] A judge's first question for any weighted index is: did you tune the weights to get the answer you wanted? We pre-empted it. We re-ran the allocation under 500 random weightings spanning the entire policy space. Panchmahal lands in the top five in 100% of them; Kheda and Kachchh, over 80%. Within realistic policy bands the whole allocation moves just 5%. The teal districts are weight-invariant — the core recommendation is a property of the data, not of our assumptions. The grey districts swing interpretably: Ahmedabad rises if you prioritise growth, Banaskantha if you prioritise inclusion.");

// ============================================================ 7 — IMPACT & ROADMAP (conclusion)
s = p.addSlide(); s.background = { color: DARK };
dot(s, M, 0.78, TEAL); dot(s, M + 0.22, 0.78, BLUE); dot(s, M + 0.44, 0.78, AMBER);
kicker(s, "From budget to impact", M + 0.66, 0.78, GOLD);
s.addText("A phased plan for inclusive growth", { x: M, y: 1.15, w: 12, h: 0.8, fontFace: HEAD, fontSize: 33, bold: true, color: WHITE });
[["NOW — 18 mo", "Quick wins", "Quality upgrades in Ahmedabad & Surat; decongest Ambaji & Dwarka."],
 ["18 — 48 mo", "Build the white space", "Capacity + connectivity in Panchmahal, Kheda, Mehsana."],
 ["4 — 7 yr", "Scale & explore", "Activate data-blind districts; monitor carrying capacity."]].forEach((h2, i) => {
  const x = M + i * 4.07, y = 2.25, cw = 3.8;
  s.addText(h2[0], { x, y, w: cw, h: 0.35, margin: 0, fontFace: BODY, fontSize: 13, bold: true, color: GOLD, charSpacing: 1 });
  s.addText(h2[1], { x, y: y + 0.38, w: cw, h: 0.5, margin: 0, fontFace: HEAD, fontSize: 21, bold: true, color: WHITE });
  s.addText(h2[2], { x, y: y + 0.95, w: cw, h: 1.0, margin: 0, fontFace: BODY, fontSize: 14, color: ICE });
});
[["~143k", "jobs created"], ["37%", "to low-literacy districts"], ["100%", "eco-capped, weight-tested"]].forEach((k, i) => {
  const x = M + i * 4.07;
  s.addText(k[0], { x, y: 5.35, w: 3.8, h: 0.7, margin: 0, fontFace: HEAD, fontSize: 34, bold: true, color: "5DCAA5" });
  s.addText(k[1], { x, y: 6.05, w: 3.8, h: 0.4, margin: 0, fontFace: BODY, fontSize: 14, color: ICE });
});
s.addText("Transform data into decisions that create meaningful impact.",
  { x: M, y: 6.7, w: 12, h: 0.5, margin: 0, fontFace: HEAD, fontSize: 16, italic: true, color: ICE });
s.addNotes("[~45s] Finally, delivery. This is phased, not a one-shot cheque. Now to eighteen months: quick wins — upgrade quality in the big hubs and decongest the crowded temples. Eighteen to forty-eight months: build the white space with capacity and the roads and rail to reach it. Years four to seven: activate the data-blind districts and monitor carrying capacity so growth stays sustainable. The payoff: roughly 143,000 jobs, 37% of the budget reaching the least-literate districts, and every rupee eco-capped and weight-tested. That is how Gujarat turns ₹6,500 crore — and its data — into inclusive, sustainable growth. Thank you.");

// ============================================================ A1 — EFFICIENT FRONTIER
s = p.addSlide(); s.background = { color: WHITE };
kicker(s, "Appendix A1", M, 0.62, MUTE);
title(s, "Efficient frontier & model assumptions");
img(s, "frontier", M - 0.1, 1.8, 6.4, 5.2);
s.addText([{ text: "Why balanced?  ", options: { bold: true, color: INK } },
  { text: "The frontier maps the economic–inclusion trade-off; balanced (red star) is a deliberate, defensible compromise — not a corner solution.", options: { color: MUTE } }],
  { x: 7.0, y: 1.9, w: 5.6, h: 1.1, fontFace: BODY, fontSize: 13.5 });
[
  "Employment: 22 jobs / ₹cr central, 15–35 range (WTTC India 2024: 46.5M jobs / ₹21tn).",
  "Yield: relative spend tiers — pilgrimage ₹800 → eco-premium ₹6,000 (the footfall ≠ value fix).",
  "Inclusion: 2011 Census literacy (relative ranking); 30% floor to bottom-quartile districts.",
  "Sustainability: congestion (visits / hotel) + Gujarat's six notified Eco-Sensitive Zones.",
  "Budget split: 85% evidenced (footfall) / 15% exploration (22 data-blind districts).",
].forEach((t, i) => {
  s.addText(t, { x: 7.0, y: 3.15 + i * 0.72, w: 5.7, h: 0.66, margin: 0, fontFace: BODY, fontSize: 12.5, color: INK, bullet: { code: "2022", indent: 14 } });
});
s.addNotes("Appendix — not spoken. The efficient frontier justifies the balanced stance; the five parameters are the model's external assumptions, each cited on the next slide.");

// ============================================================ A2 — REFERENCES & DATA SOURCES
s = p.addSlide(); s.background = { color: WHITE };
kicker(s, "Appendix A2", M, 0.62, MUTE);
title(s, "References & data sources");
function srcGroup(x, y, head, items, col) {
  s.addText(head, { x, y, w: 5.7, h: 0.35, margin: 0, fontFace: BODY, fontSize: 13, bold: true, color: col, charSpacing: 1 });
  items.forEach((it, i) => s.addText(it, { x, y: y + 0.42 + i * 0.5, w: 5.7, h: 0.46, margin: 0, fontFace: BODY, fontSize: 13, color: INK, bullet: { code: "2022", indent: 14 } }));
}
srcGroup(M, 1.85, "Competition datasets — QUB GIFT City Datathon 2026", [
  "Hotel & accommodation dataset",
  "Gujarat tourism statistics (orig. Commissioner of Tourism, Gujarat)",
  "Gujarat census dataset",
], TEAL);
srcGroup(M, 4.25, "Geospatial", [
  "Gujarat district GeoJSON — india-maps-data (Survey of India base)",
], TEAL);
srcGroup(6.95, 1.85, "Government & institutional sources", [
  "Ministry of Tourism, Govt. of India — India Tourism Statistics",
  "World Travel & Tourism Council (WTTC) — Economic Impact Report 2024",
  "Tourism Satellite Account (TSA) of India",
  "Census of India 2011",
  "Eco-Sensitive Zone notifications — MoEFCC / Gujarat Forest Dept.",
], BLUE);
s.addText("All sources listed were directly used in the analysis. No other datasets were incorporated.",
  { x: M, y: 6.75, w: 11.9, h: 0.4, margin: 0, fontFace: BODY, fontSize: 12, italic: true, color: MUTE });
s.addNotes("Appendix — not spoken. Only sources actually used in the PRAVAAH analysis are listed.");

// ============================================================ A3 — TOOLS & TECHNOLOGIES
s = p.addSlide(); s.background = { color: WHITE };
kicker(s, "Appendix A3", M, 0.62, MUTE);
title(s, "Tools & technologies");
const cats = [
  ["Analytics & modelling", TEAL, "Python · Pandas · NumPy · openpyxl"],
  ["Visualisation", BLUE, "Matplotlib"],
  ["Geospatial analysis", AMBER, "GeoPandas · Shapely · GeoJSON"],
  ["Presentation development", SKILL, "PptxGenJS · python-pptx"],
  ["Robustness testing", "7A4FB5", "Monte Carlo simulation (Dirichlet weight sampling)"],
  ["Framework", GOLD, "PRAVAAH allocation framework"],
];
cats.forEach((c, i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const x = M + col * 6.05, y = 1.9 + row * 1.25, cw = 5.75;
  s.addShape(p.shapes.RECTANGLE, { x, y, w: cw, h: 1.05, fill: { color: CARD }, line: { color: LINE, width: 1 } });
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.13, h: 1.05, fill: { color: c[1] }, line: { type: "none" } });
  s.addText(c[0], { x: x + 0.35, y: y + 0.16, w: cw - 0.6, h: 0.35, margin: 0, fontFace: BODY, fontSize: 14, bold: true, color: INK, charSpacing: 0.5 });
  s.addText(c[2], { x: x + 0.35, y: y + 0.55, w: cw - 0.6, h: 0.4, margin: 0, fontFace: BODY, fontSize: 13.5, color: MUTE });
});
s.addText([
  { text: "Project resources & validation.  ", options: { bold: true, color: INK } },
  { text: "Public government and institutional reports (Ministry of Tourism, WTTC, India TSA, Census 2011) were used to harden the model's assumptions. Literature-informed multipliers — tourism jobs-per-crore and spend-per-visit by segment — were sensitivity-tested across documented ranges, not fixed at single values. Generative AI tools were used to accelerate coding and presentation development; all analyses, assumptions, validation, and recommendations were reviewed and verified by the team.", options: { color: MUTE } },
], { x: M, y: 5.55, w: 11.9, h: 1.5, fontFace: BODY, fontSize: 12.5, lineSpacingMultiple: 1.05 });
s.addNotes("Appendix — not spoken. Only tools actually used are listed (visuals were built in Matplotlib + GeoPandas; the deck in PptxGenJS). AI-disclosure line included — confirm it aligns with QUB submission rules.");

p.writeFile({ fileName: "/Users/shreyashprajapati/Downloads/QUB_Datathon/presentation/PRAVAAH_Gujarat_Tourism.pptx" })
  .then(f => console.log("WROTE", f));
