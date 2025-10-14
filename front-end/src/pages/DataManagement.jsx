import React, { useState } from 'react';

export default function DataManagement() {
  const [lastSync, setLastSync] = useState(new Date().toLocaleString());
  const [loading, setLoading] = useState(false);

  const handleSync = async (source) => {
    setLoading(true);
    await new Promise((res) => setTimeout(res, 1500));
    setLastSync(new Date().toLocaleString());
    setLoading(false);
    alert(`Synced data from ${source}`);
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-3xl font-bold">Data Management</h1>
      <p className="text-gray-600">Manage data sources, synchronization, and access control.</p>

      <div className="mt-4 space-y-2">
        <p>Last Sync: <strong>{lastSync}</strong></p>
        <div className="space-x-2">
          <button
            onClick={() => handleSync('Excel')}
            disabled={loading}
            className={`px-4 py-2 rounded text-white ${loading ? 'bg-gray-400' : 'bg-yellow-600 hover:bg-yellow-700'}`}
          >
            Upload Excel Data
          </button>
        </div>
      </div>
    </div>
  );
}
