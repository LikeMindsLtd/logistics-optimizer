// Export your logistics data as a JS object
const logisticsData = {
  steelPlants: [
    { name: "Bhilai Steel Plant", location: "Chhattisgarh" },
    { name: "Durgapur Steel Plant", location: "West Bengal" },
    { name: "Rourkela Steel Plant", location: "Odisha" },
    { name: "Bokaro Steel Plant", location: "Jharkhand" },
    { name: "IISCO Steel Plant", location: "West Bengal" }
  ],
  trainLogistics: [
    { rakeNo: "38547", route: "Paradip → Rourkela" },
    { rakeNo: "39211", route: "Paradip → Bhilai" },
    { rakeNo: "40258", route: "Vizag → Bhilai" },
    { rakeNo: "41274", route: "Vizag → Rourkela" },
    { rakeNo: "42381", route: "Haldia → Durgapur" },
    { rakeNo: "43792", route: "Haldia → Bokaro" },
    { rakeNo: "44903", route: "Haldia → Burnpur" }
  ],
  importVessels: [
    { shipName: "Vishva Vijeta", capacityDWT: 56638 },
    { shipName: "Vishva Malhar", capacityDWT: 56616 },
    { shipName: "Swarna Mala", capacityDWT: 51196 },
    { shipName: "Swarna Kalash", capacityDWT: 47878 },
    { shipName: "Vishva Nidhi", capacityDWT: 50000 },
    { shipName: "Sampurna Swarajya", capacityDWT: 32950 },
    { shipName: "Suvarna Swarajya", capacityDWT: 32902 },
    { shipName: "Swarna Pushp", capacityDWT: 47795 }
  ],
  portToPlantLogistics: [
    { port: "Paradip Port" },
    { port: "Vizag Port" },
    { port: "Haldia Port" },
    { port: "Kolkata/Haldia" }
  ]
};

export default logisticsData;
