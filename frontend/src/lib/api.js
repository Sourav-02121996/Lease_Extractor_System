import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";
export const API = `${BACKEND_URL}/api`;

const client = axios.create({ baseURL: API });

export const getStats = () => client.get("/documents/stats").then((r) => r.data);
export const listDocuments = () => client.get("/documents").then((r) => r.data);
export const getDocument = (id) => client.get(`/documents/${id}`).then((r) => r.data);
export const uploadDocument = (formData, onProgress) =>
  client
    .post("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: onProgress,
    })
    .then((r) => r.data);
export const saveDraft = (id, fields) =>
  client.put(`/documents/${id}/draft`, { fields }).then((r) => r.data);
export const approveDocument = (id, fields) =>
  client.post(`/documents/${id}/approve`, { fields }).then((r) => r.data);
export const getApprovedCount = () =>
  client.get("/export/approved/count").then((r) => r.data);

export const exportUrl = `${API}/export/approved`;
export const exportExcelUrl = `${API}/export/approved/excel`;

export default client;
