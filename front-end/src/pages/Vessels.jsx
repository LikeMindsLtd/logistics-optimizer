import React, { useEffect, useState } from 'react';

const PAGE_SIZE = 100; // Load 100 records per page
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/main/v1/data/vessels";

const Vessels = () => {
  const [vessels, setVessels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [allLoaded, setAllLoaded] = useState(false);

  // Fetch vessels/contracts from API
  const fetchVessels = async (currentPage) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}?page=${currentPage}&limit=${PAGE_SIZE}`);
      if (!res.ok) throw new Error(`API Error: ${res.status} ${res.statusText}`);
      const data = await res.json();

      if (!data.data || data.data.length === 0) {
        setAllLoaded(true);
      } else {
        setVessels((prev) => {
          const newVessels = data.data.filter(
            (v) => !prev.some(
              (existing) => existing.vessel_id === v.vessel_id && existing.load_port === v.load_port
            )
          );
          return [...prev, ...newVessels];
        });
      }
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch contract data from the API.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVessels(page);

    // Optional: Poll API every 15s to keep data fresh
    const interval = setInterval(() => fetchVessels(1), 15000);
    return () => clearInterval(interval);
  }, [page]);

  const handleLoadMore = () => {
    if (!loading && !allLoaded) setPage((prev) => prev + 1);
  };

  const getDemurrageClass = (rate) => {
    if (rate > 100000) return 'bg-red-100 text-red-800 font-bold';
    if (rate > 75000) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  if (error && vessels.length === 0) {
    return (
      <div className="p-8 text-center bg-gray-50 min-h-screen">
        <p className="p-4 bg-red-100 text-red-700 rounded-xl shadow-md border border-red-200">{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-8 space-y-8 font-inter">
      <h1 className="text-4xl font-extrabold text-gray-900 border-b-4 border-indigo-200 pb-3">
        Ocean Freight Contract & Cost Analysis
      </h1>
      <p className="text-sm text-gray-500">
        Monitoring long-term charter party contracts and associated cost risks like demurrage.
      </p>

      {loading && vessels.length === 0 && (
        <div className="flex justify-center items-center h-64">
          <svg className="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          <p className="text-lg text-gray-600 ml-3">Fetching contract data...</p>
        </div>
      )}

      {vessels.length > 0 && (
        <div className="overflow-x-auto bg-white rounded-xl shadow-lg border border-gray-100">
          <table className="min-w-full divide-y divide-gray-200">
            <caption className="p-4 text-xl font-semibold text-left text-gray-700 bg-white">
              Vessel Contract Details ({vessels.length} records loaded)
            </caption>
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="py-3 px-4 text-xs font-medium text-gray-500 uppercase text-left rounded-tl-xl">Vessel ID</th>
                <th className="py-3 px-4 text-xs font-medium text-gray-500 uppercase text-left">Route & Material</th>
                <th className="py-3 px-4 text-xs font-medium text-gray-500 uppercase text-right">Quantity (t)</th>
                <th className="py-3 px-4 text-xs font-medium text-gray-500 uppercase text-right">Laydays (h)</th>
                <th className="py-3 px-4 text-xs font-medium text-gray-500 uppercase text-right">Freight (INR/t)</th>
                <th className="py-3 px-4 text-xs font-medium text-gray-500 uppercase text-right">Demurrage Rate (INR/hr)</th>
                <th className="py-3 px-4 text-xs font-medium text-gray-500 uppercase text-right rounded-tr-xl">Daily Demurrage Risk (INR)</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {vessels.map((v, index) => {
                const dailyDemurrage = v.demurrage_rate_inr_hr * 24;
                return (
                  <tr key={v.vessel_id + index} className="hover:bg-indigo-50/50 transition duration-150">
                    <td className="py-3 px-4 text-sm font-medium text-gray-900">{v.vessel_id}</td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      <p className="font-semibold text-gray-800">{v.load_port} → {v.discharge_port}</p>
                      <p className="text-xs text-indigo-500 font-medium">{v.material}</p>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-sm font-medium text-gray-700 text-right">
                      {v.contract_quantity_tonnes.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-600 text-right">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${v.laydays_allowed_hours < 96 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                        {v.laydays_allowed_hours}
                      </span>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-600 text-right">
                      ₹{v.ocean_freight_inr_tonne.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-sm text-right">
                      ₹{v.demurrage_rate_inr_hr.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-sm font-bold text-gray-800 text-right">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-lg ${getDemurrageClass(dailyDemurrage)}`}>
                        ₹{dailyDemurrage.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Load More Button */}
      <div className="flex justify-center items-center mt-6 space-x-4">
        {!allLoaded && (
          <button
            onClick={handleLoadMore}
            disabled={loading}
            className={`px-6 py-3 text-lg font-medium rounded-xl shadow-lg transition duration-300 transform active:scale-95 ${
              loading
                ? 'bg-gray-400 text-gray-700 cursor-not-allowed flex items-center'
                : 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-indigo-500 focus:ring-opacity-50'
            }`}
          >
            {loading ? 'Loading...' : `Load More Contracts (Page ${page + 1})`}
          </button>
        )}
        {allLoaded && (
          <p className="text-lg font-medium text-green-700 bg-green-100 p-3 rounded-lg shadow-md border border-green-200">
            All {vessels.length} contract records loaded!
          </p>
        )}
      </div>
    </div>
  );
};

export default Vessels;
