export type Posting = {
  id: number;
  source_record_id: string;

  title: string | null;
  organization: string | null;
  territory: string | null;
  staff_type: string | null;
  status: string | null;
  publication_date: string | null;
  deadline_date: string | null;
  detail_url: string | null;
  summary: string | null;

  institucio_desenvolupat: string | null;
  ambit: string | null;
  titol: string | null;
  num_places: number | null;
  tipus_personal: string | null;
  grup_titulacio: string | null;
  sistema_seleccio: string | null;
  data_finalitzacio: string | null;
  estat: string | null;
  expedient: string | null;
  url_web: string | null;

  last_changed_at: string | null;
};

export type PostingChange = {
  id: number;
  posting_id: number;
  change_type: string;
  field_name: string | null;
  old_value: string | null;
  new_value: string | null;
  detected_at: string | null;
};

export type FilterOptions = {
  organization: string[];
  territory: string[];
  staff_type: string[];
  status: string[];
  user_status: string[];
};


export type PostingKpis = {
  total_offers: number;
  open_offers: number;
  organizations_with_offers: number;
};
