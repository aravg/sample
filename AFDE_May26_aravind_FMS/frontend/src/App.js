const { useState, useEffect, useCallback } = React;

// ─── API Service ─────────────────────────────────────────────────────────────
const API_BASE = "http://127.0.0.1:8000";

const api = {
  getFeedback: () => axios.get(`${API_BASE}/feedback`),
  getFeedbackById: (id) => axios.get(`${API_BASE}/feedback/${id}`),
  createFeedback: (data) => axios.post(`${API_BASE}/feedback`, data),
  updateFeedback: (id, data) => axios.put(`${API_BASE}/feedback/${id}`, data),
  deleteFeedback: (id) => axios.delete(`${API_BASE}/feedback/${id}`),
  search: (params) => axios.get(`${API_BASE}/search`, { params }),
  getStats: () => axios.get(`${API_BASE}/feedback/stats`),
};

// ─── Utilities ────────────────────────────────────────────────────────────────
const RATING_LABELS = { 1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent" };

function RatingBadge({ rating }) {
  return (
    <span className={`rating-badge rating-${rating}`}>
      {"★".repeat(rating)} {RATING_LABELS[rating]}
    </span>
  );
}

function StarSelector({ value, onChange }) {
  const [hovered, setHovered] = useState(0);
  return (
    <div className="star-rating">
      {[1, 2, 3, 4, 5].map((s) => (
        <span
          key={s}
          className={`star ${s <= (hovered || value) ? "filled" : "empty"}`}
          onMouseEnter={() => setHovered(s)}
          onMouseLeave={() => setHovered(0)}
          onClick={() => onChange(s)}
        >★</span>
      ))}
      {value > 0 && (
        <span style={{ marginLeft: 8, fontSize: "0.85rem", color: "var(--text-muted)", alignSelf: "center" }}>
          {RATING_LABELS[value]}
        </span>
      )}
    </div>
  );
}

function Alert({ type, message, onClose }) {
  if (!message) return null;
  return (
    <div className={`alert alert-${type}`}>
      <span>{type === "success" ? "✓" : "✕"}</span>
      <span>{message}</span>
      {onClose && <button onClick={onClose} style={{ marginLeft: "auto", background: "none", border: "none", cursor: "pointer", fontWeight: 700 }}>×</button>}
    </div>
  );
}

function Spinner() { return <div className="spinner"></div>; }

// ─── Feedback Form (shared by create & edit) ──────────────────────────────────
function FeedbackForm({ initial, onSubmit, onCancel, loading }) {
  const [form, setForm] = useState(
    initial || { participant_name: "", program_name: "", rating: 0, comments: "" }
  );
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (initial) setForm(initial);
  }, [initial]);

  const validate = () => {
    const errs = {};
    if (!form.participant_name.trim()) errs.participant_name = "Participant name is required";
    if (!form.program_name.trim()) errs.program_name = "Program/Event name is required";
    if (!form.rating || form.rating < 1) errs.rating = "Please select a rating";
    return errs;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
    if (errors[name]) setErrors((e) => ({ ...e, [name]: undefined }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label className="form-label">Participant Name <span className="required">*</span></label>
        <input
          name="participant_name"
          className={`form-control ${errors.participant_name ? "error" : ""}`}
          placeholder="Enter participant name"
          value={form.participant_name}
          onChange={handleChange}
        />
        {errors.participant_name && <p className="form-error">{errors.participant_name}</p>}
      </div>

      <div className="form-group">
        <label className="form-label">Training / Event / Product <span className="required">*</span></label>
        <input
          name="program_name"
          className={`form-control ${errors.program_name ? "error" : ""}`}
          placeholder="e.g. React Workshop, Q1 Training"
          value={form.program_name}
          onChange={handleChange}
        />
        {errors.program_name && <p className="form-error">{errors.program_name}</p>}
      </div>

      <div className="form-group">
        <label className="form-label">Rating <span className="required">*</span></label>
        <StarSelector value={form.rating} onChange={(v) => { setForm((f) => ({ ...f, rating: v })); setErrors((e) => ({ ...e, rating: undefined })); }} />
        {errors.rating && <p className="form-error">{errors.rating}</p>}
      </div>

      <div className="form-group">
        <label className="form-label">Comments</label>
        <textarea
          name="comments"
          className="form-control"
          placeholder="Share your experience..."
          value={form.comments}
          onChange={handleChange}
        />
      </div>

      <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
        {onCancel && <button type="button" className="btn btn-ghost" onClick={onCancel}>Cancel</button>}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? <><Spinner /> Saving...</> : "Save Feedback"}
        </button>
      </div>
    </form>
  );
}

// ─── Dashboard ────────────────────────────────────────────────────────────────
function Dashboard({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getStats()
      .then((r) => setStats(r.data))
      .catch(() => setError("Could not load stats. Is the backend running?"));
  }, []);

  const formatDate = (d) => new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Overview of all feedback collected in the system</p>
      </div>

      {error && <Alert type="error" message={error} />}

      {!stats ? (
        <div className="loading-center"><Spinner /></div>
      ) : (
        <>
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-label">Total Feedback</div>
              <div className="stat-value">{stats.total_count}</div>
              <div className="stat-sub">All time submissions</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Average Rating</div>
              <div className="stat-value">{stats.average_rating > 0 ? stats.average_rating.toFixed(1) : "—"}</div>
              <div className="stat-sub">Out of 5.0</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Excellent Ratings</div>
              <div className="stat-value" style={{ color: "var(--success)" }}>
                {stats.recent_feedback.filter((f) => f.rating === 5).length}
              </div>
              <div className="stat-sub">Recent 5-star entries</div>
            </div>
          </div>

          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 600 }}>Recent Submissions</h3>
              <button className="btn btn-primary btn-sm" onClick={() => onNavigate("list")}>View All →</button>
            </div>

            {stats.recent_feedback.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📭</div>
                <p>No feedback yet. <span style={{ color: "var(--primary)", cursor: "pointer" }} onClick={() => onNavigate("submit")}>Submit the first one →</span></p>
              </div>
            ) : (
              <table className="feedback-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Participant</th>
                    <th>Program / Event</th>
                    <th>Rating</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recent_feedback.map((f) => (
                    <tr key={f.feedback_id}>
                      <td style={{ color: "var(--text-muted)" }}>#{f.feedback_id}</td>
                      <td style={{ fontWeight: 500 }}>{f.participant_name}</td>
                      <td><span className="tag">{f.program_name}</span></td>
                      <td><RatingBadge rating={f.rating} /></td>
                      <td style={{ color: "var(--text-muted)", fontSize: "0.82rem" }}>{formatDate(f.submitted_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// ─── Submit Feedback Page ─────────────────────────────────────────────────────
function SubmitFeedback() {
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);
  const [key, setKey] = useState(0);

  const handleSubmit = async (form) => {
    setLoading(true);
    setAlert(null);
    try {
      await api.createFeedback(form);
      setAlert({ type: "success", message: "Feedback submitted successfully!" });
      setKey((k) => k + 1);
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to submit feedback. Check backend connection.";
      setAlert({ type: "error", message: typeof msg === "string" ? msg : JSON.stringify(msg) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Submit Feedback</h2>
        <p>Fill in the form below to share your experience</p>
      </div>
      <div className="card" style={{ maxWidth: 600 }}>
        {alert && <Alert type={alert.type} message={alert.message} onClose={() => setAlert(null)} />}
        <FeedbackForm key={key} onSubmit={handleSubmit} loading={loading} />
      </div>
    </div>
  );
}

// ─── Edit Modal ───────────────────────────────────────────────────────────────
function EditModal({ feedback, onClose, onSaved }) {
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);

  const handleSubmit = async (form) => {
    setLoading(true);
    try {
      await api.updateFeedback(feedback.feedback_id, form);
      onSaved();
    } catch (err) {
      setAlert({ type: "error", message: err.response?.data?.detail || "Update failed" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h3>Edit Feedback #{feedback.feedback_id}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {alert && <Alert type={alert.type} message={alert.message} />}
          <FeedbackForm
            initial={{
              participant_name: feedback.participant_name,
              program_name: feedback.program_name,
              rating: feedback.rating,
              comments: feedback.comments || "",
            }}
            onSubmit={handleSubmit}
            onCancel={onClose}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}

// ─── Detail Modal ─────────────────────────────────────────────────────────────
function DetailModal({ feedback, onClose, onEdit }) {
  const formatDate = (d) =>
    new Date(d).toLocaleString("en-IN", { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" });

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h3>Feedback Details</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
            <tbody>
              {[
                ["ID", `#${feedback.feedback_id}`],
                ["Participant", feedback.participant_name],
                ["Program / Event", feedback.program_name],
                ["Rating", <RatingBadge rating={feedback.rating} />],
                ["Comments", feedback.comments || <span style={{ color: "var(--text-muted)" }}>—</span>],
                ["Submitted At", formatDate(feedback.submitted_at)],
              ].map(([label, value]) => (
                <tr key={label}>
                  <td style={{ padding: "9px 0", color: "var(--text-muted)", width: 130, verticalAlign: "top", fontWeight: 500 }}>{label}</td>
                  <td style={{ padding: "9px 0" }}>{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>Close</button>
          <button className="btn btn-primary" onClick={() => { onClose(); onEdit(feedback); }}>Edit</button>
        </div>
      </div>
    </div>
  );
}

// ─── Feedback List Page ───────────────────────────────────────────────────────
function FeedbackList() {
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);

  const [keyword, setKeyword] = useState("");
  const [ratingFilter, setRatingFilter] = useState("");
  const [programFilter, setProgramFilter] = useState("");
  const [searching, setSearching] = useState(false);

  const [viewItem, setViewItem] = useState(null);
  const [editItem, setEditItem] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const loadAll = useCallback(() => {
    setLoading(true);
    api.getFeedback()
      .then((r) => { setFeedbacks(r.data); setLoading(false); })
      .catch(() => { setAlert({ type: "error", message: "Failed to load feedback" }); setLoading(false); });
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  const handleSearch = async () => {
    setSearching(true);
    try {
      const params = {};
      if (keyword.trim()) params.keyword = keyword.trim();
      if (ratingFilter) params.rating = ratingFilter;
      if (programFilter.trim()) params.program_name = programFilter.trim();
      const r = await api.search(params);
      setFeedbacks(r.data);
    } catch { setAlert({ type: "error", message: "Search failed" }); }
    finally { setSearching(false); }
  };

  const handleReset = () => {
    setKeyword(""); setRatingFilter(""); setProgramFilter("");
    loadAll();
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.deleteFeedback(deleteId);
      setAlert({ type: "success", message: "Feedback deleted successfully" });
      setDeleteId(null);
      loadAll();
    } catch { setAlert({ type: "error", message: "Delete failed" }); }
    finally { setDeleting(false); }
  };

  const formatDate = (d) => new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });

  return (
    <div>
      <div className="page-header">
        <h2>All Feedback</h2>
        <p>Search, filter, and manage all submitted feedback</p>
      </div>

      {alert && <Alert type={alert.type} message={alert.message} onClose={() => setAlert(null)} />}

      {/* Search & Filter */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="search-bar">
          <div className="form-group" style={{ flex: 2, minWidth: 200 }}>
            <label className="form-label">Search</label>
            <div className="search-input-wrap">
              <span className="search-icon">🔍</span>
              <input
                className="form-control"
                placeholder="Name, program, or keyword…"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
            </div>
          </div>
          <div className="form-group" style={{ minWidth: 140 }}>
            <label className="form-label">Rating</label>
            <select className="form-control" value={ratingFilter} onChange={(e) => setRatingFilter(e.target.value)}>
              <option value="">All ratings</option>
              {[1,2,3,4,5].map((r) => <option key={r} value={r}>{r} – {RATING_LABELS[r]}</option>)}
            </select>
          </div>
          <div className="form-group" style={{ flex: 1, minWidth: 160 }}>
            <label className="form-label">Program / Event</label>
            <input
              className="form-control"
              placeholder="Filter by program…"
              value={programFilter}
              onChange={(e) => setProgramFilter(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
          </div>
          <div style={{ display: "flex", gap: 8, alignSelf: "flex-end" }}>
            <button className="btn btn-primary" onClick={handleSearch} disabled={searching}>
              {searching ? <Spinner /> : "Search"}
            </button>
            <button className="btn btn-ghost" onClick={handleReset}>Reset</button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>{feedbacks.length} record(s)</span>
        </div>

        {loading ? (
          <div className="loading-center"><Spinner /></div>
        ) : feedbacks.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>No feedback found matching your criteria.</p>
          </div>
        ) : (
          <table className="feedback-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Participant</th>
                <th>Program / Event</th>
                <th>Rating</th>
                <th>Comments</th>
                <th>Submitted At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {feedbacks.map((f) => (
                <tr key={f.feedback_id}>
                  <td style={{ color: "var(--text-muted)", fontSize: "0.82rem" }}>#{f.feedback_id}</td>
                  <td style={{ fontWeight: 500 }}>{f.participant_name}</td>
                  <td><span className="tag">{f.program_name}</span></td>
                  <td><RatingBadge rating={f.rating} /></td>
                  <td style={{ maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", color: "var(--text-muted)", fontSize: "0.82rem" }}>
                    {f.comments || "—"}
                  </td>
                  <td style={{ color: "var(--text-muted)", fontSize: "0.82rem", whiteSpace: "nowrap" }}>{formatDate(f.submitted_at)}</td>
                  <td>
                    <div className="actions-cell">
                      <button className="btn btn-ghost btn-sm" onClick={() => setViewItem(f)} title="View">👁</button>
                      <button className="btn btn-ghost btn-sm" onClick={() => setEditItem(f)} title="Edit">✏️</button>
                      <button className="btn btn-danger btn-sm" onClick={() => setDeleteId(f.feedback_id)} title="Delete">🗑</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* View Modal */}
      {viewItem && (
        <DetailModal feedback={viewItem} onClose={() => setViewItem(null)} onEdit={(f) => setEditItem(f)} />
      )}

      {/* Edit Modal */}
      {editItem && (
        <EditModal
          feedback={editItem}
          onClose={() => setEditItem(null)}
          onSaved={() => { setEditItem(null); setAlert({ type: "success", message: "Feedback updated!" }); loadAll(); }}
        />
      )}

      {/* Delete Confirmation */}
      {deleteId && (
        <div className="modal-overlay">
          <div className="modal" style={{ maxWidth: 380 }}>
            <div className="modal-header">
              <h3>Confirm Delete</h3>
              <button className="modal-close" onClick={() => setDeleteId(null)}>×</button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: "0.9rem" }}>Are you sure you want to delete feedback <strong>#{deleteId}</strong>? This action cannot be undone.</p>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setDeleteId(null)}>Cancel</button>
              <button className="btn btn-danger" onClick={handleDelete} disabled={deleting}>
                {deleting ? <><Spinner /> Deleting...</> : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── App Shell ────────────────────────────────────────────────────────────────
function App() {
  const [page, setPage] = useState("dashboard");

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: "📊" },
    { id: "submit", label: "Submit Feedback", icon: "✍️" },
    { id: "list", label: "All Feedback", icon: "📋" },
  ];

  const renderPage = () => {
    if (page === "dashboard") return <Dashboard onNavigate={setPage} />;
    if (page === "submit") return <SubmitFeedback />;
    if (page === "list") return <FeedbackList />;
    return null;
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>Feedback MS</h1>
          <p>Management System</p>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <div
              key={item.id}
              className={`nav-item ${page === item.id ? "active" : ""}`}
              onClick={() => setPage(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </div>
          ))}
        </nav>
      </aside>
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
