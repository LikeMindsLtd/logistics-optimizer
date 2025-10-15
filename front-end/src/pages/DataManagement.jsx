import { useState } from 'react'; 
import ExcelUploader from '../components/ExcelUploader';
import AITrainingTrigger from '../components/AITrainingTrigger';

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
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Data Management</h1>
      <p className="text-gray-600">Manage data sources, synchronization, and model training.</p>

      <AITrainingTrigger />
      <div className="space-y-4 pt-4 border-t">
        <h2 className="text-2xl font-semibold">Data Operations</h2>
        <p>Last System Data Sync: <strong>{lastSync}</strong></p>
        <div className="space-x-4 flex">
          <ExcelUploader />
        </div>
      </div>
    </div>
  );
}