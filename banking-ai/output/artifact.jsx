/**
 * Banking AI Intelligence — browsable artifact component.
 * Filters by lane, institution, and minimum relevance score.
 *
 * Props:
 *   report  - the final report JSON produced by synthesizer.py
 *   intent  - the research intent string
 *   date    - ISO date string
 */

const LANES = ["All", "Content", "Competitor", "Technical"];
const INSTITUTIONS = ["All", "JPMorgan", "Capital One", "Goldman Sachs", "Bank of America", "Wells Fargo"];
const SCORES = [1, 5, 7, 8, 9];

const LANE_COLORS = {
  content:    { bg: "#dbeafe", text: "#1e40af" },
  competitor: { bg: "#fce7f3", text: "#9d174d" },
  technical:  { bg: "#d1fae5", text: "#065f46" },
};

const SCORE_COLOR = (s) => {
  if (s >= 9) return "#15803d";
  if (s >= 7) return "#b45309";
  return "#6b7280";
};

function Tag({ label, bg, text }) {
  return (
    <span style={{
      background: bg, color: text,
      fontSize: 11, fontWeight: 600, padding: "2px 7px",
      borderRadius: 99, display: "inline-block",
    }}>
      {label}
    </span>
  );
}

function ScoreBadge({ score }) {
  if (!score) return null;
  return (
    <span style={{
      color: SCORE_COLOR(score), fontWeight: 700, fontSize: 13,
      marginLeft: 6, whiteSpace: "nowrap",
    }}>
      {score}/10
    </span>
  );
}

function Card({ item }) {
  const colors = LANE_COLORS[item.category] || { bg: "#f3f4f6", text: "#374151" };
  return (
    <div style={{
      border: "1px solid #e5e7eb", borderRadius: 10, padding: "16px 18px",
      marginBottom: 12, background: "#fff",
    }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
        <a href={item.url} target="_blank" rel="noreferrer"
          style={{ fontWeight: 600, fontSize: 15, color: "#1d4ed8", textDecoration: "none", lineHeight: 1.3 }}>
          {item.title}
        </a>
        <ScoreBadge score={item.relevance_score} />
      </div>
      <div style={{ marginTop: 6, display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }}>
        <span style={{ fontSize: 12, color: "#6b7280" }}>{item.source}</span>
        <Tag label={item.category} bg={colors.bg} text={colors.text} />
        {item.institution && (
          <Tag label={item.institution} bg="#f3f4f6" text="#374151" />
        )}
      </div>
      <p style={{ marginTop: 8, fontSize: 14, color: "#374151", lineHeight: 1.55 }}>
        {item.summary}
      </p>
      <p style={{ marginTop: 6, fontSize: 13, color: "#6b7280", fontStyle: "italic", lineHeight: 1.45 }}>
        {item.why_it_matters}
      </p>
    </div>
  );
}

function FilterBar({ lane, setLane, institution, setInstitution, minScore, setMinScore }) {
  const btnStyle = (active) => ({
    padding: "6px 14px", borderRadius: 99, border: "none", cursor: "pointer",
    fontWeight: 600, fontSize: 13,
    background: active ? "#1d4ed8" : "#f3f4f6",
    color: active ? "#fff" : "#374151",
  });
  return (
    <div style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "center", marginBottom: 20 }}>
      <div style={{ display: "flex", gap: 6 }}>
        {LANES.map((l) => (
          <button key={l} style={btnStyle(lane === l)} onClick={() => { setLane(l); setInstitution("All"); }}>
            {l}
          </button>
        ))}
      </div>

      {(lane === "All" || lane === "Competitor") && (
        <select value={institution} onChange={(e) => setInstitution(e.target.value)}
          style={{ padding: "6px 10px", borderRadius: 8, border: "1px solid #d1d5db", fontSize: 13, cursor: "pointer" }}>
          {INSTITUTIONS.map((i) => <option key={i}>{i}</option>)}
        </select>
      )}

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginLeft: "auto" }}>
        <span style={{ fontSize: 13, color: "#6b7280" }}>Min score:</span>
        <div style={{ display: "flex", gap: 4 }}>
          {SCORES.map((s) => (
            <button key={s} style={btnStyle(minScore === s)} onClick={() => setMinScore(s)}>
              {s === 1 ? "Any" : `${s}+`}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function flattenReport(report) {
  const items = [];
  const seen = new Set();

  const add = (item) => {
    if (!item || !item.url || seen.has(item.url)) return;
    seen.add(item.url);
    items.push(item);
  };

  (report.top_picks || []).forEach(add);

  Object.values(report.competitor_moves || {}).forEach((arr) => arr.forEach(add));

  const cwyt = report.content_worth_your_time || {};
  [...(cwyt.articles || []), ...(cwyt.videos || [])].forEach(add);

  const radar = report.technical_radar || {};
  [
    ...(radar.models_and_capabilities || []),
    ...(radar.frameworks_and_tooling || []),
    ...(radar.research_papers || []),
  ].forEach(add);

  return items;
}

export default function App({ report, intent, date }) {
  const [lane, setLane] = React.useState("All");
  const [institution, setInstitution] = React.useState("All");
  const [minScore, setMinScore] = React.useState(1);

  const allItems = React.useMemo(() => flattenReport(report), [report]);

  const filtered = allItems.filter((item) => {
    if (lane !== "All" && item.category !== lane.toLowerCase()) return false;
    if (institution !== "All" && item.institution !== institution) return false;
    if (minScore > 1 && (item.relevance_score || 0) < minScore) return false;
    return true;
  });

  const topPicks = (report.top_picks || []).filter(
    (i) => lane === "All" && institution === "All" && minScore <= (i.relevance_score || 0)
  );

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", maxWidth: 780, margin: "0 auto", padding: "32px 24px" }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>Banking AI Intelligence</h1>
        <p style={{ fontSize: 13, color: "#6b7280", marginTop: 4 }}>
          {date} &nbsp;·&nbsp; {intent}
        </p>
      </div>

      <FilterBar
        lane={lane} setLane={setLane}
        institution={institution} setInstitution={setInstitution}
        minScore={minScore} setMinScore={setMinScore}
      />

      {topPicks.length > 0 && (
        <div style={{ marginBottom: 28 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, color: "#111827", marginBottom: 12 }}>
            What Caught My Attention
          </h2>
          {topPicks.map((item, i) => <Card key={i} item={item} />)}
        </div>
      )}

      <div>
        <h2 style={{ fontSize: 16, fontWeight: 700, color: "#111827", marginBottom: 12 }}>
          {filtered.length} item{filtered.length !== 1 ? "s" : ""}
          {lane !== "All" || institution !== "All" || minScore > 1 ? " (filtered)" : ""}
        </h2>
        {filtered.length === 0 ? (
          <p style={{ color: "#6b7280" }}>No items match the current filters.</p>
        ) : (
          filtered.map((item, i) => <Card key={i} item={item} />)
        )}
      </div>
    </div>
  );
}
