import React, { useEffect, useState } from 'react';

const PAGE_SIZE = 100; // Load 100 records at a time
const API_BASE = "http://localhost:8000/api/main/v1/data/trains";

// Helper: Fetch trains from API with pagination
const fetchTrainsAPI = async (page, limit) => {
  const res = await fetch(`${API_BASE}?page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  const data = await res.json();
  return Array.isArray(data.data) ? data.data : [];
};

const Trains = () => {
  const [trains, setTrains] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [allLoaded, setAllLoaded] = useState(false);
  const [error, setError] = useState(null);

  const fetchTrains = async (currentPage = 1) => {
    setLoading(true);
    try {
      const newData = await fetchTrainsAPI(currentPage, PAGE_SIZE);

      if (newData.length === 0) {
        setAllLoaded(true);
      } else {
        setTrains(prev => {
          const combined = [...prev];
          newData.forEach(item => {
            if (!combined.some(t => t.trip_id === item.trip_id)) {
              combined.push(item);
            }
          });
          return combined;
        });
      }

      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch train data.");
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch + polling for latest page
  useEffect(() => {
    fetchTrains(page);

    const interval = setInterval(() => {
      fetchTrains(page);
    }, 10000);

    return () => clearInterval(interval);
  }, [page]);

  const handleLoadMore = () => {
    if (!loading && !allLoaded) setPage(prev => prev + 1);
  };

  const getDelayClass = (delay) => {
    if (delay > 10) return 'bg-red-100 text-red-800';
    if (delay > 5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  if (error && trains.length === 0) return <p className="p-6 text-red-600">{error}</p>;

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-3xl font-bold">Train Logistics & Trip Analysis</h1>
      <p className="text-gray-600">Monitoring raw materials and finished goods via rail (Loaded: {trains.length} trips)</p>

      <div className="overflow-x-auto bg-white rounded-xl shadow border">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="px-4 py-2 text-left">Trip ID</th>
              <th className="px-4 py-2 text-left">Flow</th>
              <th className="px-4 py-2 text-left">Material</th>
              <th className="px-4 py-2 text-left">Route</th>
              <th className="px-4 py-2 text-right">Qty (t)</th>
              <th className="px-4 py-2 text-right">Distance (km)</th>
              <th className="px-4 py-2 text-right">Total Time (h)</th>
              <th className="px-4 py-2 text-right">Delay (h)</th>
              <th className="px-4 py-2 text-right">Total Cost (INR)</th>
            </tr>
          </thead>
          <tbody>
            {trains.map(t => (
              <tr key={t.trip_id} className="hover:bg-indigo-50/50">
                <td className="px-4 py-2">{t.trip_id}</td>
                <td className="px-4 py-2">
                  <span className={`px-2 inline-flex text-xs font-semibold rounded-full ${t.material_flow==='Inbound'?'bg-indigo-100 text-indigo-800':'bg-pink-100 text-pink-800'}`}>
                    {t.material_flow}
                  </span>
                </td>
                <td className="px-4 py-2">{t.material}</td>
                <td className="px-4 py-2">{t.source} → {t.destination}</td>
                <td className="px-4 py-2 text-right">{t.quantity_tonnes.toLocaleString()}</td>
                <td className="px-4 py-2 text-right">{t.distance_km.toLocaleString()}</td>
                <td className="px-4 py-2 text-right">{t.total_time_h.toFixed(1)}</td>
                <td className="px-4 py-2 text-right">
                  <span className={`px-2 inline-flex text-xs font-semibold rounded-full ${getDelayClass(t.delay_h)}`}>
                    {t.delay_h.toFixed(1)}
                  </span>
                </td>
                <td className="px-4 py-2 text-right">₹{t.total_trip_cost_inr.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Load More Button */}
      <div className="flex justify-center mt-6">
        {!allLoaded ? (
          <button
            onClick={handleLoadMore}
            disabled={loading}
            className={`px-6 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 ${loading ? 'cursor-not-allowed opacity-70' : ''}`}
          >
            {loading ? "Loading..." : `Load More (Next 100)`} 
          </button>
        ) : (
          <p className="text-green-700 font-semibold">All {trains.length} trips loaded!</p>
        )}
      </div>
    </div>
  );
};

export default Trains;
