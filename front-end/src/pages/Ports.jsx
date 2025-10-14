import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/main/v1/data/ports";

export default function Ports() {
  const location = useLocation();
  const navigate = useNavigate();
  const selectedPort = location.state?.selectedPort;

  const [portsData, setPortsData] = useState([]);
  const [filteredPorts, setFilteredPorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPortsData = async () => {
    try {
      const res = await fetch(API_BASE);
      if (!res.ok) throw new Error(`API Error: ${res.status} ${res.statusText}`);
      const data = await res.json();
      const allData = Array.isArray(data.data) ? data.data : [];
      setPortsData(allData);
    } catch (err) {
      console.error("Error fetching ports:", err);
      setError("Failed to fetch port data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortsData();
  }, []);

  useEffect(() => {
    if (selectedPort) {
      const matches = portsData.filter(
        (item) => item.port_name === selectedPort.port_name
      );
      setFilteredPorts(matches);
    } else {
      const uniquePorts = portsData.filter(
        (item, index, self) =>
          index === self.findIndex((x) => x.port_name === item.port_name)
      );
      setFilteredPorts(uniquePorts);
    }
  }, [selectedPort, portsData]);

  const handlePortClick = (port) => {
    navigate("/ports", { state: { selectedPort: port } });
  };

  const displayNumber = (value) =>
    value !== null && value !== undefined && value !== ""
      ? Number(value).toLocaleString()
      : "N/A";

  if (loading) return <p className="p-6 text-gray-600">Loading ports...</p>;
  if (error) return <p className="p-6 text-red-600">{error}</p>;

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-8 space-y-8 font-inter">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
        Port
      </h1>

      {selectedPort ? (
        <div className="text-lg text-gray-700 p-4 bg-white rounded-xl shadow border-l-4 border-teal-500 flex justify-between items-center">
          <p className="font-semibold">
            Showing All Records for{" "}
            <span className="text-teal-600">{selectedPort.port_name}</span>
          </p>
          <button
            onClick={() => navigate("/ports")}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition shadow-md font-medium"
          >
            Back to All Ports
          </button>
        </div>
      ) : (
        <p className="text-sm text-gray-500">
          View all historical records. (Showing {filteredPorts.length}  ports)
        </p>
      )}

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filteredPorts.map((port, index) => (
          <div
            key={`${port.port_name}-${index}`}
            onClick={() => !selectedPort && handlePortClick(port)}
            className={`bg-white p-6 rounded-xl shadow-lg border-t-4 border-indigo-400 transition duration-200 ${
              !selectedPort
                ? "cursor-pointer hover:shadow-xl hover:scale-[1.03]"
                : ""
            } space-y-2`}
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {port.port_name || "Unknown Port"}
            </h2>

            {selectedPort && (
              <p className="text-sm text-gray-600">
                <span className="font-semibold text-teal-600">Record Date:</span>{" "}
                {port.date || "N/A"}
              </p>
            )}

            <div className="space-y-1 text-sm">
              <p className="text-gray-700">
                <span className="font-medium text-indigo-500">
                  Coal Stock (tonnes):
                </span>{" "}
                {displayNumber(port.coal_eod_storage_tonnes)}
              </p>

              <p className="text-gray-700">
                <span className="font-medium text-orange-500">
                  Limestone Stock (tonnes):
                </span>{" "}
                {displayNumber(port.limestone_eod_storage_tonnes)}
              </p>

              <p className="text-gray-700 font-bold border-t pt-2 mt-2">
                <span className="font-medium text-gray-800">
                  Total Cargo Flow Today (tonnes):
                </span>{" "}
                {displayNumber(port.total_cargo_flow_today_tonnes)}
              </p>

              <p className="text-gray-600">
                <span className="font-medium">Coal Arrived:</span>{" "}
                {displayNumber(port.coal_arrived_tonnes)}
              </p>

              <p className="text-gray-600">
                <span className="font-medium">Limestone Arrived:</span>{" "}
                {displayNumber(port.limestone_arrived_tonnes)}
              </p>

              <p className="text-gray-600">
                <span className="font-medium">Steel Exported:</span>{" "}
                {displayNumber(port.steel_arrived_tonnes)}
              </p>

              <p className="text-gray-700 pt-1">
                <span className="font-medium text-teal-600">
                  Steel Storage Utilization (%):
                </span>{" "}
                {port.steel_storage_utilization_percent
                  ? `${port.steel_storage_utilization_percent}%`
                  : "N/A"}
              </p>
            </div>
          </div>
        ))}
      </div>

      {!selectedPort && (
        <p className="text-center text-gray-500 text-sm mt-4">
          Data sourced from API. Click a card to view historical records.
        </p>
      )}
    </div>
  );
}
