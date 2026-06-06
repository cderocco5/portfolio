import Card from "../components/Card";
import Chart from "../components/Chart";

export default function Dashboard() {
  // Sample alert data
  const alerts = [
    { severity: "high", time: "10:00" },
    { severity: "medium", time: "11:00" },
    { severity: "low", time: "12:00" },
    { severity: "high", time: "13:00" },
  ];

  const chartData = alerts.map((a, idx) => ({
    time: a.time,
    count: idx + 1,
  }));

  return (
    <div className="p-4 grid grid-cols-3 gap-4">
      <Card title="Total Alerts" value={alerts.length} />
      <Card title="High Severity" value={alerts.filter(a => a.severity === "high").length} />
      <Chart data={chartData} />
    </div>
  );
}