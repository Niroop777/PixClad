// frontend/src/pages/Upload.jsx
import { useState } from "react";
import api from "../api";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return alert("No file selected");

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const res = await api.post("/api/upload", formData); // axios sets content-type automatically
      setResult(res.data.file);
      alert("Upload successful");
    } catch (err) {
      console.error(err);
      alert("Upload failed: " + (err.response?.data?.msg || err.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex justify-center items-center h-[80vh]">
      <form
        onSubmit={handleUpload}
        className="bg-white shadow-lg rounded-2xl p-6 w-80 flex flex-col gap-4"
      >
        <h2 className="text-xl font-bold text-center">Upload File</h2>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit" className="bg-green-600 text-white p-2 rounded" disabled={uploading}>
          {uploading ? "Uploading..." : "Upload"}
        </button>

        {result && (
          <div className="mt-4 text-left">
            <p><strong>Name:</strong> {result.name}</p>
            <p><strong>Type:</strong> {result.type}</p>
            <p><strong>Category:</strong> {result.category}</p>
            <p><strong>Confidence:</strong> {result.confidence ?? "N/A"}</p>
            <a href={result.url} target="_blank" rel="noreferrer" className="text-blue-600 underline">
              Open file
            </a>
          </div>
        )}
      </form>
    </div>
  );
}
