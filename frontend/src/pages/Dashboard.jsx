// frontend/src/pages/Dashboard.jsx
import { useEffect, useState } from "react";
import api from "../api";

export default function Dashboard() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await api.get("/api/files");
        setFiles(res.data.files || []);
      } catch (err) {
        console.error(err);
        alert("Failed to fetch files: " + (err.response?.data?.msg || err.message));
      } finally {
        setLoading(false);
      }
    };
    fetchFiles();
  }, []);

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <div className="mt-4 grid grid-cols-1 gap-4">
        {files.length === 0 ? (
          <p>No files yet</p>
        ) : (
          files.map((f) => (
            <div key={f.id} className="p-4 border rounded">
              <p><strong>{f.name}</strong></p>
              <p>Type: {f.type} | Category: {f.category}</p>
              <a href={f.url} target="_blank" rel="noreferrer" className="text-blue-600 underline">Open</a>
              <p className="text-xs text-gray-500">Uploaded: {new Date(f.created_at).toLocaleString()}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
