import React, { useState } from "react";
import axios from "axios";

const TABLE_OPTIONS = [
  { label: "Plants", value: "plants" },
  { label: "Ports", value: "ports" },
  { label: "Trains", value: "trains" },
  { label: "Vessels", value: "vessels" },
  { label: "Port Tariffs", value: "port_tariffs" },
  { label: "Vessel Delay History", value: "vessel_delay_history" },
];

export default function ExcelUploader() {
  const [table, setTable] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!table || !file) {
      alert("Please select a table and a file.");
      return;
    }

    // 1. Create a fresh FormData object for the submission
    const formData = new FormData();
    formData.append("table", table);
    formData.append("file", file);

    setLoading(true);
    setResponse(null);

    try {
      // 2. IMPORTANT: Pass ONLY the formData object. 
      //    Do not pass any manual headers or config.
      const res = await axios.post(
        "http://127.0.0.1:5000/api/main/v1/data/upload-excel",
        formData
      );
      setResponse(res.data);
      alert("Excel uploaded successfully! 🎉");
    } catch (err) {
      console.error("Upload Error:", err.response?.data || err.message);
      // Display the actual error message from the backend if available
      setResponse(err.response?.data || { message: "Network or Server Error", details: err.message });
      alert("Upload failed. See the response display for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-4 bg-white shadow rounded">
      <h2 className="text-lg font-semibold mb-4">Upload Excel File</h2>

      <form onSubmit={handleSubmit}>
        {/* Table selection */}
        <div className="mb-4">
          <label className="block mb-2 font-medium">Choose Table:</label>
          <div className="flex flex-wrap gap-4">
            {TABLE_OPTIONS.map((opt) => (
              <label key={opt.value} className="flex items-center gap-2">
                <input
                  type="radio"
                  name="table"
                  value={opt.value}
                  checked={table === opt.value}
                  onChange={() => setTable(opt.value)}
                  className="accent-yellow-500"
                />
                {opt.label}
              </label>
            ))}
          </div>
        </div>

        {/* File input */}
        <div className="mb-4">
          <label className="block mb-2 font-medium">Choose Excel File:</label>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full p-2 border-2 border-dashed border-gray-300 rounded cursor-pointer hover:border-yellow-500"
          />
          {file && <p className="mt-1 text-sm text-gray-600">{file.name}</p>}
        </div>

        {/* Submit */}
        <button
          type="submit"
          className={`w-full py-2 px-4 rounded bg-yellow-500 text-white font-semibold hover:bg-yellow-600 transition ${
            loading ? "opacity-50 cursor-not-allowed" : ""
          }`}
          disabled={loading}
        >
          {loading ? "Uploading..." : "Upload"}
        </button>
      </form>

      {/* Response display */}
      {response && (
        <pre className="mt-4 p-2 bg-gray-100 rounded text-sm overflow-auto">
          {JSON.stringify(response, null, 2)}
        </pre>
      )}
    </div>
  );
}