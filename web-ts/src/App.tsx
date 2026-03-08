import { useEffect, useMemo, useState } from "react";
import { fetchOptions, fetchPostingDetail, fetchPostings, fetchPostingsKpis } from "./api";
import type { FilterOptions, Posting, PostingChange, PostingKpis } from "./types";

function fmt(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}

export default function App() {
  const [options, setOptions] = useState<FilterOptions>({ organization: [], territory: [], staff_type: [], status: [], user_status: [] });
  const [items, setItems] = useState<Posting[]>([]);
  const [total, setTotal] = useState(0);
  const [kpis, setKpis] = useState<PostingKpis>({ total_offers: 0, open_offers: 0, organizations_with_offers: 0 });
  const [selected, setSelected] = useState<Posting | null>(null);
  const [changes, setChanges] = useState<PostingChange[]>([]);

  const [q, setQ] = useState("");
  const [organization, setOrganization] = useState("");
  const [territory, setTerritory] = useState("");
  const [staffType, setStaffType] = useState("");
  const [status, setStatus] = useState("");
  const [minPublicationDate, setMinPublicationDate] = useState("2026-01-01");

  useEffect(() => {
    void fetchOptions().then(setOptions);
  }, []);

  const filterParams = useMemo(() => {
    const p = new URLSearchParams();
    if (q) p.set("q", q);
    if (organization) p.set("organization", organization);
    if (territory) p.set("territory", territory);
    if (staffType) p.set("staff_type", staffType);
    if (status) p.set("status", status);
    if (minPublicationDate) p.set("min_publication_date", minPublicationDate);
    return p;
  }, [q, organization, territory, staffType, status, minPublicationDate]);

  const params = useMemo(() => {
    const p = new URLSearchParams(filterParams);
    p.set("limit", "20");
    return p;
  }, [filterParams]);

  useEffect(() => {
    void fetchPostings(params).then((res) => {
      setItems(res.items);
      setTotal(res.total);
    });
  }, [params]);

  useEffect(() => {
    void fetchPostingsKpis(filterParams).then(setKpis);
  }, [filterParams]);

  async function openDetail(item: Posting) {
    setSelected(item);
    const detail = await fetchPostingDetail(item.id);
    setChanges(detail.changes);
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <h1>FeinaPublica.cat</h1>
        <p>El teu portal d'ocupació pública de referencia</p>
      </header>

      <section className="kpi-grid">
        <article className="card kpi-card">
          <div className="kpi-label">Número total d'ofertes</div>
          <div className="kpi-value">{kpis.total_offers}</div>
        </article>
        <article className="card kpi-card">
          <div className="kpi-label">Ofertes obertes</div>
          <div className="kpi-value">{kpis.open_offers}</div>
        </article>
        <article className="card kpi-card">
          <div className="kpi-label">Organismes amb ofertes</div>
          <div className="kpi-value">{kpis.organizations_with_offers}</div>
        </article>
      </section>

      <section className="filters card">
        <input placeholder="Text lliure" value={q} onChange={(e) => setQ(e.target.value)} />
        <select value={organization} onChange={(e) => setOrganization(e.target.value)}>
          <option value="">Ens convocant</option>
          {options.organization.map((x) => <option key={x} value={x}>{x}</option>)}
        </select>
        <select value={territory} onChange={(e) => setTerritory(e.target.value)}>
          <option value="">Territori</option>
          {options.territory.map((x) => <option key={x} value={x}>{x}</option>)}
        </select>
        <select value={staffType} onChange={(e) => setStaffType(e.target.value)}>
          <option value="">Tipus personal</option>
          {options.staff_type.map((x) => <option key={x} value={x}>{x}</option>)}
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">Estat</option>
          {options.status.map((x) => <option key={x} value={x}>{x}</option>)}
        </select>
        <input type="date" value={minPublicationDate} onChange={(e) => setMinPublicationDate(e.target.value)} />
      </section>

      <main className="layout">
        <section className="card table-card">
          <div className="section-title">Ofertes ({total})</div>
          <table>
            <thead>
              <tr>
                <th>Identificador</th>
                <th>Identificador del registre d'origen</th>
                <th>Títol de la convocatòria</th>
                <th>Organisme o entitat convocant</th>
                <th>Àmbit territorial</th>
                <th>Tipus de personal</th>
                <th>Estat de la convocatòria</th>
                <th>Data de publicació</th>
                <th>Data límit de presentació</th>
                <th>Nombre de places convocades</th>
                <th>Número d'expedient</th>
                <th>Enllaç al detall de la convocatòria</th>
                <th>Enllaç a la web oficial</th>
                <th>Data de l'última actualització</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} onClick={() => void openDetail(item)}>
                  <td>{item.id}</td>
                  <td>{item.source_record_id}</td>
                  <td>{fmt(item.title)}</td>
                  <td>{fmt(item.organization)}</td>
                  <td>{fmt(item.territory)}</td>
                  <td>{fmt(item.staff_type)}</td>
                  <td>{fmt(item.status)}</td>
                  <td>{fmt(item.publication_date)}</td>
                  <td>{fmt(item.deadline_date)}</td>
                  <td>{fmt(item.num_places)}</td>
                  <td>{fmt(item.expedient)}</td>
                  <td>{item.detail_url ? <a href={item.detail_url} target="_blank" rel="noreferrer">CIDO</a> : "-"}</td>
                  <td>{item.url_web ? <a href={item.url_web} target="_blank" rel="noreferrer">Web</a> : "-"}</td>
                  <td>{fmt(item.last_changed_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <aside className="stack">
          <section className="card">
            <div className="section-title">Detall</div>
            {selected ? (
              <>
                <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>
{JSON.stringify(
  {
    id: selected.id,
    source_record_id: selected.source_record_id,
    title: selected.title,
    organization: selected.organization,
    territory: selected.territory,
    staff_type: selected.staff_type,
    status: selected.status,
    publication_date: selected.publication_date,
    deadline_date: selected.deadline_date,
    detail_url: selected.detail_url,
    summary: selected.summary,
    institucio_desenvolupat: selected.institucio_desenvolupat,
    ambit: selected.ambit,
    titol: selected.titol,
    num_places: selected.num_places,
    tipus_personal: selected.tipus_personal,
    grup_titulacio: selected.grup_titulacio,
    sistema_seleccio: selected.sistema_seleccio,
    data_finalitzacio: selected.data_finalitzacio,
    estat: selected.estat,
    expedient: selected.expedient,
    url_web: selected.url_web,
    last_changed_at: selected.last_changed_at,
  },
  null,
  2
)}
                </pre>
                {selected.detail_url ? <a href={selected.detail_url} target="_blank" rel="noreferrer">Anar a fitxa CIDO</a> : null}
                {" "}
                {selected.url_web ? <a href={selected.url_web} target="_blank" rel="noreferrer">Anar a web convocatòria</a> : null}
                <hr />
                <ul className="changes">
                  {changes.map((c) => (
                    <li key={c.id}>{c.change_type} {c.field_name ? `(${c.field_name})` : ""}</li>
                  ))}
                </ul>
              </>
            ) : (
              <p>Selecciona una oferta de la taula.</p>
            )}
          </section>
        </aside>
      </main>
    </div>
  );
}


